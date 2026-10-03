from backend.db.connection import SessionLocal
from backend.services.call_state_service import CallStateService


def register_state_tools(mcp):

    @mcp.tool()
    def update_call_state(
        thread_id: str,
        patient_id: int = 0,
        patient_name: str = "",
        patient_phone_number: str = "",
        existing_patient: str = "",
        reason_for_call: str = "",
        call_type: str = "",
        doctor_name: str = "",
        doctor_id: int = 0,
        preferred_date: str = "",
        preferred_time: str = "",
        slot_id: int = 0,
        appointment_id: int = 0,
        stage: str = "",
        confirmed: str = "",
    ):
        """Record what you have learned so far in this call. Call this whenever
        the patient gives you a new detail (name, phone, reason, doctor, date,
        time) or when you decide the call_type
        (book|reschedule|cancel|availability|other) or move to a new stage.
        Pass only the fields you want to set; leave the rest blank/0.
        thread_id identifies this conversation (use the one given to you)."""
        # Normalize: treat 0 for id fields as "unset".
        fields = {
            "patient_id": patient_id or None,
            "patient_name": patient_name,
            "patient_phone_number": patient_phone_number,
            "existing_patient": existing_patient,
            "reason_for_call": reason_for_call,
            "call_type": call_type,
            "doctor_name": doctor_name,
            "doctor_id": doctor_id or None,
            "preferred_date": preferred_date,
            "preferred_time": preferred_time,
            "slot_id": slot_id or None,
            "appointment_id": appointment_id or None,
            "stage": stage,
            "confirmed": confirmed,
        }
        db = SessionLocal()
        try:
            service = CallStateService(db)
            state = service.update(thread_id, **fields)
            return {"success": True, "state": state}
        finally:
            db.close()

    @mcp.tool()
    def get_call_state(thread_id: str):
        """Read back everything recorded for this call so you can confirm
        details with the patient before taking an action."""
        db = SessionLocal()
        try:
            service = CallStateService(db)
            return {"success": True, "state": service.get(thread_id)}
        finally:
            db.close()
