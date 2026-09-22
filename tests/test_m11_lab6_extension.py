"""The extension's own test — an extension without a test is an extension you will delete.

`lab_6_estate_memory_tool` attaches three tools to the capstone's server object. That is only
safe if the capstone's own promises still hold AND the new tools inherit the same boundary. This
file asserts both, so a future edit that breaks either one fails loudly instead of quietly.

The second test is the one that matters: it does not test code this file's author wrote. It tests
code the author BORROWED (`_resolve`), which is the whole reason an extension should import the
capstone's helpers rather than re-implement a path check.

Run:
    uv run pytest -q tests/test_m11_lab6_extension.py
"""
from __future__ import annotations

import pytest
from fastmcp import Client

# Importing the extension registers its tools on the shared server object. The import is the
# fixture, and the side effect is the point.
import M11_capstone.code.lab_6_estate_memory_tool  # noqa: F401
from M11_capstone.code.devops_assistant import mcp

CAPSTONE_TOOLS = {"system_metrics", "list_logs", "read_log", "list_runbooks", "restart_service"}
EXTENSION_TOOLS = {"save_note", "read_note", "list_notes"}


async def test_your_tools_appear_beside_the_capstone_s_own():
    async with Client(mcp) as client:
        names = {t.name for t in await client.list_tools()}
    assert EXTENSION_TOOLS <= names, "the extension's tools are not registered"
    assert CAPSTONE_TOOLS <= names, "the capstone's own tools disappeared"


async def test_the_new_tool_reuses_the_capstone_s_boundary():
    """The whole point of importing _resolve: traversal must be refused, for free."""
    async with Client(mcp) as client:
        for attempt in ("../../etc/passwd", "/etc/passwd", "..\\..\\windows\\win.ini"):
            data = (await client.call_tool("read_note", {"name": attempt})).data
            assert data["error"] == "path_not_allowed", (
                f"{attempt!r} was not refused with the capstone's own error code: {data}")


async def test_an_empty_note_is_refused_rather_than_stored():
    """`text.strip()` not `text`: three spaces is not content."""
    async with Client(mcp) as client:
        data = (await client.call_tool("save_note", {"name": "blank", "text": "   "})).data
    assert data["ok"] is False
    assert data["error"] == "empty_note"


async def test_a_missing_note_lists_the_alternatives():
    async with Client(mcp) as client:
        data = (await client.call_tool("read_note", {"name": "no-such-note"})).data
    assert data["ok"] is False
    assert data["error"] == "not_found"
    assert data["available"], "a missing note must teach the caller what exists"


async def test_both_directions_of_the_note_are_bounded():
    """A note tool that echoes 20 000 characters back into a model's context is a DoS."""
    long_text = "x" * 20000
    async with Client(mcp) as client:
        written = (await client.call_tool("save_note", {"name": "too-big",
                                                        "text": long_text})).data
        read_back = (await client.call_tool("read_note", {"name": "too-big"})).data
    assert written["truncated"] is True
    assert written["bytes"] <= 8192
    assert len(read_back["content"]) <= 8192


@pytest.mark.parametrize("name", ["failover-drill", "note.v2", "postgres-ha", "a_b-1"])
async def test_ordinary_names_round_trip(name: str):
    async with Client(mcp) as client:
        await client.call_tool("save_note", {"name": name, "text": f"body for {name}"})
        data = (await client.call_tool("read_note", {"name": name})).data
    assert data["ok"] is True
    assert data["content"] == f"body for {name}"
