"""Lesson 1.3 (part 1) — decorators, and the metadata trap that bites every MCP tool.

@mcp.tool is a decorator. If you write your own wrapper and forget functools.wraps, the
wrapped function loses its name, its annotations and its docstring — which is precisely the
data MCP turns into a tool definition. The tool then appears in the list as `<lambda>` with
an empty schema, and nothing raises an error to tell you why.

Run:
    uv run python -m M3_asyncio_decorators.code.decorators
"""
from __future__ import annotations

import functools
import inspect


# --- a decorator WITHOUT functools.wraps: the failure case ------------------------------
def naive_logger(fn):
    def wrapper(*args, **kwargs):
        print(f"    [naive] calling ... something")
        return fn(*args, **kwargs)
    return wrapper


# --- the same decorator done correctly ---------------------------------------------------
def logged(fn):
    """Log a call, preserving everything introspection depends on."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        print(f"    [logged] {fn.__name__}{inspect.signature(fn)}")
        return fn(*args, **kwargs)

    return wrapper


def register_tool(registry: dict):
    """The shape of a tool registry — this is what @mcp.tool does underneath.

    It stores the function's NAME, its SIGNATURE-derived schema and its DOCSTRING and returns
    the function unchanged, so the code that follows still sees an ordinary function.
    """

    def decorator(fn):
        registry[fn.__name__] = {
            "function": fn,
            "description": inspect.getdoc(fn) or "",
            "parameters": {
                name: (str(p.annotation), p.default)
                for name, p in inspect.signature(fn).parameters.items()
            },
        }
        return fn

    return decorator


TOOLS: dict = {}


@register_tool(TOOLS)
def disk_usage(path: str, human: bool = True) -> dict:
    """Report disk usage for a path.

    Args:
        path: Filesystem path to inspect.
        human: Scale the numbers to KB/MB/GB instead of bytes.
    """
    return {"path": path, "human": human}


def describe(fn) -> None:
    print(f"  __name__     {getattr(fn, '__name__', '<missing>')}")
    print(f"  __doc__      {(inspect.getdoc(fn) or '<missing>')[:60]!r}")
    print(f"  __annotations__ {getattr(fn, '__annotations__', {})}")


def main() -> None:
    print("=== the trap ===")
    print("  without functools.wraps:")

    @naive_logger
    def provision(vm_name: str, cpu_cores: int = 2) -> dict:
        """Provision a VM."""
        return {"vm_name": vm_name}

    describe(provision)
    print("  -> a tool registered from this would have no name and no parameters.")

    print("\n  with functools.wraps:")
    describe(logged(provision))
    print("  -> the metadata survives, so the generated schema is usable.")

    print("\n=== a registry decorator, i.e. what @mcp.tool is ===")
    print(f"  registered: {list(TOOLS)}")
    entry = TOOLS["disk_usage"]
    print(f"  description: {entry['description'].splitlines()[0]}")
    for name, (ann, default) in entry["parameters"].items():
        print(f"    {name:8} {ann:5} default={default}")

    print("\n=== the rule ===")
    print("  Any decorator that wraps a tool function MUST use @functools.wraps.")
    print("  It is not style: it is what makes the tool describable to a model.")


if __name__ == "__main__":
    main()
