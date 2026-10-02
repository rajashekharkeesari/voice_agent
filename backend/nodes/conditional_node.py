from backend.states.supervisor_state import SupervisorState
def supervisor_to_appointment_condition(state:SupervisorState):
    if state.intent is  appointment_intent:
        return "appointment"
    else:
        return "end"