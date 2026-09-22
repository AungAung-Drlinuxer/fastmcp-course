"""LAB 1 — inventory the capstone's surface before you trust a single value from it.

A production server is judged on what it DECLARES, not on what it is documented to do. This lab
asks the running server for its own inventory over MCP, so the answer cannot drift from the code
the way a README does.

Two things to watch, both verified against fastmcp 4.0.5:

  * the schema of a tool read on the SERVER side lives at `.parameters`
  * the schema of the same tool read through a CLIENT lives at `.input_schema`

`read_log.parameters` has no `required` key for a tool with no arguments at all (it is `None`),
and `required: ['name']` for a tool with one mandatory argument. Never hand-write that table.

Run:
    uv run python -m M11_capstone.code.lab_1_surface_probe
"""
from __future__ import annotations

import asyncio
import json

from fastmcp import Client

from M11_capstone.code.devops_assistant import mcp


async def main() -> None:
    async with Client(mcp) as client:
        print("=== 1. tools, with the arguments each one REQUIRES ===")
        tools = await client.list_tools()
        for tool in tools:
            schema = tool.input_schema
            required = schema.get("required") or []
            optional = sorted(set(schema.get("properties", {})) - set(required))
            print(f"  {tool.name:16} required={required} optional={optional}")
        print(f"  -- {len(tools)} tools")

        print("\n=== 2. the same schema, read from the server side ===")
        server_side = await mcp.list_tools()
        read_log = next(t for t in server_side if t.name == "read_log")
        # client objects expose `.input_schema`; server objects expose `.parameters`.
        print(f"  server object type      : {type(read_log).__name__}")
        print(f"  has .parameters         : {hasattr(read_log, 'parameters')}")
        print(f"  has .input_schema       : {hasattr(read_log, 'input_schema')}")
        print("  .parameters (verbatim)  :")
        print(json.dumps(read_log.parameters, indent=2))

        print("=== 3. resources and resource TEMPLATES are different lists ===")
        print(f"  list_resources()            -> {await client.list_resources()}")
        for template in await client.list_resource_templates():
            print(f"  list_resource_templates()   -> uri_template={template.uri_template!r} "
                  f"mime_type={template.mime_type}")

        print("\n=== 4. prompts, with the arguments they accept ===")
        for prompt in await client.list_prompts():
            names = [arg.name for arg in (prompt.arguments or [])]
            print(f"  {prompt.name:16} args={names}")

        print("\n=== 5. the verdict ===")
        expected_tools = {"system_metrics", "list_logs", "read_log", "list_runbooks",
                          "restart_service"}
        actual_tools = {t.name for t in tools}
        expected_templates = {"config://{host}", "runbook://{name}"}
        actual_templates = {t.uri_template for t in await client.list_resource_templates()}
        expected_prompts = {"rca_error_log", "capacity_review"}
        actual_prompts = {p.name for p in await client.list_prompts()}

        ok = (expected_tools <= actual_tools
              and expected_templates <= actual_templates
              and expected_prompts <= actual_prompts)
        print(f"  tools     missing={sorted(expected_tools - actual_tools)}")
        print(f"  templates missing={sorted(expected_templates - actual_templates)}")
        print(f"  prompts   missing={sorted(expected_prompts - actual_prompts)}")
        print(f"  verdict   {'COMPLETE' if ok else 'INCOMPLETE'}")


if __name__ == "__main__":
    asyncio.run(main())
