"""Lesson 1.3 (part 2) — why MCP servers are async, demonstrated with real timings.

An MCP server calls out to APIs, databases and the filesystem. Measured on this machine, the
same three "requests" take about 3x longer sequentially than concurrently — and that gap is
what a student feels as a slow agent. The numbers below are measured at runtime, not quoted.

Run:
    uv run python -m M3_asyncio_decorators.code.async_io
"""
from __future__ import annotations

import asyncio
import time

LATENCY = 0.25  # seconds; stands in for one Wikipedia request


async def fetch(name: str) -> str:
    """Pretend to fetch something slow without blocking the event loop."""
    await asyncio.sleep(LATENCY)          # await yields control; time.sleep() would not
    return f"{name}:ok"


def fetch_blocking(name: str) -> str:
    """The wrong way inside an async server: this freezes every other task."""
    time.sleep(LATENCY)
    return f"{name}:ok"


async def sequential(names: list[str]) -> tuple[list[str], float]:
    start = time.perf_counter()
    out = [await fetch(n) for n in names]
    return out, time.perf_counter() - start


async def concurrent(names: list[str]) -> tuple[list[str], float]:
    start = time.perf_counter()
    out = await asyncio.gather(*(fetch(n) for n in names))
    return list(out), time.perf_counter() - start


async def blocked(names: list[str]) -> float:
    """Shows the damage: a blocking call inside a coroutine will not interleave."""
    start = time.perf_counter()
    await asyncio.gather(*(asyncio.to_thread(fetch_blocking, n) for n in names))
    return time.perf_counter() - start


async def main() -> None:
    names = ["python", "mcp", "fastmcp", "pydantic"]

    seq, seq_s = await sequential(names)
    con, con_s = await concurrent(names)
    blk_s = await blocked(names)

    print("=== same work, three ways (measured) ===")
    print(f"  sequential   {seq_s:6.2f}s   {seq[:2]}")
    print(f"  concurrent   {con_s:6.2f}s   {con[:2]}")
    print(f"  blocking*    {blk_s:6.2f}s   (* run in a thread so the demo finishes)")
    print()
    print(f"  speed-up from gather: {seq_s / con_s:.1f}x")

    print("\n=== the timeout, which every real tool needs ===")
    try:
        await asyncio.wait_for(fetch("slow"), timeout=0.05)
    except asyncio.TimeoutError:
        print("  asyncio.TimeoutError raised and caught — this becomes a clean tool error")
        print("  in M5, instead of an agent that hangs until the client gives up.")

    print("\n=== rules for MCP tools ===")
    print("  1. `async def` for anything that does I/O.")
    print("  2. `await asyncio.sleep()`, never `time.sleep()` inside a coroutine.")
    print("  3. A blocking library the course cannot avoid -> `await asyncio.to_thread(...)`.")
    print("  4. Put a `wait_for` timeout on every outbound call.")


if __name__ == "__main__":
    asyncio.run(main())
