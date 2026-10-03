"""Voice assistant entrypoint for pipecat.

A single receptionist agent runs the whole call (identify -> reason -> task ->
confirm), so there is no per-utterance keyword routing on the live path. The
agent keeps conversation + persistent memory per caller (thread_id) and keeps
structured call state in the DB via its state tools.

pipecat's LangchainProcessor calls ``compiled_graph.astream({"input": text})``
and pushes every yielded chunk to TTS, so the reply is spoken incrementally.
The caller's thread is taken from the processor config (session_id).
"""

from typing import Any, AsyncIterator

from langchain_core.runnables import Runnable

from backend.nodes.streaming import DEFAULT_THREAD_ID, astream_answer


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


def _thread_id_from_config(config) -> str:
    """pipecat passes config={"configurable": {"session_id": <participant>}}.
    Use it as the conversation thread so each caller has isolated memory."""
    if isinstance(config, dict):
        configurable = config.get("configurable") or {}
        return (
            configurable.get("thread_id")
            or configurable.get("session_id")
            or DEFAULT_THREAD_ID
        )
    return DEFAULT_THREAD_ID


class _VoiceGraphRunnable(Runnable):
    """Runnable consumed by pipecat's LangchainProcessor.

    astream({"input": text}) -> yields reply chunks for incremental TTS.
    """

    async def astream(
        self, input: Any, config=None, **kwargs
    ) -> AsyncIterator[str]:
        user_text = _extract_input(input)
        thread_id = _thread_id_from_config(config)
        async for chunk in astream_answer(user_text, thread_id):
            yield chunk

    async def ainvoke(self, input: Any, config=None, **kwargs) -> str:
        parts = []
        async for chunk in self.astream(input, config, **kwargs):
            parts.append(chunk)
        return "".join(parts)

    def invoke(self, input: Any, config=None, **kwargs) -> str:
        import asyncio

        return asyncio.run(self.ainvoke(input, config, **kwargs))


# What pipecat imports.
compiled_graph = _VoiceGraphRunnable()

# Backwards-compatible alias.
workflow = compiled_graph
