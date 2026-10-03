"""Two-node LangGraph workflow for the hospital voice assistant.

Structure (as designed):

    START -> supervisor
    supervisor -> (conditional) -> appointment | END
    appointment -> supervisor        (loops back; supervisor then ENDs)

The conditional routes to the appointment node when the request is
appointment-related and hasn't been handled yet. The appointment node sets
`handled=True`, so on the loop-back the supervisor conditional goes to END
(no infinite loop).

pipecat integration: pipecat's LangchainProcessor calls
``compiled_graph.astream({"input": text})`` and streams the yielded text to
TTS. The raw StateGraph yields state updates, so we wrap it in a small adapter
(``compiled_graph``) that runs the graph and yields the final ``output`` text.
The plain compiled graph is exported as ``app``.
"""

from typing import Any, AsyncIterator

from langchain_core.runnables import Runnable
from langgraph.graph import END, START, StateGraph

from backend.nodes.appointment_node import appointment_node
from backend.nodes.conditional_node import (
    supervisor_to_appointment_condition,
)
from backend.nodes.streaming import (
    DEFAULT_THREAD_ID,
    _get_async_checkpointer,
)
from backend.nodes.supervisor_node import supervisor_node
from backend.states.Hospital_state import HospitalState

# ---------------------------------------------------------------------------
# Build the graph
# ---------------------------------------------------------------------------
workflow = StateGraph(HospitalState)

workflow.add_node("supervisor", supervisor_node)
workflow.add_node("appointment", appointment_node)

workflow.add_edge(START, "supervisor")

workflow.add_conditional_edges(
    "supervisor",
    supervisor_to_appointment_condition,
    {
        "appointment": "appointment",
        END: END,
    },
)

workflow.add_edge("appointment", "supervisor")

# Compile with a persistent ASYNC checkpointer so each caller's conversation is
# remembered across turns (identity, reason, booking details). pipecat invokes
# the graph asynchronously (ainvoke/astream), which the sync SqliteSaver can't
# serve.
app = workflow.compile(checkpointer=_get_async_checkpointer())


# ---------------------------------------------------------------------------
# pipecat adapter: {"input": text} -> streamed reply text
# ---------------------------------------------------------------------------
def _extract_input(payload: Any) -> str:
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        return (
            payload.get("input")
            or payload.get("text")
            or payload.get("message")
            or ""
        )
    return getattr(payload, "input", "") or ""


def _output_of(result) -> str:
    if isinstance(result, dict):
        return result.get("output", "") or ""
    return getattr(result, "output", "") or ""


def _thread_config(config) -> dict:
    """pipecat passes config={"configurable": {"session_id": <participant>}}.
    Map it to the thread_id the checkpointer needs so each caller has isolated
    conversation memory. Each turn starts a fresh `handled`/`output` by
    resetting those; identity/reason persist via the checkpointer + call-state
    store."""
    thread_id = DEFAULT_THREAD_ID
    if isinstance(config, dict):
        configurable = config.get("configurable") or {}
        thread_id = (
            configurable.get("thread_id")
            or configurable.get("session_id")
            or DEFAULT_THREAD_ID
        )
    return {"configurable": {"thread_id": thread_id}}


class _VoiceGraphRunnable(Runnable):
    """Adapter consumed by pipecat's LangchainProcessor.

    astream({"input": text}) -> yields the graph's final reply text.
    """

    async def astream(
        self, input: Any, config=None, **kwargs
    ) -> AsyncIterator[str]:
        user_text = _extract_input(input)
        result = await app.ainvoke(
            {"input": user_text, "handled": False, "output": ""},
            config=_thread_config(config),
        )
        text = _output_of(result)
        if text:
            yield text

    async def ainvoke(self, input: Any, config=None, **kwargs) -> str:
        user_text = _extract_input(input)
        result = await app.ainvoke(
            {"input": user_text, "handled": False, "output": ""},
            config=_thread_config(config),
        )
        return _output_of(result)

    def invoke(self, input: Any, config=None, **kwargs) -> str:
        import asyncio

        # The graph uses an async checkpointer, so run the async path.
        return asyncio.run(self.ainvoke(input, config, **kwargs))


# What pipecat imports.
compiled_graph = _VoiceGraphRunnable()
