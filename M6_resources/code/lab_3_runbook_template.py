"""LAB 3 — a URI template: one resource per service, discovered from the URI.

`runbook://{service}` is not one resource; it is a RULE for a family of them. The variable
name in the URI becomes the function parameter name, and the parameter's type hint becomes
the validation.

Run:
    uv run python -m M6_resources.code.lab_3_runbook_template
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from fastmcp import Client, FastMCP

mcp = FastMCP("lab3-runbook-template")

LAB_DATA = Path(__file__).with_name("lab_data")
LAB_DATA.mkdir(exist_ok=True)

(LAB_DATA / "nginx.md").write_text(
    "# nginx runbook\n\n1. `nginx -t` before any reload\n2. `systemctl reload nginx`\n",
    encoding="utf-8",
)
(LAB_DATA / "postgres.md").write_text(
    "# PostgreSQL runbook\n\n1. `cnpg status postgres-ha`\n2. check replication lag\n",
    encoding="utf-8",
)
(LAB_DATA / "kasm.md").write_text(
    "# Kasm Workspaces runbook\n\n1. `docker ps --filter name=kasm`\n2. drain, then restart\n",
    encoding="utf-8",
)


@mcp.resource("runbook://{service}", mime_type="text/markdown")
def runbook(service: str) -> str:
    """The runbook for a named service.

    Args:
        service: The service whose runbook to read, e.g. 'nginx'.
    """
    path = LAB_DATA / f"{service}.md"
    if not path.is_file():
        available = sorted(p.stem for p in LAB_DATA.glob("*.md"))
        raise FileNotFoundError(
            f"no runbook for {service!r}; available: {', '.join(available) or 'none'}")
    return path.read_text(encoding="utf-8")


# --- a second template, one variable typed as an integer ---------------------------------
@mcp.resource("kasm://{pool}/sessions/{count}", mime_type="text/plain")
def pool_sessions(pool: str, count: int) -> str:
    """A synthetic view of how many sessions a pool may hold.

    Args:
        pool: The Kasm pool name.
        count: How many sessions to report on.
    """
    return f"pool={pool} count={count} (count arrived as {type(count).__name__})"


async def main() -> None:
    async with Client(mcp) as client:
        print("=== static resources (expect none) ===")
        print("  ", [str(r.uri) for r in await client.list_resources()])

        print("\n=== templates (two of them) ===")
        for template in await client.list_resource_templates():
            print(f"  {template.uri_template:34} {template.mime_type}")

        print("\n=== reading through the template ===")
        for service in ("nginx", "postgres", "kasm"):
            text = (await client.read_resource(f"runbook://{service}"))[0].text
            print(f"  runbook://{service:9} -> {text.splitlines()[0]}")

        print("\n=== the typed variable ===")
        print("  ", (await client.read_resource("kasm://default/sessions/12"))[0].text)

        print("\n=== a value the type hint rejects ===")
        try:
            await client.read_resource("kasm://default/sessions/many")
        except Exception as exc:
            print(f"  {type(exc).__name__}: {str(exc).splitlines()[0][:110]}")

        print("\n=== a service with no runbook ===")
        try:
            await client.read_resource("runbook://oracle")
        except Exception as exc:
            print(f"  {type(exc).__name__}: {str(exc).splitlines()[0][:140]}")

        print("\n=== a URI that no template matches ===")
        try:
            await client.read_resource("runbook://nginx/sub/page")
        except Exception as exc:
            print(f"  {type(exc).__name__}: {str(exc).splitlines()[0][:110]}")


if __name__ == "__main__":
    asyncio.run(main())
