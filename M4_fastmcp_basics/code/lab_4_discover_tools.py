"""LAB 4 — discover a server the way a host application does.

This is the client half of Lesson 2.1: connect, ask what exists, print the contract that a
model would be shown, then call something. No LLM, no API key.

The one field to stare at is `input_schema`. Server-side the same schema is `.parameters`
(see VERIFIED.md); through a client it is `.input_schema`. That rename is the single most
common source of "my tutorial does not work" in FastMCP 4.x.

Run:
    uv run python -m M4_fastmcp_basics.code.lab_4_discover_tools
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastmcp import Client

SERVER = Path(__file__).with_name("lab_1_echo_server.py")


async def main() -> None:
    async with Client(SERVER) as client:
        tools = await client.list_tools()

        print("=== the inventory ===")
        for tool in tools:
            print(f"  {tool.name:12} {tool.description.strip().splitlines()[0]}")

        print()
        print("=== the contract, as the model would receive it ===")
        for tool in tools:
            if tool.name != "word_count":
                continue
            print(f"  {tool.name}.input_schema =")
            print(json.dumps(tool.input_schema, indent=2))
            # Reading `.parameters` here would raise:
            #   AttributeError: 'Tool' object has no attribute 'parameters'
            # Reading `.inputSchema` would emit a deprecation warning instead:
            #   FastMCPDeprecationWarning: ... renamed this field to `input_schema`.

        print()
        print("=== a good call and a rejected one ===")
        print("  echo      ->", (await client.call_tool("echo", {"message": "hello"})).data)
        try:
            # The underscore is not in the schema. This is a name error, not a type error.
            await client.call_tool("word_count", {"the_text": "x"})
        except Exception as exc:
            print(f"  bad name  : {type(exc).__name__}: {str(exc).splitlines()[0][:100]}")
        try:
            # 12 is not a string. Pydantic rejects this BEFORE the function body runs.
            await client.call_tool("echo", {"message": 12})
        except Exception as exc:
            print(f"  bad type  : {type(exc).__name__}: {str(exc).splitlines()[0][:100]}")


if __name__ == "__main__":
    asyncio.run(main())
