"""MCP client that connects to the Hospital MCP server and exposes its tools
as LangChain tools for the agent/graph.

We talk to the MCP server with the official ``mcp`` SDK over streamable HTTP
and wrap each remote tool in a LangChain ``StructuredTool``. This avoids a
hard dependency on langchain-mcp-adapters (whose pinned ``mcp`` range
conflicts with the fastmcp server), while keeping the agent tool-calling
interface unchanged.

Public API:
    - async get_mcp_tools()   -> list[StructuredTool] (raises if server down)
    - load_mcp_tools_sync()   -> list[StructuredTool] ([] if server down)
    - tools                   -> lazily populated module-level list
"""

import os

from dotenv import load_dotenv

load_dotenv()

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000/mcp")

# Populated by load_mcp_tools_sync()/get_mcp_tools(). Starts empty so importing
# this module has no side effects and never raises.
tools: list = []


_JSON_TO_PY = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
    "array": list,
    "object": dict,
}


def _schema_to_pydantic(name: str, schema: dict):
    """Build a pydantic model from a (simple) JSON schema so LangChain can use
    it as the tool's args_schema."""
    from pydantic import create_model

    schema = schema or {}
    properties = schema.get("properties", {}) or {}
    required = set(schema.get("required", []) or [])

    fields = {}
    for field_name, spec in properties.items():
        py_type = _JSON_TO_PY.get(spec.get("type", "string"), str)
        default = ... if field_name in required else spec.get("default", None)
        fields[field_name] = (py_type, default)

    return create_model(f"{name}_Args", **fields)


async def get_mcp_tools():
    """Load tools from the running MCP server as LangChain StructuredTools."""
    from langchain_core.tools import StructuredTool
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client

    # We open a fresh session per tool call (stateless), which keeps the
    # wrapped tools usable outside the original async context.
    async def _list_tool_specs():
        async with streamable_http_client(MCP_SERVER_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                listed = await session.list_tools()
                return listed.tools

    async def _call_remote(tool_name: str, arguments: dict):
        async with streamable_http_client(MCP_SERVER_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments or {})
                # Prefer structured content; fall back to text blocks.
                if getattr(result, "structuredContent", None):
                    return result.structuredContent
                texts = []
                for block in result.content or []:
                    text = getattr(block, "text", None)
                    if text:
                        texts.append(text)
                return "\n".join(texts)

    specs = await _list_tool_specs()

    langchain_tools = []
    for spec in specs:
        name = spec.name
        description = spec.description or name
        args_model = _schema_to_pydantic(name, spec.input_schema)

        def _make_coro(tool_name):
            async def _tool(**kwargs):
                return await _call_remote(tool_name, kwargs)

            return _tool

        langchain_tools.append(
            StructuredTool.from_function(
                coroutine=_make_coro(name),
                name=name,
                description=description,
                args_schema=args_model,
            )
        )

    return langchain_tools


def load_mcp_tools_sync():
    """Best-effort synchronous load. Returns [] if the MCP server is not
    running so the rest of the app keeps working.

    Works whether or not there is already a running event loop: inside an
    async context (like the pipecat bot) we can't call asyncio.run(), so we
    run the coroutine in a dedicated worker thread with its own loop.
    """
    import asyncio

    global tools

    def _run_in_new_loop():
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(get_mcp_tools())
        finally:
            loop.close()

    try:
        try:
            asyncio.get_running_loop()
            in_loop = True
        except RuntimeError:
            in_loop = False

        if in_loop:
            # A loop is already running (e.g. the pipecat pipeline). Run the
            # async load in a separate thread to avoid nested-loop errors.
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                tools = pool.submit(_run_in_new_loop).result()
        else:
            tools = asyncio.run(get_mcp_tools())
    except Exception as exc:  # noqa: BLE001 - MCP tools are optional
        from loguru import logger

        logger.warning(
            "Could not load MCP tools from {} ({}). "
            "Continuing without external tools.",
            MCP_SERVER_URL,
            exc,
        )
        tools = []
    return tools
