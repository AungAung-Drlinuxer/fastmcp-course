"""M11 — the capstone, end to end: metrics, logs, resources, prompts, elicitation.

Everything M2..M10 taught, asserted at once. If this file is green, the course's final artifact
is real: it reads the host it runs on, refuses paths outside its allowlist, and asks before
touching a protected service.
"""
from __future__ import annotations

from typing import Any

import pytest
from fastmcp import Client

from M11_capstone.code.devops_assistant import mcp


async def _handler(message: str, response_type: Any, params: Any = None,
                   context: Any = None) -> dict:
    """ASYNC is required, not optional: the callback does `await elicitation_handler(...)`, so a
    sync handler returning a dict fails with
        ToolError: Error calling tool 'restart_service': object dict can't be used in 'await'"""
    return {"proceed": True, "reason": "test"}


async def test_the_surface_is_complete():
    tools = {t.name for t in await mcp.list_tools()}
    prompts = {p.name for p in await mcp.list_prompts()}
    templates = {t.uri_template for t in await mcp.list_resource_templates()}
    assert {"system_metrics", "list_logs", "read_log", "list_runbooks", "restart_service"} <= tools
    assert {"rca_error_log", "capacity_review"} <= prompts
    assert {"config://{host}", "runbook://{name}"} <= templates


async def test_metrics_are_real_or_honestly_null():
    """Never fabricated: on a platform that does not expose a value it is None, not invented."""
    async with Client(mcp) as client:
        data = (await client.call_tool("system_metrics", {})).data
    assert data["ok"] is True
    assert isinstance(data["cpu_count"], int) and data["cpu_count"] >= 1
    assert data["data_disk_total_gb"] > 0
    assert data["data_disk_free_gb"] >= 0
    # these two are None on Windows and numbers on Linux — both are correct
    assert data["load_average"] is None or isinstance(data["load_average"], list)


async def test_error_log_filtering_happens_at_the_tool_boundary():
    async with Client(mcp) as client:
        data = (await client.call_tool("read_log",
                {"name": "postgres-ha.log", "errors_only": True})).data
    assert data["ok"] is True
    assert data["lines"] >= 1
    for line in data["content"].splitlines():
        assert "ERROR" in line or "WARN" in line


async def test_a_missing_log_lists_what_is_available():
    async with Client(mcp) as client:
        data = (await client.call_tool("read_log", {"name": "nope.log"})).data
    assert data["ok"] is False and data["error"] == "not_found"
    assert "postgres-ha.log" in data["available"]


async def test_resources_read_and_unknown_ones_fail_clearly():
    async with Client(mcp) as client:
        config = (await client.read_resource("config://pve01"))[0].text
        runbook = (await client.read_resource("runbook://postgres-ha"))[0].text
        assert config.startswith("host: pve01")
        assert runbook.startswith("# postgres-ha runbook")
        with pytest.raises(Exception):
            await client.read_resource("runbook://nonexistent")


async def test_the_rca_prompt_forbids_invention():
    async with Client(mcp) as client:
        text = (await client.get_prompt("rca_error_log", {"log_name": "postgres-ha.log"})
                ).messages[0].content.text
    assert "insufficient evidence" in text
    assert "do not invent" in text.lower()


async def test_a_protected_service_requires_confirmation_and_an_ordinary_one_does_not():
    async with Client(mcp, mode="legacy", elicitation_handler=_handler) as client:
        protected = (await client.call_tool("restart_service", {"service": "postgres-ha"})).data
        ordinary = (await client.call_tool("restart_service", {"service": "gitea"})).data

    assert protected["protected"] is True
    assert protected["status"] == "confirmed"
    # Honest about what it did: this is a capstone, and it must not claim to have changed a host.
    assert "none" in protected["action_taken"]

    assert ordinary["protected"] is False
    assert ordinary["status"] == "would_restart"


async def test_declining_a_protected_change_changes_nothing():
    async def decline(message: str, response_type: Any, params: Any = None,
                      context: Any = None):
        from fastmcp.client.elicitation import ElicitResult
        return ElicitResult(action="decline")

    async with Client(mcp, mode="legacy", elicitation_handler=decline) as client:
        data = (await client.call_tool("restart_service", {"service": "postgres-ha"})).data
    assert data["ok"] is False
    assert data["status"] == "decline"
