from models.hospital import Hospital


class HospitalRepository:

    def __init__(self, session):
        self.session = session

    def get_by_id(self, hospital_id):
        return self.session.get(
            Hospital,
            hospital_id
        )

    def get_by_name(self, name):
        return (
            self.session.query(Hospital)
            .filter(Hospital.name == name)
            .first()
        )

    def get_all(self):
        return (
            self.session.query(Hospital)
            .order_by(Hospital.name)
            .all()
        )