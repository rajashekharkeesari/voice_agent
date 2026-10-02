from models.hospital_hours import HospitalHours


class HospitalHoursRepository:

    def __init__(self, session):
        self.session = session

    def create(
        self,
        hospital_id,
        day_of_week,
        opening_time,
        closing_time,
        is_open=True
    ):
        hours = HospitalHours(
            hospital_id=hospital_id,
            day_of_week=day_of_week,
            opening_time=opening_time,
            closing_time=closing_time,
            is_open=is_open
        )

        self.session.add(hours)
        self.session.commit()
        self.session.refresh(hours)

        return hours

    def get_by_id(self, hours_id):
        return self.session.get(
            HospitalHours,
            hours_id
        )

    def get_by_day(self, hospital_id, day_of_week):
        return (
            self.session.query(HospitalHours)
            .filter(
                HospitalHours.hospital_id == hospital_id,
                HospitalHours.day_of_week == day_of_week
            )
            .first()
        )

    def get_by_hospital(self, hospital_id):
        return (
            self.session.query(HospitalHours)
            .filter(
                HospitalHours.hospital_id == hospital_id
            )
            .order_by(HospitalHours.id)
            .all()
        )

    def get_weekly_hours(self, hospital_id):
        return self.get_by_hospital(hospital_id)

    def update(
        self,
        hours_id,
        day_of_week=None,
        opening_time=None,
        closing_time=None,
        is_open=None
    ):
        hours = self.get_by_id(hours_id)

        if not hours:
            return None

        fields = {
            "day_of_week": day_of_week,
            "opening_time": opening_time,
            "closing_time": closing_time,
            "is_open": is_open
        }

        for field, value in fields.items():
            if value is not None:
                setattr(hours, field, value)

        self.session.commit()
        self.session.refresh(hours)

        return hours

    def delete(self, hours_id):
        hours = self.get_by_id(hours_id)

        if not hours:
            return None

        self.session.delete(hours)
        self.session.commit()

        return hours