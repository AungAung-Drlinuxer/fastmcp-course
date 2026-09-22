"""LAB 11B — extend the audit harness to catch what metadata cannot.

`functools.wraps` keeps `__name__`, `__doc__` and `__annotations__`, so
`audit_tool` says OK. But a sync wrapper around an async tool is still broken —
it returns a coroutine instead of a value. The only thing that catches that is
`inspect.iscoroutinefunction`.

Run:
    uv run python -m M3_asyncio_decorators.code.lab_11b_audit_async
"""
from __future__ import annotations

import asyncio
import functools
import inspect
from typing import Any

PLACEHOLDER_NAMES = {"wrapper", "decorator", "inner", "wrapped", "func", "<lambda>"}
MISSING = "<missing>"


def timed_sync(fn):
    """WRONG for async tools: a sync wrapper around a coroutine function."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper


def timed_async(fn):
    """RIGHT: the wrapper is a coroutine function too."""

    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        return await fn(*args, **kwargs)

    return wrapper


def audit_tool(fn) -> dict[str, Any]:
    """Report whether a function carries everything a tool needs — metadata AND async-ness."""
    name = getattr(fn, "__name__", MISSING)
    doc = inspect.getdoc(fn)
    annotations = getattr(fn, "__annotations__", {}) or {}
    body_params = [
        p for p in inspect.signature(fn).parameters.values()
        if p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
    ]
    problems: list[str] = []

    if name in PLACEHOLDER_NAMES:
        problems.append(f"name is a placeholder: {name!r}")
    if not doc:
        problems.append("no docstring: the tool has no description")
    if not annotations:
        problems.append("no annotations: every parameter will be schema-unknown")
    if not body_params:
        problems.append("signature is only *args/**kwargs: no schema can be generated")

    is_async = inspect.iscoroutinefunction(fn)
    wants_async = getattr(fn, "__tool_is_async__", None)
    if wants_async is True and not is_async:
        problems.append(
            "the tool body is async but the wrapper is not: an `async def wrapper` "
            "with `await fn(...)` is required"
        )

    return {
        "name": name,
        "documented": bool(doc),
        "annotation_count": len(annotations),
        "body_parameters": [p.name for p in body_params],
        "has_wrapped": hasattr(fn, "__wrapped__"),
        "is_coroutine_function": is_async,
        "wants_async": wants_async,
        "verdict": "OK" if not problems else "BROKEN",
        "problems": problems,
    }


def assert_async_tool(fn) -> None:
    """A tool that does I/O must be a coroutine function, whatever it is wrapped in."""
    if not inspect.iscoroutinefunction(fn):
        raise AssertionError(
            f"{fn.__name__} is not a coroutine function — tools that do I/O must be "
            f"`async def`, and any wrapper around them must be too"
        )


async def good_async_tool(vm_name: str) -> dict:
    """Provision a virtual machine.

    Args:
        vm_name: DNS-safe name, 1-63 chars, lowercase only.
    """
    await asyncio.sleep(0.01)
    return {"vm_name": vm_name}


def main() -> None:
    print("=== the same async tool, through three wrappers ===")
    candidates = {
        "bare": good_async_tool,
        "timed_sync": timed_sync(good_async_tool),
        "timed_async": timed_async(good_async_tool),
    }
    for label, fn in candidates.items():
        report = audit_tool(fn)
        print(f"  {label:12} {report['verdict']:7} async={report['is_coroutine_function']} "
              f"name={report['name']}")
    print("  -> metadata alone says OK for all three; only iscoroutinefunction separates them")

    print("\n=== the marker that makes the audit able to see it ===")

    @functools.wraps(good_async_tool)
    async def good_async_tool_wrapper(vm_name: str) -> dict:
        return await good_async_tool(vm_name)

    good_async_tool_wrapper.__tool_is_async__ = True

    plain_sync = timed_sync(good_async_tool)
    plain_sync.__tool_is_async__ = True          # declare the intent
    print(f"  intent declared, wrapper async : {audit_tool(good_async_tool_wrapper)['verdict']}")
    report = audit_tool(plain_sync)
    print(f"  intent declared, wrapper sync  : {report['verdict']}")
    for problem in report["problems"]:
        print(f"      - {problem}")

    print("\n=== assert_async_tool: the five-line CI gate ===")
    for label, fn in candidates.items():
        try:
            assert_async_tool(fn)
            print(f"  {label:12} passed")
        except AssertionError as exc:
            print(f"  {label:12} FAILED: {str(exc).splitlines()[0]}")

    print("\n=== behaviour: what a sync wrapper actually returns ===")
    broken_result = timed_sync(good_async_tool)("web-01")
    print(f"  timed_sync(...) -> {type(broken_result).__name__} "
          f"iscoroutine={inspect.iscoroutine(broken_result)}")

    async def drive() -> None:
        print(f"  timed_async(...) -> {await timed_async(good_async_tool)('web-01')}")
        print(f"  awaiting the sync wrapper's output works: {await broken_result}")

    asyncio.run(drive())
    print("  -> the broken wrapper LOOKS fine at the call site; the damage shows up later")


if __name__ == "__main__":
    main()
