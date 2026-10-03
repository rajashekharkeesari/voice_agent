from backend.models.hospital_details import HospitalService


class HospitalRepository:
    """Data access for the Hospital table (model: HospitalService)."""

    def __init__(self, session):
        self.session = session

    def get_by_id(self, hospital_id):
        return self.session.get(HospitalService, hospital_id)

    def get_by_name(self, name):
        return (
            self.session.query(HospitalService)
            .filter(HospitalService.Hospital_name == name)
            .first()
        )

    def get_all(self):
        return (
            self.session.query(HospitalService)
            .order_by(HospitalService.Hospital_name)
            .all()
        )

    def create(self, hospital_name, contact_no=None, is_active=True):
        hospital = HospitalService(
            Hospital_name=hospital_name,
            contact_no=contact_no,
            is_active=is_active,
        )
        self.session.add(hospital)
        self.session.commit()
        self.session.refresh(hospital)
        return hospital
