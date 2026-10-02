from backend.Repositories.patient_repository import PatientRepository

class PatientService:
    def __init__(self, session):
        self.patient_repository = PatientRepository(session)

    def register_patient(self,patient_data):
        return self.patient_repository.create_patient(patient_data)
    def validate_patient(self,patient_id):
        return self.patient_repository.get_patient_by_id(patient_id)