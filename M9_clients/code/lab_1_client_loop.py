"""LAB 1 — the client loop, with no LLM anywhere in it.

Fixes the two client-side mistakes in this module's `tool_loop.py` and extends the discovery
to ALL FOUR surfaces (tools, resources, resource templates, prompts) against real servers.

Fixes, both measured against fastmcp 4.0.5:
  1. `tool.parameters` on a CLIENT-side object raises
         AttributeError: 'Tool' object has no attribute 'parameters'
     The client-side object is `mcp_types._types.Tool`; its schema is `tool.input_schema`.
     `.parameters` is the SERVER-side name on `fastmcp.tools.function_tool.FunctionTool`.
  2. hello_server.py has no resources, no templates and no prompts, so the four-surface half of
     the lesson needs three servers, not one.

Run:
    uv run python -m M9_clients.code.lab_1_client_loop
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastmcp import Client

ROOT = Path(__file__).parents[2]
HELLO = ROOT / "M4_fastmcp_basics" / "code" / "hello_server.py"


async def part_a_tools_over_stdio() -> None:
    """The real thing: the client owns the child process and speaks JSON-RPC over its pipes."""
    print("=== A. tools, discovered over stdio ===")
    async with Client(HELLO) as client:
        tools = await client.list_tools()
        resources = await client.list_resources()
        templates = await client.list_resource_templates()
        prompts = await client.list_prompts()

        print(f"  tools     : {[t.name for t in tools]}")
        print(f"  resources : {[str(r.uri) for r in resources]}")
        print(f"  templates : {[t.uri_template for t in templates]}")
        print(f"  prompts   : {[p.name for p in prompts]}")
        print("  A server is allowed to have none of the last three. Asking anyway is correct:")
        print("  a client that ASSUMES a surface exists breaks on the next server it meets.")

        print("\n=== A2. the schema a model would be shown ===")
        add_tool = next(t for t in tools if t.name == "add")
        print(f"  type(add_tool).__module__ = {type(add_tool).__module__}")
        print(json.dumps(add_tool.input_schema, indent=2))
        # Read `add_tool.parameters` here and you get the AttributeError quoted in the docstring.

        print("\n=== A3. three ways to decide what to call ===")
        call = {"name": "add", "arguments": {"a": 2, "b": 3}}
        result = await client.call_tool(call["name"], call["arguments"])
        print(f"  direct    : {call['name']}{call['arguments']} -> {result.data}")

        incoming = json.loads('{"tool": "add", "arguments": {"a": 10, "b": 5}}')
        known = {t.name for t in tools}
        if incoming["tool"] not in known:
            print(f"  dispatched: unknown tool {incoming['tool']!r} — reject before calling")
        else:
            result = await client.call_tool(incoming["tool"], incoming["arguments"])
            print(f"  dispatched: {incoming['tool']} -> {result.data}")

        unknown = json.loads('{"tool": "delete_everything", "arguments": {}}')
        if unknown["tool"] not in known:
            print(f"  unknown   : reject {unknown['tool']!r} before it reaches the server")
            print(f"              (the server would answer with the same names: {sorted(known)})")

        try:
            await client.call_tool("add", {"a": "two", "b": 3})
        except Exception as exc:
            print(f"  invalid   : {type(exc).__name__}: {str(exc).splitlines()[0][:70]}")
        try:
            await client.call_tool("add", {})
        except Exception as exc:
            print(f"  missing   : {type(exc).__name__}: {str(exc).splitlines()[0][:70]}")


async def part_b_resources_in_process() -> None:
    """Resources and resource templates, from the M6 server object itself."""
    from M6_resources.code.runbooks import mcp as runbook_server

    print("\n=== B. resources and templates ===")
    async with Client(runbook_server) as client:
        print(f"  static resources  : {[str(r.uri) for r in await client.list_resources()]}")
        templates = await client.list_resource_templates()
        print(f"  uri templates     : {[t.uri_template for t in templates]}")

        inv = await client.read_resource("inventory://hosts")
        print(f"  inventory://hosts -> {str(inv[0].text)[:60]!r}")

        text = (await client.read_resource("runbook://postgres"))[0].text
        print(f"  runbook://postgres -> {text.splitlines()[0]!r}")
        try:
            await client.read_resource("runbook://nginx")
        except Exception as exc:
            print(f"  runbook://nginx  -> {type(exc).__name__}: {str(exc).splitlines()[0][:80]}")


async def part_c_prompts_in_process() -> None:
    """Prompts are chosen by the USER before the task, and rendered by the server."""
    from M7_prompts.code.highlight import mcp as prompt_server

    print("\n=== C. prompts ===")
    async with Client(prompt_server) as client:
        prompts = await client.list_prompts()
        for prompt in prompts:
            args = {a.name: a.required for a in (prompt.arguments or [])}
            print(f"  {prompt.name:20} arguments={args}")

        rendered = await client.get_prompt("rca_over_logs",
                                           {"service": "postgres-ha", "window_minutes": 30})
        first_line = rendered.messages[0].content.text.splitlines()[0]
        print(f"  get_prompt -> {first_line[:80]!r}")

        steps = await client.get_prompt("dns_lookup_failure", {"hostname": "git.drlinuxer.com"})
        print(f"  dns_lookup_failure -> {len(steps.messages)} messages (one per step)")


async def main() -> None:
    await part_a_tools_over_stdio()
    await part_b_resources_in_process()
    await part_c_prompts_in_process()
    print("\n=== the whole lesson, in one line ===")
    print("  list_* -> choose -> call_tool. No model. The model is only one possible chooser.")


if __name__ == "__main__":
    asyncio.run(main())
