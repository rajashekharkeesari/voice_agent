from backend.models.hospital_closures import HospitalClosures


class HospitalClosureRepository:

    def __init__(self, session):
        self.session = session

    def create(
        self,
        hospital_id,
        closure_day,
        reason
    ):
        closure = HospitalClosures(
            hospital_id=hospital_id,
            closure_day=closure_day,
            reason=reason
        )

        self.session.add(closure)
        self.session.commit()
        self.session.refresh(closure)

        return closure

    def get_by_id(self, closure_id):
        return self.session.get(
            HospitalClosures,
            closure_id
        )

    def get_by_day(
        self,
        hospital_id,
        closure_day
    ):
        return (
            self.session.query(HospitalClosures)
            .filter(
                HospitalClosures.hospital_id == hospital_id,
                HospitalClosures.closure_day == closure_day
            )
            .first()
        )

    def get_by_hospital(self, hospital_id):
        return (
            self.session.query(HospitalClosures)
            .filter(
                HospitalClosures.hospital_id == hospital_id
            )
            .order_by(HospitalClosures.closure_day)
            .all()
        )

    def get_between_dates(
        self,
        hospital_id,
        start_date,
        end_date
    ):
        return (
            self.session.query(HospitalClosures)
            .filter(
                HospitalClosures.hospital_id == hospital_id,
                HospitalClosures.closure_day.between(
                    start_date,
                    end_date
                )
            )
            .order_by(HospitalClosures.closure_day)
            .all()
        )

    def delete(self, closure_id):
        closure = self.get_by_id(closure_id)

        if not closure:
            return None

        self.session.delete(closure)
        self.session.commit()

        return closure