from backend.Repositories.patient_repository import PatientRepository


class PatientService:
    def __init__(self, session):
        self.session = session
        self.patient_repository = PatientRepository(session)

    def register_patient(self, name, age, phone_number):
        return self.patient_repository.create_patient(
            name=name,
            age=age,
            phone_number=phone_number,
        )

    def validate_patient(self, patient_id):
        return self.patient_repository.get_patient_by_id(patient_id)

    def get_patient_by_phone(self, phone_number):
        return self.patient_repository.get_patient_by_phone(phone_number)

    def find_patients_by_name(self, name):
        return self.patient_repository.find_by_name(name)

    def identify_patient(self, phone_number, name):
        """Identify a patient by phone number, confirming the name matches.

        Returns one of:
            {"found": True,  "patient": <Patient>}
            {"found": False, "reason": "no_phone_match"}   -> offer to register
            {"found": False, "reason": "name_mismatch",
             "patient_on_file": <name>}                    -> verify / re-ask
        """
        patient = self.patient_repository.get_patient_by_phone(phone_number)
        if patient is None:
            return {"found": False, "reason": "no_phone_match"}

        given = (name or "").strip().lower()
        on_file = (patient.name or "").strip().lower()
        # Accept exact or partial name match (first name, etc.).
        if given and (given == on_file or given in on_file or on_file in given):
            return {"found": True, "patient": patient}

        return {
            "found": False,
            "reason": "name_mismatch",
            "patient_on_file": patient.name,
        }
