"""LAB 2 — a static JSON resource: structured, read-only data behind one URI.

Two ways to answer with JSON, and they do NOT produce the same bytes:
    inventory://hosts     a dict returned from Python — FastMCP serialises it COMPACTLY
    inventory://hosts.txt the file's own text returned verbatim — pretty, indented

Run:
    uv run python -m M6_resources.code.lab_2_static_json
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastmcp import Client, FastMCP

mcp = FastMCP("lab2-static-json")

LAB_DATA = Path(__file__).with_name("lab_data")
LAB_DATA.mkdir(exist_ok=True)

(LAB_DATA / "inventory.json").write_text(
    json.dumps(
        {
            "hosts": [
                {"name": "pve01", "role": "hypervisor", "cpu": 72},
                {"name": "kasm-agent1", "role": "lab-agent", "cpu": 16},
            ]
        },
        indent=2,
    ),
    encoding="utf-8",
)


# --- shape 1: return the parsed data, let FastMCP serialise it ---------------------------
@mcp.resource("inventory://hosts", mime_type="application/json")
def host_inventory() -> dict:
    """The current host inventory, as structured data."""
    return json.loads((LAB_DATA / "inventory.json").read_text(encoding="utf-8"))


# --- shape 2: return the file text untouched ---------------------------------------------
@mcp.resource("inventory://hosts.txt", mime_type="application/json")
def host_inventory_pretty() -> str:
    """The same inventory, byte-for-byte as it is stored on disk."""
    return (LAB_DATA / "inventory.json").read_text(encoding="utf-8")


async def main() -> None:
    async with Client(mcp) as client:
        print("=== two URIs, both application/json ===")
        for resource in await client.list_resources():
            print(f"  {str(resource.uri):26} {resource.mime_type:18} {resource.description}")

        print("\n=== inventory://hosts (dict -> compact JSON) ===")
        compact = (await client.read_resource("inventory://hosts"))[0]
        print("  type :", type(compact).__name__, "| mime:", compact.mime_type)
        print("  text :", compact.text)
        data = json.loads(compact.text)
        print("  hosts:", [h["name"] for h in data["hosts"]])
        print("  total cpu:", sum(h["cpu"] for h in data["hosts"]))

        print("\n=== inventory://hosts.txt (file text -> pretty JSON) ===")
        pretty = (await client.read_resource("inventory://hosts.txt"))[0]
        print(pretty.text)

        print("=== the same JSON, different bytes ===")
        print("  compact bytes:", len(compact.text))
        print("  pretty  bytes:", len(pretty.text))
        print("  equal as data:", json.loads(compact.text) == json.loads(pretty.text))


if __name__ == "__main__":
    asyncio.run(main())
