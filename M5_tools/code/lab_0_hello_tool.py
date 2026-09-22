"""M5 beginner lab — your first tool, run from top to bottom.

This file exists for readers who have never built a server. Nothing here is clever; every line
is the smallest possible version of something Lesson 2.2 does for real.

Read it once, then RUN it:

    uv run python -m M5_tools.code.lab_0_hello_tool

You are not expected to write this file yet. Type it only when you feel ready.
"""
from __future__ import annotations

import asyncio

from fastmcp import Client, FastMCP

# A server is an object. Its name is only a label.
mcp = FastMCP("hello")


@mcp.tool
def greet(name: str = "world") -> dict:
    """Say hello to someone.

    Args:
        name: Who to greet.
    """
    return {"ok": True, "message": f"hello, {name}"}


@mcp.tool
def add(a: float, b: float) -> dict:
    """Add two numbers.

    Args:
        a: The first number.
        b: The second number.
    """
    return {"ok": True, "result": a + b}


async def main() -> None:
    # 1. ask the server what it publishes — no client needed for this part
    print("=== 1. the names this server publishes ===")
    print([tool.name for tool in await mcp.list_tools()])

    async with Client(mcp) as client:
        # 2. the client sees a description of every tool: this is what a model reads
        print("\n=== 2. what a model can read about each tool ===")
        for tool in await client.list_tools():
            print(f"  {tool.name:6} {tool.description.splitlines()[0]}")

        # 3. calling a tool: name + arguments as a dict
        print("\n=== 3. calling a tool ===")
        print(" ", (await client.call_tool("greet", {})).data)
        print(" ", (await client.call_tool("greet", {"name": "Aung"})).data)
        print(" ", (await client.call_tool("add", {"a": 2, "b": 3})).data)

        # 4. a wrong type is refused BEFORE the function body runs
        print("\n=== 4. what happens when an argument is wrong ===")
        try:
            await client.call_tool("add", {"a": 2, "b": "three"})
        except Exception as exc:
            print(" ", type(exc).__name__ + ":", str(exc).splitlines()[0])
            print("  (add() never ran — the argument was refused before the body)")

        # 5. the reply is an object with named parts, not just text
        print("\n=== 5. reading the shape of a reply ===")
        result = await client.call_tool("add", {"a": 2, "b": 3})
        print("  is_error           ", result.is_error)
        print("  structured_content ", result.structured_content)
        print("  content            ", result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())