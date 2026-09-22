"""LAB 4 — `@register_tool`: writing the decorator that `@mcp.tool` really is.

`@mcp.tool` looks magic. It is not. Underneath it is a decorator *factory* that
keeps a registry, reads three attributes off your function, and hands your
function straight back so the rest of the file still sees an ordinary function.

This lab builds that by hand, adds a JSON-Schema-shaped `parameters` block, and
prints the registry the way a client would see it.

Run:
    uv run python -m M3_asyncio_decorators.code.lab_4_register_tool
"""
from __future__ import annotations

import functools
import inspect
import json
from typing import Any

TOOLS: dict[str, dict] = {}


def _schema_for(annotation: Any) -> dict:
    """Map a Python annotation onto the JSON Schema fragment a tool schema needs."""
    if annotation is int:
        return {"type": "integer"}
    if annotation is float:
        return {"type": "number"}
    if annotation is bool:
        return {"type": "boolean"}
    if annotation is str:
        return {"type": "string"}
    if annotation is list:
        return {"type": "array", "items": {}}
    if annotation is dict:
        return {"type": "object"}
    return {}


def register_tool(registry: dict):
    """The shape of a tool registry — this is what `@mcp.tool` does underneath.

    It stores the name, a signature-derived schema and the docstring, then
    returns the function UNCHANGED.
    """

    def decorator(fn):
        doc = inspect.getdoc(fn) or ""
        properties: dict[str, dict] = {}
        required: list[str] = []
        for name, parameter in inspect.signature(fn).parameters.items():
            if parameter.kind in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD):
                continue
            spec = _schema_for(parameter.annotation)
            doc_line = _arg_description(doc, name)
            if doc_line:
                spec["description"] = doc_line
            if parameter.default is not inspect.Parameter.empty:
                spec["default"] = parameter.default
            else:
                required.append(name)
            properties[name] = spec
        registry[fn.__name__] = {
            "name": fn.__name__,
            "function": fn,
            "description": doc.splitlines()[0] if doc else "",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False,
            },
        }
        return fn

    return decorator


def _arg_description(doc: str, parameter: str) -> str:
    """Pull `parameter: text` out of the Args: block of a Google-style docstring."""
    lines = inspect.cleandoc(doc).splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip().rstrip(":") == "Args")
    except StopIteration:
        return ""
    for line in lines[start + 1:]:
        stripped = line.strip()
        if not stripped:
            continue
        if not line.startswith((" ", "\t")) and stripped.endswith(":"):
            break
        head, _, tail = stripped.partition(":")
        if head.strip() == parameter:
            return tail.strip()
    return ""


@register_tool(TOOLS)
def disk_usage(path: str, human: bool = True) -> dict:
    """Report disk usage for a path.

    Args:
        path: Filesystem path to inspect.
        human: Scale the numbers to KB/MB/GB instead of bytes.
    """
    return {"path": path, "human": human}


@register_tool(TOOLS)
def restart_service(name: str, replicas: int = 1, force: bool = False) -> dict:
    """Restart a service by name.

    Args:
        name: Service name as it appears in the cluster.
        replicas: How many replicas to restart; 0 means all of them.
        force: Skip the drain step. Destructive.
    """
    return {"name": name, "replicas": replicas, "force": force}


@register_tool(TOOLS)
def cluster_status(verbose: bool = False) -> dict:
    """Return a summary of cluster health."""
    return {"verbose": verbose, "healthy": True}


def main() -> None:
    print("=== the registry after three @register_tool decorations ===")
    for name in TOOLS:
        print(f"  {name}")

    print("\n=== what a client would receive for `disk_usage` ===")
    entry = TOOLS["disk_usage"]
    print(f"  description : {entry['description']}")
    print("  parameters  :")
    print(json.dumps(entry["parameters"], indent=4, ensure_ascii=False))

    print("\n=== the same view for every tool ===")
    for name, entry in TOOLS.items():
        required = entry["parameters"]["required"]
        optional = [p for p in entry["parameters"]["properties"] if p not in required]
        print(f"  {name:16} required={required} optional={optional}")

    print("\n=== the functions themselves are unchanged ===")
    print(f"  disk_usage('/tmp')            -> {disk_usage('/tmp')}")
    print(f"  restart_service('api', 2)     -> {restart_service('api', 2)}")
    print(f"  cluster_status(verbose=True)  -> {cluster_status(verbose=True)}")
    print("  -> the decorator added a registration, not a wrapper")

    print("\n=== `register_tool` returned the original object ===")
    print(f"  TOOLS['disk_usage']['function'] is disk_usage: "
          f"{TOOLS['disk_usage']['function'] is disk_usage}")
    print(f"  __name__ still readable: {TOOLS['disk_usage']['function'].__name__}")
    print("  -> a decorator that RETURNS fn keeps the whole call path free of wrappers")

    print("\n=== the description came from the docstring, not from the name ===")
    print(f"  cluster_status has no Args: block -> description="
          f"{TOOLS['cluster_status']['description']!r}")
    print(f"  its parameter still has a description? "
          f"{'description' in TOOLS['cluster_status']['parameters']['properties']['verbose']}")


if __name__ == "__main__":
    main()
