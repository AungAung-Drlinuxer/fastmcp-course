"""LAB 1 — build a decorator by hand, then let `@` build the same thing for you.

A decorator is nothing more than a function that takes a function and returns a
function. Everything else is syntax sugar. This lab proves that by writing the
same wrapper three different ways and comparing what each one produced.

Run:
    uv run python -m M3_asyncio_decorators.code.lab_1_decorator_mechanics
"""
from __future__ import annotations

import functools
import inspect
import time


def timed(fn):
    """Wrap a function so every call prints how long it took."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"    {fn.__name__} took {elapsed * 1000:.2f} ms")
        return result

    return wrapper


def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


def main() -> None:
    print("=== step 1: the long way, no @ syntax at all ===")
    timed_add = timed(add)
    print(f"  add            -> {add!r}")
    print(f"  timed_add      -> {timed_add!r}")
    print(f"  timed_add(2,3) -> {timed_add(2, 3)}")

    print("\n=== step 2: the @ syntax does exactly the same thing ===")

    @timed
    def multiply(a: int, b: int) -> int:
        """Multiply two integers."""
        return a * b

    print(f"  multiply(4,5)  -> {multiply(4, 5)}")

    print("\n=== step 3: an identity decorator changes nothing ===")

    def identity(fn):
        return fn

    @identity
    def untouched(x: int) -> int:
        """Return x unchanged."""
        return x

    print(f"  untouched(9)   -> {untouched(9)}")
    print(f"  untouched is the *original* function object: {untouched.__name__ == 'untouched'}")

    print("\n=== step 4: proof that metadata survived the wrapping ===")
    for fn in (timed_add, multiply):
        print(f"  --- {fn.__name__} ---")
        print(f"  __name__         {fn.__name__}")
        print(f"  __doc__          {inspect.getdoc(fn)}")
        print(f"  __annotations__  {fn.__annotations__}")
        print(f"  signature        {inspect.signature(fn)}")

    print("\n=== step 5: the original function is still reachable ===")
    print(f"  multiply.__wrapped__ is not None: {getattr(multiply, '__wrapped__', None) is not None}")
    print(f"  the undecorated add still works:  add(1, 2) = {add(1, 2)}")

    print("\n=== step 6: a decorator can refuse to wrap ===")
    seen: dict = {}

    def only_once(fn):
        def wrapper(*args, **kwargs):
            if seen.get(fn.__name__):
                print(f"    refused: {fn.__name__} already ran")
                return None
            seen[fn.__name__] = True
            return fn(*args, **kwargs)

        return wrapper

    @only_once
    def ticket() -> str:
        return "issued"

    print(f"  ticket() first  -> {ticket()}")
    print(f"  ticket() second -> {ticket()}")
    print("  -> a decorator may change behaviour, not just add logging.")


if __name__ == "__main__":
    main()
