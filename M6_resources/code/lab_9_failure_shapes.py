"""LAB 9 — failing loudly versus failing silently: the four outcomes of a read.

A resource can fail in four distinct ways, and they are NOT equally useful:

    1. unknown URI          -> MCPError: Resource not found: '...'      (router, before your code)
    2. missing file, raises -> MCPError: Error reading resource '...': no runbook for ...
    3. returns ""           -> SUCCESS with empty text — the silent failure
    4. raises a custom error -> whatever message you chose, wrapped

Case 3 is the dangerous one: the model reads an empty string as "this runbook is empty"
and moves on. Case 2 gives the model something it can act on.

Run:
    uv run python -m M6_resources.code.lab_9_failure_shapes
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from fastmcp import Client, FastMCP

mcp = FastMCP("lab9-failure-shapes")

LAB_DATA = Path(__file__).with_name("lab_data")
LAB_DATA.mkdir(exist_ok=True)
(LAB_DATA / "postgres.md").write_text("# PostgreSQL runbook\n", encoding="utf-8")


# --- 1. the correct pattern: check, then raise with the available names -------------------
@mcp.resource("loud://{service}", mime_type="text/markdown")
def loud(service: str) -> str:
    """The runbook for a named service; missing ones raise with the available list.

    Args:
        service: The service whose runbook to read.
    """
    path = LAB_DATA / f"{service}.md"
    if not path.is_file():
        available = sorted(p.stem for p in LAB_DATA.glob("*.md"))
        raise FileNotFoundError(
            f"no runbook for {service!r}; available: {', '.join(available) or 'none'}")
    return path.read_text(encoding="utf-8")


# --- 2. the WRONG pattern, kept for contrast ---------------------------------------------
@mcp.resource("silent://{service}", mime_type="text/markdown")
def silent(service: str) -> str:
    """Same idea, but a missing runbook returns an empty string. Never ship this.

    Args:
        service: The service whose runbook to read.
    """
    path = LAB_DATA / f"{service}.md"
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


# --- 3. a custom exception type, to see what survives the wire ---------------------------
class RunbookUnavailable(RuntimeError):
    """A domain error raised on purpose."""


@mcp.resource("custom://{service}", mime_type="text/markdown")
def custom(service: str) -> str:
    """Raise a custom exception type and see how much of it reaches the client.

    Args:
        service: The service whose runbook to read.
    """
    path = LAB_DATA / f"{service}.md"
    if not path.is_file():
        raise RunbookUnavailable(f"RunbookUnavailable: {service} has no runbook on this host")
    return path.read_text(encoding="utf-8")


async def main() -> None:
    async with Client(mcp) as client:
        print("=== 1. a read that works ===")
        text = (await client.read_resource("loud://postgres"))[0].text
        print("   loud://postgres    ->", repr(text))

        print("\n=== 2. unknown URI: the router never calls your function ===")
        try:
            await client.read_resource("nosuch://thing")
        except Exception as exc:
            print(f"   {type(exc).__name__}: {str(exc).splitlines()[0][:90]}")

        print("\n=== 3. loud failure: the message names what IS available ===")
        try:
            await client.read_resource("loud://oracle")
        except Exception as exc:
            print(f"   {type(exc).__name__}: {str(exc).splitlines()[0][:120]}")

        print("\n=== 4. SILENT failure: success with nothing in it ===")
        item = (await client.read_resource("silent://oracle"))[0]
        print(f"   type={type(item).__name__} text={item.text!r} "
              f"len={len(item.text)} is_error=False")
        print("   -> the model reads this as 'the runbook is empty', not 'unknown service'")

        print("\n=== 5. a custom exception: the TYPE does not survive ===")
        try:
            await client.read_resource("custom://oracle")
        except Exception as exc:
            print(f"   client sees : {type(exc).__name__}: {str(exc).splitlines()[0][:110]}")
            print("   message kept: ", "RunbookUnavailable" in str(exc))

        print("\n=== 6. what a model can DO with each message ===")
        print("   'Resource not found: nosuch://thing'    -> wrong URI, no next step")
        print("   'no runbook for oracle; available: ...' -> retry with a valid service")
        print("   ''                                      -> no signal at all")


if __name__ == "__main__":
    asyncio.run(main())
