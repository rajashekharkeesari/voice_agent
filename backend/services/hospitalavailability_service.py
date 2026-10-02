from backend.repositories.hospital_repository import HospitalRepository
from backend.repositories.hospital_hours_repository import HospitalHoursRepository
from backend.repositories.hospital_closures_repository import HospitalClosureRepository


class HospitalAvailabilityService:

    def __init__(self, session):

        self.hospital_repository = HospitalRepository(session)

        self.hospital_hours_repository = (
            HospitalHoursRepository(session)
        )

        self.hospital_closure_repository = (
            HospitalClosureRepository(session)
        )

        def check_hospital_availability_day(
        self,
        hospital_name,
        day
    ):

        hospital = self.hospital_repository.get_by_name(
            hospital_name
        )

        if not hospital:
            raise ValueError("Hospital not found.")

        # Check whether hospital is closed
        closure = self.hospital_closure_repository.get_by_day(
            hospital_id=hospital.id,
            closure_day=day
        )

        if closure:
            return {
                "available": False,
                "message": "Hospital is closed on this day.",
                "reason": closure.reason
            }

        # Check normal weekly schedule
        hours = self.hospital_hours_repository.get_by_day(
            hospital_id=hospital.id,
            day_of_week=day.strftime("%A")
        )

        if not hours or not hours.is_open:
            return {
                "available": False,
                "message": "Hospital is not working on this day."
            }

        return {
            "available": True,
            "message": "Hospital is working on this day.",
            "opening_time": hours.opening_time,
            "closing_time": hours.closing_time
        }

        def check_hospital_availability_by_time(
        self,
        hospital_name,
        day,
        time
    ):

        hospital = self.hospital_repository.get_by_name(
            hospital_name
        )

        if not hospital:
            raise ValueError("Hospital not found.")

        # 1. Check special closure
        closure = self.hospital_closure_repository.get_by_day(
            hospital_id=hospital.id,
            closure_day=day
        )

        if closure:
            return {
                "available": False,
                "message": "Hospital is closed on this day.",
                "reason": closure.reason
            }

        # 2. Get normal working hours
        hours = self.hospital_hours_repository.get_by_day(
            hospital_id=hospital.id,
            day_of_week=day.strftime("%A")
        )

        if not hours or not hours.is_open:
            return {
                "available": False,
                "message": "Hospital is not working on this day."
            }

        # 3. Check time
        if hours.opening_time <= time <= hours.closing_time:

            return {
                "available": True,
                "message": "Hospital is working at this time.",
                "opening_time": hours.opening_time,
                "closing_time": hours.closing_time
            }

        return {
            "available": False,
            "message": "Hospital is closed at this time.",
            "opening_time": hours.opening_time,
            "closing_time": hours.closing_time
        }




        def get_hospital_closures(self, hospital_name):

        hospital = self.hospital_repository.get_by_name(
            hospital_name
        )

        if not hospital:
            raise ValueError("Hospital not found.")

        return self.hospital_closure_repository.get_by_hospital(
            hospital.id
        )