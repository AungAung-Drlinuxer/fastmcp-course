"""LAB 1 — read an annotation the way a schema generator must.

A type hint is DATA. This lab turns the catalog of hint forms into a printed report, so the
shape of every hint stops being guesswork. Nothing here validates anything: we only READ.

Run:
    uv run python -m M2_types_pydantic.code.lab_1_annotation_report
"""
from __future__ import annotations

import types
import typing
from typing import Any, Literal, get_args, get_origin

# The catalog. One line per hint form the course uses.
CATALOG: list[tuple[str, object]] = [
    ("str", str),
    ("int", int),
    ("float", float),
    ("bool", bool),
    ("list[str]", list[str]),
    ("dict[str, Any]", dict[str, Any]),
    ("str | None", str | None),
    ("int | None", int | None),
    ("str | int", str | int),
    ("Literal[...]", Literal["ubuntu", "rocky", "windows"]),
    ("list[dict[str, int]]", list[dict[str, int]]),
    ("Any", Any),
]


def kind_of(annotation: object) -> str:
    """Classify a hint into the small set of shapes a schema generator cares about."""
    origin = get_origin(annotation)

    if origin is None:
        # No origin means it is either a bare class or a special form such as Any.
        if annotation is Any:
            return "any (no constraint at all)"
        if isinstance(annotation, type):
            return "scalar"
        return "opaque"

    if origin is typing.Union or origin is types.UnionType:
        parts = get_args(annotation)
        has_none = any(p is type(None) for p in parts)
        return "nullable union" if has_none else "union"

    if origin is Literal:
        return "enum (Literal)"

    if origin is list:
        return "array"

    if origin is dict:
        return "object"

    return f"other ({getattr(origin, '__name__', origin)})"


def render(annotation: object) -> str:
    """A one-line human summary of a hint, built only from get_origin/get_args."""
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is None:
        return getattr(annotation, "__name__", repr(annotation))

    if origin is typing.Union or origin is types.UnionType:
        return " | ".join(render(a) for a in args)

    if origin is Literal:
        return "enum{" + ", ".join(repr(a) for a in args) + "}"

    head = getattr(origin, "__name__", str(origin))
    if not args:
        return head
    return f"{head}[{', '.join(render(a) for a in args)}]"


def main() -> None:
    print("=== annotation catalog ===")
    print(f"  {'hint':22} {'kind':24} {'origin':22} args")
    for label, annotation in CATALOG:
        origin = get_origin(annotation)
        args = ", ".join(render(a) for a in get_args(annotation)) or "-"
        origin_name = getattr(origin, "__name__", str(origin)) if origin is not None else "None"
        print(f"  {label:22} {kind_of(annotation):24} {origin_name:22} {args}")

    print()
    print("=== the same catalog, summarised ===")
    for label, annotation in CATALOG:
        print(f"  {label:22} -> {render(annotation)}")

    print()
    print("=== a Union is detected by its origin, and both spellings work ===")
    modern = str | int
    legacy = typing.Union[str, int]
    print(f"  str | int          get_origin -> {get_origin(modern)}")
    print(f"  Union[str, int]    get_origin -> {get_origin(legacy)}")
    print(f"  both are union-like: {get_origin(modern) is types.UnionType} / "
          f"{get_origin(legacy) is typing.Union}")
    print(f"  get_args(str | int)  -> {get_args(modern)}")
    print(f"  get_args(int | None) -> {get_args(modern if False else int | None)}")

    print()
    print("=== None is not a type you can forget ===")
    print(f"  type(None) is types.NoneType -> {type(None) is types.NoneType}")
    print(f"  int | None args              -> {get_args(int | None)}")
    print("  note: `int | None` ALSO appear as required when no default is given.")


if __name__ == "__main__":
    main()
