"""LAB 7 — every question shape, and the exact schema each one generates.

`response_type` is not "a type"; it is the thing that decides what the host
renders and what comes back. This lab prints the REAL schema for each shape and
then answers every one of them from a single handler.

Measured in FastMCP 4.0.5: a scalar type (str/bool/int) and a bare list[str] are
wrapped as {"value": ...} on the wire; the dict/titled forms are already
`{"type": "object", ...}` and are sent verbatim.

Run:
    uv run python -m M8_elicitation.code.lab_7_question_shapes
"""
from __future__ import annotations

import asyncio
import json
from typing import Any, Literal

from fastmcp import Client, Context, FastMCP
from fastmcp.client.elicitation import ElicitResult
from fastmcp.server.elicitation import parse_elicit_response_type
from pydantic import BaseModel, Field

mcp = FastMCP("question-shapes")


class Decimals(BaseModel):
    """Numeric input inside a model — the schema keeps the bounds."""

    replicas: int = Field(default=2, ge=1, le=16, description="Replica count")
    cpu_limit: float = Field(default=1.0, gt=0, description="CPU limit in cores")


SHAPES = {
    "str": str,
    "bool": bool,
    "int": int,
    "Literal": Literal["dev", "staging", "prod"],
    "list[str]": ["ap-southeast-1", "us-east-1"],
    "dict titled": {"dev": {"title": "Development"}, "prod": {"title": "Production"}},
    "list[list[str]]": [["ap-southeast-1a", "ap-southeast-1b"]],
    "BaseModel": Decimals,
}


@mcp.tool
async def ask_str(ctx: Context) -> dict:
    r = await ctx.elicit("Your name?", str)
    return {"action": getattr(r, "action", None), "data": getattr(r, "data", None)}


@mcp.tool
async def ask_bool(ctx: Context) -> dict:
    r = await ctx.elicit("Restart now?", bool)
    return {"action": getattr(r, "action", None), "data": getattr(r, "data", None)}


@mcp.tool
async def ask_int(ctx: Context) -> dict:
    r = await ctx.elicit("How many replicas?", int, response_title="Replica count")
    return {"action": getattr(r, "action", None), "data": getattr(r, "data", None)}


@mcp.tool
async def ask_literal(ctx: Context) -> dict:
    r = await ctx.elicit("Which environment?", Literal["dev", "staging", "prod"])
    return {"action": getattr(r, "action", None), "data": getattr(r, "data", None)}


@mcp.tool
async def ask_choice(ctx: Context) -> dict:
    r = await ctx.elicit("Which region?", ["ap-southeast-1", "us-east-1"])
    return {"action": getattr(r, "action", None), "data": getattr(r, "data", None)}


@mcp.tool
async def ask_titled(ctx: Context) -> dict:
    r = await ctx.elicit("Which environment?",
                         {"dev": {"title": "Development"}, "prod": {"title": "Production"}})
    return {"action": getattr(r, "action", None), "data": getattr(r, "data", None)}


@mcp.tool
async def ask_multi(ctx: Context) -> dict:
    r = await ctx.elicit("Which availability zones?", [["ap-southeast-1a", "ap-southeast-1b"]])
    return {"action": getattr(r, "action", None), "data": getattr(r, "data", None)}


@mcp.tool
async def ask_model(ctx: Context) -> dict:
    r = await ctx.elicit("Sizing for the deployment?", Decimals)
    data = getattr(r, "data", None)
    return {"action": getattr(r, "action", None),
            "replicas": getattr(data, "replicas", None),
            "cpu_limit": getattr(data, "cpu_limit", None)}


ANSWERS: dict[str, dict[str, Any]] = {
    "Your name?": {"value": "Alice"},
    "Restart now?": {"value": True},
    "How many replicas?": {"value": 3},
    "Which environment?": {"value": "dev"},
    "Which region?": {"value": "ap-southeast-1"},
    "Which availability zones?": {"value": ["ap-southeast-1a"]},
    "Sizing for the deployment?": {"replicas": 4, "cpu_limit": 2.5},
}


def make_handler():
    async def handler(message: str, response_type: Any, params: Any = None,
                      context: Any = None) -> Any:
        schema = getattr(params, "requested_schema", None)
        print(f"    [host] receives a generated class: {getattr(response_type, '__name__', response_type)!r}")
        print(f"    [host] schema: {json.dumps(schema)}")
        return ANSWERS[message]

    return handler


async def main() -> None:
    print("=== the schema behind each shape (server side, before any call) ===")
    for name, response_type in SHAPES.items():
        config = parse_elicit_response_type(response_type)
        print(f"  {name:16} is_raw={str(config.is_raw):5} {json.dumps(config.schema)}")

    print("\n=== the same shapes, answered by one host ===")
    async with Client(mcp, mode="legacy", elicitation_handler=make_handler()) as client:
        for tool in ("ask_str", "ask_bool", "ask_int", "ask_literal",
                     "ask_choice", "ask_titled", "ask_multi", "ask_model"):
            print(f"  {tool}:")
            print("    ->", (await client.call_tool(tool, {})).data)

    print("\n=== the same call, declined: no data, still a decision ===")
    async def no_thanks(message: str, response_type: Any, params: Any = None,
                        context: Any = None) -> Any:
        return ElicitResult(action="decline")

    async with Client(mcp, mode="legacy", elicitation_handler=no_thanks) as client:
        print("  ask_bool ->", (await client.call_tool("ask_bool", {})).data)


if __name__ == "__main__":
    asyncio.run(main())
