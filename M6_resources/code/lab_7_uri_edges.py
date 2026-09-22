"""LAB 7 — URI edges: what the router accepts and what it refuses.

Every line here was measured, because this is the class of behaviour students guess at:
    - is the authority case-insensitive?          (yes)
    - is the scheme case-insensitive?             (yes — but the PATH is not)
    - does a trailing slash work?                 (no)
    - does a query string work?                   (no — it is not part of the path)
    - can a template variable contain a slash?    (no — the URI is mapped to one segment)

Run:
    uv run python -m M6_resources.code.lab_7_uri_edges
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from fastmcp import Client, FastMCP

mcp = FastMCP("lab7-uri-edges")

LAB_DATA = Path(__file__).with_name("lab_data")
LAB_DATA.mkdir(exist_ok=True)
(LAB_DATA / "postgres.md").write_text("# PostgreSQL runbook\n", encoding="utf-8")


@mcp.resource("config://motd", mime_type="text/plain")
def motd() -> str:
    """A static resource whose URI is completely fixed."""
    return "lab7 motd\n"


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


CASES = [
    ("runbook://postgres", "the exact URI"),
    ("runbook://POSTGRES", "authority in upper case"),
    ("runbook://postgres/", "trailing slash"),
    ("config://motd?x=1", "a query string"),
    ("CONFIG://motd", "scheme in upper case"),
    ("runbook://nginx/sub/page", "extra path segment"),
    ("runbook://..%2F..%2Fetc%2Fpasswd", "percent-encoded traversal"),
    ("config://MOTD", "path in upper case"),
]


async def main() -> None:
    async with Client(mcp) as client:
        print("=== URI edges, measured ===")
        for uri, why in CASES:
            try:
                text = (await client.read_resource(uri))[0].text
                print(f"  {uri:34} OK    {text.splitlines()[0][:34]!r}")
            except Exception as exc:
                print(f"  {uri:34} FAIL  {type(exc).__name__}: "
                      f"{str(exc).splitlines()[0][:60]}")
            print(f"  {'':34}       ({why})")

        print("\n=== what the router CAN match, listed by the server ===")
        for template in await client.list_resource_templates():
            print(f"  {template.uri_template}")

        print("\n=== the practical rule ===")
        print("  build URIs in ONE place, lower case, no trailing slash, no query:")
        for service in ("postgres",):
            print("   ", f"runbook://{service}")


if __name__ == "__main__":
    asyncio.run(main())
