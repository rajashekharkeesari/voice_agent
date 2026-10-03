"""Appointment agent: a focused ReAct agent for the appointment flow.
Shares the LLM and the MCP tools (which include the appointment tools)."""

from langgraph.prebuilt import create_react_agent

from backend.LLM.llm import get_llm
from backend.mcp_client.client import load_mcp_tools_sync

APPOINTMENT_PROMPT = """
You are the appointment assistant for a hospital voice system.
Your job is to help the patient book, look up, or cancel an appointment.
Collect the information you need (doctor or department, preferred date and
time, and the patient's identity) one question at a time. Use the available
tools to check doctors and availability and to create the appointment.
Keep replies short and natural since they will be spoken aloud.
"""

__all__ = ["APPOINTMENT_PROMPT", "build_appointment_agent"]


def build_appointment_agent():
    tools = load_mcp_tools_sync()
    return create_react_agent(
        model=get_llm(),
        tools=tools,
        prompt=APPOINTMENT_PROMPT,
    )
