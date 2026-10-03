"""Supervisor agent: a tool-using ReAct agent built on the shared LLM and the
MCP-provided hospital tools. Built lazily so importing this module never
requires the MCP server or a valid API key."""

from langgraph.prebuilt import create_react_agent

from backend.LLM.llm import get_llm
from backend.mcp_client.client import load_mcp_tools_sync

SYSTEM_PROMPT = """
You are the supervisor for a hospital voice assistant.
You are responsible for:
- Understanding the user's request.
- Determining whether the request concerns appointments,
  doctors, patients, hospital availability, or other hospital services.
- Using the available tools when necessary.
- Asking for missing information.
- Returning a clear, concise spoken response to the patient.
Keep replies short and natural since they will be spoken aloud.
"""

__all__ = ["SYSTEM_PROMPT", "build_supervisor_agent"]


def build_supervisor_agent():
    """Create the supervisor ReAct agent. Loads MCP tools if available."""
    tools = load_mcp_tools_sync()
    return create_react_agent(
        model=get_llm(),
        tools=tools,
        prompt=SYSTEM_PROMPT,
    )
