"""LAB 7 — a dispatcher: from a schema to a tool call, with unknown names rejected first.

This is the client half of what a model actually does. A model does not "run" a tool; it emits a
structured request — a name and an arguments object — and SOMETHING ELSE executes it. In this
lesson that something else is 30 lines you can read.

The dispatcher below is fed a transcript of emissions, including the hostile ones: a tool that
does not exist, a wrong argument name, a wrong type, a missing required argument, and a turn with
two calls in it. Nothing raises out of the loop; every outcome becomes data with a reason, which
is what a model (or a log) needs in order to recover.

Run:
    uv run python -m M9_clients.code.lab_7_dispatch_table
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from fastmcp import Client

ROOT = Path(__file__).parents[2]
HELLO = ROOT / "M4_fastmcp_basics" / "code" / "hello_server.py"

# What a model emits, in the shape LangChain hands back: names it may only see through the schema.
EMISSIONS: list[dict[str, Any]] = [
    {"turn": 1, "tool": "add", "arguments": {"a": 2, "b": 3}},
    {"turn": 2, "tool": "add", "arguments": {"a": 10, "b": 5}},
    {"turn": 3, "tool": "delete_everything", "arguments": {}},
    {"turn": 4, "tool": "add", "arguments": {"a": "two", "b": 3}},
    {"turn": 5, "tool": "add", "arguments": {"a": 1}},
    {"turn": 6, "tool": "add", "arguments": {"first": 1, "second": 2}},
    {"turn": 7, "tool": "add", "arguments": {"a": 1, "b": 2, "c": 3}},
    {"turn": 8, "tool": "ping", "arguments": {}},
]


async def dispatch(client: Client, known: set[str], emission: dict[str, Any]) -> dict[str, Any]:
    """One emission -> one outcome. Never raises: the outcome carries the reason."""
    name = emission["tool"]
    if name not in known:
        # Reject BEFORE the wire. The server would answer, but the round trip is wasted and the
        # error the model reads is less specific than this one.
        return {"ok": False, "reason": "unknown_tool", "hint": sorted(known)}
    try:
        result = await client.call_tool(name, emission["arguments"])
        return {"ok": True, "data": result.data, "is_error": result.is_error}
    except Exception as exc:
        # A validation failure, a missing argument, an unreachable server: all the same to us.
        return {"ok": False, "reason": type(exc).__name__,
                "detail": str(exc).splitlines()[0][:64]}


async def main() -> None:
    async with Client(HELLO) as client:
        tools = await client.list_tools()
        known = {t.name for t in tools}
        print("=== the dispatcher's whole world ===")
        print(f"  known names: {sorted(known)}")
        for tool in tools:
            print(f"  {tool.name:6} {json.dumps(tool.input_schema['properties'])}")

        print("\n=== executing the emissions ===")
        outcomes: list[dict[str, Any]] = []
        for emission in EMISSIONS:
            outcome = await dispatch(client, known, emission)
            outcomes.append(outcome)
            label = f"turn {emission['turn']:>2} {emission['tool']}({emission['arguments']})"
            if outcome["ok"]:
                print(f"  {label:52} -> OK {outcome['data']!r}")
            else:
                print(f"  {label:52} -> {outcome['reason']:16} {outcome.get('detail', outcome.get('hint'))}")

        print("\n=== the same outcomes as the model would receive them ===")
        for emission, outcome in zip(EMISSIONS, outcomes):
            as_text = (f"result: {outcome['data']!r}" if outcome["ok"]
                       else f"error: {outcome['reason']} — fix the arguments. "
                            f"valid names: {outcome.get('hint', 'see schema')}")
            print(f"  turn {emission['turn']:>2} -> {as_text}")

        ok = sum(1 for o in outcomes if o["ok"])
        print(f"\n=== summary (counted in code, not by eye) ===")
        print(f"  emissions {len(EMISSIONS)}   succeeded {ok}   refused/failed {len(EMISSIONS) - ok}")
        reasons: dict[str, int] = {}
        for outcome in outcomes:
            if not outcome["ok"]:
                reasons[outcome["reason"]] = reasons.get(outcome["reason"], 0) + 1
        for reason, count in sorted(reasons.items()):
            print(f"    {reason:16} x{count}")

        print("\n=== a turn with two calls in it ===")
        turn = [{"name": "add", "args": {"a": 1, "b": 1}, "id": "call_1"},
                {"name": "ping", "args": {}, "id": "call_2"}]
        for call in turn:
            outcome = await dispatch(client, known, {"tool": call["name"], "arguments": call["args"]})
            print(f"  {call['id']:8} {call['name']:6} -> {outcome.get('data', outcome.get('reason'))!r}")
        print("  One model turn can request SEVERAL tools. A client that assumes one call per")
        print("  turn silently drops work — and looks correct in every small test.")


if __name__ == "__main__":
    asyncio.run(main())
