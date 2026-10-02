from pydantic import BaseModel, Field


class HospitalState(BaseModel):

    # Common state
    call_type: str = ""
    patient_first_name: str = ""
    patient_last_name: str = ""
    patient_phone_number: str = ""

    existing_patient: bool = False
    reason_for_call: str = ""

    messages_list: list = Field(default_factory=list)
    tools_used: list = Field(default_factory=list)

    # Agent-specific state
    supervisor: SupervisorState | None = None
    appointment: AppointmentState | None = None
    is_running: bool = True
    last_updated: str = ""
    error_message: str | None = None