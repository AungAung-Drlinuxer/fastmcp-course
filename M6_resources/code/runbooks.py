"""Lesson 2.3 — resources: read-only data the client can enumerate.

The distinction that matters: a TOOL does something and is chosen by the model; a RESOURCE
is something that exists and can be read by reference. A runbook is a resource. Restarting a
service is a tool. Mixing them is the most common design mistake in first MCP servers.

This file ships both kinds, plus a URI template, and shows what a client sees for each.

Run:
    uv run python -m M6_resources.code.runbooks
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastmcp import Client, FastMCP

mcp = FastMCP("runbooks")

DATA = Path(__file__).with_name("data")
DATA.mkdir(exist_ok=True)

# Seed a couple of files so the lesson runs anywhere. In a real server these would be the
# operator's own runbooks, mounted read-only.
(DATA / "postgres.md").write_text(
    "# PostgreSQL runbook\n\n1. `cnpg status postgres-ha`\n2. check replication lag\n"
    "3. failover only after confirming synchronous_standby_names\n", encoding="utf-8")
(DATA / "redis.md").write_text(
    "# Redis runbook\n\n1. `redis-cli -a *** info replication`\n2. confirm sentinel quorum\n",
    encoding="utf-8")
(DATA / "inventory.json").write_text(json.dumps(
    {"hosts": [{"name": "pve01", "role": "hypervisor", "cpu": 72},
               {"name": "kasm-agent1", "role": "lab-agent", "cpu": 16}]}, indent=2),
    encoding="utf-8")


# --- a STATIC resource: one fixed document ----------------------------------------------
@mcp.resource("inventory://hosts", mime_type="application/json")
def host_inventory() -> dict:
    """The current host inventory, as structured data."""
    return json.loads((DATA / "inventory.json").read_text(encoding="utf-8"))


# --- a URI TEMPLATE: one resource per service, discovered from the URI -------------------
@mcp.resource("runbook://{service}", mime_type="text/markdown")
def runbook(service: str) -> str:
    """The runbook for a named service.

    Args:
        service: The service whose runbook to read, e.g. 'postgres'.
    """
    path = DATA / f"{service}.md"
    if not path.is_file():
        # A resource MUST return something readable or raise clearly. Silently returning ""
        # looks to the model like "this runbook is empty", which is worse than "unknown".
        available = sorted(p.stem for p in DATA.glob("*.md"))
        raise FileNotFoundError(
            f"no runbook for {service!r}; available: {', '.join(available) or 'none'}")
    return path.read_text(encoding="utf-8")


async def main() -> None:
    print("=== what the client can enumerate ===")
    async with Client(mcp) as client:
        resources = await client.list_resources()
        templates = await client.list_resource_templates()
        print("  static resources  :", [str(r.uri) for r in resources])
        # NOTE for 4.x: the attribute is snake_case. It was `uriTemplate` in 2.x.
        print("  uri templates     :", [t.uri_template for t in templates])

        print("\n=== reading a static resource ===")
        inv = await client.read_resource("inventory://hosts")
        print(" ", str(inv[0].text)[:120].replace("\n", " "))

        print("\n=== reading through the template ===")
        for service in ("postgres", "redis"):
            text = (await client.read_resource(f"runbook://{service}"))[0].text
            print(f"  runbook://{service}  -> {text.splitlines()[0]}")

        print("\n=== and what happens for an unknown one ===")
        try:
            await client.read_resource("runbook://nginx")
        except Exception as exc:
            print(f"  {type(exc).__name__}: {str(exc).splitlines()[0][:100]}")

    print("\n=== resource or tool? ===")
    for label, verdict in [
        ("a runbook", "resource — it exists; read it by URI"),
        ("the host inventory", "resource — structured, read-only"),
        ("restart a service", "tool — it changes state"),
        ("search the wiki", "tool — it takes a query and returns a result set"),
        ("the current cluster version", "resource if it is cheap and fixed; tool if it costs a call"),
    ]:
        print(f"  {label:26} {verdict}")


if __name__ == "__main__":
    asyncio.run(main())
