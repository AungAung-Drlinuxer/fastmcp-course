"""LAB 2 — closures: the mechanism that makes a decorator able to "remember".

A wrapper is an inner function. It is returned *after* the outer function has
already finished running. For the wrapper to still be able to talk about `fn`,
Python has to keep `fn` alive in a cell. That is a closure, and it is the reason
a decorator can hold configuration without a class.

Run:
    uv run python -m M3_asyncio_decorators.code.lab_2_closures
"""
from __future__ import annotations

import functools
import inspect


def make_multiplier(factor: int):
    """Return a function that multiplies its argument by `factor`."""

    def multiply(x: int) -> int:
        # `factor` is not defined here and not a global: it is a free variable
        # captured from the enclosing scope.
        return x * factor

    return multiply


def make_counter():
    """Return a counter that survives between calls — state without a class."""
    count = 0

    def bump() -> int:
        nonlocal count  # without this, `count = count + 1` would create a NEW local
        count += 1
        return count

    return bump


def head(name: str, count: int = 3):
    """Show only the first `count` items, and remember both settings."""

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(items, *args, **kwargs):
            return fn(items[:count], *args, **kwargs)

        return wrapper

    return decorator


def audit(fn):
    """Print the call, the arguments it received and the arguments it passed on."""
    calls: list[dict] = []

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        calls.append({"args": args, "kwargs": kwargs})
        print(f"    audit -> {fn.__name__} args={args} kwargs={kwargs}")
        return fn(*args, **kwargs)

    wrapper.calls = calls  # attach state to the function object itself
    return wrapper


@audit
def manifest(service: str, replicas: int = 1, *, namespace: str = "default") -> dict:
    """Build a tiny deployment manifest."""
    return {"service": service, "replicas": replicas, "namespace": namespace}


def main() -> None:
    print("=== step 1: a closure remembers a value ===")
    double = make_multiplier(2)
    triple = make_multiplier(3)
    print(f"  double(10) -> {double(10)}")
    print(f"  triple(10) -> {triple(10)}")
    print("  -> two functions, one code object, different closed-over state")

    print("\n=== step 2: the cell that holds it ===")
    print(f"  double.__closure__          {double.__closure__}")
    print(f"  free variables              {double.__code__.co_freevars}")
    print(f"  value in the first cell     {double.__closure__[0].cell_contents}")

    print("\n=== step 3: state that survives between calls ===")
    counter = make_counter()
    print(f"  bump() -> {counter()}")
    print(f"  bump() -> {counter()}")
    print(f"  bump() -> {counter()}")
    other = make_counter()
    print(f"  a fresh counter starts at   {other()}")
    print("  -> each closure owns its own `count`; this is how a decorator counts calls")

    print("\n=== step 4: nonlocal is mandatory for rebinding ===")

    def broken():
        n = 0

        def bump():
            # No `nonlocal n`: this line makes `n` local to bump, so Python raises
            # UnboundLocalError on the `+=` because it is read before assignment.
            n += 1
            return n

        return bump

    try:
        broken()()
    except UnboundLocalError as exc:
        print(f"  UnboundLocalError: {exc}")

    print("\n=== step 5: *args / **kwargs forwarding through a decorator ===")
    print(f"  {manifest('api')}")
    print(f"  {manifest('api', replicas=3, namespace='prod')}")
    print(f"  recorded calls: {manifest.calls}")

    print("\n=== step 6: the wrapper's signature is the ORIGINAL signature ===")
    print(f"  inspect.signature(manifest)  {inspect.signature(manifest)}")
    print(f"  keyword-only `namespace` survived: {'namespace' in inspect.signature(manifest).parameters}")
    print("  -> because functools.wraps copies __wrapped__, and signature() follows it")


if __name__ == "__main__":
    main()
