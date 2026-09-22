"""LAB 9 — the attack matrix, run against the REAL hardened tool.

This lab imports the `mcp` object out of `M10_security.code.path_validation` and calls it through
a real in-process FastMCP `Client`. Nothing is mocked: the refusals you see are produced by the
same `_resolve_within` the shipped tool uses.

The matrix is split into two families, because the two families FAIL for different reasons:

  * traversal / absolute-path attempts  -> refused by the boundary      (`path_not_allowed`)
  * shell-metacharacter attempts        -> refused by the filesystem   (`not_found`)

Family two is the important insight: `postgres.log; rm -rf /` is not rejected by a filter. It is
rejected because there is no shell to interpret the `;`. The string is a *filename*, and no file
is called that.

Run:
    uv run python -m M10_security.code.lab_3_attack_matrix
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastmcp import Client

from M10_security.code.path_validation import LOG_ROOT, mcp

TRAVERSAL = [
    "../../etc/shadow",              # POSIX traversal
    "..\\..\\windows\\win.ini",      # Windows traversal, backslashes
    "/etc/passwd",                   # absolute path
    "logs/../../../etc/hosts",       # traversal from a subdirectory
]

INJECTION = [
    "postgres.log; rm -rf /",        # chaining with ;
    "$(id)",                         # command substitution
    "postgres.log && curl evil",     # chaining with && plus a fetch
]


async def collect() -> list[dict]:
    rows: list[dict] = []
    async with Client(mcp) as client:
        for family, attempts in (("traversal", TRAVERSAL), ("injection", INJECTION)):
            for attempt in attempts:
                result = await client.call_tool("read_log", {"name": attempt})
                data = result.data
                rows.append({
                    "family": family,
                    "attempt": attempt,
                    "ok": data["ok"],
                    "error": data.get("error"),
                    "hint": data.get("hint"),
                    "is_error": bool(result.is_error),
                })
    return rows


def main() -> None:
    print(f"allowlist root: {LOG_ROOT}")
    print(f"files in root : {sorted(p.name for p in LOG_ROOT.glob('*') if p.is_file())}")
    print(f"exists outside: /etc/passwd on this host -> {Path('/etc/passwd').exists()}\n")

    rows = asyncio.run(collect())

    print(f"{'family':10} {'attempt':32} {'ok':6} {'error':18} hint")
    print("-" * 118)
    for row in rows:
        hint = (row["hint"] or "")[:44]
        print(f"{row['family']:10} {row['attempt']:32} {str(row['ok']):6} "
              f"{row['error'] or '-':18} {hint}")

    refused = [r for r in rows if r["ok"] is False]
    raised = [r for r in rows if r["is_error"]]
    print()
    print(f"attempts          : {len(rows)}")
    print(f"refused as data   : {len(refused)}   ({len(refused)/len(rows):.0%})")
    print(f"raised ToolError  : {len(raised)}   (a refusal is data, not an exception)")
    print(f"any file leaked   : {'YES' if any(r['ok'] for r in rows) else 'no'}")

    # Machine-checkable evidence, written next to the module.
    evidence = Path(__file__).with_name("attack_matrix.json")
    evidence.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"\nevidence written : {evidence}")

    # A clean assertion so this file doubles as a CI check.
    assert not any(r["ok"] for r in rows), "the boundary leaked"
    assert not raised, "a refusal must be data, not an exception"
    print("verdict           : PASS — every attempt refused, none raised")


if __name__ == "__main__":
    main()
