"""LAB 5 — measure the mode requirement yourself.

The claim "elicitation needs mode='legacy'" is not folklore; it is a measured
fact about which protocol era carries a back-channel. This lab walks every
accepted mode value and prints what actually happened.

Run:
    uv run python -m M8_elicitation.code.lab_5_mode_matrix
"""
from __future__ import annotations

import asyncio
from typing import Any

from fastmcp import Client, Context, FastMCP

mcp = FastMCP("mode-matrix")


@mcp.tool
async def ping_user(ctx: Context) -> dict:
    """The smallest tool that needs a back-channel."""
    result = await ctx.elicit("Reply with anything.", str)
    action = getattr(result, "action", "accept")
    if action != "accept":
        return {"ok": False, "status": action}
    return {"ok": True, "status": "accepted", "data": result.data}


async def handler(message: str, response_type: Any, params: Any = None,
                  context: Any = None) -> Any:
    return {"value": "hello"}


async def probe(mode: str | None) -> dict[str, Any]:
    """Try one mode end to end and report it as a table row."""
    row: dict[str, Any] = {"mode": mode or "(default / auto)"}
    try:
        kwargs = {} if mode is None else {"mode": mode}
        async with Client(mcp, elicitation_handler=handler, **kwargs) as client:
            row["protocol_version"] = client.protocol_version
            try:
                await client.call_tool("ping_user", {})
                row["result"] = "OK — elicitation worked"
            except Exception as exc:  # noqa: BLE001
                row["result"] = f"{type(exc).__name__}: {exc}"
    except Exception as exc:  # noqa: BLE001
        row["protocol_version"] = "-"
        row["result"] = f"{type(exc).__name__}: {exc}"
    return row


async def main() -> None:
    rows = []
    for mode in (None, "legacy", "auto", "2026-07-28", "2025-11-25", "2025-06-18"):
        rows.append(await probe(mode))

    print(f"{'mode':22} {'protocol_version':18} result")
    print("-" * 100)
    for row in rows:
        print(f"{row['mode']:22} {str(row['protocol_version']):18} {row['result']}")

    worked = [r["mode"] for r in rows if r["result"].startswith("OK")]
    print("\nmodes where elicitation worked:", worked)
    print("accepted values are only 'legacy', 'auto' and '2026-07-28'")


if __name__ == "__main__":
    asyncio.run(main())
