from pydantic import BaseModel, Field


class SupervisorState(BaseModel):
    """State for the supervisor/orchestrator that routes the conversation."""

    # Where the supervisor decided to route the request.
    # e.g. "appointment", "doctor_info", "hospital_info", "general"
    route: str = "general"

    intent: str = ""
    needs_clarification: bool = False
    clarification_question: str = ""

    handled: bool = False
    response: str = ""

    history: list[str] = Field(default_factory=list)
