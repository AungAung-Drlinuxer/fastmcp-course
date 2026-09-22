"""Lesson 3.2 (part 1) — an MCP client you wrote yourself, with NO LLM.

Students often believe the model is what makes an MCP client work. It is not: `list_tools` ->
choose -> `call_tool` is an ordinary program. Seeing that loop without a model in it makes the
LangGraph version in the next file much easier to read, and it works in an air-gapped lab with
no API key at all.

Run:
    uv run python -m M9_clients.code.tool_loop
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from fastmcp import Client

SERVER = Path(__file__).parents[2] / "M4_fastmcp_basics" / "code" / "hello_server.py"


async def main() -> None:
    async with Client(SERVER) as client:
        tools = await client.list_tools()
        resources = await client.list_resources()
        templates = await client.list_resource_templates()
        prompts = await client.list_prompts()

        print("=== the four things a client discovers ===")
        print(f"  tools     : {[t.name for t in tools]}")
        print(f"  resources : {[str(r.uri) for r in resources]}")
        print(f"  templates : {[t.uri_template for t in templates]}")
        print(f"  prompts   : {[p.name for p in prompts]}")

        print("\n=== the schema the 'model' would be shown ===")
        add_tool = next(t for t in tools if t.name == "add")
        print(json.dumps(add_tool.parameters, indent=2))

        print("\n=== three ways to decide what to call ===")
        # 1. by name, from the schema
        call = {"name": "add", "arguments": {"a": 2, "b": 3}}
        result = await client.call_tool(call["name"], call["arguments"])
        print(f"  direct    : {call['name']}{call['arguments']} -> {result.data}")

        # 2. dispatch through the discovered schema — this is what a model emits
        incoming = json.loads('{"tool": "add", "arguments": {"a": 10, "b": 5}}')
        known = {t.name for t in tools}
        if incoming["tool"] not in known:
            print(f"  dispatched: unknown tool {incoming['tool']!r} — reject before calling")
        else:
            result = await client.call_tool(incoming["tool"], incoming["arguments"])
            print(f"  dispatched: {incoming['tool']} -> {result.data}")

        # 3. a bad call: the client learns the contract from the error, not from a crash
        try:
            await client.call_tool("add", {"a": "two", "b": 3})
        except Exception as exc:
            print(f"  invalid   : {type(exc).__name__}: {str(exc).splitlines()[0][:70]}")

        print("\n=== what an interactive console needs ===")
        print("  /tools                 list what is available")
        print("  /call <tool> <json>    invoke with arguments")
        print("  /resources             list static resources")
        print("  /prompts               list prompts, then get_prompt to render one")
        print("  These map one-to-one onto the client methods used above, which is why the")
        print("  console in the next lesson is short: the protocol does the work.")


if __name__ == "__main__":
    asyncio.run(main())
