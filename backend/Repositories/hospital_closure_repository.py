from models.hospital_closures import HospitalClosures


class HospitalClosureRepository:
    def __init__(self, session):
        self.session = session

    def create_closure(self, closure_day, reason):
        closure = HospitalClosures(closure_day=closure_day, reason=reason)
        self.session.add(closure)
        self.session.commit()
        return closure

    def get_closure_by_date(self, closure_day):
        return self.session.query(HospitalClosures).filter(HospitalClosures.closure_day == closure_day).first()

    def get_closures_between_dates(self, start_date, end_date):
        return self.session.query(HospitalClosures).filter(HospitalClosures.closure_day.between(start_date, end_date)).order_by(HospitalClosures.closure_day).all()

    def is_hospital_closed(self, closure_day):
        return self.get_closure_by_date(closure_day) is not None

    def delete_closure(self, closure_id):
        closure = self.session.get(HospitalClosures, closure_id)
        if not closure:
            return None
        self.session.delete(closure)
        self.session.commit()
        return closure

    get_hospital_closure_by_id = lambda self, closure_id: self.session.get(HospitalClosures, closure_id)
    create_hospital_closure = create_closure
    get_hospital_closure_by_day = get_closure_by_date
    get_closure_between_dates = get_closures_between_dates
    get_is_hospital_closed = is_hospital_closed
    delete_hospital_closure = delete_closure
