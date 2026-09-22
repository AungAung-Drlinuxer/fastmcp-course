"""LAB 8 — `to_thread` and `wait_for`: the two lines that keep a server alive.

Every MCP tool that talks to the outside world needs a timeout. Without one, a
slow upstream becomes an agent that hangs — which looks to the user like a broken
server, not like a broken API. And every blocking library the course cannot
avoid needs `asyncio.to_thread`, or it takes the loop down with it.

Run:
    uv run python -m M3_asyncio_decorators.code.lab_8_to_thread_timeout
"""
from __future__ import annotations

import asyncio
import time

LATENCY = 0.25


def blocking_csv_parse(rows: int) -> int:
    """Stand-in for a pure-CPU or blocking-library call that cannot be made async."""
    time.sleep(LATENCY)
    return rows * 2


async def slow_call(seconds: float, label: str) -> str:
    await asyncio.sleep(seconds)
    return f"{label}:ok"


async def call_with_timeout(seconds: float, label: str, timeout: float) -> str:
    """The pattern every outbound call in this course uses."""
    try:
        return await asyncio.wait_for(slow_call(seconds, label), timeout=timeout)
    except asyncio.TimeoutError:
        raise RuntimeError(f"{label} timed out after {timeout}s") from None


async def retry(coro_factory, attempts: int = 3, base_delay: float = 0.05):
    """Retry an async call with exponential backoff, and give up loudly."""
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return await coro_factory(attempt)
        except (asyncio.TimeoutError, RuntimeError) as exc:
            last = exc
            delay = base_delay * (2 ** (attempt - 1))
            print(f"    attempt {attempt} failed ({exc}); sleeping {delay:.2f}s")
            await asyncio.sleep(delay)
    raise RuntimeError(f"all {attempts} attempts failed") from last


async def main() -> None:
    print("=== step 1: a blocking library moved off the loop ===")
    start = time.perf_counter()
    serial = [blocking_csv_parse(1), blocking_csv_parse(1), blocking_csv_parse(1)]
    serial_s = time.perf_counter() - start
    start = time.perf_counter()
    threaded = await asyncio.gather(
        *(asyncio.to_thread(blocking_csv_parse, 1) for _ in range(3))
    )
    threaded_s = time.perf_counter() - start
    print(f"  three blocking calls, called in order : {serial_s:.2f}s")
    print(f"  the same calls via asyncio.to_thread : {threaded_s:.2f}s")
    print(f"  results {serial} -> {threaded}")
    print("  -> to_thread does not make the work faster; it stops it blocking the loop")

    print("\n=== step 2: a timeout on an outbound call ===")
    try:
        print(f"  fast call  -> {await call_with_timeout(0.05, 'fast', timeout=1.0)}")
    except RuntimeError as exc:
        print(f"  unexpected: {exc}")
    try:
        await call_with_timeout(5.0, 'slow', timeout=0.10)
    except RuntimeError as exc:
        print(f"  slow call  -> RuntimeError: {exc}")
    print("  -> catching TimeoutError and re-raising a clear message is what a tool needs")

    print("\n=== step 3: what the RAW TimeoutError looks like if you do not catch it ===")
    try:
        await asyncio.wait_for(slow_call(5.0, "raw"), timeout=0.05)
    except asyncio.TimeoutError as exc:
        print(f"  {type(exc).__name__}: {exc!r}")
        print("  -> note: asyncio.TimeoutError IS builtins.TimeoutError on 3.11+")
        print(f"  TimeoutError is asyncio.TimeoutError: "
              f"{asyncio.TimeoutError is TimeoutError}")

    print("\n=== step 4: a timeout does not leak the task ===")
    leaked = asyncio.create_task(slow_call(30.0, "leaked"))
    try:
        await asyncio.wait_for(leaked, timeout=0.05)
    except asyncio.TimeoutError:
        pass
    await asyncio.sleep(0)
    print(f"  task cancelled? {leaked.cancelled() or leaked.done()}")
    print("  -> wait_for cancels the task it was wrapping, so nothing keeps running")

    print("\n=== step 5: retry with backoff ===")
    state = {"n": 0}

    async def flaky(attempt: int) -> str:
        state["n"] += 1
        if state["n"] < 3:
            raise RuntimeError("upstream 503")
        return f"success on try {attempt}"

    print(f"  result -> {await retry(flaky, attempts=4)}")

    async def always_down(attempt: int) -> str:
        raise RuntimeError("upstream 503")

    try:
        await retry(always_down, attempts=2)
    except RuntimeError as exc:
        print(f"  gave up -> {exc}")

    print("\n=== step 6: the four-line guard every outbound call gets ===")
    print("  try:")
    print("      data = await asyncio.wait_for(fetch(url), timeout=10)")
    print("  except asyncio.TimeoutError:")
    print("      return {'ok': False, 'error': 'timeout', 'url': url}   # data, not a crash")


if __name__ == "__main__":
    asyncio.run(main())
