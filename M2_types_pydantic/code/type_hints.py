"""Lesson 1.2 (part 1) — type hints are DATA, not documentation.

This is the single most important idea in Phase 1. MCP does not read your prose; it reads
your annotations and your docstring, and it builds a JSON Schema from them. If the annotation
is imprecise, the model is handed an imprecise contract — and then calls your tool wrongly
and gets blamed for it.

Run:
    uv run python -m M2_types_pydantic.code.type_hints
"""
from __future__ import annotations

import types
import typing
from typing import Any, Literal, get_args, get_origin

# Every annotation below is inert until something reads it. Nothing validates at runtime.
Simple = str | int
OptionalList = list[str] | None
Mapping = dict[str, Any]
Choice = Literal["ubuntu", "rocky", "windows"]


def explain(annotation: object) -> str:
    """Describe a type annotation the way a schema generator would have to."""
    origin = get_origin(annotation)
    if origin is None:
        # A bare class, e.g. `str` or a Literal instance's type
        if isinstance(annotation, type):
            return f"base type {annotation.__name__}"
        return f"opaque {annotation!r}"
    if origin is typing.Union or origin is types.UnionType:
        parts = get_args(annotation)
        non_none = [p for p in parts if p is not type(None)]
        nullable = len(non_none) != len(parts)
        joined = " | ".join(getattr(p, "__name__", str(p)) for p in non_none)
        return f"choice of {joined}" + (" or None (nullable)" if nullable else "")
    if origin is Literal:
        values = ", ".join(repr(v) for v in get_args(annotation))
        return f"exactly one of {values}"
    args = get_args(annotation)
    inner = ", ".join(getattr(a, "__name__", str(a)) for a in args)
    return f"{getattr(origin, '__name__', origin)} of ({inner})"


def main() -> None:
    print("=== what a schema generator can learn from an annotation ===")
    for name, ann in [
        ("Simple", Simple),
        ("OptionalList", OptionalList),
        ("Mapping", Mapping),
        ("Choice", Choice),
        ("bare str", str),
    ]:
        print(f"  {name:14} {str(ann):32} -> {explain(ann)}")

    print("\n=== why Literal matters more than str ===")
    print("  A `str` parameter lets the model send 'Ubuntu 24.04' or 'ubuntu-server' and the")
    print("  call fails deep inside your code. A Literal turns those into an enum in the")
    print("  schema, so the constraint is part of the contract the model is shown.")
    print("  Measured — a Literal produces this in the generated schema:")
    print('    "os_type": {"enum": ["ubuntu", "rocky", "windows"], "type": "string"}')


if __name__ == "__main__":
    main()
