from backend.db.connection import SessionLocal
from backend.services.doctorservice import DoctorService


def register_doctor_tools(mcp):

    @mcp.tool()
    def get_doctor_by_id(doctor_id: int):
        """Get a doctor using the doctor ID."""
        db = SessionLocal()
        try:
            service = DoctorService(db)
            doctor = service.get_doctor_by_id(doctor_id)

            if not doctor:
                return {"success": False, "message": "Doctor not found."}

            return {
                "success": True,
                "doctor": {
                    "id": doctor.id,
                    "name": doctor.name,
                    "department_id": doctor.department_id,
                },
            }
        finally:
            db.close()

    @mcp.tool()
    def get_doctors_by_department(department_id: int):
        """Get all doctors belonging to a department."""
        db = SessionLocal()
        try:
            service = DoctorService(db)
            doctors = service.get_doctors_by_department(department_id)

            return {
                "success": True,
                "doctors": [
                    {
                        "id": doctor.id,
                        "name": doctor.name,
                        "department_id": doctor.department_id,
                    }
                    for doctor in doctors
                ],
            }
        finally:
            db.close()

    @mcp.tool()
    def get_all_doctors():
        """Get all doctors in the hospital."""
        db = SessionLocal()
        try:
            service = DoctorService(db)
            doctors = service.get_all_doctors()

            return {
                "success": True,
                "doctors": [
                    {
                        "id": doctor.id,
                        "name": doctor.name,
                        "department_id": doctor.department_id,
                    }
                    for doctor in doctors
                ],
            }
        finally:
            db.close()

    @mcp.tool()
    def find_doctor_by_name(name: str):
        """Find doctors by (partial) name, e.g. "Smith". Use this to turn a
        spoken doctor name into a doctor_id before booking."""
        db = SessionLocal()
        try:
            service = DoctorService(db)
            doctors = service.find_doctors_by_name(name)
            return {
                "success": True,
                "doctors": [
                    {
                        "id": d.id,
                        "name": d.name,
                        "department_id": d.department_id,
                    }
                    for d in doctors
                ],
            }
        finally:
            db.close()
