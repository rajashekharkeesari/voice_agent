from backend.LLM import llm 
from backend.mcp_client import tools
from langchain.agents import create_agent
from langchain.agents import AgentExecutor
from langchain.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

SYSTEM_PROMPT = """
You are the supervisor for a hospital voice assistant.
You are responsible for:
- Understanding the user's request.
- Determining whether the request concerns appointments,
  doctors, patients, hospital availability, or other hospital services.
- Using the available tools when necessary.
- Asking for missing information.
- Returning a clear response to the user.
"""


supervisor_agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
)
