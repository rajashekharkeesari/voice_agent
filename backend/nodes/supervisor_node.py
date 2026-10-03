"""Supervisor node: takes the user transcript from state.input, runs the
supervisor ReAct agent, and writes the spoken reply to state.output."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from backend.agents.supervisor_agent import SYSTEM_PROMPT
from backend.LLM.llm import get_llm
from backend.mcp_client.client import load_mcp_tools_sync


def _extract_text(result) -> str:
    """Pull the final assistant text out of a react-agent result or a plain
    LLM response."""
    if isinstance(result, dict) and "messages" in result:
        for message in reversed(result["messages"]):
            if isinstance(message, AIMessage) and message.content:
                return _as_text(message.content)
        return ""
    return _as_text(getattr(result, "content", result))


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


def supervisor_node(state):
    """LangGraph node. `state` is a HospitalState-compatible object/dict."""
    user_text = _get(state, "input", "")

    try:
        # Prefer a tool-using agent when tools are available.
        tools = load_mcp_tools_sync()
        if tools:
            from langgraph.prebuilt import create_react_agent

            agent = create_react_agent(
                model=get_llm(), tools=tools, prompt=SYSTEM_PROMPT
            )
            result = agent.invoke(
                {"messages": [HumanMessage(content=user_text)]}
            )
            reply = _extract_text(result)
        else:
            # No tools: just ask the LLM directly.
            response = get_llm().invoke(
                [
                    SystemMessage(content=SYSTEM_PROMPT),
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


def _get(state, key, default=None):
    if isinstance(state, dict):
        return state.get(key, default)
    return getattr(state, key, default)
