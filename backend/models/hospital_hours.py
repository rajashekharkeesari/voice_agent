from sqlalchemy import Boolean, Column, Integer, String, Time

from db.connection import Base


class HospitalHours(Base):
    __tablename__ = "hospital_hours"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(String, nullable=False)
    opening_time = Column(Time, nullable=False)
    closing_time = Column(Time, nullable=False)
    is_open = Column(Boolean, nullable=False, default=True)