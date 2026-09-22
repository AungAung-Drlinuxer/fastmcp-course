"""LAB 1 — a static text resource: one URI, one document, no arguments.

Two static resources, both `text/plain`:
    config://motd                 computed in Python, not on disk
    config://nginx/site-enabled   read from a real .txt file

Run:
    uv run python -m M6_resources.code.lab_1_static_text
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from fastmcp import Client, FastMCP

mcp = FastMCP("lab1-static-text")

# The anchor for every file this lab touches. `with_name` keeps the path relative to THIS
# file, so the lab works from any working directory.
LAB_DATA = Path(__file__).with_name("lab_data")
LAB_DATA.mkdir(exist_ok=True)

# Seed the file so the lab runs on a fresh checkout. In a real server this file is the
# operator's own config, mounted read-only.
(LAB_DATA / "site-enabled.txt").write_text(
    "server_name chat.drlinuxer.com;\n"
    "upstream api { server 10.0.0.11:8000; }\n"
    "listen 443 ssl;\n",
    encoding="utf-8",
)


# --- resource 1: computed, no file involved ----------------------------------------------
@mcp.resource("config://motd", mime_type="text/plain")
def motd() -> str:
    """The message of the day greeting, as plain text."""
    return "lab1: static resource, no arguments, no side effects\n"


# --- resource 2: file-backed, still static -----------------------------------------------
@mcp.resource("config://nginx/site-enabled", mime_type="text/plain")
def nginx_site() -> str:
    """The nginx site file this lab seeded, read verbatim from disk."""
    return (LAB_DATA / "site-enabled.txt").read_text(encoding="utf-8")


async def main() -> None:
    async with Client(mcp) as client:
        print("=== the client can enumerate both ===")
        for resource in await client.list_resources():
            print(f"  {str(resource.uri):32} {resource.mime_type:12} {resource.name}")

        print("\n=== reading config://motd ===")
        result = await client.read_resource("config://motd")
        print("  result type :", type(result).__name__)
        print("  len(result) :", len(result))
        print("  item type   :", type(result[0]).__name__)
        print("  mime_type   :", result[0].mime_type)
        print("  text        :", repr(result[0].text))
        print("  uri echoed  :", result[0].uri)

        print("\n=== reading config://nginx/site-enabled ===")
        nginx = await client.read_resource("config://nginx/site-enabled")
        for number, line in enumerate(nginx[0].text.splitlines(), 1):
            print(f"  {number}: {line}")

        print("\n=== reading a URI that is not registered ===")
        try:
            await client.read_resource("config://missing")
        except Exception as exc:
            print(f"  {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
