"""LAB 7 — output bounding as a context-exhaustion defence.

A tool that returns everything is not "helpful"; it is a denial-of-service against the caller's
context window. This lab writes a deliberately huge log inside the allowlist root, then calls the
real tools with hostile arguments (`max_lines=99999`, `max_matches=99999`) to show that the SERVER
clamps, not the caller.

The three bounds you will observe:
  * `max_lines`   clamped to 1..1000
  * `MAX_BYTES`   the returned body is cut at 64 KiB and flagged with `truncated_bytes`
  * `grep_log`    `max_matches` clamped to 1..200, and every matched line cut at 300 chars

Run:
    uv run python -m M10_security.code.lab_4_output_bounds
"""
from __future__ import annotations

import asyncio
import json

from fastmcp import Client

from M10_security.code.path_validation import LOG_ROOT, MAX_BYTES, mcp

HUGE_LINES = 4000
LONG_LINE_CHARS = 200


def seed_logs() -> None:
    """Write two adversarial fixtures INSIDE the allowlist root, where a tool may read them."""
    (LOG_ROOT / "huge.log").write_text(
        "\n".join(f"2026-09-19 03:{i % 60:02d}:00 INFO line {i} " + ("z" * 40)
                  for i in range(HUGE_LINES)),
        encoding="utf-8",
    )
    # 400 lines, each 200 characters: 80,000 bytes total, comfortably over MAX_BYTES.
    (LOG_ROOT / "wide.log").write_text(
        "\n".join("W" * LONG_LINE_CHARS for _ in range(400)),
        encoding="utf-8",
    )


async def probe() -> dict:
    out: dict = {}
    async with Client(mcp) as client:
        out["clamped_lines"] = (await client.call_tool(
            "read_log", {"name": "huge.log", "max_lines": 99999})).data
        out["clamped_low"] = (await client.call_tool(
            "read_log", {"name": "huge.log", "max_lines": 0})).data
        out["byte_capped"] = (await client.call_tool(
            "read_log", {"name": "wide.log", "max_lines": 1000})).data
        out["grep_clamped"] = (await client.call_tool(
            "grep_log", {"name": "huge.log", "pattern": "INFO", "max_matches": 99999})).data
        out["grep_cut_line"] = (await client.call_tool(
            "grep_log", {"name": "wide.log", "pattern": "W", "max_matches": 3})).data
    return out


def main() -> None:
    seed_logs()
    huge_bytes = (LOG_ROOT / "huge.log").stat().st_size
    wide_bytes = (LOG_ROOT / "wide.log").stat().st_size
    print(f"allowlist root : {LOG_ROOT}")
    print(f"huge.log       : {huge_bytes:>9,} bytes on disk")
    print(f"wide.log       : {wide_bytes:>9,} bytes on disk")
    print(f"MAX_BYTES      : {MAX_BYTES:>9,} bytes  (the return-value ceiling)\n")

    result = asyncio.run(probe())

    print("=== max_lines is clamped by the SERVER, not honoured from the client ===")
    for key, asked in (("clamped_lines", 99999), ("clamped_low", 0)):
        row = result[key]
        body_bytes = len(row["content"].encode("utf-8"))
        print(f"  {key:14} asked max_lines={asked:<6} -> lines={row['lines']:<5} "
              f"bytes={body_bytes:<8,} truncated={row['truncated_bytes']}")

    print("\n=== MAX_BYTES cuts the body even when the line count is legal ===")
    row = result["byte_capped"]
    body_bytes = len(row["content"].encode("utf-8"))
    print(f"  lines requested : 1000 (legal)")
    print(f"  lines returned  : {row['lines']}")
    print(f"  content bytes   : {body_bytes:,}  (source file was {wide_bytes:,})")
    print(f"  truncated_bytes : {row['truncated_bytes']}   <- the caller is TOLD it was cut")

    print("\n=== grep_log clamps max_matches and cuts each matched line ===")
    row = result["grep_clamped"]
    print(f"  asked max_matches=99999 -> matches={row['matches']} (ceiling 200)")
    row = result["grep_cut_line"]
    longest = max(len(h["text"]) for h in row["results"])
    print(f"  matched line of 200 chars -> returned {longest} chars (cut at 300 per line)")

    print("\n=== what an unbounded tool would have returned for the same call ===")
    print(f"  huge.log whole file : {huge_bytes:,} bytes  = {huge_bytes/4:,.0f} rough tokens")
    print(f"  bounded read_log    : {len(result['clamped_lines']['content'].encode()):,} bytes")
    saved = 1 - len(result["clamped_lines"]["content"].encode()) / huge_bytes
    print(f"  reduction           : {saved:.1%}")
    print("\n  A 4000-line log is small. Substitute a 40 GB WAL file and the unbounded tool")
    print("  returns a string your host application cannot even hold in memory.")

    evidence = LOG_ROOT.parent / "output_bounds.json"
    evidence.write_text(json.dumps(
        {k: {kk: (vv[:120] if kk == "content" else vv) for kk, vv in v.items()}
         for k, v in result.items()}, indent=2), encoding="utf-8")
    print(f"\nevidence written : {evidence}")

    assert result["clamped_lines"]["lines"] <= 1000
    assert result["clamped_low"]["lines"] >= 1
    assert result["grep_clamped"]["matches"] <= 200
    assert len(result["byte_capped"]["content"].encode()) <= MAX_BYTES
    print("verdict          : PASS — three independent bounds all held")


if __name__ == "__main__":
    main()
