"""LAB 6 — EXTEND THE CAPSTONE: add your own tool without touching the capstone's file.

The capstone is a course artifact, not a personal project; overwriting it makes the next lesson
fail and hides what you changed. The pattern this lab teaches is the one real teams use: import
the server OBJECT and attach to it.

    from M11_capstone.code.devops_assistant import mcp, _fail, _resolve

`mcp` is an ordinary `FastMCP` instance. `@mcp.tool` on it registers another tool exactly the way
the five in the capstone were registered. Nothing in `devops_assistant.py` is edited.

The two helpers are imported deliberately. They are the two IDEAS every tool in a serious server
reuses:

    _resolve(root, name)  the allowlist boundary — resolve, then prove the result is inside
    _fail(code, hint, **) the structured failure — the model reads `hint`, the client branches
                          on `error`

Wrap the whole extension in its own module so a grader can see your work in one diff-sized file,
then prove it works by listing the tools through a client and finding your three new names in the
list.

Run:
    uv run python -m M11_capstone.code.lab_6_estate_memory_tool

Try to break it:
    uv run python -m M11_capstone.code.lab_6_estate_memory_tool --attack
"""
from __future__ import annotations

import asyncio
import sys
import time

from fastmcp import Client

# The capstone's server object and its two shared helpers. Importing them is the whole trick.
from M11_capstone.code.devops_assistant import HOME, _fail, _resolve, mcp

ATTACK = "--attack" in sys.argv

MEMORY = HOME / "data" / "memory"
MEMORY.mkdir(parents=True, exist_ok=True)
MAX_CHARS = 8 * 1024


# --- the extension: one new capability, three tools, zero edits to the capstone --------------
@mcp.tool
def save_note(name: str, text: str) -> dict:
    """Record a note in the estate memory directory.

    Args:
        name: Note name without the extension, e.g. 'postgres-failover-2026-09'.
        text: The note body. Markdown is fine; it is stored verbatim.
    """
    try:
        target = _resolve(MEMORY, f"{name}.md")
    except ValueError as exc:
        # Same boundary, same error code as the log tools: one vocabulary across the server.
        return _fail("path_not_allowed", str(exc))
    if not text.strip():
        return _fail("empty_note", "refusing to write a note with no content")
    body = text[:MAX_CHARS]
    target.write_text(body, encoding="utf-8")
    return {"ok": True, "name": name, "bytes": len(body.encode("utf-8")),
            "truncated": len(text) > MAX_CHARS, "saved_at": time.strftime("%Y-%m-%dT%H:%M:%S")}


@mcp.tool
def read_note(name: str) -> dict:
    """Read a note back, or explain exactly which notes exist.

    Args:
        name: Note name without the extension.
    """
    try:
        target = _resolve(MEMORY, f"{name}.md")
    except ValueError as exc:
        return _fail("path_not_allowed", str(exc))
    if not target.is_file():
        available = sorted(p.stem for p in MEMORY.glob("*.md"))
        return _fail("not_found", f"no note named {name!r}",
                     available=available or ["<none yet — save one first>"])
    text = target.read_text(encoding="utf-8")
    return {"ok": True, "name": name, "content": text[:MAX_CHARS],
            "truncated": len(text) > MAX_CHARS}


@mcp.tool
def list_notes() -> dict:
    """List the notes this server has stored."""
    return {"ok": True, "notes": sorted(p.stem for p in MEMORY.glob("*.md") if p.is_file())}


async def main() -> None:
    async with Client(mcp) as client:
        names = [t.name for t in await client.list_tools()]
        print("=== 1. the capstone's surface, now with your tools in it ===")
        print(f"  {names}")
        added = {"save_note", "read_note", "list_notes"}
        print(f"  capstone tools still present : "
              f"{ {'system_metrics', 'list_logs', 'read_log', 'list_runbooks', 'restart_service'} <= set(names) }")
        print(f"  your tools present           : {added <= set(names)}")
        print(f"  total tools                  : {len(names)} (was 5)")

        print("\n=== 2. save -> read -> list ===")
        saved = (await client.call_tool("save_note", {
            "name": "failover-drill",
            "text": "# Failover drill 2026-09\n\nPrimary restarted twice; sync standby "
                    "was missing both times.\nAction: fix synchronous_standby_names first.",
        })).data
        print(f"  save_note -> {saved}")
        read = (await client.call_tool("read_note", {"name": "failover-drill"})).data
        print(f"  read_note -> {read['content'].splitlines()[0]!r} "
              f"({len(read['content'])} chars, truncated={read['truncated']})")
        print(f"  list_notes -> {(await client.call_tool('list_notes', {})).data}")

        print("\n=== 3. the structured failure, using the capstone's vocabulary ===")
        missing = (await client.call_tool("read_note", {"name": "does-not-exist"})).data
        print(f"  {missing}")

        print("\n=== 4. the allowlist boundary, inherited for free ===")
        for attempt in ("../../etc/passwd", "/etc/passwd", "..\\..\\windows\\win.ini"):
            data = (await client.call_tool("read_note", {"name": attempt})).data
            print(f"  {attempt!r:26} -> {data['error']}: {data['hint'][:60]}")
        print("  You wrote none of that check. Reusing _resolve IS the security lesson.")

        if ATTACK:
            print("\n=== 5. break it on purpose ===")
            empty = (await client.call_tool("save_note", {"name": "blank", "text": "   "})).data
            print(f"  empty text      -> {empty}")
            long_note = "x" * 20000
            big = (await client.call_tool("save_note", {"name": "big", "text": long_note})).data
            print(f"  20k characters  -> bytes={big['bytes']} truncated={big['truncated']}")
            back = (await client.call_tool("read_note", {"name": "big"})).data
            print(f"  read back       -> {len(back['content'])} chars, truncated={back['truncated']}")
            print("  Both directions are bounded. A note-taking tool that echoes 20 000 characters")
            print("  back into a model's context is a denial-of-service on the context window.")

    print("\n=== 6. what you changed ===")
    print("  M11_capstone/code/devops_assistant.py : UNCHANGED (that is the whole point)")
    print("  M11_capstone/code/lab_6_estate_memory_tool.py : your extension, all in one file")


if __name__ == "__main__":
    asyncio.run(main())