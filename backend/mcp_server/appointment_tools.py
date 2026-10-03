from datetime import datetime

from backend.db.connection import SessionLocal
from backend.services.appointment_service import AppointmentService


def _parse_date(value):
    """Accept ISO date/datetime strings; return a datetime or None."""
    if not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def register_appointment_tools(mcp):

    @mcp.tool()
    def book_appointment(
        patient_id: int,
        doctor_id: int,
        appointment_date: str,
        slot_id: int,
    ):
        """Book an appointment. appointment_date is an ISO string
        (YYYY-MM-DD or YYYY-MM-DDTHH:MM)."""
        parsed = _parse_date(appointment_date)
        if parsed is None:
            return {
                "success": False,
                "message": "Invalid appointment_date. Use YYYY-MM-DD.",
            }

        db = SessionLocal()
        try:
            service = AppointmentService(db)
            appointment = service.book_appointment(
                patient_id=patient_id,
                doctor_id=doctor_id,
                appointment_date=parsed,
                slot_id=slot_id,
            )
            if appointment is None:
                return {
                    "success": False,
                    "message": "That slot is already booked.",
                }
            return {
                "success": True,
                "appointment": {
                    "id": appointment.id,
                    "patient_id": appointment.patient_id,
                    "doctor_id": appointment.doctor_id,
                    "appointment_date": appointment.appointment_date.isoformat(),
                    "slot_id": appointment.slot_id,
                    "status": appointment.status,
                },
            }
        finally:
            db.close()

    @mcp.tool()
    def get_patient_appointments(patient_id: int):
        """List all appointments for a patient."""
        db = SessionLocal()
        try:
            service = AppointmentService(db)
            appointments = service.get_appointments_for_patient(patient_id)
            return {
                "success": True,
                "appointments": [
                    {
                        "id": a.id,
                        "doctor_id": a.doctor_id,
                        "appointment_date": a.appointment_date.isoformat(),
                        "slot_id": a.slot_id,
                        "status": a.status,
                    }
                    for a in appointments
                ],
            }
        finally:
            db.close()

    @mcp.tool()
    def cancel_appointment(appointment_id: int):
        """Cancel an existing appointment (frees its slot)."""
        db = SessionLocal()
        try:
            service = AppointmentService(db)
            appointment = service.cancel_appointment(appointment_id)
            if appointment is None:
                return {"success": False, "message": "Appointment not found."}
            return {"success": True, "status": appointment.status}
        finally:
            db.close()

    @mcp.tool()
    def reschedule_appointment(
        appointment_id: int,
        new_slot_id: int,
        new_appointment_date: str = "",
    ):
        """Move an appointment to a new slot (and optionally a new date,
        'YYYY-MM-DD'). Frees the old slot and books the new one."""
        parsed_date = None
        if new_appointment_date:
            parsed_date = _parse_date(new_appointment_date)
            if parsed_date is None:
                return {
                    "success": False,
                    "message": "Invalid new_appointment_date. Use YYYY-MM-DD.",
                }

        db = SessionLocal()
        try:
            service = AppointmentService(db)
            result = service.reschedule_appointment(
                appointment_id=appointment_id,
                new_slot_id=new_slot_id,
                new_appointment_date=parsed_date,
            )
            if not result["ok"]:
                messages = {
                    "not_found": "Appointment not found.",
                    "slot_unavailable": "That slot is not available.",
                    "slot_conflict": "That slot is already booked.",
                    "bad_date": "Invalid date. Use YYYY-MM-DD.",
                }
                return {
                    "success": False,
                    "message": messages.get(result["reason"], "Could not reschedule."),
                }
            appt = result["appointment"]
            return {
                "success": True,
                "appointment": {
                    "id": appt.id,
                    "patient_id": appt.patient_id,
                    "doctor_id": appt.doctor_id,
                    "appointment_date": appt.appointment_date.isoformat(),
                    "slot_id": appt.slot_id,
                    "status": appt.status,
                },
            }
        finally:
            db.close()
