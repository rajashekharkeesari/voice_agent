from backend.db.connection import SessionLocal
from backend.services.hospitalavailability_service import (
    DoctorAvailabilityService,
    HospitalAvailabilityService,
)


def register_availability_tools(mcp):

    @mcp.tool()
    def list_available_slots(doctor_id: int, date: str):
        """List a doctor's available appointment slots for a date
        (date = 'YYYY-MM-DD'). Returns slot ids to use when booking."""
        db = SessionLocal()
        try:
            service = DoctorAvailabilityService(db)
            try:
                slots = service.list_available_slots(doctor_id, date)
            except ValueError:
                return {
                    "success": False,
                    "message": "Invalid date. Use YYYY-MM-DD.",
                }
            return {
                "success": True,
                "slots": [
                    {
                        "slot_id": s.id,
                        "start_time": s.start_time.isoformat()
                        if s.start_time
                        else None,
                        "end_time": s.end_time.isoformat()
                        if s.end_time
                        else None,
                        "status": s.status,
                    }
                    for s in slots
                ],
            }
        finally:
            db.close()

    @mcp.tool()
    def get_hospital_hours(hospital_id: int = 1):
        """Get the weekly opening hours for the hospital."""
        db = SessionLocal()
        try:
            service = HospitalAvailabilityService(db)
            hours = service.get_weekly_hours(hospital_id)
            return {
                "success": True,
                "hours": [
                    {
                        "day_of_week": h.day_of_week,
                        "opening_time": h.opening_time.isoformat()
                        if h.opening_time
                        else None,
                        "closing_time": h.closing_time.isoformat()
                        if h.closing_time
                        else None,
                        "is_open": h.is_open,
                    }
                    for h in hours
                ],
            }
        finally:
            db.close()

    @mcp.tool()
    def get_hospital_closures(hospital_id: int = 1):
        """List upcoming/known closure days for the hospital."""
        db = SessionLocal()
        try:
            service = HospitalAvailabilityService(db)
            closures = service.get_closures(hospital_id)
            return {
                "success": True,
                "closures": [
                    {
                        "closure_day": c.closure_day.isoformat(),
                        "reason": c.reason,
                    }
                    for c in closures
                ],
            }
        finally:
            db.close()
