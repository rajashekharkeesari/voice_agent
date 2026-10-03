from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from backend.db.connection import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    slot_id = Column(Integer, ForeignKey("doctor_slots.id"), nullable=False)
    status = Column(String, nullable=False)