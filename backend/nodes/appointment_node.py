from backend.agents.appointment_agent import appointment_agent
from backend.states.hospital_state import HospitalState


def appointment_node(state: HospitalState):

    result = appointment_agent.invoke({
        "messages": state.orchestrator.messages_list
    })

    state.orchestrator.messages_list = result["messages"]


    return state