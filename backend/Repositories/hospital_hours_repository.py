from models.hospital_hours import HospitalHours


class HospitalHoursRepository:
    def __init__(self, session):
        self.session = session

    def create_hospital_hours(self, day_of_week, opening_time, closing_time, is_open=True):
        hours = HospitalHours(day_of_week=day_of_week, opening_time=opening_time, closing_time=closing_time, is_open=is_open)
        self.session.add(hours)
        self.session.commit()
        return hours

    def get_hours_by_day(self, day_of_week):
        return self.session.query(HospitalHours).filter(HospitalHours.day_of_week == day_of_week).first()

    def get_weekly_hours(self):
        return self.session.query(HospitalHours).order_by(HospitalHours.id).all()

    def update_hospital_hours(self, hours_id, day_of_week=None, opening_time=None, closing_time=None, is_open=None):
        hours = self.session.get(HospitalHours, hours_id)
        if not hours:
            return None
        for field, value in {"day_of_week": day_of_week, "opening_time": opening_time, "closing_time": closing_time, "is_open": is_open}.items():
            if value is not None:
                setattr(hours, field, value)
        self.session.commit()
        return hours

    def is_hospital_open(self, day_of_week, at_time=None):
        hours = self.get_hours_by_day(day_of_week)
        if not hours or not hours.is_open:
            return False
        return at_time is None or hours.opening_time <= at_time <= hours.closing_time

    get_hospital_is_open = get_hours_by_day
    get_hospital_hours_by_id = lambda self, hours_id: self.session.get(HospitalHours, hours_id)
