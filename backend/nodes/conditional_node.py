"""Routing helpers for the LangGraph workflow.

route_from_input decides which branch to take based on simple keyword
matching on the user transcript. This keeps routing fast and deterministic;
the heavy lifting (tool calls, phrasing) happens inside the agent nodes.
"""

APPOINTMENT_KEYWORDS = (
    "appointment",
    "appointments",
    "book",
    "booking",
    "schedule",
    "reschedule",
    "rescheduling",
    "move",
    "change",
    "postpone",
    "cancel",
    "slot",
    "slots",
    "available",
    "availability",
    "doctor",
    "visit",
)


def _get(state, key, default=None):
    if isinstance(state, dict):
        return state.get(key, default)
    return getattr(state, key, default)


def route_from_input(state) -> str:
    """Return the name of the next node: 'appointment' or 'supervisor'."""
    text = (_get(state, "input", "") or "").lower()
    if any(keyword in text for keyword in APPOINTMENT_KEYWORDS):
        return "appointment"
    return "supervisor"
