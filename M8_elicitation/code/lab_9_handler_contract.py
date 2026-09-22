"""LAB 9 — the handler contract: break it on purpose, then fix it.

The three measured failures in the callback all look reasonable in source:
a sync `def`, a three-argument handler, and a handler that raises instead of
returning an outcome. This lab runs the broken versions first so that the error
messages are yours, not somebody else's story.

Run:
    uv run python -m M8_elicitation.code.lab_9_handler_contract
"""
from __future__ import annotations

import asyncio
from typing import Any

from fastmcp import Client, Context, FastMCP
from fastmcp.client.elicitation import ElicitResult

mcp = FastMCP("handler-contract")


@mcp.tool
async def restart_service(service: str, ctx: Context) -> dict:
    """Ask before restarting, so the handler contract is exercised.

    Args:
        service: Which service to restart.
    """
    result = await ctx.elicit(f"Restart {service} now?", bool)
    action = getattr(result, "action", "accept")
    if action != "accept":
        return {"ok": False, "status": action}
    return {"ok": True, "status": "restarted", "service": service,
            "confirmed": result.data}


async def good_handler(message: str, response_type: Any, params: Any = None,
                       context: Any = None) -> Any:
    """Four parameters, async, and the outcome expressed by the RETURN VALUE."""
    return {"value": True}


def sync_handler(message: str, response_type: Any, params: Any = None,
                 context: Any = None) -> Any:
    """WRONG: a plain def. The callback awaits it unconditionally."""
    return {"value": True}


def three_arg_handler(message: str, response_type: Any, params: Any) -> Any:
    """WRONG: three parameters. The callback always passes four."""
    return {"value": True}


async def raising_handler(message: str, response_type: Any, params: Any = None,
                          context: Any = None) -> Any:
    """WRONG: raising turns a decision into a tool failure."""
    raise RuntimeError("the user closed the window")


async def none_handler(message: str, response_type: Any, params: Any = None,
                       context: Any = None) -> Any:
    """WRONG: None is not a decision either."""
    return None


async def run(label: str, handler: Any, tool: str = "restart_service") -> None:
    print(f"=== {label} ===")
    try:
        async with Client(mcp, mode="legacy", elicitation_handler=handler) as client:
            print("  ->", (await client.call_tool(tool, {"service": "nginx"})).data)
    except Exception as exc:  # noqa: BLE001
        print(f"  !! {type(exc).__name__}: {exc}")
    print()


async def main() -> None:
    await run("correct: async, four parameters, returns data", good_handler)
    await run("sync def", sync_handler)
    await run("three parameters", three_arg_handler)
    await run("raises instead of returning an outcome", raising_handler)
    await run("returns None", none_handler)

    print("=== no elicitation_handler at all ===")
    try:
        async with Client(mcp, mode="legacy") as client:
            print("  ->", (await client.call_tool("restart_service", {"service": "nginx"})).data)
    except Exception as exc:  # noqa: BLE001
        print(f"  !! {type(exc).__name__}: {exc}")

    print("\n=== the correct decline, for contrast ===")
    async def declining(message: str, response_type: Any, params: Any = None,
                        context: Any = None) -> Any:
        return ElicitResult(action="decline")

    async with Client(mcp, mode="legacy", elicitation_handler=declining) as client:
        print("  ->", (await client.call_tool("restart_service", {"service": "nginx"})).data)


if __name__ == "__main__":
    asyncio.run(main())
