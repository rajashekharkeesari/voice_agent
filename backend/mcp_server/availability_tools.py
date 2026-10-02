from backend.services.doctor_availability_service import (
    DoctorAvailabilityService
)

from backend.db.connection import get_db


def register_availability_tools(mcp):

    @mcp.tool()
    def check_doctor_availability(
        doctor_id: int,
        date: str
    ):
        """
        Check whether a doctor is available on a particular date.

        date format:
        YYYY-MM-DD
        """

        db = get_db()

        try:
            service = DoctorAvailabilityService(db)

            result = service.is_doctor_available(
                doctor_id=doctor_id,
                date=date
            )

            return {
                "success": True,
                "result": result
            }

        finally:
            db.close()


    @mcp.tool()
    def get_free_slots(
        doctor_id: int,
        date: str
    ):
        """
        Get free appointment slots for a doctor on a date.
        """

        db = get_db()

        try:
            service = DoctorAvailabilityService(db)

            slots = service.get_free_slots(
                doctor_id=doctor_id,
                date=date
            )

            return {
                "success": True,
                "slots": [
                    {
                        "id": slot.id,
                        "doctor_id": slot.doctor_id,
                        "date": str(slot.date),
                        "start_time": str(slot.start_time),
                        "end_time": str(slot.end_time),
                        "status": slot.status
                    }
                    for slot in slots
                ]
            }

        finally:
            db.close()


    @mcp.tool()
    def get_available_slots(
        doctor_id: int,
        date: str
    ):
        """
        Get all available slots for a doctor on a particular date.
        """

        db = get_db()

        try:
            service = DoctorAvailabilityService(db)

            slots = service.get_available_slots(
                doctor_id=doctor_id,
                date=date
            )

            return {
                "success": True,
                "slots": [
                    {
                        "id": slot.id,
                        "doctor_id": slot.doctor_id,
                        "date": str(slot.date),
                        "start_time": str(slot.start_time),
                        "end_time": str(slot.end_time),
                        "status": slot.status
                    }
                    for slot in slots
                ]
            }

        finally:
            db.close()


    @mcp.tool()
    def get_available_doctors(
        department_id: int,
        start_date: str,
        end_date: str
    ):
        """
        Get doctors available within a date range
        for a particular department.
        """

        db = get_db()

        try:
            service = DoctorAvailabilityService(db)

            doctors = service.get_available_doctors(
                department_id=department_id,
                start_date=start_date,
                end_date=end_date
            )

            return {
                "success": True,
                "doctors": [
                    {
                        "id": doctor.id,
                        "name": doctor.name,
                        "department_id": doctor.department_id
                    }
                    for doctor in doctors
                ]
            }

        finally:
            db.close()


    @mcp.tool()
    def get_doctor_availability(
        doctor_id: int,
        start_date: str,
        end_date: str
    ):
        """
        Get a doctor's availability between two dates.
        """

        db = get_db()

        try:
            service = DoctorAvailabilityService(db)

            result = service.get_doctor_availability(
                doctor_id=doctor_id,
                start_date=start_date,
                end_date=end_date
            )

            return {
                "success": True,
                "availability": result
            }

        finally:
            db.close()