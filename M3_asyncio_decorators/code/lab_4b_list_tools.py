"""LAB 4B — read the registry that @mcp.tool filled in.

`@mcp.tool` is a registration decorator: it stores a tool definition and hands the
function back. This lab asks the server for that registry and prints exactly what
a client would receive.

Run:
    uv run python -m M3_asyncio_decorators.code.lab_4b_list_tools
"""
from __future__ import annotations

import asyncio
import json

from fastmcp import FastMCP

mcp = FastMCP("lab-4b")


@mcp.tool
def disk_usage(path: str, human: bool = True) -> dict:
    """Report disk usage for a path.

    Args:
        path: Filesystem path to inspect.
        human: Scale the numbers to KB/MB/GB instead of bytes.
    """
    return {"path": path, "human": human}


async def main() -> None:
    tools = await mcp.list_tools()          # server side -> FunctionTool objects
    print(f"=== {len(tools)} tool(s) registered ===")
    for tool in tools:
        print(f"  name        : {tool.name}")
        print(f"  description : {(tool.description or '').splitlines()[0]}")
        print(f"  object type : {type(tool).__name__}")
        print("  parameters  :")
        print(json.dumps(tool.parameters, indent=4))   # server side name: .parameters
        print()

    print("=== the function is still an ordinary, callable function ===")
    print(f"  disk_usage('/tmp')            -> {disk_usage('/tmp')}")
    print(f"  disk_usage.__name__           -> {disk_usage.__name__}")
    print(f"  disk_usage.__annotations__    -> {disk_usage.__annotations__}")


if __name__ == "__main__":
    asyncio.run(main())
