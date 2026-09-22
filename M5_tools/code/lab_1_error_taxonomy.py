"""M5_tools LAB 1 — the error taxonomy: what the model actually receives.

Three versions of the same arithmetic tool, called the same way, with a bad denominator.
The point is not which one "works" — it is what arrives on the other side of the wire.

Run:
    uv run python -m M5_tools.code.lab_1_error_taxonomy
"""
from __future__ import annotations

import asyncio
import json
from typing import Any

from fastmcp import Client, FastMCP

mcp = FastMCP("lab1-error-taxonomy")


@mcp.tool
def divide_raises(a: float, b: float) -> float:
    """Divide a by b and let Python raise when b is zero.

    Args:
        a: The numerator.
        b: The denominator.
    """
    return a / b


@mcp.tool
def divide_returns_full(a: float, b: float) -> dict:
    """Divide a by b, returning a structured failure when b is zero.

    Args:
        a: The numerator.
        b: The denominator.
    """
    if b == 0:
        return {"ok": False, "error": "division_by_zero",
                "hint": "b must be non-zero. Call with b=1 to test, or read the operand first."}
    return {"ok": True, "result": a / b}


@mcp.tool
def divide_returns_bare(a: float, b: float) -> dict:
    """Divide a by b, returning a structured failure WITHOUT a hint.

    Args:
        a: The numerator.
        b: The denominator.
    """
    if b == 0:
        return {"ok": False, "error": "division_by_zero"}
    return {"ok": True, "result": a / b}


async def observe(client: Client, name: str, args: dict[str, Any]) -> dict[str, Any]:
    """Call a tool and report the four things that matter, never raising."""
    result = await client.call_tool(name, args, raise_on_error=False)
    text = result.content[0].text if result.content else None
    return {
        "tool": name,
        "is_error": result.is_error,
        "has_structured_content": result.structured_content is not None,
        "structured_content": result.structured_content,
        "text_content": text,
    }


async def main() -> None:
    async with Client(mcp) as client:
        rows = []
        for name in ("divide_raises", "divide_returns_full", "divide_returns_bare"):
            rows.append(await observe(client, name, {"a": 1.0, "b": 0.0}))

        print("=== what the client receives for b=0 ===")
        for row in rows:
            print(f"\n--- {row['tool']}")
            print(f"    is_error            {row['is_error']}")
            print(f"    structured_content  {json.dumps(row['structured_content'])}")
            print(f"    text_content        {row['text_content']}")

        print("\n=== the three questions an agent asks ===")
        for row in rows:
            structured = row["structured_content"] or {}
            print(f"    {row['tool']:22} "
                  f"knows_what_broke={('error' in structured)!s:5} "
                  f"knows_what_to_do={('hint' in structured)!s:5} "
                  f"can_branch_on_it={(not row['is_error'])!s:5}")

        print("\n=== the same tool with a GOOD argument ===")
        good = await observe(client, "divide_returns_full", {"a": 9.0, "b": 3.0})
        print(f"    is_error            {good['is_error']}")
        print(f"    structured_content  {json.dumps(good['structured_content'])}")


if __name__ == "__main__":
    asyncio.run(main())
