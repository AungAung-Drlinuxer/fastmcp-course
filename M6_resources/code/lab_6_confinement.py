"""LAB 6 — confinement: Path.resolve() inside a resource.

Two layers stop a traversal attempt, and this lab shows both:
    layer 1  the URI router refuses to match a variable containing `/`
    layer 2  Path.resolve() + a parent check, proved with a direct call

Layer 2 is the one you keep when the variable is allowed to be a path. M10 completes this
idea against a tool that really does accept slashes.

Run:
    uv run python -m M6_resources.code.lab_6_confinement
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from fastmcp import Client, FastMCP

mcp = FastMCP("lab6-confinement")

LAB_DATA = Path(__file__).with_name("lab_data")
LAB_DATA.mkdir(exist_ok=True)
(LAB_DATA / "postgres.md").write_text("# PostgreSQL runbook\n", encoding="utf-8")

# `.resolve()` is what makes the boundary enforceable rather than aspirational: it collapses
# `..` and follows symlinks BEFORE the containment check runs.
RUNBOOK_ROOT = LAB_DATA.resolve()


def safe_path(name: str) -> Path:
    """Resolve `name` under RUNBOOK_ROOT and prove the result stays inside it."""
    candidate = (RUNBOOK_ROOT / name).resolve()
    if RUNBOOK_ROOT not in candidate.parents:
        raise ValueError(f"path escapes the runbook directory: {name!r}")
    return candidate


@mcp.resource("runbook://{service}", mime_type="text/markdown")
def runbook(service: str) -> str:
    """The runbook for a named service, read only from the runbook directory.

    Args:
        service: The service whose runbook to read.
    """
    try:
        path = safe_path(f"{service}.md")
    except ValueError as exc:
        available = sorted(p.stem for p in RUNBOOK_ROOT.glob("*.md"))
        raise FileNotFoundError(
            f"no runbook for {service!r}; available: {', '.join(available) or 'none'}"
        ) from exc
    if not path.is_file():
        available = sorted(p.stem for p in RUNBOOK_ROOT.glob("*.md"))
        raise FileNotFoundError(
            f"no runbook for {service!r}; available: {', '.join(available) or 'none'}")
    return path.read_text(encoding="utf-8")


async def main() -> None:
    print("=== layer 1: the router refuses a variable with a slash ===")
    async with Client(mcp) as client:
        for uri in ("runbook://postgres",
                    "runbook://../../etc/passwd",
                    "runbook://..%2F..%2Fetc%2Fpasswd",
                    "runbook://postgres/extra"):
            try:
                text = (await client.read_resource(uri))[0].text
                print(f"  {uri:38} -> read ok: {text.splitlines()[0]!r}")
            except Exception as exc:
                print(f"  {uri:38} -> {type(exc).__name__}: "
                      f"{str(exc).splitlines()[0][:90]}")

    print("\n=== layer 2: safe_path called directly, bypassing the router ===")
    for probe in ("postgres.md", "../lab_data/postgres.md", "../../../etc/passwd",
                  "..", "/etc/hosts", "subdir/notes.md"):
        try:
            print(f"  {probe!r:30} -> {safe_path(probe).relative_to(RUNBOOK_ROOT.parent)}")
        except ValueError as exc:
            print(f"  {probe!r:30} -> ValueError: {exc}")

    print("\n=== what the traversal attempt looked like from the client ===")
    print("  it never reached the function: the URI matched no template at all.")
    print("  that is why layer 2 is defensive, not redundant: a template whose variable")
    print("  IS allowed to contain a path loses layer 1 entirely. M10 builds that case.")


if __name__ == "__main__":
    asyncio.run(main())
