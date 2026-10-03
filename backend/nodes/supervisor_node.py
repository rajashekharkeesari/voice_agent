"""Supervisor node (receptionist front).

Greets, identifies the patient (phone + name), offers registration, finds and
classifies the reason for the call, and handles non-appointment reasons
(availability, general hospital questions) itself. Appointment-type reasons are
routed onward to the appointment node by the conditional edge.

Runs a tool-using ReAct sub-agent so it can call the MCP tools and the call
state tools. The caller's thread_id (for memory + the state store) is read from
the LangGraph config.
"""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from backend.agents.receptionist_agent import build_supervisor_prompt
from backend.LLM.llm import get_llm
from backend.mcp_client.client import load_mcp_tools_sync


def _as_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                parts.append(block.get("text", ""))
            else:
                parts.append(str(block))
        return " ".join(p for p in parts if p).strip()
    return str(content)


def _extract_text(result) -> str:
    """Pull the final assistant text out of a react-agent result or a plain
    LLM response."""
    if isinstance(result, dict) and "messages" in result:
        for message in reversed(result["messages"]):
            if isinstance(message, AIMessage) and message.content:
                return _as_text(message.content)
        return ""
    return _as_text(getattr(result, "content", result))


def _get(state, key, default=None):
    if isinstance(state, dict):
        return state.get(key, default)
    return getattr(state, key, default)


def _thread_id_from_config(config) -> str:
    if isinstance(config, dict):
        configurable = config.get("configurable") or {}
        return (
            configurable.get("thread_id")
            or configurable.get("session_id")
            or "default"
        )
    return "default"


def supervisor_node(state, config=None):
    """LangGraph node. Returns {"output": <reply>} (handled stays False so the
    conditional can route to the appointment node when needed)."""
    user_text = _get(state, "input", "")
    thread_id = _thread_id_from_config(config)
    prompt = build_supervisor_prompt(thread_id)

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

        logger.error("supervisor_node failed: {}", exc)
        reply = (
            "Sorry, I'm having trouble reaching the system right now. "
            "Please try again in a moment."
        )

    return {"output": reply or "I'm sorry, could you repeat that?"}
