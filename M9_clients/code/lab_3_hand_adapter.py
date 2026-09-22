"""LAB 3 — write the MCP -> LangChain adapter by hand, and watch the one-liner fail.

The tutorial's claim is that `load_mcp_tools` is not magic: a LangChain tool is a name, a
description, an argument schema and an async callable. This lab builds exactly that, on purpose
in two versions — first the version that looks right and silently loses the arguments, then the
version that works — and finally tries the one-liner so you can see what actually happens with
this project's pinned stack.

Every error string printed below was measured, not paraphrased.

Run:
    uv run python -m M9_clients.code.lab_3_hand_adapter
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Callable

from fastmcp import Client
from langchain_core.tools import StructuredTool
from pydantic import Field, create_model

ROOT = Path(__file__).parents[2]
HELLO = ROOT / "M4_fastmcp_basics" / "code" / "hello_server.py"

# JSON Schema type name -> Python type. This is the M2 payoff: the server GENERATED the schema
# from its type hints, and the client turns that same schema back into a validating model.
JSON_TO_PY: dict[str, Callable[..., Any]] = {
    "string": str, "number": float, "integer": int, "boolean": bool,
    "array": list, "object": dict,
}


def args_model_from_schema(tool_name: str, schema: dict) -> type:
    """Build the Pydantic model LangChain validates arguments against."""
    required = set(schema.get("required") or [])
    fields: dict[str, tuple] = {}
    for key, spec in (schema.get("properties") or {}).items():
        annotation = JSON_TO_PY.get(spec.get("type", "string"), Any)
        default = ... if key in required else spec.get("default", None)
        fields[key] = (annotation, Field(default=default,
                                         description=spec.get("description", "")))
    return create_model(f"{tool_name}_args", **fields)


def adapter_without_schema(name: str, description: str, client: Client) -> StructuredTool:
    """Version 1 — no args_schema. This is the mistake that looks reasonable."""

    async def _call(**kwargs: Any) -> Any:
        result = await client.call_tool(name, kwargs)
        return result.data

    return StructuredTool.from_function(coroutine=_call, name=name,
                                        description=description, args_schema=None)


def adapter(name: str, description: str, schema: dict, client: Client) -> StructuredTool:
    """Version 2 — the schema carried across the wire, in Pydantic form."""

    async def _call(**kwargs: Any) -> Any:
        result = await client.call_tool(name, kwargs)
        return result.data

    return StructuredTool.from_function(coroutine=_call, name=name,
                                        description=description,
                                        args_schema=args_model_from_schema(name, schema))


async def main() -> None:
    async with Client(HELLO) as client:
        discovered = await client.list_tools()
        add_mcp = next(t for t in discovered if t.name == "add")
        print("=== the MCP side of the adapter ===")
        print(f"  name        {add_mcp.name!r}")
        print(f"  description {add_mcp.description!r}")
        print(f"  input_schema {json.dumps(add_mcp.input_schema)}")

        print("\n=== version 1: args_schema=None ===")
        broken = adapter_without_schema("add", add_mcp.description or "", client)
        print(f"  name ... {broken.name!r}")
        print(f"  args_schema was auto-built as {broken.args_schema.__name__!r}")
        print("  the schema the model would be shown:")
        print(f"  {json.dumps(broken.tool_call_schema.model_json_schema()['properties'])}")
        print("  ^ there is no 'a' and no 'b' in it. The model is never told they exist.")
        try:
            await broken.ainvoke({"a": 2, "b": 3})
        except Exception as exc:
            first = str(exc).splitlines()[0]
            print(f"  ainvoke({{'a': 2, 'b': 3}}) -> {type(exc).__name__}: {first}")
            print("  LangChain dropped the unknown keys, so the MCP server received {}")

        print("\n=== version 2: args_schema from the MCP schema ===")
        add = adapter("add", add_mcp.description or "", add_mcp.input_schema, client)
        print(f"  args_schema {add.args_schema.__name__} fields={sorted(add.args)}")
        print("  the schema the model would be shown:")
        print(json.dumps(add.tool_call_schema.model_json_schema(), indent=2))
        print(f"  ainvoke({{'a': 2, 'b': 3}}) -> {await add.ainvoke({'a': 2, 'b': 3})!r}")
        print(f"  ainvoke({{'a': 'two', 'b': 3}}) is rejected before the server is touched:")
        try:
            await add.ainvoke({"a": "two", "b": 3})
        except Exception as exc:
            print(f"    {type(exc).__name__}: {str(exc).splitlines()[0][:70]}")

        tools = [adapter(t.name, t.description or "", t.input_schema, client) for t in discovered]
        print(f"\n  all adapted: {[(t.name, sorted(t.args)) for t in tools]}")

    print("\n=== the one-liner, attempted ===")
    for label, statement in (
        ("from langchain_mcp_adapters.tools import load_mcp_tools",
         "from langchain_mcp_adapters.tools import load_mcp_tools"),
        ("from langchain_mcp_adapters.client import MultiServerMCPClient",
         "from langchain_mcp_adapters.client import MultiServerMCPClient"),
    ):
        try:
            exec(statement, {})
            print(f"  {label}\n    -> imports fine here")
        except Exception as exc:
            print(f"  {label}\n    -> {type(exc).__name__}: {str(exc).splitlines()[0][:110]}")
    print("  Measured against langchain-mcp-adapters 0.3.1 with mcp 2.2.0 (see VERIFIED.md,")
    print("  'What was NOT verified'): the adapter package imports, its tool-loading modules do")
    print("  not. Two independent breakages — an SDK module rename and a moved class — which is")
    print("  exactly why this lesson makes you write the 10-line adapter yourself.")


if __name__ == "__main__":
    asyncio.run(main())
