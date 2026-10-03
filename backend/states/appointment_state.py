from pydantic import BaseModel, Field


class AppointmentState(BaseModel):
    """State specific to the appointment booking flow."""

    doctor_name: str = ""
    doctor_id: int | None = None
    department: str = ""

    preferred_date: str = ""
    preferred_time: str = ""
    slot_id: int | None = None

    appointment_id: int | None = None
    status: str = ""  # e.g. "collecting", "confirmed", "cancelled"

    notes: list[str] = Field(default_factory=list)
