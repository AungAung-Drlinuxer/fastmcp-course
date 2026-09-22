"""M9 — the client loop is ordinary code; the model is one replaceable node."""
from __future__ import annotations

from pathlib import Path

from fastmcp import Client

SERVER = Path(__file__).parents[1] / "M4_fastmcp_basics" / "code" / "hello_server.py"


async def test_a_client_can_launch_a_server_file_over_stdio():
    """This is how an editor does it: the client owns the child process."""
    async with Client(SERVER) as client:
        names = {t.name for t in await client.list_tools()}
        assert {"ping", "add"} <= names
        assert (await client.call_tool("add", {"a": 4, "b": 6})).data == 10


async def test_the_schema_is_what_a_model_would_choose_from():
    async with Client(SERVER) as client:
        tools = await client.list_tools()
    add = next(t for t in tools if t.name == "add")
    assert add.description
    assert set(add.input_schema["properties"]) == {"a", "b"}
