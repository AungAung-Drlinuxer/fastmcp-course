"""Lesson 2.2 (part 1) — tools that fail the way an agent can reason about.

An exception is invisible to a model: it sees a transport-level error and learns nothing. A
structured error is DATA — the agent can read `{"ok": false, "error": "division_by_zero"}` and
decide what to try instead. This file shows both, and the difference in what the model sees.

Run:
    uv run python -m M5_tools.code.calculator
"""
from __future__ import annotations

import asyncio
import json
from typing import Any

from fastmcp import Client, FastMCP

mcp = FastMCP("calculator")


def _ok(**payload: Any) -> dict:
    return {"ok": True, **payload}


def _fail(code: str, hint: str) -> dict:
    """Every failure carries a machine-readable code AND a human/agent-readable hint.

    The code lets a client branch; the hint is what the model actually reads. Omitting the
    hint produces an agent that retries the same wrong call.
    """
    return {"ok": False, "error": code, "hint": hint}


@mcp.tool
def divide(a: float, b: float) -> dict:
    """Divide a by b, reporting a zero denominator as data instead of raising.

    Args:
        a: The numerator.
        b: The denominator. Must not be zero.
    """
    if b == 0:
        return _fail("division_by_zero", "The denominator must be non-zero; try a different b.")
    return _ok(result=a / b)


@mcp.tool
def sqrt_of(x: float) -> dict:
    """Take the square root of a non-negative number.

    Args:
        x: The value to take the root of. Negative values are rejected as data.
    """
    if x < 0:
        return _fail("negative_input", "Square roots of negative numbers are not supported here.")
    return _ok(result=x ** 0.5)


@mcp.tool
def safe_divide(a: float, b: float) -> float:
    """Divide a by b, raising on a zero denominator — the WRONG pattern, for contrast.

    Args:
        a: The numerator.
        b: The denominator.
    """
    return a / b


async def main() -> None:
    async with Client(mcp) as client:
        print("=== structured failure: the model can read this ===")
        print(" ", (await client.call_tool("divide", {"a": 1, "b": 0})).data)
        print(" ", (await client.call_tool("sqrt_of", {"x": -4})).data)

        print("\n=== raised exception: the model sees a tool error with no plan ===")
        try:
            await client.call_tool("safe_divide", {"a": 1, "b": 0})
        except Exception as exc:
            print(f"  {type(exc).__name__}: {str(exc).splitlines()[0][:80]}")
            print("  What the agent received is an error string, not a reason it can act on.")

        print("\n=== the rule ===")
        print("  Raise for BAD REQUESTS (wrong types — Pydantic catches those for you).")
        print("  Return a structured error for BAD SITUATIONS the caller could have avoided,")
        print("  because those are the ones an agent can retry intelligently.")


if __name__ == "__main__":
    asyncio.run(main())
