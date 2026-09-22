"""LAB 3 — build the JSON Schema by hand, then fix the two things it gets wrong.

The naive generator reads `param.annotation` directly. Under `from __future__ import
annotations` every annotation is a STRING, so the naive version emits `{"type": "object"}` for
every parameter. The fix is `get_type_hints`, which resolves the strings to real objects.

The second gap cannot be fixed by introspection at all: `inspect` cannot see a `Field`, and it
cannot see which part of the docstring describes a parameter. That gap is why Pydantic exists.

Run:
    uv run python -m M2_types_pydantic.code.lab_3_signature_schema
"""
from __future__ import annotations

import inspect
import json
import re
from typing import Literal, get_args, get_origin, get_type_hints

PRIMITIVES = {str: "string", int: "integer", float: "number", bool: "boolean"}


def naive_fragment(annotation: object) -> dict:
    """Read the annotation as-is. Wrong under PEP 563 — that is the point."""
    if annotation is inspect.Parameter.empty:
        return {}
    if annotation in PRIMITIVES:
        return {"type": PRIMITIVES[annotation]}
    if get_origin(annotation) is Literal:
        values = list(get_args(annotation))
        return {"type": "string", "enum": values}
    return {"type": "object"}


def resolve(fn) -> dict:
    """Resolve string annotations into real objects using the function's own globals."""
    return get_type_hints(fn)


def fragment(annotation: object) -> dict:
    """A fragment built from a RESOLVED annotation."""
    origin = get_origin(annotation)

    if origin is Literal:
        values = list(get_args(annotation))
        inner = {int: "integer", str: "string", bool: "boolean"}.get(type(values[0]), "string")
        return {"type": inner, "enum": values}

    if origin is not None:
        parts = get_args(annotation)
        non_none = [p for p in parts if p is not type(None)]
        if len(non_none) == 1:
            # X | None -> the schema of X; nullability is expressed by leaving it out of
            # `required`, which only works when there is a default.
            return fragment(non_none[0])
        return {"anyOf": [fragment(p) for p in non_none]}

    if annotation in PRIMITIVES:
        return {"type": PRIMITIVES[annotation]}

    return {"type": "object"}


def schema_from_signature(fn, resolved: bool = True) -> dict:
    """Build an input schema the way an MCP server must."""
    signature = inspect.signature(fn)
    hints = resolve(fn) if resolved else {}
    properties: dict = {}
    required: list[str] = []

    for name, param in signature.parameters.items():
        annotation = hints.get(name, param.annotation)
        piece = fragment(annotation)
        if param.default is not inspect.Parameter.empty:
            piece["default"] = param.default
        properties[name] = piece
        if param.default is inspect.Parameter.empty:
            required.append(name)

    out: dict = {"type": "object", "properties": properties, "additionalProperties": False}
    if required:
        out["required"] = required
    return out


def docstring_args(fn) -> dict[str, str]:
    """Extract `name: text` lines from a Google-style `Args:` block."""
    doc = inspect.getdoc(fn) or ""
    found: dict[str, str] = {}
    inside = False
    for line in doc.splitlines():
        stripped = line.strip()
        if stripped.startswith("Args:"):
            inside = True
            continue
        if inside:
            if not line.startswith((" ", "\t")) and stripped:
                inside = False
                continue
            match = re.match(r"^(\w+)\s*:\s*(.+)$", stripped)
            if match:
                found[match.group(1)] = match.group(2).strip()
    return found


def with_descriptions(fn) -> dict:
    """Add the one thing introspection cannot see on its own."""
    schema = schema_from_signature(fn)
    descriptions = docstring_args(fn)
    for name, text in descriptions.items():
        if name in schema["properties"]:
            schema["properties"][name]["description"] = text
    return schema


def plan_vm(vm_name: str, cpu_cores: int = 2,
            os_type: Literal["ubuntu", "rocky", "windows"] = "ubuntu",
            memory_gb: int | None = None) -> dict:
    """Plan a virtual machine.

    Args:
        vm_name: Name of the virtual machine.
        cpu_cores: How many virtual cores to assign.
        os_type: Which operating system image to use.
        memory_gb: Memory in GB. Omit to let the platform choose.
    """
    return {"vm_name": vm_name, "cpu_cores": cpu_cores, "os_type": os_type, "memory_gb": memory_gb}


def main() -> None:
    print("=== raw annotations under `from __future__ import annotations` ===")
    for name, param in inspect.signature(plan_vm).parameters.items():
        print(f"  {name:12} {param.annotation!r}")

    print()
    print("=== schema built from the RAW annotations (the naive generator) ===")
    print(json.dumps(schema_from_signature(plan_vm, resolved=False), indent=2))

    print()
    print("=== the same schema, after resolving with get_type_hints ===")
    print(json.dumps(schema_from_signature(plan_vm), indent=2))

    print()
    print("=== descriptions live in the docstring, not in the signature ===")
    print("  docstring_args() ->", json.dumps(docstring_args(plan_vm), indent=2))
    print("  schema with descriptions merged in:")
    print(json.dumps(with_descriptions(plan_vm), indent=2))

    print()
    print("=== what the hand-rolled version still cannot do ===")
    print("  1. It cannot express ge=/le= — there is no Field to read.")
    print("  2. It cannot VALIDATE. It only describes. A wrong call still reaches your body.")
    print("  Pydantic closes both gaps in the next lab.")


if __name__ == "__main__":
    main()
