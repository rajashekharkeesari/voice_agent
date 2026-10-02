from backend.services.doctor_service import DoctorService
from backend.db.connection import get_db


def register_doctor_tools(mcp):

    @mcp.tool()
    def get_doctor_by_id(doctor_id: int):
        """
        Get a doctor using doctor ID.
        """

        db = get_db()

        try:
            service = DoctorService(db)

            doctor = service.get_doctor_by_id(doctor_id)

            if not doctor:
                return {
                    "success": False,
                    "message": "Doctor not found."
                }

            return {
                "success": True,
                "doctor": {
                    "id": doctor.id,
                    "name": doctor.name,
                    "department_id": doctor.department_id
                }
            }

        finally:
            db.close()


    @mcp.tool()
    def get_doctors_by_department(department_id: int):
        """
        Get all doctors belonging to a department.
        """

        db = get_db()

        try:
            service = DoctorService(db)

            doctors = service.get_doctors_by_department(
                department_id
            )

            return {
                "success": True,
                "doctors": [
                    {
                        "id": doctor.id,
                        "name": doctor.name,
                        "department_id": doctor.department_id
                    }
                    for doctor in doctors
                ]
            }

        finally:
            db.close()


    @mcp.tool()
    def get_all_doctors():
        """
        Get all doctors in the hospital.
        """

        db = get_db()

        try:
            service = DoctorService(db)

            doctors = service.get_all_doctors()

            return {
                "success": True,
                "doctors": [
                    {
                        "id": doctor.id,
                        "name": doctor.name,
                        "department_id": doctor.department_id
                    }
                    for doctor in doctors
                ]
            }

        finally:
            db.close()