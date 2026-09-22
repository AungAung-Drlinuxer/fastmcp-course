"""LAB 1 — print the JSON-RPC that a real MCP client and server exchange.

Nothing here is simulated: the client and the server are the real ones, and the JSON printed is
what the protocol actually carried. Seeing it once makes every later lesson less abstract.

Run:
    uv run python -m M0_orientation.code.lab_1_see_the_protocol
"""
from __future__ import annotations

import asyncio
import json

from fastmcp import Client, FastMCP

mcp = FastMCP("lab-1")


@mcp.tool
def add(a: float, b: float) -> float:
    """Add two numbers.

    Args:
        a: The first number.
        b: The second number.
    """
    return a + b


async def main() -> None:
    async with Client(mcp) as client:
        # tools/list — what the server advertises to any client
        tools = await client.list_tools()
        print("=== tools/list (what the client discovers) ===")
        print(json.dumps(
            [{"name": t.name,
              "description": t.description,
              # NOTE: on the CLIENT side the field is `input_schema` (snake_case).
              # The server-side object exposes the same schema as `.parameters`.
              # `inputSchema` (camelCase) is deprecated in 4.x.
              "input_schema": t.input_schema} for t in tools],
            indent=2))

        # tools/call — the invocation itself
        print("\n=== tools/call ===")
        result = await client.call_tool("add", {"a": 2, "b": 3})
        print("  data              :", result.data)
        print("  structured_content:", result.structured_content)
        print("  is_error          :", result.is_error)
        print("  content           :", str(result.content)[:90])

        print("\n=== what to notice ===")
        print("  input_schema was NOT written by hand — it came from the annotations")
        print("  `a: float, b: float`. The description came from the docstring's first line.")
        print("  So an annotation and a docstring are not documentation: they are the contract.")


if __name__ == "__main__":
    asyncio.run(main())
