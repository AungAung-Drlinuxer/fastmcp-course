"""M5_tools LAB 8 — the docstring is the contract, in three measurable pieces.

The same function body, documented three ways. The client schema changes; the arithmetic does
not. This is the cheapest quality improvement available to an MCP server, and it is the reason
`Args:` is not decoration.

Run:
    uv run python -m M5_tools.code.lab_8_docstring_contract
"""
from __future__ import annotations

import asyncio
import json

from fastmcp import Client, FastMCP

mcp = FastMCP("lab8-docstring-contract")

FACTORS = {"a": 6.0, "b": 7.0}


def _scale(a: float, b: float) -> dict:
    return {"ok": True, "product": a * b}


@mcp.tool
def scale_silent(a: float, b: float) -> dict:
    return _scale(a, b)


@mcp.tool
def scale_summary_only(a: float, b: float) -> dict:
    """Multiply two numbers."""
    return _scale(a, b)


@mcp.tool
def scale_documented(a: float, b: float) -> dict:
    """Multiply two numbers and report the product.

    Args:
        a: The first factor.
        b: The second factor.
    """
    return _scale(a, b)


async def main() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()

        print("=== what the model can read about each tool ===")
        for tool in tools:
            summary = tool.description.splitlines()[0] if tool.description else None
            print(f"\n--- {tool.name}")
            print(f"    description : {json.dumps(summary)}")
            for key, spec in tool.input_schema["properties"].items():
                print(f"    {key} spec     : {json.dumps(spec)}")

        print("\n=== the same three tools, counted ===")
        for tool in tools:
            documented = sum(1 for spec in tool.input_schema["properties"].values()
                             if "description" in spec)
            print(f"    {tool.name:20} has_summary={tool.description is not None!s:5} "
                  f"described_params={documented}/{len(tool.input_schema['properties'])}")

        print("\n=== they all still compute the same thing ===")
        for tool in tools:
            result = await client.call_tool(tool.name, dict(FACTORS))
            print(f"    {tool.name:20} -> {json.dumps(result.data)}")

        print("\n=== the anti-pattern, one line of code ===")
        print("    scale_silent has no docstring, so the model is told nothing.")
        print("    A tool the model cannot describe is a tool the model will not choose.")


if __name__ == "__main__":
    asyncio.run(main())
