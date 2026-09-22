"""A second self-test, written to show what the capstone's own one leaves out.

The capstone's `main()` prints the first line of each thing it reads. That is the right shape for
a smoke test, and it hides exactly the bugs a first-line-only view cannot see: the capstone's
`capacity_review` prompt has a literal `{host}` on its THIRD line, and no amount of first-line
printing would ever reveal it.

So this file checks five things the capstone's self-test does not:

  1. each tool's REQUIRED arguments, read from the CLIENT-side schema (`.input_schema`)
  2. every resource template with its mime type, not just the first line of one resource
  3. metrics as JSON, because JSON is what actually crosses the wire
  4. the three tool outcomes side by side: refusal, absence, and a guarded success
  5. BOTH prompts rendered in full, with their length and their first line

Run:
    uv run python -m M11_capstone.code.my_self_test
"""
from __future__ import annotations

import asyncio
import json

from fastmcp import Client

from M11_capstone.code.devops_assistant import mcp


async def main() -> None:
    async with Client(mcp) as client:
        print("=== 1. surface, with the ARGUMENTS of each tool ===")
        for tool in await client.list_tools():
            schema = tool.input_schema                      # client-side name, NOT .parameters
            required = schema.get("required") or []         # `or []` for the no-argument tools
            optional = sorted(set(schema.get("properties", {})) - set(required))
            print(f"  {tool.name:16} requires {str(required):22} optional {optional}")

        print("\n=== 2. every resource template, with its mime type ===")
        print(f"  static resources: {[str(r.uri) for r in await client.list_resources()]}")
        for template in await client.list_resource_templates():
            print(f"  {template.uri_template:22} {template.mime_type}")

        print("\n=== 3. metrics as JSON, because that is what the wire carries ===")
        print(json.dumps((await client.call_tool("system_metrics", {})).data, indent=2))

        print("\n=== 4. three tool outcomes side by side ===")
        for name, args in [("read_log", {"name": "../../etc/passwd"}),
                           ("read_log", {"name": "nope.log"}),
                           ("restart_service", {"service": "gitea", "reason": ""})]:
            data = (await client.call_tool(name, args)).data
            label = data.get("error") or data.get("status") or ""
            print(f"  {name:16} {str(args)[:36]:38} ok={str(data['ok']):5} {label}")
        print("  refusal -> path_not_allowed | absence -> not_found | ordinary -> would_restart")

        print("\n=== 5. BOTH prompts render in full — the step people skip ===")
        for prompt in await client.list_prompts():
            given = ({"log_name": "postgres-ha.log"} if prompt.name == "rca_error_log"
                     else {"host": "pve01"})
            text = (await client.get_prompt(prompt.name, given)).messages[0].content.text
            print(f"  {prompt.name:16} {len(text):4} chars, first line "
                  f"{text.splitlines()[0][:44]!r}")
            # Check for the class of bug the capstone actually has: a placeholder that was never
            # substituted because the line was not an f-string.
            leftover = [c for c in ("{host}", "{log_name}", "{name}") if c in text]
            print(f"  {'':16} leftover placeholders: {leftover or 'none'}")


if __name__ == "__main__":
    asyncio.run(main())
