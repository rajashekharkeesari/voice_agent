"""Streaming receptionist with persistent + conversation memory.

A single receptionist agent runs the whole call. It streams its reply as it is
generated (so pipecat speaks incrementally) and remembers the conversation per
caller via a persistent SqliteSaver checkpointer.

Memory:
  - Conversation memory: LangGraph checkpointer keyed by thread_id (the pipecat
    participant id). The agent sees the running message history each turn.
  - Persistent memory: SqliteSaver writes that history to disk, so a dropped
    call can resume. Structured call state (identity, reason, booking slots)
    also lives in the DB via the update_call_state / get_call_state tools, so
    state reflects BOTH patient utterances and the AI's decisions.

Degrades gracefully: if there is no API key / tools / server, it still answers
(LLM-only) or yields a short spoken apology, so the bot is never silent.
"""

import os

from langchain_core.messages import AIMessageChunk, HumanMessage, SystemMessage

from backend.agents.receptionist_agent import build_receptionist_prompt
from backend.LLM.llm import get_llm
from backend.mcp_client.client import load_mcp_tools_sync

DEFAULT_THREAD_ID = "default"

# Persistent checkpointer (SqliteSaver) shared across turns/threads.
_checkpointer = None
_checkpointer_ctx = None

# Cache the compiled agent per (thread_id, tool_count) so the receptionist
# prompt (which embeds thread_id) is stable and memory persists across turns.
_agent_cache: dict = {}


def _get_checkpointer():
    """Return a persistent SqliteSaver (falls back to in-memory MemorySaver
    if the sqlite saver package isn't available)."""
    global _checkpointer, _checkpointer_ctx
    if _checkpointer is not None:
        return _checkpointer

    db_path = os.getenv("CHECKPOINT_DB", "receptionist_memory.sqlite")
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver

        # from_conn_string returns a context manager; enter it for the process
        # lifetime so the connection stays open.
        _checkpointer_ctx = SqliteSaver.from_conn_string(db_path)
        _checkpointer = _checkpointer_ctx.__enter__()
    except Exception:  # noqa: BLE001 - fall back to in-memory
        from langgraph.checkpoint.memory import MemorySaver

        _checkpointer = MemorySaver()
    return _checkpointer


def _get_agent(thread_id: str, tools):
    key = (thread_id, len(tools))
    agent = _agent_cache.get(key)
    if agent is None:
        from langgraph.prebuilt import create_react_agent

        agent = create_react_agent(
            model=get_llm(),
            tools=tools,
            prompt=build_receptionist_prompt(thread_id),
            checkpointer=_get_checkpointer(),
        )
        _agent_cache[key] = agent
    return agent


def _chunk_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                parts.append(block.get("text", ""))
            else:
                parts.append(str(block))
        return "".join(parts)
    return str(content or "")


async def _astream_llm_only(user_text: str, thread_id: str):
    """No tools available: still behave like the receptionist, best-effort."""
    prompt = build_receptionist_prompt(thread_id)
    async for chunk in get_llm().astream(
        [SystemMessage(content=prompt), HumanMessage(content=user_text)]
    ):
        text = _chunk_text(getattr(chunk, "content", chunk))
        if text:
            yield text


async def _astream_agent(user_text: str, tools, thread_id: str):
    agent = _get_agent(thread_id, tools)
    config = {"configurable": {"thread_id": thread_id or DEFAULT_THREAD_ID}}

    async for message_chunk, _metadata in agent.astream(
        {"messages": [HumanMessage(content=user_text)]},
        config=config,
        stream_mode="messages",
    ):
        if not isinstance(message_chunk, AIMessageChunk):
            continue
        if getattr(message_chunk, "tool_call_chunks", None):
            continue
        text = _chunk_text(message_chunk.content)
        if text:
            yield text


async def astream_answer(user_text: str, thread_id: str = DEFAULT_THREAD_ID):
    """Yield the receptionist's reply incrementally, remembering the call on
    this thread_id."""
    emitted_any = False
    try:
        tools = load_mcp_tools_sync()
        if tools:
            async for text in _astream_agent(user_text, tools, thread_id):
                emitted_any = True
                yield text
        else:
            async for text in _astream_llm_only(user_text, thread_id):
                emitted_any = True
                yield text
    except Exception as exc:  # noqa: BLE001 - never leave the bot silent
        from loguru import logger

        logger.error("astream_answer failed: {}", exc)
        if not emitted_any:
            yield (
                "Sorry, I'm having a little trouble right now. "
                "Could you say that again?"
            )
