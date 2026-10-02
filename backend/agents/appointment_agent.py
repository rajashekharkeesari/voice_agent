from langchain.agents import create_agent
from backend.LLM import llm
from backend.mcp_client import tools
from langchain.prompts import PromptTemplate
from backend.states.appointment_state import AppointmentState


system_prompt=PromptTemplate.from_template("""
You are an appointment agent for a hospital voice assistant.
You are responsible for:
- Understanding the user's request regarding appointments.
- Using the available tools to get appointment information.
- Asking for missing information.
- Returning a clear response to the user.
{AppointmentState}
""")

appointment_agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt
   
)