"""Shared chat model for the agents and graph nodes.

Provider-agnostic: pick Llama / Qwen / OpenAI (or any OpenAI-compatible
endpoint) with environment variables. The model is created lazily so importing
this module (and compiling the LangGraph) never requires a key or a running
server; it's only built when first invoked.

Configure in backend/.env with LLM_PROVIDER:

  # 1) Ollama (local Llama/Qwen; run `ollama serve` + `ollama pull <model>`)
  LLM_PROVIDER = ollama
  LLM_MODEL    = llama3.1          # or: qwen2.5, llama3.2, qwen2.5:14b, ...
  OLLAMA_BASE_URL = http://localhost:11434   # optional (this is the default)

  # 2) Groq (hosted Llama/Qwen, very fast; needs a Groq API key)
  LLM_PROVIDER = groq
  LLM_MODEL    = llama-3.3-70b-versatile    # or: qwen-2.5-32b, ...
  GROQ_API_KEY = gsk_...

  # 3) Any OpenAI-compatible server (vLLM, Together, OpenRouter, LM Studio...)
  LLM_PROVIDER   = openai_compatible
  LLM_MODEL      = meta-llama/Llama-3.1-8B-Instruct
  LLM_BASE_URL   = http://localhost:8001/v1
  LLM_API_KEY    = sk-...           # some servers accept any non-empty value

  # 4) OpenAI (default, original behaviour)
  LLM_PROVIDER = openai
  LLM_MODEL    = gpt-4o-mini
  OPENAI_API_KEY = sk-...

All providers stream (streaming=True) so TTS speaks incrementally.
"""

import os

from dotenv import load_dotenv

load_dotenv()

_llm = None


def _build_llm():
    provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()

    # Shared across providers. OPENAI_MODEL kept for backwards compatibility.
    model = os.getenv("LLM_MODEL") or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.3"))

    if provider == "ollama":
        # Local Llama/Qwen via Ollama. Uses langchain-ollama if available,
        # otherwise falls back to Ollama's OpenAI-compatible endpoint.
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        try:
            from langchain_ollama import ChatOllama

            return ChatOllama(
                model=model,
                temperature=temperature,
                base_url=base_url,
            )
        except ImportError:
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=model,
                temperature=temperature,
                streaming=True,
                base_url=f"{base_url.rstrip('/')}/v1",
                api_key="ollama",  # Ollama ignores the key but one is required
            )

    if provider == "groq":
        # Hosted Llama/Qwen via Groq.
        try:
            from langchain_groq import ChatGroq

            return ChatGroq(
                model=model,
                temperature=temperature,
                api_key=os.getenv("GROQ_API_KEY"),
            )
        except ImportError:
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=model,
                temperature=temperature,
                streaming=True,
                base_url="https://api.groq.com/openai/v1",
                api_key=os.getenv("GROQ_API_KEY"),
            )

    if provider in ("openai_compatible", "openai-compatible", "custom"):
        # Any OpenAI-compatible server (vLLM, Together, OpenRouter, LM Studio).
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model,
            temperature=temperature,
            streaming=True,
            base_url=os.getenv("LLM_BASE_URL"),
            api_key=os.getenv("LLM_API_KEY") or "not-needed",
        )

    # Default: OpenAI.
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=model,
        temperature=temperature,
        streaming=True,
        api_key=os.getenv("OPENAI_API_KEY"),
    )


def get_llm():
    """Return a singleton chat model, created on first use."""
    global _llm
    if _llm is None:
        _llm = _build_llm()
    return _llm


class _LazyLLM:
    """Transparent proxy so existing `llm.invoke(...)` / `create_react_agent(
    model=llm, ...)` call sites keep working while deferring construction."""

    def __getattr__(self, name):
        return getattr(get_llm(), name)

    def __call__(self, *args, **kwargs):
        return get_llm()(*args, **kwargs)


# Importable singleton used across the codebase.
llm = _LazyLLM()
