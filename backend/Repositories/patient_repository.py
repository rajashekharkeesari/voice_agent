from backend.models.patients import Patient


class PatientRepository:

    def __init__(self, session):
        self.session = session

    def get_patient_by_id(self, patient_id):
        return (
            self.session.query(Patient)
            .filter(Patient.id == patient_id)
            .first()
        )

    def get_patient_by_phone(self, phone_number):
        return (
            self.session.query(Patient)
            .filter(Patient.phone_number == phone_number)
            .first()
        )

    def find_by_name(self, name):
        """Case-insensitive partial match on patient name."""
        pattern = f"%{(name or '').strip()}%"
        return (
            self.session.query(Patient)
            .filter(Patient.name.ilike(pattern))
            .order_by(Patient.name)
            .all()
        )

    def create_patient(self, name, age, phone_number):
        new_patient = Patient(
            name=name,
            age=age,
            phone_number=phone_number
        )

        self.session.add(new_patient)
        self.session.commit()
        self.session.refresh(new_patient)

        return new_patient

    def update_patient(
        self,
        patient_id,
        name=None,
        age=None,
        phone_number=None
    ):
        patient = self.get_patient_by_id(patient_id)

        if not patient:
            return None

        if name is not None:
            patient.name = name

        if age is not None:
            patient.age = age

        if phone_number is not None:
            patient.phone_number = phone_number

        self.session.commit()
        self.session.refresh(patient)

        return patient

    def delete_patient(self, patient_id):
        patient = self.get_patient_by_id(patient_id)

        if not patient:
            return None

        self.session.delete(patient)
        self.session.commit()

        return patient

    # Alias
    get_patient_by_phone_number = get_patient_by_phone