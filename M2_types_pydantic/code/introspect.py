"""Lesson 1.2 (part 2) — build a JSON Schema by hand, so you know what FastMCP does for you.

Writing the generator once is the fastest way to stop being confused by MCP: you see exactly
where each schema field comes from — the parameter name, the annotation, the default, and
nothing else. FastMCP does this automatically in M4; doing it by hand first makes it visible.

Run:
    uv run python -m M2_types_pydantic.code.introspect
"""
from __future__ import annotations

import inspect
import json
from typing import Literal, get_args, get_origin

_PRIMITIVES = {str: "string", int: "integer", float: "number", bool: "boolean"}


def annotation_to_schema(annotation: object, default: object = inspect.Parameter.empty) -> dict:
    """Turn one Python annotation into a JSON Schema fragment.

    Handles the subset MCP actually uses: primitives, Literal, and X | None. Anything else is
    left to Pydantic, which is the point of the next file.
    """
    if annotation is inspect.Parameter.empty:
        return {}
    origin = get_origin(annotation)

    if origin is Literal:
        values = list(get_args(annotation))
        schema: dict = {"enum": values, "type": type(values[0]).__name__ if values else "string"}
        schema["type"] = {int: "integer", str: "string", bool: "boolean"}.get(type(values[0]), "string")
        return schema

    if origin is not None:
        parts = get_args(annotation)
        non_none = [p for p in parts if p is not type(None)]
        if len(non_none) == 1:
            # X | None -> the schema of X, with null represented by dropping it from `required`
            return annotation_to_schema(non_none[0], default)
        return {"anyOf": [annotation_to_schema(p) for p in non_none]}

    if annotation in _PRIMITIVES:
        return {"type": _PRIMITIVES[annotation]}

    return {"type": "object"}


def function_to_schema(fn) -> dict:
    """Build the input schema for a function the way an MCP server must."""
    signature = inspect.signature(fn)
    properties: dict = {}
    required: list[str] = []

    for name, param in signature.parameters.items():
        fragment = annotation_to_schema(param.annotation, param.default)
        if param.default is not inspect.Parameter.empty:
            fragment["default"] = param.default
        properties[name] = fragment
        if param.default is inspect.Parameter.empty:
            required.append(name)

    schema: dict = {"type": "object", "properties": properties, "additionalProperties": False}
    if required:
        schema["required"] = required
    return schema


def describe_hint(vm_name: str, cpu_cores: int = 2, os_type: Literal["ubuntu", "rocky", "windows"] = "ubuntu") -> dict:
    """Plan a virtual machine. Change this line and watch the schema change.

    Args:
        vm_name: Name of the virtual machine.
        cpu_cores: How many virtual cores to assign.
        os_type: Which operating system image to use.
    """
    return {"vm_name": vm_name, "cpu_cores": cpu_cores, "os_type": os_type}


def main() -> None:
    print("=== schema generated from the signature alone ===")
    print(json.dumps(function_to_schema(describe_hint), indent=2))
    print()
    print("=== the docstring, which the schema above CANNOT see ===")
    print(inspect.getdoc(describe_hint))
    print()
    print("Note what is missing: no descriptions. A hand-rolled generator has to add them.")
    print("In M2's third file Pydantic does it via Field(description=...). In M4 FastMCP")
    print("merges both sources — annotation for shape, docstring for meaning.")


if __name__ == "__main__":
    main()
