from backend.Repositories.doctor_repository import DoctorRepository


class DoctorService:
    """Business layer around the doctor repository.

    NOTE: the module is named ``doctorservice`` (no underscore). Import it as
    ``from backend.services.doctorservice import DoctorService``.
    """

    def __init__(self, session):
        self.session = session
        self.doctor_repository = DoctorRepository(session)

    def get_doctor_by_id(self, doctor_id):
        return self.doctor_repository.get_doctor_by_id(doctor_id)

    def get_doctors_by_department(self, department_id):
        return self.doctor_repository.get_doctors_by_department(department_id)

    def get_all_doctors(self):
        return self.doctor_repository.get_all_doctors()

    def find_doctors_by_name(self, name):
        return self.doctor_repository.find_by_name(name)

    def create_doctor(self, name, department_id):
        return self.doctor_repository.create_doctor(name, department_id)
