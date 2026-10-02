from backend.services.patient_service import PatientService
from backend.db.connection import get_db


def register_patient_tools(mcp):

    @mcp.tool()
    def register_patient(
        name: str,
        age: int,
        phone_number: str
    ):
        """
        Register a new patient.
        """

        db = get_db()

        try:
            service = PatientService(db)

            patient = service.register_patient(
                name=name,
                age=age,
                phone_number=phone_number
            )

            if not patient:
                return {
                    "success": False,
                    "message": "Patient could not be registered"
                }

            return {
                "success": True,
                "patient": {
                    "id": patient.id,
                    "name": patient.name,
                    "age": patient.age,
                    "phone_number": patient.phone_number
                }
            }

        except ValueError as e:

            return {
                "success": False,
                "message": str(e)
            }

        finally:
            db.close()


    @mcp.tool()
    def validate_patient(
        patient_id: int
    ):
        """
        Check whether a patient exists using patient ID.
        """

        db = get_db()

        try:
            service = PatientService(db)

            patient = service.validate_patient(
                patient_id
            )

            if not patient:
                return {
                    "success": False,
                    "message": "Patient not found"
                }

            return {
                "success": True,
                "patient": {
                    "id": patient.id,
                    "name": patient.name,
                    "age": patient.age,
                    "phone_number": patient.phone_number
                }
            }

        except ValueError as e:

            return {
                "success": False,
                "message": str(e)
            }

        finally:
            db.close()


    @mcp.tool()
    def get_patient_by_phone(
        phone_number: str
    ):
        """
        Find a patient using their phone number.
        """

        db = get_db()

        try:
            service = PatientService(db)

            patient = service.get_patient_by_phone(
                phone_number
            )

            if not patient:
                return {
                    "success": False,
                    "message": "Patient not found"
                }

            return {
                "success": True,
                "patient": {
                    "id": patient.id,
                    "name": patient.name,
                    "age": patient.age,
                    "phone_number": patient.phone_number
                }
            }

        except ValueError as e:

            return {
                "success": False,
                "message": str(e)
            }

        finally:
            db.close()


    @mcp.tool()
    def update_patient(
        patient_id: int,
        name: str = None,
        age: int = None,
        phone_number: str = None
    ):
        """
        Update patient information.
        """

        db = get_db()

        try:
            service = PatientService(db)

            patient = service.update_patient(
                patient_id=patient_id,
                name=name,
                age=age,
                phone_number=phone_number
            )

            if not patient:
                return {
                    "success": False,
                    "message": "Patient not found"
                }

            return {
                "success": True,
                "patient": {
                    "id": patient.id,
                    "name": patient.name,
                    "age": patient.age,
                    "phone_number": patient.phone_number
                }
            }

        except ValueError as e:

            return {
                "success": False,
                "message": str(e)
            }

        finally:
            db.close()


    @mcp.tool()
    def delete_patient(
        patient_id: int
    ):
        """
        Delete a patient.
        """

        db = get_db()

        try:
            service = PatientService(db)

            patient = service.delete_patient(
                patient_id
            )

            if not patient:
                return {
                    "success": False,
                    "message": "Patient not found"
                }

            return {
                "success": True,
                "patient": {
                    "id": patient.id,
                    "name": patient.name,
                    "age": patient.age,
                    "phone_number": patient.phone_number
                }
            }

        except ValueError as e:

            return {
                "success": False,
                "message": str(e)
            }

        finally:
            db.close()