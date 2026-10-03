from sqlalchemy import Column, Integer, String, Text

from backend.db.connection import Base


class CallState(Base):
    """Per-conversation receptionist state, keyed by thread_id (the caller's
    session). Updated from both patient utterances and AI decisions as the
    call progresses, so the flow has structured slots and can resume."""

    __tablename__ = "call_states"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, unique=True, index=True, nullable=False)

    # Identity
    patient_id = Column(Integer, nullable=True)
    patient_name = Column(String, default="")
    patient_phone_number = Column(String, default="")
    existing_patient = Column(String, default="")  # "yes" | "no" | ""

    # Call intent
    reason_for_call = Column(Text, default="")
    call_type = Column(String, default="")  # book|reschedule|cancel|availability|other

    # Appointment working slots
    doctor_name = Column(String, default="")
    doctor_id = Column(Integer, nullable=True)
    preferred_date = Column(String, default="")
    preferred_time = Column(String, default="")
    slot_id = Column(Integer, nullable=True)
    appointment_id = Column(Integer, nullable=True)

    # Flow bookkeeping
    stage = Column(String, default="greeting")
    confirmed = Column(String, default="")  # "yes" | "no" | ""
    last_updated = Column(String, default="")
