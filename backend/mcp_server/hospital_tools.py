from backend.db.connection import SessionLocal
from backend.Repositories.hospital_repository import HospitalRepository


def register_hospital_tools(mcp):

    @mcp.tool()
    def get_hospital_info(hospital_id: int = 1):
        """Get basic information about the hospital (name, contact)."""
        db = SessionLocal()
        try:
            repo = HospitalRepository(db)
            hospital = repo.get_by_id(hospital_id)
            if not hospital:
                return {"success": False, "message": "Hospital not found."}
            return {
                "success": True,
                "hospital": {
                    "id": hospital.id,
                    "name": hospital.Hospital_name,
                    "contact_no": hospital.contact_no,
                    "is_active": hospital.is_active,
                },
            }
        finally:
            db.close()

    @mcp.tool()
    def list_hospitals():
        """List all hospitals."""
        db = SessionLocal()
        try:
            repo = HospitalRepository(db)
            hospitals = repo.get_all()
            return {
                "success": True,
                "hospitals": [
                    {
                        "id": h.id,
                        "name": h.Hospital_name,
                        "contact_no": h.contact_no,
                        "is_active": h.is_active,
                    }
                    for h in hospitals
                ],
            }
        finally:
            db.close()
