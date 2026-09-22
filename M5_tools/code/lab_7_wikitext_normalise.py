"""M5_tools LAB 7 — the wikitext shape trap: a string vs {"*": "..."} .

MediaWiki returns `wikitext` in two shapes. Code written for one shape produces
`TypeError: unhashable type: 'slice'` on the other, and that message names neither the field
nor the API. This lab reproduces the crash inside the tool, then normalises both shapes in one
line, and keeps the crash reproducible with a regression check.

Run:
    uv run python -m M5_tools.code.lab_7_wikitext_normalise
"""
from __future__ import annotations

import asyncio
import json
from typing import Any

from fastmcp import Client, FastMCP

mcp = FastMCP("lab7-wikitext-shape")

SMALL_PAGE = "Short {{Infobox}} page text."          # arrives as a plain string
LARGE_PAGE = {"*": "Long page text " * 40}           # arrives wrapped in a dict

# Both shapes, as the API really sends them.
PAYLOADS: dict[str, Any] = {
    "small": {"parse": {"title": "Small", "wikitext": SMALL_PAGE}},
    "large": {"parse": {"title": "Large", "wikitext": LARGE_PAGE}},
}


def wikitext_of(parse: dict) -> str:
    """Normalise both upstream shapes to a string. The whole fix is this one line."""
    raw = parse.get("wikitext", "")
    return raw.get("*", "") if isinstance(raw, dict) else (raw or "")


@mcp.tool
def get_text_naive(page: str) -> dict:
    """Slice the wikitext directly — correct for small pages, a TypeError for large ones.

    Args:
        page: Either 'small' or 'large'.
    """
    parse = PAYLOADS[page]["parse"]
    text = parse.get("wikitext", "")
    return {"ok": True, "title": parse.get("title"), "preview": text[:40]}  # crashes on dict


@mcp.tool
def get_text_safe(page: str) -> dict:
    """Slice the wikitext after normalising the shape.

    Args:
        page: Either 'small' or 'large'.
    """
    parse = PAYLOADS[page]["parse"]
    text = wikitext_of(parse)
    return {"ok": True, "title": parse.get("title"), "length": len(text),
            "shape": type(parse.get("wikitext")).__name__, "preview": text[:40]}


async def main() -> None:
    print("=== the two shapes, as the upstream sends them ===")
    for name, payload in PAYLOADS.items():
        raw = payload["parse"]["wikitext"]
        print(f"    {name:5} type={type(raw).__name__:5} "
              f"keys={list(raw) if isinstance(raw, dict) else 'n/a'}")

    print("\n=== the normaliser, checked directly (no server involved) ===")
    for name, payload in PAYLOADS.items():
        text = wikitext_of(payload["parse"])
        print(f"    {name:5} -> {len(text):4} chars, starts {text[:22]!r}")

    async with Client(mcp) as client:
        print("\n=== safe tool: both shapes, one code path ===")
        for page in PAYLOADS:
            result = await client.call_tool("get_text_safe", {"page": page})
            print(f"    {json.dumps(result.data)}")

        print("\n=== naive tool: the small page works, the large page raises ===")
        for page in PAYLOADS:
            result = await client.call_tool("get_text_naive", {"page": page},
                                            raise_on_error=False)
            if result.is_error:
                text = result.content[0].text if result.content else ""
                print(f"    {page:5} -> is_error=True  {text}")
            else:
                print(f"    {page:5} -> {json.dumps(result.data)}")

        print("\n=== the failure the student actually sees in the traceback ===")
        try:
            LARGE_PAGE[:10]
        except TypeError as exc:
            print(f"    TypeError: {exc}")
        print("    Nothing in that message says 'wikitext' or 'MediaWiki'. Normalise at the")
        print("    boundary, and the message never has to be read.")


if __name__ == "__main__":
    asyncio.run(main())
