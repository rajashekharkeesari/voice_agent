"""Appointment node (receptionist action).

Handles book / reschedule / cancel with a confirm-as-you-go flow, using the
MCP tools and the call-state store. Sets handled=True so the supervisor
conditional ends the turn after this node runs (no infinite loop).
"""

from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.receptionist_agent import build_appointment_prompt
from backend.LLM.llm import get_llm
from backend.mcp_client.client import load_mcp_tools_sync
from backend.nodes.supervisor_node import (
    _extract_text,
    _get,
    _thread_id_from_config,
)


def appointment_node(state, config=None):
    user_text = _get(state, "input", "")
    thread_id = _thread_id_from_config(config)
    prompt = build_appointment_prompt(thread_id)

    try:
        tools = load_mcp_tools_sync()
        if tools:
            from langgraph.prebuilt import create_react_agent

            agent = create_react_agent(
                model=get_llm(), tools=tools, prompt=prompt
            )
            result = agent.invoke(
                {"messages": [HumanMessage(content=user_text)]}
            )
            reply = _extract_text(result)
        else:
            response = get_llm().invoke(
                [
                    SystemMessage(content=prompt),
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

    return {
        "output": reply or "Could you repeat the appointment details?",
        "handled": True,
    }
