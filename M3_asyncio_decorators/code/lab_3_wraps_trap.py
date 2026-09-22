"""LAB 3 — the metadata trap, measured end to end.

Two decorators do the same job. One forgets `functools.wraps`. Then both results
are pushed through a *registry that behaves like a JSON-Schema generator* (it
skips `*args` and `**kwargs` because no tool schema can express them).

The point of the lab is the last line of output: the broken tool was registered,
listed and reported — and nothing raised.

Run:
    uv run python -m M3_asyncio_decorators.code.lab_3_wraps_trap
"""
from __future__ import annotations

import functools
import inspect
from typing import Any


# --- the broken decorator --------------------------------------------------------------
def naive_logger(fn):
    def wrapper(*args, **kwargs):
        print(f"    [naive] about to call something")
        return fn(*args, **kwargs)

    return wrapper


# --- the correct decorator -------------------------------------------------------------
def logged(fn):
    """Log a call, preserving everything introspection depends on."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        print(f"    [logged] {fn.__name__}")
        return fn(*args, **kwargs)

    return wrapper


# --- a tiny stand-in for a schema generator --------------------------------------------
def annotation_name(annotation: Any) -> str:
    """Turn a type annotation into the JSON Schema type name a generator would pick."""
    if annotation is inspect.Parameter.empty:
        return "unknown"
    if isinstance(annotation, type):
        if annotation is int:
            return "integer"
        if annotation is float:
            return "number"
        if annotation is bool:
            return "boolean"
        if annotation is str:
            return "string"
        return "object"
    return "unknown"


def build_tool_definition(fn) -> dict:
    """Read a function the way a tool registry does: name, docstring, signature.

    This mirrors FastMCP's path. Two details matter and both are deliberate:

    * the NAME comes from `fn.__name__`;
    * the DESCRIPTION comes from the docstring;
    * parameters of kind VAR_POSITIONAL / VAR_KEYWORD are skipped, because a
      JSON Schema object has no way to express `*args` — the same reason a
      pydantic-derived model silently drops them.
    """
    signature = inspect.signature(fn)
    properties: dict[str, dict] = {}
    required: list[str] = []
    for name, parameter in signature.parameters.items():
        if parameter.kind in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD):
            continue
        entry: dict[str, Any] = {"type": annotation_name(parameter.annotation)}
        if parameter.default is not inspect.Parameter.empty:
            entry["default"] = parameter.default
        properties[name] = entry
        if parameter.default is inspect.Parameter.empty:
            required.append(name)
    return {
        "name": getattr(fn, "__name__", "<lambda>"),
        "description": inspect.getdoc(fn) or "",
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
    }


REGISTRY: dict[str, dict] = {}


def register(fn):
    """Register a tool. Note what is NOT here: any validation at all."""
    REGISTRY[getattr(fn, "__name__", "<lambda>")] = build_tool_definition(fn)
    return fn


def describe(fn) -> None:
    print(f"  __name__         {getattr(fn, '__name__', '<missing>')!r}")
    print(f"  __doc__          {(inspect.getdoc(fn) or '<missing>')[:52]!r}")
    print(f"  __annotations__  {getattr(fn, '__annotations__', {})}")
    print(f"  __wrapped__      {hasattr(fn, '__wrapped__')}")


def main() -> None:
    print("=== step 1: two fresh functions, two decorators ===")

    def provision(vm_name: str, cpu_cores: int = 2) -> dict:
        """Provision a virtual machine.

        Args:
            vm_name: Name of the virtual machine.
            cpu_cores: How many cores to allocate.
        """
        return {"vm_name": vm_name, "cpu_cores": cpu_cores}

    broken = naive_logger(provision)
    correct = logged(provision)

    print("  WITHOUT functools.wraps:")
    describe(broken)
    print("  WITH functools.wraps:")
    describe(correct)

    print("\n=== step 2: what a schema generator makes of each ===")
    for label, fn in (("broken", broken), ("correct", correct)):
        tool = build_tool_definition(fn)
        print(f"  {label:8} name={tool['name']!r} description={tool['description'][:30]!r}")
        print(f"           properties={tool['parameters']['properties']}")

    print("\n=== step 3: register both — nothing validates ===")
    register(broken)
    register(correct)
    print(f"  registry keys: {sorted(REGISTRY)}")
    print(f"  entries:       {len(REGISTRY)}")
    print("  -> the broken tool is in the list. No exception was raised.")

    print("\n=== step 4: ask the broken tool something ===")
    broken_tool = build_tool_definition(broken)
    print(f"  name to advertise : {broken_tool['name']!r}")
    print(f"  description       : {broken_tool['description']!r}")
    print(f"  property count    : {len(broken_tool['parameters']['properties'])}")

    print("\n=== step 5: the fix, and what it restores ===")
    fixed = build_tool_definition(correct)
    print(f"  name to advertise : {fixed['name']!r}")
    print(f"  description       : {fixed['description'].splitlines()[0]!r}")
    for name, spec in fixed["parameters"]["properties"].items():
        print(f"    {name:10} {spec}")

    print("\n=== the rule ===")
    print("  @functools.wraps is not style. It is the difference between a tool a")
    print("  model can call and a nameless tool with an empty schema.")


if __name__ == "__main__":
    main()
