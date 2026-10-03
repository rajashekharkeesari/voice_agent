from sqlalchemy import Column, Date, ForeignKey, Integer, String

from backend.db.connection import Base


class HospitalClosures(Base):
    __tablename__ = "hospital_closures"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("Hospital.id"), nullable=False)
    closure_day = Column(Date, nullable=False)
    reason = Column(String, nullable=False)
