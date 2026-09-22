"""LAB 4 — the enumeration trap: a template is NOT a resource.

This lab is deliberately built to make the trap visible:
    - this server has ZERO static resources  -> list_resources() returns []
    - it has one template                    -> list_resource_templates() returns it
    - the attribute is `uri_template`        -> `.uriTemplate` raises AttributeError

Run:
    uv run python -m M6_resources.code.lab_4_enumeration_trap
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from fastmcp import Client, FastMCP

mcp = FastMCP("lab4-enumeration")

LAB_DATA = Path(__file__).with_name("lab_data")
LAB_DATA.mkdir(exist_ok=True)

(LAB_DATA / "nginx.md").write_text("# nginx runbook\n", encoding="utf-8")


@mcp.resource("runbook://{service}", mime_type="text/markdown")
def runbook(service: str) -> str:
    """The runbook for a named service.

    Args:
        service: The service whose runbook to read.
    """
    path = LAB_DATA / f"{service}.md"
    if not path.is_file():
        available = sorted(p.stem for p in LAB_DATA.glob("*.md"))
        raise FileNotFoundError(
            f"no runbook for {service!r}; available: {', '.join(available) or 'none'}")
    return path.read_text(encoding="utf-8")


async def main() -> None:
    print("=== server side: what is registered ===")
    print("  list_resources()        ->", await mcp.list_resources())
    templates = await mcp.list_resource_templates()
    print("  list_resource_templates() ->", len(templates), "template(s)")
    for template in templates:
        print("   object type :", type(template).__name__)
        print("   uri_template:", template.uri_template)
        print("   mime_type   :", template.mime_type)
        print("   name        :", template.name)
        # The template variables become a JSON Schema, exactly like a tool's parameters.
        print("   parameters  :", template.parameters)
        # `matches` is a server-side helper that answers "would this URI hit me?".
        for probe in ("runbook://nginx", "runbook://a/b"):
            print(f"   matches({probe!r}) ->", template.matches(probe))

    print("\n=== the attribute name that no longer works (2.x tutorials use it) ===")
    template = templates[0]
    try:
        print("  ", template.uriTemplate)
    except AttributeError as exc:
        print(f"  AttributeError: {exc}")

    print("\n=== client side: the same two calls ===")
    async with Client(mcp) as client:
        resources = await client.list_resources()
        client_templates = await client.list_resource_templates()
        print("  list_resources()          ->", resources)
        print("  list_resource_templates() ->",
              [t.uri_template for t in client_templates])

        print("\n=== but the template still READS fine ===")
        text = (await client.read_resource("runbook://nginx"))[0].text
        print("  runbook://nginx ->", repr(text))

        print("\n=== proof that the enumerations are disjoint ===")
        static_uris = {str(r.uri) for r in resources}
        template_uris = {t.uri_template for t in client_templates}
        print("  a template URI is never in list_resources():",
              "runbook://{service}" not in static_uris)
        print("  and no template equals a concrete URI:",
              "runbook://nginx" not in template_uris)


if __name__ == "__main__":
    asyncio.run(main())
