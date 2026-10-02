from backend.services.hospital_availability_service import (
    HospitalAvailabilityService
)

from backend.db.connection import get_db


def register_hospital_tools(mcp):

    @mcp.tool()
    def check_hospital_availability(
        hospital_name: str,
        date: str
    ):
        """
        Check whether the hospital is working on a particular date.

        Date format:
        YYYY-MM-DD
        """

        db = get_db()

        try:
            service = HospitalAvailabilityService(db)

            result = service.check_hospital_availability_day(
                hospital_name=hospital_name,
                day=date
            )

            return {
                "success": True,
                "result": result
            }

        except ValueError as e:

            return {
                "success": False,
                "message": str(e)
            }

        finally:
            db.close()


    @mcp.tool()
    def check_hospital_availability_by_time(
        hospital_name: str,
        date: str,
        time: str
    ):
        """
        Check whether the hospital is open at a specific date and time.

        Date:
        YYYY-MM-DD

        Time:
        HH:MM
        """

        db = get_db()

        try:
            service = HospitalAvailabilityService(db)

            result = service.check_hospital_availability_by_time(
                hospital_name=hospital_name,
                day=date,
                time=time
            )

            return {
                "success": True,
                "result": result
            }

        except ValueError as e:

            return {
                "success": False,
                "message": str(e)
            }

        finally:
            db.close()


    @mcp.tool()
    def get_hospital_hours(
        hospital_name: str
    ):
        """
        Get the weekly working hours of a hospital.
        """

        db = get_db()

        try:
            service = HospitalAvailabilityService(db)

            hours = service.get_hospital_hours(
                hospital_name
            )

            return {
                "success": True,
                "hours": [
                    {
                        "id": item.id,
                        "hospital_id": item.hospital_id,
                        "day_of_week": item.day_of_week,
                        "opening_time": str(
                            item.opening_time
                        ),
                        "closing_time": str(
                            item.closing_time
                        ),
                        "is_open": item.is_open
                    }
                    for item in hours
                ]
            }

        except ValueError as e:

            return {
                "success": False,
                "message": str(e)
            }

        finally:
            db.close()


    @mcp.tool()
    def get_hospital_closures(
        hospital_name: str
    ):
        """
        Get hospital closure days.
        """

        db = get_db()

        try:
            service = HospitalAvailabilityService(db)

            closures = service.get_hospital_closures(
                hospital_name
            )

            return {
                "success": True,
                "closures": [
                    {
                        "id": closure.id,
                        "hospital_id": closure.hospital_id,
                        "closure_day": str(
                            closure.closure_day
                        ),
                        "reason": closure.reason
                    }
                    for closure in closures
                ]
            }

        except ValueError as e:

            return {
                "success": False,
                "message": str(e)
            }

        finally:
            db.close()