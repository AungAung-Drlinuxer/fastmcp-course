"""LAB 7 — sequential vs gather, measured, plus the damage a blocking call does.

The numbers printed here are measured at runtime on the machine that runs the
lab. Four "requests" with a fixed latency each; three ways to run them; and a
heartbeat task that shows whether the event loop was free while they ran.

Run:
    uv run python -m M3_asyncio_decorators.code.lab_7_sequential_vs_gather
"""
from __future__ import annotations

import asyncio
import time

LATENCY = 0.25  # seconds; one stand-in request
NAMES = ["python", "mcp", "fastmcp", "pydantic"]


async def fetch(name: str) -> str:
    """A well-behaved async request: sleeps without holding the loop."""
    await asyncio.sleep(LATENCY)
    return f"{name}:ok"


def fetch_blocking(name: str) -> str:
    """A badly-behaved request: time.sleep freezes the whole loop."""
    time.sleep(LATENCY)
    return f"{name}:ok"


async def heartbeat(stop: asyncio.Event, ticks: list[int]) -> None:
    """Count how many times the loop came back to us while other work ran."""
    while not stop.is_set():
        ticks[0] += 1
        await asyncio.sleep(0.02)


async def sequential(names: list[str]) -> tuple[list[str], float]:
    start = time.perf_counter()
    out = [await fetch(n) for n in names]
    return out, time.perf_counter() - start


async def gathered(names: list[str]) -> tuple[list[str], float]:
    start = time.perf_counter()
    out = await asyncio.gather(*(fetch(n) for n in names))
    return list(out), time.perf_counter() - start


async def blocking_in_loop(names: list[str]) -> float:
    """time.sleep called directly inside a coroutine — the loop is dead for 1s."""
    start = time.perf_counter()
    for n in names:
        fetch_blocking(n)
    return time.perf_counter() - start


async def blocking_in_threads(names: list[str]) -> float:
    """The same blocking function, moved off the loop with asyncio.to_thread."""
    start = time.perf_counter()
    await asyncio.gather(*(asyncio.to_thread(fetch_blocking, n) for n in names))
    return time.perf_counter() - start


async def measure_with_heartbeat(coro_factory, label: str) -> float:
    stop = asyncio.Event()
    ticks = [0]
    hb = asyncio.create_task(heartbeat(stop, ticks))
    start = time.perf_counter()
    await coro_factory()
    elapsed = time.perf_counter() - start
    stop.set()
    await hb
    await asyncio.sleep(0)  # let the heartbeat task finish
    print(f"  {label:22} {elapsed:6.2f}s   heartbeat ticks during it: {ticks[0]}")
    return elapsed


async def main() -> None:
    print("=== step 1: same four requests, two orders ===")
    seq, seq_s = await sequential(NAMES)
    con, con_s = await gathered(NAMES)
    print(f"  sequential   {seq_s:6.2f}s   {seq[:2]} ...")
    print(f"  concurrent   {con_s:6.2f}s   {con[:2]} ...")
    print(f"  speed-up     {seq_s / con_s:6.1f}x")
    print(f"  theoretical ceiling with 4 equal tasks: {len(NAMES)}.0x")

    print("\n=== step 2: the loop is free during await, dead during time.sleep ===")
    await measure_with_heartbeat(lambda: gathered(NAMES), "async fetch (gather)")
    await measure_with_heartbeat(lambda: blocking_in_loop(NAMES), "time.sleep in loop")
    await measure_with_heartbeat(lambda: blocking_in_threads(NAMES), "to_thread(blocking)")

    print("\n=== step 3: the numbers a user actually feels ===")
    print(f"  gather saved {seq_s - con_s:.2f}s on four calls")
    print(f"  extrapolated to 20 calls: {20 * LATENCY:.2f}s -> {LATENCY:.2f}s")

    print("\n=== step 4: gather preserves order, not completion order ===")

    async def uneven(name: str, delay: float) -> str:
        await asyncio.sleep(delay)
        return name

    results = await asyncio.gather(
        uneven("slowest", 0.20),
        uneven("fastest", 0.02),
        uneven("middle", 0.10),
    )
    print(f"  gather results in argument order: {results}")
    print("  -> document order is stable; use as_completed when you want finish order")

    print("\n=== step 5: a single failure with return_exceptions=False ===")

    async def boom(name: str) -> str:
        if name == "bad":
            raise ValueError(f"{name} is not a valid topic")
        return f"{name}:ok"

    try:
        await asyncio.gather(boom("good"), boom("bad"), boom("also-good"))
    except ValueError as exc:
        print(f"  ValueError escaped gather: {exc}")
        print("  -> the other two tasks keep running in the background, unobserved")

    print("\n=== step 6: return_exceptions=True turns failures into values ===")
    mixed = await asyncio.gather(
        boom("good"), boom("bad"), boom("also-good"), return_exceptions=True
    )
    for item in mixed:
        print(f"  {type(item).__name__:16} {item}")

    print("\n=== the rules ===")
    print("  1. Independent I/O in a loop -> `await asyncio.gather(...)`.")
    print("  2. `time.sleep` inside a coroutine -> the whole server stalls. Use `asyncio.sleep`.")
    print("  3. A blocking library you cannot replace -> `await asyncio.to_thread(...)`.")
    print("  4. `asyncio.gather` gives you the first exception; the rest still run.")


if __name__ == "__main__":
    asyncio.run(main())
