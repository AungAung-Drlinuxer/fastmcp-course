"""Lesson 2.2 (part 2) — connecting a tool to a real external API.

Three tools over the Wikipedia REST API, which is the shape every integration lesson takes:
search -> enumerate -> fetch. The interesting engineering is not the HTTP call; it is what the
tool does when the network is unavailable, because an on-prem lab usually is.

Run:
    uv run python -m M5_tools.code.wikipedia                 # uses fixtures if offline
    uv run python -m M5_tools.code.wikipedia --live          # forces the real API
"""
from __future__ import annotations

import asyncio
import json
import sys
from typing import Any

import httpx
from fastmcp import Client, FastMCP

mcp = FastMCP("wikipedia")

API = "https://en.wikipedia.org/w/api.php"
TIMEOUT = 10.0
LIVE = "--live" in sys.argv

# Fixtures keep this lesson runnable in an air-gapped lab. A course that only works when the
# internet is up fails on the day the lab is isolated, so the fallback is part of the design —
# and it is also honest behaviour for a production tool facing a flaky upstream.
FIXTURES: dict[str, Any] = {
    "search": {"query": {"search": [
        {"title": "Model Context Protocol", "snippet": "An open standard for connecting AI..."},
        {"title": "JSON-RPC", "snippet": "A remote procedure call protocol encoded in JSON..."},
    ]}},
    "sections": {"parse": {"sections": [
        {"index": "1", "line": "History", "level": "2"},
        {"index": "2", "line": "Architecture", "level": "2"},
        {"index": "3", "line": "Adoption", "level": "2"},
    ]}},
    "content": {"parse": {"title": "Model Context Protocol",
                          "wikitext": "The Model Context Protocol (MCP) is an open standard..."}},
}


async def _get(params: dict[str, str], fixture_key: str) -> dict:
    """Call the API, or fall back to a fixture. Returns a wrapper so the caller can tell which."""
    if LIVE:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(API, params=params,
                                        headers={"User-Agent": "fastmcp-course/0.1"})
            response.raise_for_status()
            return {"source": "live", "payload": response.json()}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(API, params=params,
                                        headers={"User-Agent": "fastmcp-course/0.1"})
            response.raise_for_status()
            return {"source": "live", "payload": response.json()}
    except Exception as exc:  # noqa: BLE001 — offline is an expected condition here
        return {"source": "fixture", "payload": FIXTURES[fixture_key],
                "note": f"live call failed ({type(exc).__name__}); served a fixture"}


@mcp.tool
async def search_articles(query: str, limit: int = 5) -> dict:
    """Search Wikipedia and return matching article titles.

    Args:
        query: What to search for.
        limit: Maximum number of results, 1-20.
    """
    limit = max(1, min(20, limit))
    result = await _get(
        {"action": "query", "list": "search", "srsearch": query, "format": "json",
         "srlimit": str(limit)}, "search")
    hits = result["payload"].get("query", {}).get("search", [])
    return {
        "ok": True,
        "source": result["source"],
        "note": result.get("note"),
        "count": len(hits),
        "results": [{"title": h.get("title")} for h in hits],
    }


@mcp.tool
async def list_sections(article: str) -> dict:
    """List the section headings of an article.

    Args:
        article: The exact article title, e.g. 'Model Context Protocol'.
    """
    result = await _get({"action": "parse", "page": article, "prop": "sections",
                         "format": "json"}, "sections")
    sections = result["payload"].get("parse", {}).get("sections", [])
    return {
        "ok": True,
        "source": result["source"],
        "note": result.get("note"),
        "article": article,
        "count": len(sections),
        "sections": [{"index": s.get("index"), "title": s.get("line"),
                      "level": s.get("level")} for s in sections],
    }


@mcp.tool
async def get_content(article: str) -> dict:
    """Fetch the raw wikitext of an article.

    Args:
        article: The exact article title.
    """
    result = await _get({"action": "parse", "page": article, "prop": "wikitext",
                         "format": "json"}, "content")
    parse = result["payload"].get("parse", {})
    # MediaWiki returns `wikitext` in two shapes depending on the request: a plain string when
    # the content is small, and `{"*": "..."}` when it is not. Handling only one of them gives
    # `TypeError: unhashable type: 'slice'` the first time a long article is fetched — an error
    # that says nothing about the real cause.
    raw_text = parse.get("wikitext", "")
    text = raw_text.get("*", "") if isinstance(raw_text, dict) else (raw_text or "")
    # Truncation is a real design decision: a 200 KB article will not fit a context window,
    # and a tool that returns it anyway makes the model fail further downstream. Truncate at
    # the tool boundary and SAY that you truncated.
    limit = 4000
    return {
        "ok": True,
        "source": result["source"],
        "note": result.get("note"),
        "title": parse.get("title", article),
        "length": len(text),
        "truncated": len(text) > limit,
        "content": text[:limit],
    }


async def _registry() -> None:
    """List what the server publishes, without a client — useful while developing.

    Async on purpose: calling asyncio.run() here would raise "cannot be called from a running
    event loop", because main() is already inside one. A server method that is async must be
    awaited, not re-entered.
    """
    print("Registered tools:", [t.name for t in await mcp.list_tools()])


async def main() -> None:
    await _registry()
    print("mode:", "LIVE" if LIVE else "live-with-fixture-fallback", "\n")
    async with Client(mcp) as client:
        search = await client.call_tool("search_articles", {"query": "model context protocol"})
        print("=== search_articles ===")
        print(json.dumps(search.data, indent=2)[:600])

        sections = await client.call_tool("list_sections", {"article": "Model Context Protocol"})
        print("\n=== list_sections ===")
        print(json.dumps(sections.data, indent=2)[:500])

        content = await client.call_tool("get_content", {"article": "Model Context Protocol"})
        d = content.data
        print("\n=== get_content (truncated at the tool boundary) ===")
        print(f"  length={d['length']} truncated={d['truncated']}")
        print(f"  content={d['content'][:90]!r}")


if __name__ == "__main__":
    asyncio.run(main())
