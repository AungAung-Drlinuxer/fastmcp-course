"""LAB 8 — what a resource may RETURN, and what the client receives for each.

FastMCP does not require you to serialise anything yourself, but the choices are not
interchangeable: a dict becomes compact JSON, an int becomes the text "2", bytes become a
base64 BLOB, and a list of Pydantic models raises.

Run:
    uv run python -m M6_resources.code.lab_8_return_shapes
"""
from __future__ import annotations

import asyncio

from fastmcp import Client, FastMCP
from pydantic import BaseModel

mcp = FastMCP("lab8-return-shapes")


class Host(BaseModel):
    name: str
    role: str
    cpu: int


@mcp.resource("shape://str", mime_type="text/plain")
def as_str() -> str:
    """A plain string is returned verbatim."""
    return "line one\nline two\n"


@mcp.resource("shape://dict", mime_type="application/json")
def as_dict() -> dict:
    """A dict is serialised to JSON by FastMCP."""
    return {"hosts": ["pve01"], "count": 1}


@mcp.resource("shape://list", mime_type="application/json")
def as_list() -> list[str]:
    """A list of strings is serialised to a JSON array."""
    return ["pve01", "kasm-agent1"]


@mcp.resource("shape://int", mime_type="text/plain")
def as_int() -> int:
    """An int becomes its own text representation."""
    return 2


@mcp.resource("shape://bytes", mime_type="image/png")
def as_bytes() -> bytes:
    """Bytes become a base64 blob, and the item loses `.text`."""
    return b"\x89PNG\r\n\x1a\nlab8"


@mcp.resource("shape://models", mime_type="application/json")
def as_models() -> list[Host]:
    """A list of Pydantic models — the shape that FAILS. Kept for contrast."""
    return [Host(name="pve01", role="hypervisor", cpu=72)]


@mcp.resource("shape://async", mime_type="text/plain")
async def as_async() -> str:
    """An async function is allowed."""
    await asyncio.sleep(0)
    return "async resource ok"


@mcp.resource("shape://default")
def as_default() -> str:
    """No mime_type given — the server fills in a default. Students ask what it is."""
    return "no mime_type declared"


@mcp.resource("shape://mismatch", mime_type="application/json")
def as_mismatch() -> str:
    """Claims JSON, returns prose. Nothing validates the claim — that is the point."""
    return "this is not JSON at all"


URIS = ("shape://str", "shape://dict", "shape://list", "shape://int",
        "shape://bytes", "shape://models", "shape://async", "shape://default",
        "shape://mismatch")


async def main() -> None:
    async with Client(mcp) as client:
        print("=== every registered URI ===")
        print("  ", [str(r.uri) for r in await client.list_resources()])

        for uri in URIS:
            try:
                item = (await client.read_resource(uri))[0]
                kind = type(item).__name__
                if hasattr(item, "text"):
                    print(f"  {uri:18} {kind:22} mime={item.mime_type:16} "
                          f"text={item.text!r}")
                else:
                    print(f"  {uri:18} {kind:22} mime={item.mime_type:16} "
                          f"blob={item.blob!r}")
            except Exception as exc:
                print(f"  {uri:18} {type(exc).__name__}: {str(exc).splitlines()[0][:70]}")

        print("\n=== the rule that follows ===")
        print("  return dict/list of PRIMITIVES for JSON; str for text; bytes for binary.")
        print("  for a list of models, return [m.model_dump() for m in models].")


if __name__ == "__main__":
    asyncio.run(main())
