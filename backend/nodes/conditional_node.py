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


def supervisor_to_appointment_condition(state):
    """Decide where the supervisor goes next.

    Routes to the appointment node when the request is appointment-related and
    the appointment step has NOT already run this turn. Once appointment has
    run (it sets handled=True and loops back to supervisor), we go to END so
    the graph doesn't loop forever.

    Returns the node name "appointment" or the END sentinel.
    """
    from langgraph.graph import END

    # If the appointment step already handled this turn, finish.
    if _get(state, "handled", False):
        return END

    text = (_get(state, "input", "") or "").lower()
    if any(keyword in text for keyword in APPOINTMENT_KEYWORDS):
        return "appointment"

    return END
