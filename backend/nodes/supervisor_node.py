from backend.agents.supervisor_agent import supervisor_agent
from backend.states.hospital_state import HospitalState


def supervisor_node(state: HospitalState):

    result = supervisor_agent.invoke({
        "messages": state.orchestrator.messages_list
    })

    state.orchestrator.messages_list = result["messages"]

    return state