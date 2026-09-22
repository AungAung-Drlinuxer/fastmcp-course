"""LAB 9 — `asyncio.gather` vs `asyncio.TaskGroup`: what happens when one task fails.

Both run tasks concurrently. They differ almost entirely in failure behaviour,
and that difference is what decides whether a tool returns a partial answer or
blows up the whole call.

`asyncio.TaskGroup` is 3.11+, which is this course's minimum. The lab prints the
interpreter's version so the claim is checked rather than trusted.

Run:
    uv run python -m M3_asyncio_decorators.code.lab_9_taskgroup_exceptions
"""
from __future__ import annotations

import asyncio
import sys
import time


async def work(name: str, delay: float, fail: bool = False) -> str:
    await asyncio.sleep(delay)
    if fail:
        raise ValueError(f"{name} failed after {delay}s")
    return f"{name}:ok"


async def main() -> None:
    print(f"=== python {sys.version.split()[0]} — TaskGroup needs 3.11+ ===")

    print("\n=== step 1: gather, all tasks succeed ===")
    results = await asyncio.gather(work("a", 0.05), work("b", 0.05), work("c", 0.05))
    print(f"  {results}")

    print("\n=== step 2: gather raises the FIRST exception, the rest keep running ===")
    started = time.perf_counter()
    try:
        await asyncio.gather(
            work("fast", 0.02),
            work("boom", 0.05, fail=True),
            work("slow", 0.40),
        )
    except ValueError as exc:
        print(f"  raised after {time.perf_counter() - started:.2f}s: {exc}")
    print("  -> gather returned at 0.05s while 'slow' still had 0.35s to run")
    print("  -> nothing cancels it: that task is now unobserved")
    await asyncio.sleep(0.4)  # let the orphan finish so the output is not interleaved

    print("\n=== step 3: TaskGroup cancels its siblings and raises ExceptionGroup ===")
    started = time.perf_counter()
    try:
        async with asyncio.TaskGroup() as group:
            group.create_task(work("fast", 0.02))
            group.create_task(work("boom", 0.05, fail=True))
            group.create_task(work("slow", 0.40))
    except* ValueError as group_exc:
        print(f"  raised after {time.perf_counter() - started:.2f}s: "
              f"{type(group_exc).__name__}")
        for exc in group_exc.exceptions:
            print(f"    {type(exc).__name__}: {exc}")
    print("  -> TaskGroup returned at 0.05s AND cancelled 'slow'; nothing is left running")

    print("\n=== step 4: a successful TaskGroup exposes its results ===")
    async with asyncio.TaskGroup() as group:
        t1 = group.create_task(work("one", 0.02))
        t2 = group.create_task(work("two", 0.03))
    print(f"  after the block: t1={t1.result()!r} t2={t2.result()!r}")
    print("  -> .result() is only safe once the block has exited successfully")

    print("\n=== step 5: gather with return_exceptions=True never raises ===")
    mixed = await asyncio.gather(
        work("good", 0.02),
        work("bad", 0.02, fail=True),
        return_exceptions=True,
    )
    for item in mixed:
        print(f"  {type(item).__name__:12} {item}")
    print("  -> this is what a tool that can partially succeed should use")

    print("\n=== step 6: turning gathered failures into a tool-shaped answer ===")

    async def safe(name: str, delay: float, fail: bool = False) -> dict:
        try:
            return {"ok": True, "name": name, "value": await work(name, delay, fail)}
        except Exception as exc:  # a boundary: convert to data, never swallow silently
            return {"ok": False, "name": name, "error": type(exc).__name__, "detail": str(exc)}

    report = await asyncio.gather(
        safe("alpha", 0.02),
        safe("beta", 0.02, fail=True),
        safe("gamma", 0.03),
    )
    ok = [row["name"] for row in report if row["ok"]]
    failed = [row["name"] for row in report if not row["ok"]]
    print(f"  ok     : {ok}")
    print(f"  failed : {failed}")
    print(f"  partial answer is possible: {bool(ok) and bool(failed)}")
    print("  -> `ok`/`error` data survives to the model; a raised exception does not")

    print("\n=== step 7: cancellation is a normal event, not a crash ===")
    victim = asyncio.create_task(work("victim", 5.0))
    await asyncio.sleep(0.02)
    victim.cancel()
    try:
        await victim
    except asyncio.CancelledError:
        print("  CancelledError caught at the await — this is the only place it is catchable")
    print(f"  cancelled(): {victim.cancelled()}")

    print("\n=== the decision table ===")
    print("  all must succeed, any failure is fatal  -> asyncio.TaskGroup")
    print("  partial success is acceptable           -> asyncio.gather(return_exceptions=True)")
    print("  need completion order                   -> asyncio.as_completed")
    print("  need a hard deadline for the group      -> asyncio.wait_for(asyncio.gather(...), t)")


if __name__ == "__main__":
    asyncio.run(main())
