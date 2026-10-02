from sqlalchemy import Column, ForeignKey, Integer, String, Time

from db.connection import Base


class DoctorSchedules(Base):
    __tablename__ = "doctor_schedules"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    schedule_day = Column(String, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    slot_duration = Column(Integer, nullable=False)  # Duration in minutes