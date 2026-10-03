from datetime import datetime

from backend.Repositories.appointment_repository import AppointmentRepository
from backend.Repositories.doctoravailbility_repository import (
    DoctorAvailabilityRepository,
)


class AppointmentService:
    def __init__(self, session):
        self.session = session
        self.appointment_repository = AppointmentRepository(session)
        self.availability_repository = DoctorAvailabilityRepository(session)

    def book_appointment(
        self,
        patient_id,
        doctor_id,
        appointment_date,
        slot_id,
        status="Scheduled",
    ):
        """Book an appointment and mark the slot as booked.

        Returns the Appointment, or None if the slot is already taken
        (either an existing appointment or a non-available slot).
        """
        # Prevent double-booking the same doctor/date/slot.
        conflict = self.appointment_repository.get_slot_appointment(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            slot_id=slot_id,
        )
        if conflict is not None:
            return None

        # Reserve the slot (fails if the slot isn't available).
        slot = self.availability_repository.get_slot_by_id(slot_id)
        if slot is not None:
            booked = self.availability_repository.book_slot(slot_id)
            if booked is None:
                return None

        return self.appointment_repository.create(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            slot_id=slot_id,
            status=status,
        )

    def get_appointment(self, appointment_id):
        return self.appointment_repository.get_by_id(appointment_id)

    def get_appointments_for_patient(self, patient_id):
        return self.appointment_repository.get_by_patient_id(patient_id)

    def get_appointments_for_doctor(self, doctor_id):
        return self.appointment_repository.get_by_doctor_id(doctor_id)

    def cancel_appointment(self, appointment_id):
        """Cancel an appointment and release its slot."""
        appointment = self.appointment_repository.get_by_id(appointment_id)
        if appointment is None:
            return None

        # Free the slot so it can be booked again.
        if appointment.slot_id is not None:
            self.availability_repository.release_slot(appointment.slot_id)

        return self.appointment_repository.update(
            appointment, status="Cancelled"
        )

    def reschedule_appointment(
        self,
        appointment_id,
        new_slot_id,
        new_appointment_date=None,
    ):
        """Move an existing appointment to a new slot (and optionally a new
        date). Releases the old slot, books the new one, and updates the
        appointment.

        Returns a dict describing the outcome so callers (tools) can relay a
        clear message:
            {"ok": True, "appointment": <Appointment>}
            {"ok": False, "reason": "not_found" | "slot_unavailable" |
                                     "slot_conflict" | "bad_date"}
        """
        appointment = self.appointment_repository.get_by_id(appointment_id)
        if appointment is None:
            return {"ok": False, "reason": "not_found"}

        doctor_id = appointment.doctor_id

        # Resolve/validate the target date.
        if new_appointment_date is None:
            target_date = appointment.appointment_date
        elif isinstance(new_appointment_date, datetime):
            target_date = new_appointment_date
        else:
            return {"ok": False, "reason": "bad_date"}

        # New slot must exist and be available.
        new_slot = self.availability_repository.get_slot_by_id(new_slot_id)
        if new_slot is None or new_slot.status != "available":
            return {"ok": False, "reason": "slot_unavailable"}

        # No other active appointment should hold the new slot.
        conflict = self.appointment_repository.get_slot_appointment(
            doctor_id=doctor_id,
            appointment_date=target_date,
            slot_id=new_slot_id,
            exclude_appointment_id=appointment_id,
        )
        if conflict is not None:
            return {"ok": False, "reason": "slot_conflict"}

        # Release the old slot, book the new one, update the appointment.
        old_slot_id = appointment.slot_id
        if old_slot_id is not None and old_slot_id != new_slot_id:
            self.availability_repository.release_slot(old_slot_id)

        self.availability_repository.book_slot(new_slot_id)

        updated = self.appointment_repository.update(
            appointment,
            slot_id=new_slot_id,
            appointment_date=target_date,
            status="Scheduled",
        )
        return {"ok": True, "appointment": updated}
