"""LAB 5B — the same decorator, once sync and once async.

An async tool wrapped by a sync decorator produces no error, no warning at the
call site, and a timing of 0.000s. This lab exists to make that visible.

Run:
    uv run python -m M3_asyncio_decorators.code.lab_5b_async_decorator
"""
from __future__ import annotations

import asyncio
import functools
import inspect
import time


def timed_sync(fn):
    """WRONG for async tools: a sync wrapper around a coroutine function."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)              # no await — returns a coroutine
        print(f"  [sync]  {fn.__name__} took {time.perf_counter() - start:.3f}s")
        return result

    return wrapper


def timed_async(fn):
    """RIGHT: the wrapper is a coroutine function too, and it awaits."""

    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await fn(*args, **kwargs)
        print(f"  [async] {fn.__name__} took {time.perf_counter() - start:.3f}s")
        return result

    return wrapper


async def fetch(name: str) -> str:
    """Pretend to fetch something slow."""
    await asyncio.sleep(0.05)
    return f"{name}:ok"


async def main() -> None:
    print("=== iscoroutinefunction ===")
    print(f"  fetch                       {inspect.iscoroutinefunction(fetch)}")
    print(f"  timed_sync(fetch)           {inspect.iscoroutinefunction(timed_sync(fetch))}")
    print(f"  timed_async(fetch)          {inspect.iscoroutinefunction(timed_async(fetch))}")

    print("\n=== the wrong wrapper: it never awaited anything ===")
    broken = timed_sync(fetch)
    result = broken("python")
    print(f"  return type: {type(result).__name__}")
    print(f"  is a coroutine: {inspect.iscoroutine(result)}")
    print(f"  awaiting it later still works: {await result}")
    print("  -> the timing above measured nothing: the body had not run yet")

    print("\n=== the right wrapper ===")
    fixed = timed_async(fetch)
    print(f"  result: {await fixed('python')}")

    print("\n=== metadata in both cases ===")
    for label, fn in (("sync", timed_sync(fetch)), ("async", timed_async(fetch))):
        print(f"  {label:6} __name__={fn.__name__:6} "
              f"coroutine={inspect.iscoroutinefunction(fn)} "
              f"signature={inspect.signature(fn)}")
    print("  -> both keep the metadata; only iscoroutinefunction tells them apart")


if __name__ == "__main__":
    asyncio.run(main())
