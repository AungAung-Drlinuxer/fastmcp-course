"""M5_tools LAB 11 — clamping untrusted limits, and the two honest policies for out-of-range.

`limit` arrives from a model, which means it is untrusted input. There are exactly two
defensible answers when it is absurd, and they are not interchangeable:

    CLAMP   — do the closest reasonable thing and say what you did
    REFUSE  — return a structured error with the legal range in the hint

Pick per tool, not per project. A read-only listing should clamp. A call that spends money or
changes state should refuse.

Run:
    uv run python -m M5_tools.code.lab_11_clamp_untrusted_limits
"""
from __future__ import annotations

import asyncio
import json

from fastmcp import Client, FastMCP

mcp = FastMCP("lab11-clamp-limits")

ITEMS = [{"id": f"ITEM-{i:03d}", "name": f"catalogue entry {i}"} for i in range(1, 31)]
MIN_LIMIT, MAX_LIMIT = 1, 20


def clamp(value: int, low: int, high: int) -> tuple[int, bool]:
    """Return (clamped_value, was_changed) — the flag is what makes the clamp reportable."""
    fixed = max(low, min(high, value))
    return fixed, fixed != value


@mcp.tool
def list_items_clamped(limit: int = 10, offset: int = 0) -> dict:
    """List catalogue entries, quietly clamping an out-of-range limit.

    Args:
        limit: How many entries to return; outside 1-20 it is clamped.
        offset: Where to start in the catalogue.
    """
    requested_limit = limit
    limit, limit_changed = clamp(limit, MIN_LIMIT, MAX_LIMIT)
    requested_offset = offset
    offset, offset_changed = clamp(offset, 0, max(0, len(ITEMS) - 1))
    page = ITEMS[offset:offset + limit]
    return {
        "ok": True,
        "requested": {"limit": requested_limit, "offset": requested_offset},
        "clamped": limit_changed or offset_changed,
        "limit": limit, "offset": offset, "count": len(page), "total": len(ITEMS),
        "items": [item["id"] for item in page],
    }


@mcp.tool
def list_items_strict(limit: int = 10, offset: int = 0) -> dict:
    """List catalogue entries, refusing a limit outside 1-20 with an actionable error.

    Args:
        limit: How many entries to return, 1-20.
        offset: Where to start in the catalogue.
    """
    if not MIN_LIMIT <= limit <= MAX_LIMIT:
        return {"ok": False, "error": "limit_out_of_range",
                "hint": f"limit must be between {MIN_LIMIT} and {MAX_LIMIT}; "
                        f"got {limit}. Use {MAX_LIMIT} and page with offset.",
                "legal": {"min": MIN_LIMIT, "max": MAX_LIMIT}}
    if offset < 0 or offset >= len(ITEMS):
        return {"ok": False, "error": "offset_out_of_range",
                "hint": f"offset must be 0-{len(ITEMS) - 1}; got {offset}.",
                "legal": {"min": 0, "max": len(ITEMS) - 1}}
    page = ITEMS[offset:offset + limit]
    return {"ok": True, "limit": limit, "offset": offset, "count": len(page),
            "total": len(ITEMS), "items": [item["id"] for item in page]}


async def show(client: Client, tool: str, args: dict) -> None:
    result = await client.call_tool(tool, args, raise_on_error=False)
    body = result.structured_content or {}
    if body.get("ok"):
        print(f"    {tool}({args}) -> count={body['count']} "
              f"clamped={body.get('clamped', False)} first={body['items'][0]}")
    else:
        print(f"    {tool}({args}) -> {body['error']}: {body['hint']}")


async def main() -> None:
    async with Client(mcp) as client:
        print(f"catalogue size: {len(ITEMS)}   legal limit: {MIN_LIMIT}-{MAX_LIMIT}")

        print("\n=== policy 1: CLAMP (read-only listing) ===")
        for args in ({"limit": 5}, {"limit": 500}, {"limit": 0}, {"limit": -3},
                     {"limit": 10, "offset": 25}, {"limit": 10, "offset": 9999}):
            await show(client, "list_items_clamped", args)

        print("\n=== policy 2: REFUSE (a call whose range is part of its meaning) ===")
        for args in ({"limit": 5}, {"limit": 500}, {"limit": 0}, {"limit": 10, "offset": 9999}):
            await show(client, "list_items_strict", args)

        print("\n=== neither is an error at the MCP layer ===")
        result = await client.call_tool("list_items_strict", {"limit": 500},
                                        raise_on_error=False)
        print(f"    is_error={result.is_error}   the refusal is data the agent can plan around")

        print("\n=== what a naive tool does with the same input ===")
        naive = ITEMS[:500]
        print(f"    limit=500 -> returns {len(naive)} entries: 'it worked', but the caller")
        print("    asked for something impossible and was never told.")


if __name__ == "__main__":
    asyncio.run(main())
