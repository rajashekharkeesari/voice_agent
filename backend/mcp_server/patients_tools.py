from backend.db.connection import SessionLocal
from backend.services.patient_service import PatientService


def register_patient_tools(mcp):

    @mcp.tool()
    def register_patient(name: str, age: int, phone_number: str):
        """Register a new patient and return the created record."""
        db = SessionLocal()
        try:
            service = PatientService(db)
            patient = service.register_patient(
                name=name, age=age, phone_number=phone_number
            )
            return {
                "success": True,
                "patient": {
                    "id": patient.id,
                    "name": patient.name,
                    "age": patient.age,
                    "phone_number": patient.phone_number,
                },
            }
        finally:
            db.close()

    @mcp.tool()
    def find_patient_by_phone(phone_number: str):
        """Look up an existing patient by phone number."""
        db = SessionLocal()
        try:
            service = PatientService(db)
            patient = service.get_patient_by_phone(phone_number)
            if not patient:
                return {"success": False, "message": "Patient not found."}
            return {
                "success": True,
                "patient": {
                    "id": patient.id,
                    "name": patient.name,
                    "age": patient.age,
                    "phone_number": patient.phone_number,
                },
            }
        finally:
            db.close()

    @mcp.tool()
    def identify_patient(phone_number: str, name: str):
        """Identify a returning patient by phone number + name. Use this first
        to look the caller up. Returns found=True with the patient (greet them
        by name), or found=False with a reason (offer to register, or re-ask
        if the name doesn't match the phone on file)."""
        db = SessionLocal()
        try:
            service = PatientService(db)
            result = service.identify_patient(phone_number, name)
            if result["found"]:
                p = result["patient"]
                return {
                    "found": True,
                    "patient": {
                        "id": p.id,
                        "name": p.name,
                        "age": p.age,
                        "phone_number": p.phone_number,
                    },
                }
            return result
        finally:
            db.close()

    @mcp.tool()
    def find_patient_by_name(name: str):
        """Find patients by (partial) name. Use this to resolve a spoken
        patient name into a patient_id before booking/rescheduling."""
        db = SessionLocal()
        try:
            service = PatientService(db)
            patients = service.find_patients_by_name(name)
            return {
                "success": True,
                "patients": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "age": p.age,
                        "phone_number": p.phone_number,
                    }
                    for p in patients
                ],
            }
        finally:
            db.close()
