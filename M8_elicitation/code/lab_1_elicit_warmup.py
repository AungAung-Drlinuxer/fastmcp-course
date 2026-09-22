"""LAB 1 — the warm-up: one server, one client, four question shapes.

Goal: see with your own eyes that (a) the server pauses mid-tool to ask, (b) the
client handler receives a GENERATED class built from the JSON Schema, not the
server's own Python type, and (c) the whole thing only works with mode="legacy".

Run:
    uv run python -m M8_elicitation.code.lab_1_elicit_warmup
"""
from __future__ import annotations

import asyncio
from typing import Any

from fastmcp import Client, Context, FastMCP
from fastmcp.client.elicitation import ElicitResult

mcp = FastMCP("warmup")


# --- four shapes of question, in the order you should learn them -------------

@mcp.tool
async def ask_name(ctx: Context) -> dict:
    """Ask for one string. FastMCP wraps it as {"value": <string>} on the wire."""
    result = await ctx.elicit("What is your name?", str)
    action = getattr(result, "action", "accept")
    if action != "accept":
        return {"ok": False, "status": action}
    return {"ok": True, "status": "accepted", "name": result.data}


@mcp.tool
async def ask_restart(ctx: Context) -> dict:
    """Ask one yes/no question. Pass bool, never a bare empty schema."""
    result = await ctx.elicit("Restart the service now?", bool)
    action = getattr(result, "action", "accept")
    if action != "accept":
        return {"ok": False, "status": action}
    return {"ok": True, "status": "accepted", "restart": result.data}


@mcp.tool
async def ask_replicas(ctx: Context) -> dict:
    """Ask for one integer."""
    result = await ctx.elicit("How many replicas should the service have?", int)
    action = getattr(result, "action", "accept")
    if action != "accept":
        return {"ok": False, "status": action}
    return {"ok": True, "status": "accepted", "replicas": result.data}


@mcp.tool
async def ask_region(ctx: Context) -> dict:
    """Ask a MULTIPLE-CHOICE question: a list of strings becomes a dropdown."""
    result = await ctx.elicit(
        "Which region should the deployment target?",
        ["ap-southeast-1", "us-east-1", "eu-west-1"],
    )
    action = getattr(result, "action", "accept")
    if action != "accept":
        return {"ok": False, "status": action}
    return {"ok": True, "status": "accepted", "region": result.data}


# --- the host side: one handler, deterministic, prints what it received ------

def make_handler(answers: dict[str, Any]):
    """Return an async elicitation handler that answers from a lookup table."""

    async def handler(message: str, response_type: Any, params: Any = None,
                      context: Any = None) -> Any:
        # response_type is a class FastMCP GENERATED from the schema it received.
        # It is never the server's own `str` / `bool` / `int` object.
        schema = getattr(params, "requested_schema", None)
        print(f"    [client] response_type = {response_type!r}")
        print(f"    [client] requested_schema = {schema}")
        print(f"    [client] message = {message!r}")
        return answers[message]

    return handler


ANSWERS = {
    "What is your name?": {"value": "Alice"},
    "Restart the service now?": {"value": True},
    "How many replicas should the service have?": {"value": 3},
    "Which region should the deployment target?": {"value": "ap-southeast-1"},
}


async def main() -> None:
    async with Client(mcp, mode="legacy", elicitation_handler=make_handler(ANSWERS)) as client:
        print(f"negotiated protocol era: {client.protocol_version}")
        for name in ("ask_name", "ask_restart", "ask_replicas", "ask_region"):
            print(f"  {name}:")
            outcome = await client.call_tool(name, {})
            print("    ->", outcome.data)
        print()

        # The same tool, three client behaviours, three different server answers.
        for action in ("decline", "cancel"):
            async def stubborn(message: str, response_type: Any, params: Any = None,
                               context: Any = None, _action: str = action) -> Any:
                print(f"    [client] the user chose to {_action!r}")
                return ElicitResult(action=_action)

            async with Client(mcp, mode="legacy", elicitation_handler=stubborn) as c2:
                print(f"  ask_name with a {action} handler:")
                print("    ->", (await c2.call_tool("ask_name", {})).data)


if __name__ == "__main__":
    asyncio.run(main())
