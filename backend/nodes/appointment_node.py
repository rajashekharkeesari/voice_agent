"""Appointment node: runs the appointment ReAct agent against the user
transcript and writes the spoken reply to state.output."""

from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.appointment_agent import APPOINTMENT_PROMPT
from backend.LLM.llm import get_llm
from backend.mcp_client.client import load_mcp_tools_sync
from backend.nodes.supervisor_node import _extract_text, _get


def appointment_node(state):
    user_text = _get(state, "input", "")

    try:
        tools = load_mcp_tools_sync()
        if tools:
            from langgraph.prebuilt import create_react_agent

            agent = create_react_agent(
                model=get_llm(), tools=tools, prompt=APPOINTMENT_PROMPT
            )
            result = agent.invoke(
                {"messages": [HumanMessage(content=user_text)]}
            )
            reply = _extract_text(result)
        else:
            response = get_llm().invoke(
                [
                    SystemMessage(content=APPOINTMENT_PROMPT),
                    HumanMessage(content=user_text),
                ]
            )
            reply = _extract_text(response)
    except Exception as exc:  # noqa: BLE001 - degrade gracefully for voice
        from loguru import logger

        logger.error("appointment_node failed: {}", exc)
        reply = (
            "Sorry, I couldn't process the appointment request just now. "
            "Could you tell me the doctor and date again?"
        )

    return {"output": reply or "Could you repeat the appointment details?"}
