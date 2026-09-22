"""M10 — the boundary stops what it claims to stop, tested with the attacks themselves."""
from __future__ import annotations

import pytest
from fastmcp import Client

from M10_security.code.path_validation import mcp


@pytest.mark.parametrize("attempt", [
    "../../etc/shadow",                 # traversal, POSIX
    "..\\..\\windows\\win.ini",    # traversal, Windows separators
    "/etc/passwd",                      # absolute path
    "logs/../../../etc/hosts",
])
async def test_traversal_is_refused(attempt):
    async with Client(mcp) as client:
        data = (await client.call_tool("read_log", {"name": attempt})).data
    assert data["ok"] is False
    assert data["error"] == "path_not_allowed"


@pytest.mark.parametrize("attempt", [
    "postgres.log; rm -rf /",           # shell chaining is meaningless: there is no shell
    "$(id)",                            # command substitution likewise
    "postgres.log && curl evil",        # injected as a NAME, so it is simply not found
])
async def test_injection_attempts_are_just_bad_filenames(attempt):
    async with Client(mcp) as client:
        data = (await client.call_tool("read_log", {"name": attempt})).data
    assert data["ok"] is False
    assert data["error"] in {"not_found", "path_not_allowed"}


async def test_the_legitimate_read_still_works():
    async with Client(mcp) as client:
        listing = (await client.call_tool("list_logs", {})).data
        assert "postgres.log" in listing["files"]

        tail = (await client.call_tool("read_log", {"name": "postgres.log", "max_lines": 2})).data
        assert tail["ok"] is True and tail["lines"] == 2

        hits = (await client.call_tool("grep_log",
                {"name": "postgres.log", "pattern": "ERROR"})).data
        assert hits["matches"] == 2
        assert all("ERROR" in h["text"] for h in hits["results"])


async def test_output_is_bounded():
    async with Client(mcp) as client:
        capped = (await client.call_tool("read_log", {"name": "postgres.log", "max_lines": 99999})).data
    assert capped["ok"] is True and capped["lines"] <= 1000
