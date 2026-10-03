"""Tests for the receptionist capabilities: patient identification by
phone+name, and the per-call state store that updates from patient and AI
turns and persists across turns.
"""

from backend.services.call_state_service import CallStateService
from backend.services.patient_service import PatientService


# ===========================================================================
# identify_patient (phone + name)
# ===========================================================================
class TestIdentify:
    def test_identify_match(self, session, seeded):
        svc = PatientService(session)
        result = svc.identify_patient(
            seeded["patient"].phone_number, "Jane"
        )
        assert result["found"] is True
        assert result["patient"].id == seeded["patient"].id

    def test_identify_full_name_match(self, session, seeded):
        svc = PatientService(session)
        result = svc.identify_patient(
            seeded["patient"].phone_number, "Jane Doe"
        )
        assert result["found"] is True

    def test_identify_name_mismatch(self, session, seeded):
        svc = PatientService(session)
        result = svc.identify_patient(
            seeded["patient"].phone_number, "Robert"
        )
        assert result["found"] is False
        assert result["reason"] == "name_mismatch"
        assert result["patient_on_file"] == "Jane Doe"

    def test_identify_no_phone_match(self, session):
        svc = PatientService(session)
        result = svc.identify_patient("000-0000", "Nobody")
        assert result["found"] is False
        assert result["reason"] == "no_phone_match"


# ===========================================================================
# Call state updates (from patient + AI turns), persisted across turns
# ===========================================================================
class TestCallState:
    def test_state_accumulates_across_turns(self, session):
        svc = CallStateService(session)
        tid = "caller-xyz"

        # Turn 1: identity recorded after identify
        svc.update(
            tid,
            patient_name="Jane Doe",
            patient_phone_number="555-0101",
            existing_patient="yes",
            stage="reason",
        )
        # Turn 2: reason -> call_type
        svc.update(
            tid,
            reason_for_call="I'd like to book with a cardiologist",
            call_type="book",
            stage="booking",
        )
        # Turn 3: booking details
        svc.update(
            tid,
            doctor_name="Dr. Smith",
            preferred_date="2026-10-10",
            preferred_time="9 AM",
        )

        state = svc.get(tid)
        # Everything from all three turns is present together.
        assert state["patient_name"] == "Jane Doe"
        assert state["existing_patient"] == "yes"
        assert state["reason_for_call"].startswith("I'd like to book")
        assert state["call_type"] == "book"
        assert state["doctor_name"] == "Dr. Smith"
        assert state["preferred_date"] == "2026-10-10"
        assert state["preferred_time"] == "9 AM"
        assert state["stage"] == "booking"

    def test_state_isolated_per_thread(self, session):
        svc = CallStateService(session)
        svc.update("callerA", call_type="book")
        svc.update("callerB", call_type="cancel")
        assert svc.get("callerA")["call_type"] == "book"
        assert svc.get("callerB")["call_type"] == "cancel"

    def test_blank_values_do_not_overwrite(self, session):
        svc = CallStateService(session)
        tid = "caller-keep"
        svc.update(tid, patient_name="Jane Doe")
        # A later update with a blank name must not wipe the stored name.
        svc.update(tid, patient_name="", call_type="book")
        state = svc.get(tid)
        assert state["patient_name"] == "Jane Doe"
        assert state["call_type"] == "book"
