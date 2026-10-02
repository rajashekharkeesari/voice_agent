from langgraph.graph import StateGraph, START, END

from backend.states.hospital_state import HospitalState
from backend.nodes.supervisor_node import supervisor_node
from backend.nodes.appointment_node import appointment_node
from backend.nodes.conditional_node import (
    supervisor_to_appointment_condition
)


workflow = StateGraph(HospitalState)

workflow.add_node("supervisor", supervisor_node)
workflow.add_node("appointment", appointment_node)

workflow.add_edge(START, "supervisor")

workflow.add_conditional_edges(
    "supervisor",
    supervisor_to_appointment_condition,
    {
        "appointment": "appointment",
        END: END
    }
)

workflow.add_edge("appointment", "supervisor")

app = workflow.compile()