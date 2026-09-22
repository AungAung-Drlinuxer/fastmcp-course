"""LAB 2 — the four capabilities are listed SEPARATELY, and a template is not a resource.

Run:
    uv run python -m M0_orientation.code.lab_2_four_surfaces
"""
from __future__ import annotations

import asyncio

from fastmcp import Client, FastMCP

mcp = FastMCP("lab-2")


@mcp.tool
def ping() -> str:
    """Return a fixed string, to prove the round trip works."""
    return "pong"


@mcp.resource("config://host")
def host_config() -> str:
    """A fixed document addressed by one URI."""
    return "host: pve01\nrole: hypervisor\n"


@mcp.resource("runbook://{service}")
def runbook(service: str) -> str:
    """A document per service, addressed by a URI TEMPLATE.

    Args:
        service: The service name.
    """
    return f"# {service} runbook\n"


@mcp.prompt
def analyse(symptom: str) -> str:
    """Guide an analysis of a symptom.

    Args:
        symptom: What the user observed.
    """
    return f"Analyse this symptom step by step: {symptom}"


async def main() -> None:
    async with Client(mcp) as client:
        print("tools             :", [t.name for t in await client.list_tools()])
        print("resources         :", [str(r.uri) for r in await client.list_resources()])
        print("resource_templates:", [t.uri_template for t in await client.list_resource_templates()])
        print("prompts           :", [p.name for p in await client.list_prompts()])

        print("\n=== why a template is NOT a resource ===")
        print("  config://host appeared in resources — it is ONE fixed URI.")
        print("  runbook://{service} appeared in TEMPLATES only — it is a PATTERN, and")
        print("  runbook://postgres and runbook://redis are two different URIs from it.")
        print("  A client that lists only resources never learns the runbooks exist.")


if __name__ == "__main__":
    asyncio.run(main())
