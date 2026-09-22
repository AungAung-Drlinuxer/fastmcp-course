"""M4 — the server publishes what it says it publishes, over the in-process transport."""
from __future__ import annotations

from fastmcp import Client

from M4_fastmcp_basics.code.hello_server import mcp


async def test_server_name_and_tools():
    assert mcp.name == "course-hello"
    names = {t.name for t in await mcp.list_tools()}
    assert {"ping", "add"} <= names


async def test_the_generated_schema_reaches_the_client():
    """Server-side and client-side tool objects expose the schema under DIFFERENT names.

    Measured on 4.0.5:
      server:  await mcp.list_tools()    -> FunctionTool          -> .parameters
      client:  await client.list_tools() -> mcp_types.Tool        -> .input_schema
      and reading `.inputSchema` on the client emits:
        FastMCPDeprecationWarning: MCP SDK v2 renamed this field to `input_schema`.
    """
    async with Client(mcp) as client:
        tool = next(t for t in await client.list_tools() if t.name == "add")
        assert set(tool.input_schema["properties"]) == {"a", "b"}
        assert tool.input_schema["required"] == ["a", "b"]
        assert tool.description.strip().startswith("Add two numbers")


async def test_round_trip():
    async with Client(mcp) as client:
        assert (await client.call_tool("ping", {})).data == "pong"
        assert (await client.call_tool("add", {"a": 2, "b": 3})).data == 5


async def test_a_bad_argument_is_rejected_before_the_function_runs():
    async with Client(mcp) as client:
        try:
            await client.call_tool("add", {"a": "two", "b": 3})
        except Exception as exc:
            assert "validation" in str(exc).lower() or "int" in str(exc).lower()
        else:
            raise AssertionError("invalid input was accepted")
