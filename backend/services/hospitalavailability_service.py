from backend.Repositories.hospital_hours_repository import (
    HospitalHoursRepository,
)
from backend.Repositories.hospital_closure_repository import (
    HospitalClosureRepository,
)


class HospitalAvailabilityService:
    def __init__(self, session):
        self.session = session
        self.hours_repository = HospitalHoursRepository(session)
        self.closure_repository = HospitalClosureRepository(session)

    def get_weekly_hours(self, hospital_id):
        return self.hours_repository.get_weekly_hours(hospital_id)

    def get_hours_for_day(self, hospital_id, day_of_week):
        return self.hours_repository.get_by_day(hospital_id, day_of_week)

    def get_closures(self, hospital_id):
        return self.closure_repository.get_by_hospital(hospital_id)

    def is_closed_on(self, hospital_id, closure_day):
        return (
            self.closure_repository.get_by_day(hospital_id, closure_day)
            is not None
        )


from datetime import datetime  # noqa: E402

from backend.Repositories.doctoravailbility_repository import (  # noqa: E402
    DoctorAvailabilityRepository,
)


class DoctorAvailabilityService:
    """Business layer for doctor slots/schedules/leaves."""

    def __init__(self, session):
        self.session = session
        self.repository = DoctorAvailabilityRepository(session)

    def list_available_slots(self, doctor_id, date):
        """date: a datetime.date (or ISO 'YYYY-MM-DD' string)."""
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d").date()
        return self.repository.get_available_slots(doctor_id, date)

    def get_slot(self, slot_id):
        return self.repository.get_slot_by_id(slot_id)
