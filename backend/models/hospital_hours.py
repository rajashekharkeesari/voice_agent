from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Time

from backend.db.connection import Base


class HospitalHours(Base):
    __tablename__ = "hospital_hours"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("Hospital.id"), nullable=False)
    day_of_week = Column(String, nullable=False)
    opening_time = Column(Time, nullable=False)
    closing_time = Column(Time, nullable=False)
    is_open = Column(Boolean, nullable=False, default=True)
