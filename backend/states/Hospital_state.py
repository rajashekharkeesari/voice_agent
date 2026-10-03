from pydantic import BaseModel, Field

from backend.states.appointment_state import AppointmentState
from backend.states.orchestrator_state import SupervisorState


class HospitalState(BaseModel):

    # --- Pipeline input/output -------------------------------------------
    # pipecat's LangchainProcessor calls the graph with {"input": <text>}.
    # The graph writes its reply back into `output`, which the processor
    # streams to TTS.
    input: str = ""
    output: str = ""

    # --- Common conversation state ---------------------------------------
    call_type: str = ""
    patient_first_name: str = ""
    patient_last_name: str = ""
    patient_phone_number: str = ""

    existing_patient: bool = False
    reason_for_call: str = ""

    messages_list: list = Field(default_factory=list)
    tools_used: list = Field(default_factory=list)

    # --- Agent-specific state --------------------------------------------
    supervisor: SupervisorState | None = None
    appointment: AppointmentState | None = None

    is_running: bool = True
    last_updated: str = ""
    error_message: str | None = None

    # Set True by the appointment node so the supervisor->appointment
    # conditional ends the graph instead of looping forever.
    handled: bool = False
