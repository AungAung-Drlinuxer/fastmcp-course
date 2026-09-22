"""M5_tools LAB 10 — truncation at the tool boundary, made measurable.

A tool that returns a 150 KB article has not returned an answer; it has spent the model's
context on a wall of text. This lab fetches a long document through three tools and shows the
numbers that decide the design: what the document really costs, what fits, and how the caller
learns that something was cut.

Run:
    uv run python -m M5_tools.code.lab_10_truncation_budget
"""
from __future__ import annotations

import asyncio
import json

from fastmcp import Client, FastMCP

mcp = FastMCP("lab10-truncation-budget")

# A stand-in for a 200 KB article: deterministic, so the numbers below never drift.
PARAGRAPH = ("The protocol defines a transport-agnostic message layer. "
             "Clients discover tools, resources and prompts at runtime. ")
DOCUMENT = PARAGRAPH * 1200                       # 1200 * 112 chars
BUDGET = 2000                                     # the tool's own ceiling, in characters

# Rough planning figure used by many hosts: ~4 characters per token for English text.
CHARS_PER_TOKEN = 4


@mcp.tool
def get_document_untruncated() -> dict:
    """Return the whole document — the tool that floods the context window."""
    return {"ok": True, "length": len(DOCUMENT), "content": DOCUMENT}


@mcp.tool
def get_document_window(offset: int = 0, limit: int = BUDGET) -> dict:
    """Return one window of the document, saying exactly which window it is.

    Args:
        offset: Character offset to start from.
        limit: Maximum characters to return, 200-4000.
    """
    offset = max(0, offset)
    limit = max(200, min(4000, limit))
    window = DOCUMENT[offset:offset + limit]
    end = offset + len(window)
    return {
        "ok": True,
        "length": len(DOCUMENT),
        "offset": offset,
        "returned": len(window),
        "truncated": end < len(DOCUMENT),
        "next_offset": end if end < len(DOCUMENT) else None,
        "content": window,
    }


@mcp.tool
def get_document_stats() -> dict:
    """Return only the shape of the document: no content at all."""
    return {"ok": True, "length": len(DOCUMENT),
            "estimated_tokens": len(DOCUMENT) // CHARS_PER_TOKEN,
            "paragraphs": DOCUMENT.count("The protocol"),
            "hint": "Call get_document_window(offset=..., limit=...) for the text you need."}


def estimate_tokens(chars: int) -> int:
    """A planning estimate, good enough to decide whether a payload fits."""
    return chars // CHARS_PER_TOKEN


async def main() -> None:
    print("=== the document, before any tool is involved ===")
    print(f"    characters       {len(DOCUMENT)}")
    print(f"    estimated tokens {estimate_tokens(len(DOCUMENT))}")

    async with Client(mcp) as client:
        print("\n=== the untruncated tool: what the caller receives ===")
        flood = await client.call_tool("get_document_untruncated", {})
        payload = json.dumps(flood.data)
        print(f"    characters on the wire   {len(payload)}")
        print(f"    estimated tokens         {estimate_tokens(len(payload))}")
        print(f"    compact tool budget      {BUDGET}")

        print("\n=== the windowed tool: the same document, in a size that fits ===")
        first = await client.call_tool("get_document_window", {})
        print(f"    offset={first.data['offset']} returned={first.data['returned']} "
              f"truncated={first.data['truncated']} next_offset={first.data['next_offset']}")

        second = await client.call_tool("get_document_window",
                                        {"offset": first.data["next_offset"]})
        print(f"    offset={second.data['offset']} returned={second.data['returned']} "
              f"truncated={second.data['truncated']} next_offset={second.data['next_offset']}")

        print("\n=== an untrusted caller asks for everything at once ===")
        huge = await client.call_tool("get_document_window", {"limit": 10_000_000})
        print(f"    limit=10000000 was clamped to {huge.data['returned']} characters "
              f"(truncated={huge.data['truncated']})")
        tiny = await client.call_tool("get_document_window", {"limit": 1})
        print(f"    limit=1 was clamped to {tiny.data['returned']} characters")
        negative = await client.call_tool("get_document_window", {"offset": -500})
        print(f"    offset=-500 was clamped to {negative.data['offset']}")

        print("\n=== the cheapest tool of all: statistics, no content ===")
        stats = await client.call_tool("get_document_stats", {})
        print(json.dumps(stats.data, indent=2))

        print("\n=== the arithmetic that decides the design ===")
        print(f"    whole document   {estimate_tokens(len(DOCUMENT)):6} tokens")
        print(f"    one window       {estimate_tokens(BUDGET):6} tokens")
        print(f"    windows needed   {-(-len(DOCUMENT) // BUDGET):6} (before the caller gives up)")


if __name__ == "__main__":
    asyncio.run(main())
