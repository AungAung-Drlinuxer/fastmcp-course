"""M5_tools LAB 5 — the search -> enumerate -> fetch trio, end to end.

One question ("what does this article say about adoption?") becomes three narrow tools. The
agent does the joining; each tool does exactly one thing. `--offline` skips the network so the
output below is reproducible in an air-gapped lab.

Run:
    uv run python -m M5_tools.code.lab_5_tool_trio --offline
    uv run python -m M5_tools.code.lab_5_tool_trio              # live if the network is up
"""
from __future__ import annotations

import asyncio
import json
import sys
from typing import Any

import httpx
from fastmcp import Client, FastMCP

mcp = FastMCP("lab5-tool-trio")

API = "https://en.wikipedia.org/w/api.php"
TIMEOUT = 8.0
OFFLINE = "--offline" in sys.argv
MAX_CHARS = 1200

FIXTURES: dict[str, Any] = {
    "search": {"query": {"search": [
        {"title": "Model Context Protocol", "snippet": "An open standard ..."},
        {"title": "JSON-RPC", "snippet": "A remote procedure call protocol ..."},
    ]}},
    "sections": {"parse": {"sections": [
        {"index": "1", "line": "Background", "level": "2"},
        {"index": "2", "line": "Features", "level": "2"},
        {"index": "3", "line": "Adoption", "level": "2"},
    ]}},
    "content": {"parse": {"title": "Model Context Protocol",
                          "wikitext": {"*": "Adoption of the Model Context Protocol has grown "
                                            "since 2024, with editor and IDE integrations.\n"
                                            "== Background ==\n"
                                            "Introduced in November 2024 as an open standard.\n"
                                            "== Features ==\n"
                                            "JSON-RPC 2.0 messages, resources, prompts, tools.\n"
                                            "== Adoption ==\n"
                                            "Editor and IDE integrations followed through 2025."}}},
}


async def _call_api(params: dict[str, str]) -> dict:
    """One place that knows how to talk to the upstream, and how to fail honestly."""
    if OFFLINE:
        raise httpx.ConnectError("offline mode requested")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(API, params=params,
                                    headers={"User-Agent": "fastmcp-course/0.1 (lab 5)"})
        response.raise_for_status()
        return {"source": "live", "payload": response.json()}


async def _with_fallback(params: dict[str, str], key: str) -> dict:
    try:
        return await _call_api(params)
    except Exception as exc:  # noqa: BLE001 — being offline is a normal condition in a lab
        return {"source": "fixture", "payload": FIXTURES[key],
                "note": f"{type(exc).__name__}: served a fixture"}


@mcp.tool
async def search_articles(query: str, limit: int = 5) -> dict:
    """Search Wikipedia and return matching article titles only.

    Args:
        query: What to search for.
        limit: Maximum number of results, 1-20.
    """
    limit = max(1, min(20, limit))
    result = await _with_fallback({"action": "query", "list": "search", "format": "json",
                                   "srsearch": query, "srlimit": str(limit)}, "search")
    if "error" in result["payload"]:
        return {"ok": False, "source": result["source"], "error": "upstream_error",
                "hint": "The upstream rejected the query; simplify it and try again."}
    hits = result["payload"].get("query", {}).get("search", [])
    return {"ok": True, "source": result["source"], "note": result.get("note"),
            "count": len(hits), "results": [{"title": h.get("title")} for h in hits]}


@mcp.tool
async def list_sections(article: str) -> dict:
    """List the section headings of one article.

    Args:
        article: The exact article title.
    """
    result = await _with_fallback({"action": "parse", "page": article, "prop": "sections",
                                   "format": "json"}, "sections")
    if "error" in result["payload"]:
        return {"ok": False, "source": result["source"], "error": "missing_title",
                "hint": f"No article named '{article}'. Run search_articles first and use a "
                        "title it returned, exactly as it was returned."}
    sections = result["payload"].get("parse", {}).get("sections", [])
    return {"ok": True, "source": result["source"], "note": result.get("note"),
            "article": article, "count": len(sections),
            "sections": [{"index": s.get("index"), "title": s.get("line"),
                          "level": s.get("level")} for s in sections]}


async def _content(article: str) -> dict:
    """The fetch logic for get_content, in a plain async function so other tools can reuse it."""
    result = await _with_fallback({"action": "parse", "page": article, "prop": "wikitext",
                                   "format": "json"}, "content")
    if "error" in result["payload"]:
        return {"ok": False, "source": result["source"], "error": "missing_title",
                "hint": f"No article named '{article}'."}
    parse = result["payload"].get("parse", {})
    raw = parse.get("wikitext", "")
    text = raw.get("*", "") if isinstance(raw, dict) else (raw or "")
    return {"ok": True, "source": result["source"], "note": result.get("note"),
            "title": parse.get("title", article), "length": len(text),
            "truncated": len(text) > MAX_CHARS, "content": text[:MAX_CHARS]}


@mcp.tool
async def get_content(article: str) -> dict:
    """Fetch the wikitext of one article, truncated to a context-friendly size.

    Args:
        article: The exact article title.
    """
    return await _content(article)


@mcp.tool
async def read_section(article: str, heading: str) -> dict:
    """Fetch only the paragraphs under one heading.

    Args:
        article: The exact article title.
        heading: The section heading, as list_sections returned it.
    """
    full = await _content(article)
    if not full["ok"]:
        return full
    text = full["content"]
    marker = f"== {heading} =="
    if marker not in text:
        return {"ok": False, "source": full["source"], "error": "unknown_section",
                "hint": f"'{heading}' is not in the first {MAX_CHARS} characters. Call "
                        f"list_sections('{article}') and use one of the headings it returned."}
    body = text.split(marker, 1)[1]
    body = body.split("==", 1)[0].strip()
    return {"ok": True, "source": full["source"], "article": article, "heading": heading,
            "chars": len(body), "text": body[:400]}


async def main() -> None:
    print("mode:", "OFFLINE (fixtures only)" if OFFLINE else "live-with-fixture-fallback")
    async with Client(mcp) as client:
        print("\n=== step 1: search ===")
        found = await client.call_tool("search_articles", {"query": "model context protocol"})
        print(json.dumps(found.data, indent=2)[:420])

        print("\n=== step 2: enumerate the sections of the first hit ===")
        title = found.data["results"][0]["title"]
        listed = await client.call_tool("list_sections", {"article": title})
        print(json.dumps(listed.data, indent=2)[:420])

        print("\n=== step 3: fetch only what was asked for ===")
        section = await client.call_tool("read_section",
                                         {"article": title, "heading": "Adoption"})
        print(json.dumps(section.data, indent=2)[:360])

        print("\n=== the hint path: asking for a section that does not exist ===")
        missing = await client.call_tool("read_section",
                                         {"article": title, "heading": "Funding"})
        print(json.dumps(missing.data, indent=2))
        print(f"is_error={missing.is_error}   <- still data, still actionable")


if __name__ == "__main__":
    asyncio.run(main())
