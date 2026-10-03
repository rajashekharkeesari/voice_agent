"""Success/fail matrix for AI <-> patient conversation capabilities.

Each test maps to a thing a patient might ask the voice assistant. Grouped
into:
  - SUCCESS: flows the system fully supports.
  - FAIL-BY-DESIGN: requests that correctly return a failure (double-book,
    bad date, not found) so the AI can relay a clear message.

Routing tests confirm the keyword router sends utterances to the right branch.
"""

from datetime import datetime

import pytest

from backend.nodes.conditional_node import route_from_input
from backend.services.appointment_service import AppointmentService
from backend.services.doctorservice import DoctorService
from backend.services.hospitalavailability_service import (
    DoctorAvailabilityService,
)
from backend.services.patient_service import PatientService


# ===========================================================================
# SUCCESS cases
# ===========================================================================
class TestSuccess:
    def test_register_patient(self, session):
        svc = PatientService(session)
        p = svc.register_patient("John Roe", 30, "555-0199")
        assert p.id is not None
        assert svc.get_patient_by_phone("555-0199").name == "John Roe"

    def test_find_doctor_by_name(self, session, seeded):
        svc = DoctorService(session)
        results = svc.find_doctors_by_name("smith")  # case-insensitive partial
        assert len(results) == 1
        assert results[0].id == seeded["doctor"].id

    def test_find_patient_by_name(self, session, seeded):
        svc = PatientService(session)
        results = svc.find_patients_by_name("jane")
        assert len(results) == 1
        assert results[0].id == seeded["patient"].id

    def test_list_available_slots(self, session, seeded):
        svc = DoctorAvailabilityService(session)
        slots = svc.list_available_slots(seeded["doctor"].id, seeded["date"])
        assert len(slots) == 2
        assert all(s.status == "available" for s in slots)

    def test_book_appointment_marks_slot_booked(self, session, seeded):
        appt_svc = AppointmentService(session)
        avail_svc = DoctorAvailabilityService(session)

        appt = appt_svc.book_appointment(
            patient_id=seeded["patient"].id,
            doctor_id=seeded["doctor"].id,
            appointment_date=datetime(2026, 10, 10, 9, 0),
            slot_id=seeded["slot1"].id,
        )
        assert appt is not None
        assert appt.status == "Scheduled"
        # The booked slot should no longer be listed as available.
        remaining = avail_svc.list_available_slots(
            seeded["doctor"].id, seeded["date"]
        )
        assert seeded["slot1"].id not in {s.id for s in remaining}

    def test_cancel_releases_slot(self, session, seeded):
        appt_svc = AppointmentService(session)
        avail_svc = DoctorAvailabilityService(session)

        appt = appt_svc.book_appointment(
            patient_id=seeded["patient"].id,
            doctor_id=seeded["doctor"].id,
            appointment_date=datetime(2026, 10, 10, 9, 0),
            slot_id=seeded["slot1"].id,
        )
        cancelled = appt_svc.cancel_appointment(appt.id)
        assert cancelled.status == "Cancelled"
        # Slot is available again after cancellation.
        available_ids = {
            s.id
            for s in avail_svc.list_available_slots(
                seeded["doctor"].id, seeded["date"]
            )
        }
        assert seeded["slot1"].id in available_ids

    def test_reschedule_moves_to_new_slot(self, session, seeded):
        appt_svc = AppointmentService(session)
        avail_svc = DoctorAvailabilityService(session)

        appt = appt_svc.book_appointment(
            patient_id=seeded["patient"].id,
            doctor_id=seeded["doctor"].id,
            appointment_date=datetime(2026, 10, 10, 9, 0),
            slot_id=seeded["slot1"].id,
        )
        result = appt_svc.reschedule_appointment(
            appointment_id=appt.id,
            new_slot_id=seeded["slot2"].id,
        )
        assert result["ok"] is True
        assert result["appointment"].slot_id == seeded["slot2"].id

        available_ids = {
            s.id
            for s in avail_svc.list_available_slots(
                seeded["doctor"].id, seeded["date"]
            )
        }
        # Old slot freed, new slot taken.
        assert seeded["slot1"].id in available_ids
        assert seeded["slot2"].id not in available_ids

    def test_list_patient_appointments(self, session, seeded):
        appt_svc = AppointmentService(session)
        appt_svc.book_appointment(
            patient_id=seeded["patient"].id,
            doctor_id=seeded["doctor"].id,
            appointment_date=datetime(2026, 10, 10, 9, 0),
            slot_id=seeded["slot1"].id,
        )
        appts = appt_svc.get_appointments_for_patient(seeded["patient"].id)
        assert len(appts) == 1


# ===========================================================================
# FAIL-BY-DESIGN cases (correct, clear failures the AI should relay)
# ===========================================================================
class TestFailByDesign:
    def test_double_book_same_slot_fails(self, session, seeded):
        appt_svc = AppointmentService(session)
        first = appt_svc.book_appointment(
            patient_id=seeded["patient"].id,
            doctor_id=seeded["doctor"].id,
            appointment_date=datetime(2026, 10, 10, 9, 0),
            slot_id=seeded["slot1"].id,
        )
        assert first is not None
        # Second booking of the same slot must fail.
        second = appt_svc.book_appointment(
            patient_id=seeded["patient"].id,
            doctor_id=seeded["doctor"].id,
            appointment_date=datetime(2026, 10, 10, 9, 0),
            slot_id=seeded["slot1"].id,
        )
        assert second is None

    def test_cancel_unknown_appointment_fails(self, session):
        appt_svc = AppointmentService(session)
        assert appt_svc.cancel_appointment(9999) is None

    def test_reschedule_unknown_appointment_fails(self, session, seeded):
        appt_svc = AppointmentService(session)
        result = appt_svc.reschedule_appointment(
            appointment_id=9999, new_slot_id=seeded["slot2"].id
        )
        assert result == {"ok": False, "reason": "not_found"}

    def test_reschedule_to_taken_slot_fails(self, session, seeded):
        appt_svc = AppointmentService(session)
        # Book slot1 and slot2 with two appointments.
        a1 = appt_svc.book_appointment(
            patient_id=seeded["patient"].id,
            doctor_id=seeded["doctor"].id,
            appointment_date=datetime(2026, 10, 10, 9, 0),
            slot_id=seeded["slot1"].id,
        )
        appt_svc.book_appointment(
            patient_id=seeded["patient"].id,
            doctor_id=seeded["doctor"].id,
            appointment_date=datetime(2026, 10, 10, 9, 30),
            slot_id=seeded["slot2"].id,
        )
        # Try to move a1 onto slot2 (already booked) -> unavailable.
        result = appt_svc.reschedule_appointment(
            appointment_id=a1.id, new_slot_id=seeded["slot2"].id
        )
        assert result["ok"] is False
        assert result["reason"] in ("slot_unavailable", "slot_conflict")

    def test_find_unknown_doctor_returns_empty(self, session, seeded):
        svc = DoctorService(session)
        assert svc.find_doctors_by_name("nonexistent") == []


# ===========================================================================
# ROUTING matrix
# ===========================================================================
@pytest.mark.parametrize(
    "utterance,expected",
    [
        ("I want to book an appointment", "appointment"),
        ("Can I reschedule my visit?", "appointment"),
        ("Please cancel my booking", "appointment"),
        ("What slots are available on Friday?", "appointment"),
        ("I need to see a doctor", "appointment"),
        ("move my appointment to tomorrow", "appointment"),
        ("What are your opening hours?", "supervisor"),
        ("Where is the hospital located?", "supervisor"),
        ("Hello", "supervisor"),
    ],
)
def test_routing(utterance, expected):
    assert route_from_input({"input": utterance}) == expected
