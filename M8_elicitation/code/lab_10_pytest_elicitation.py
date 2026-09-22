"""LAB 10 — testing an elicitation flow without a human in the loop.

An elicitation handler is just a coroutine, so a test can hand the server any
decision it likes. That makes all three outcomes testable, including the one no
manual tester performs: cancel.

Run:
    uv run pytest M8_elicitation/code/lab_10_pytest_elicitation.py -q
"""
from __future__ import annotations

from typing import Any

import pytest
from fastmcp import Client, Context, FastMCP
from fastmcp.client.elicitation import ElicitResult
from pydantic import BaseModel, Field

mcp = FastMCP("elicitation-under-test")

AUDIT: list[dict[str, Any]] = []


class Approval(BaseModel):
    """A ticket reference proves a human really looked at this."""

    proceed: bool = Field(description="True to continue, false to stop")
    ticket: str = Field(default="", description="Change ticket reference")


@mcp.tool
async def deploy(version: str, ctx: Context) -> dict:
    """Deploy a version, but only with a ticket from a human.

    Args:
        version: The version tag to deploy.
    """
    answer = await ctx.elicit(
        message=f"Deploy {version} to production? A change ticket is required.",
        response_type=Approval,
    )
    action = getattr(answer, "action", "accept")
    if action != "accept":
        AUDIT.append({"version": version, "status": action})
        return {"ok": False, "status": action}

    if not answer.data.proceed:
        AUDIT.append({"version": version, "status": "refused_by_user"})
        return {"ok": False, "status": "refused_by_user"}

    AUDIT.append({"version": version, "status": "deployed", "ticket": answer.data.ticket})
    return {"ok": True, "status": "deployed", "version": version,
            "ticket": answer.data.ticket}


def handler_returning(value: dict[str, Any]):
    async def handler(message: str, response_type: Any, params: Any = None,
                      context: Any = None) -> Any:
        return value

    return handler


def handler_with_action(action: str):
    async def handler(message: str, response_type: Any, params: Any = None,
                      context: Any = None) -> Any:
        return ElicitResult(action=action)

    return handler


@pytest.fixture(autouse=True)
def clean_audit():
    """Module-level state belongs to the test, not to the previous test."""
    AUDIT.clear()
    yield
    AUDIT.clear()


async def test_accept_with_a_ticket_deploys():
    async with Client(mcp, mode="legacy",
                      elicitation_handler=handler_returning(
                          {"proceed": True, "ticket": "CHG-1"})) as client:
        data = (await client.call_tool("deploy", {"version": "1.4.0"})).data
    assert data == {"ok": True, "status": "deployed", "version": "1.4.0", "ticket": "CHG-1"}
    assert AUDIT[0]["status"] == "deployed"


async def test_accept_but_proceed_false_is_a_refusal_not_a_deploy():
    async with Client(mcp, mode="legacy",
                      elicitation_handler=handler_returning(
                          {"proceed": False, "ticket": ""})) as client:
        data = (await client.call_tool("deploy", {"version": "1.4.0"})).data
    assert data["status"] == "refused_by_user"
    assert AUDIT[0]["status"] == "refused_by_user"


async def test_decline_is_reported_and_changes_nothing():
    async with Client(mcp, mode="legacy",
                      elicitation_handler=handler_with_action("decline")) as client:
        data = (await client.call_tool("deploy", {"version": "1.4.0"})).data
    assert data["status"] == "decline"
    assert AUDIT == [{"version": "1.4.0", "status": "decline"}]


async def test_cancel_is_distinct_from_decline():
    async with Client(mcp, mode="legacy",
                      elicitation_handler=handler_with_action("cancel")) as client:
        data = (await client.call_tool("deploy", {"version": "1.4.0"})).data
    assert data["status"] == "cancel"


async def test_the_default_mode_cannot_elicit_at_all():
    """A regression guard for the mode requirement itself."""
    async with Client(mcp, elicitation_handler=handler_returning(
            {"proceed": True, "ticket": "CHG-1"})) as client:
        with pytest.raises(Exception) as excinfo:
            await client.call_tool("deploy", {"version": "1.4.0"})
    assert "unavailable on 2026-07-28" in str(excinfo.value)


async def test_the_handler_is_async_or_the_tool_fails():
    def sync_def(message: str, response_type: Any, params: Any = None,
                 context: Any = None) -> Any:
        return {"proceed": True, "ticket": "CHG-1"}

    async with Client(mcp, mode="legacy", elicitation_handler=sync_def) as client:
        with pytest.raises(Exception) as excinfo:
            await client.call_tool("deploy", {"version": "1.4.0"})
    assert "await" in str(excinfo.value)
