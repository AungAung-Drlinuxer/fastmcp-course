"""LAB 6 — the event loop, seen from the outside.

`async def` does not run anything. It builds a coroutine object, which is inert
until something drives it. This lab exists to make that visible: it prints the
object, shows the "coroutine was never awaited" warning on purpose, and then
shows two tasks interleaving at their `await` points.

Run:
    uv run python -m M3_asyncio_decorators.code.lab_6_event_loop
"""
from __future__ import annotations

import asyncio
import gc
import inspect
import time
import warnings
from collections.abc import Coroutine
from typing import Any


async def greet(name: str) -> str:
    """Sleep briefly, then return a greeting. The sleep is the yield point."""
    print(f"    [greet] start {name}")
    await asyncio.sleep(0.05)
    print(f"    [greet] end   {name}")
    return f"hello {name}"


async def marker(label: str, delay: float) -> str:
    """Print before and after an await so interleaving is visible in the output."""
    print(f"    [ {label} ] before await")
    await asyncio.sleep(delay)
    print(f"    [ {label} ] after  await")
    return label


async def ticker(seconds: float) -> int:
    """Count how many times the loop got back to us in `seconds`."""
    ticks = 0
    end = time.perf_counter() + seconds
    while time.perf_counter() < end:
        await asyncio.sleep(0.01)
        ticks += 1
    return ticks


def main() -> None:
    print("=== step 1: calling a coroutine function runs NOTHING ===")
    started = time.perf_counter()
    coro_obj: Coroutine[Any, Any, str] = greet("world")
    elapsed = time.perf_counter() - started
    print(f"  greet('world') returned {coro_obj!r}")
    print(f"  time taken                {elapsed * 1000:.3f} ms")
    print(f"  is a coroutine            {inspect.iscoroutine(coro_obj)}")
    print("  -> no 'start' line was printed: the body has not executed")

    print("\n=== step 2: dropping a coroutine without awaiting it ===")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        abandoned = greet("nobody")
        del abandoned
        gc.collect()  # the garbage collector is what notices, so collect explicitly
        for item in caught:
            print(f"  {item.category.__name__}: {str(item.message).splitlines()[0]}")
        if not caught:
            print("  (no warning on this interpreter)")
    tidy = greet("nobody")
    tidy.close()
    print(f"  after close(): cr_frame={tidy.cr_frame!r} — the coroutine is shut down")
    print("  -> forgetting `await` gives you this warning, not an error; the call never ran")

    print("\n=== step 3: asyncio.run drives one coroutine to completion ===")
    result = asyncio.run(greet("solo"))
    print(f"  asyncio.run(...) -> {result!r}")

    print("\n=== step 4: two tasks interleave at their await points ===")
    print("  sequential awaits:")

    async def sequential_pair() -> None:
        print(f"    {await marker('A', 0.10)}")
        print(f"    {await marker('B', 0.10)}")

    asyncio.run(sequential_pair())

    print("  gathered tasks:")

    async def gathered_pair() -> None:
        results = await asyncio.gather(marker("A", 0.10), marker("B", 0.10))
        print(f"    results {results}")

    asyncio.run(gathered_pair())
    print("  -> gather schedules both, so both 'before await' lines print first")

    print("\n=== step 5: the loop keeps returning control ===")
    ticks = asyncio.run(ticker(0.20))
    print(f"  ticks in 0.20s of awaiting (10 ms sleep each): {ticks}")
    print("  -> the loop is not blocked while a task sleeps; it runs other tasks")

    print("\n=== step 6: await works on three different kinds of thing ===")

    async def awaiting_three() -> None:
        await asyncio.sleep(0.01)                 # a coroutine
        task = asyncio.create_task(greet("task"))  # a Task, scheduled now
        await task                                 # await the Task's result
        await asyncio.gather(greet("g1"), greet("g2"))

    asyncio.run(awaiting_three())

    print("\n=== step 7: a coroutine object can only be awaited ONCE ===")
    once = greet("once")

    async def await_twice() -> None:
        await once
        try:
            await once
        except RuntimeError as exc:
            print(f"  RuntimeError: {exc}")

    asyncio.run(await_twice())

    print("\n=== rules ===")
    print("  1. `async def` returns a coroutine object; only `await`/`run` executes it.")
    print("  2. `await` is the yield point. Code with no await never shares the loop.")
    print("  3. One `asyncio.run()` per program, at the top of `main`.")
    print("  4. A Task is a coroutine the loop is already driving; keep the reference.")


if __name__ == "__main__":
    main()
