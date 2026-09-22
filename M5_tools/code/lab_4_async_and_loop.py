"""M5_tools LAB 4 — async tools, the running loop, and why concurrency is not decoration.

Two measurements: an async tool that awaits I/O three times takes about as long as one call
when the caller gathers them, and the same three calls issued in sequence take three times as
long. Then the mistake that every student makes once: calling asyncio.run() from inside a
coroutine.

Run:
    uv run python -m M5_tools.code.lab_4_async_and_loop
"""
from __future__ import annotations

import asyncio
import time

from fastmcp import Client, FastMCP

mcp = FastMCP("lab4-async-and-loop")

CALLS = 3
WAIT = 0.30  # seconds each I/O hop pretends to take


@mcp.tool
async def fetch_reading(probe: str) -> dict:
    """Read one probe value, simulating a network round trip.

    Args:
        probe: Name of the probe to read.
    """
    await asyncio.sleep(WAIT)  # stands in for await httpx_client.get(...)
    return {"ok": True, "probe": probe, "value_c": 20.0, "asyncio": True}


@mcp.tool
def fetch_reading_sync(probe: str) -> dict:
    """The same tool written as a blocking function — the pattern that stalls the server.

    Args:
        probe: Name of the probe to read.
    """
    time.sleep(WAIT)  # blocks the event loop for every other client too
    return {"ok": True, "probe": probe, "value_c": 20.0, "asyncio": False}


async def sequential(client: Client) -> float:
    start = time.perf_counter()
    for i in range(CALLS):
        await client.call_tool("fetch_reading", {"probe": f"p{i}"})
    return time.perf_counter() - start


async def concurrent(client: Client) -> float:
    start = time.perf_counter()
    await asyncio.gather(*(client.call_tool("fetch_reading", {"probe": f"p{i}"})
                           for i in range(CALLS)))
    return time.perf_counter() - start


async def local_registry() -> None:
    """A plain coroutine, to show why you cannot re-enter the event loop."""
    print("    (this line must never print)")


async def main() -> None:
    async with Client(mcp) as client:
        print("=== registry, read without a client at all ===")
        print("    tools:", [t.name for t in await mcp.list_tools()])

        seq = await sequential(client)
        con = await concurrent(client)
        print(f"\n=== {CALLS} I/O calls of {WAIT}s each ===")
        print(f"    sequential  {seq:.2f}s")
        print(f"    concurrent  {con:.2f}s   (asyncio.gather)")
        print(f"    verdict     concurrent is faster: {con < seq}")

        print("\n=== the mistake: asyncio.run() inside a running loop ===")
        coro = local_registry()
        try:
            asyncio.run(coro)
        except RuntimeError as exc:
            print(f"    RuntimeError: {exc}")
        finally:
            coro.close()  # a coroutine that is never awaited would warn; close it explicitly
        print("    That is why M5_tools/code/wikipedia.py has `async def _registry()`")
        print("    and calls `await mcp.list_tools()` instead of asyncio.run(...).")

        print("\n=== a sync tool still works — it just blocks ===")
        result = await client.call_tool("fetch_reading_sync", {"probe": "p0"})
        print("   ", result.data)


if __name__ == "__main__":
    asyncio.run(main())
