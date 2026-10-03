from backend.models.doctors import Doctor

class DoctorRepository:
    def __init__(self,session):
        self.session = session
    def get_doctor_by_id(self, doctor_id):
        return self.session.query(Doctor).filter(Doctor.id == doctor_id).first()
    def create_doctor(self, name, department_id):
        new_doctor = Doctor(name=name, department_id=department_id)
        self.session.add(new_doctor)
        self.session.commit()
        return new_doctor
    def update_doctor(self, doctor_id, name=None, department_id=None):
        doctor = self.get_doctor_by_id(doctor_id)
        if not doctor:
            return None
        if name is not None:
            doctor.name = name
        if department_id is not None:
            doctor.department_id = department_id
        self.session.commit()
        return doctor
    def delete_doctor(self, doctor_id):
        doctor = self.get_doctor_by_id(doctor_id)
        if not doctor:
            return None
        self.session.delete(doctor)
        self.session.commit()
        return doctor
    def get_doctors_by_department(self, department_id):
        return self.session.query(Doctor).filter(Doctor.department_id == department_id).all()

    get_doctor_by_department = get_doctors_by_department

    def find_by_name(self, name):
        """Case-insensitive partial match on doctor name (e.g. "smith")."""
        pattern = f"%{(name or '').strip()}%"
        return (
            self.session.query(Doctor)
            .filter(Doctor.name.ilike(pattern))
            .order_by(Doctor.name)
            .all()
        )

    def get_all_doctors(self):
        return self.session.query(Doctor).order_by(Doctor.name).all()

        