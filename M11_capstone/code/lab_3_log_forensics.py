"""LAB 3 — log forensics: filter at the tool boundary, then find the FIRST anomalous event.

The RCA prompt tells the model to identify the FIRST anomalous event, "not the loudest one". This
lab does exactly that with no model involved, so you can see why the instruction is there:

    postgres-ha.log contains four ERROR lines and two WARN lines.
    The loudest thing in the file is the connection failure to kasm-app (3 mentions).
    The FIRST anomalous event is the replication lag warning, six lines earlier.

A tool that returned the whole file and let the reader sort it out invites the loudest-events
answer. `errors_only=true` plus a bounded `max_lines` makes the file small enough that the first
line of the output IS the first anomaly.

Run:
    uv run python -m M11_capstone.code.lab_3_log_forensics
"""
from __future__ import annotations

import asyncio

from fastmcp import Client

from M11_capstone.code.devops_assistant import mcp


async def main() -> None:
    async with Client(mcp) as client:
        print("=== 1. discover, never guess ===")
        listing = (await client.call_tool("list_logs", {})).data
        print(f"  files: {listing['files']}")

        print("\n=== 2. the whole file, unhelpfully ===")
        whole = (await client.call_tool("read_log",
                 {"name": "postgres-ha.log", "max_lines": 1000})).data
        print(f"  {whole['lines']} lines, truncated={whole['truncated']}")

        print("\n=== 3. filtered at the tool boundary ===")
        filtered = (await client.call_tool("read_log",
                    {"name": "postgres-ha.log", "errors_only": True})).data
        print(f"  {filtered['lines']} lines, truncated={filtered['truncated']}")
        for line in filtered["content"].splitlines():
            print(f"    {line}")

        print("\n=== 4. first vs loudest ===")
        lines = filtered["content"].splitlines()
        first = lines[0]
        # "loudest" = the message text that repeats most often, ignoring the timestamp.
        counts: dict[str, int] = {}
        for line in lines:
            tail = line[20:].strip()
            key = tail.split(":")[0]
            counts[key] = counts.get(key, 0) + 1
        loudest = max(counts.items(), key=lambda pair: pair[1])
        print(f"  FIRST anomalous event : {first}")
        print(f"  LOUDEST message group : {loudest[0]!r} x{loudest[1]}")
        print("  -> they are different lines. An assistant that starts from the loudest one")
        print("     blames the connection failure for a lag problem that began earlier.")

        print("\n=== 5. the filter is a real filter, not a string search for the word ERROR ===")
        for name in ("postgres-ha.log", "kasm-agent.log"):
            data = (await client.call_tool("read_log",
                    {"name": name, "errors_only": True})).data
            kinds = sorted({w for line in data["content"].splitlines()
                            for w in ("ERROR", "WARN", "INFO") if w in line})
            print(f"  {name:18} lines={data['lines']} kinds={kinds}")

        print("\n=== 6. bounded output ===")
        for n in (-5, 0, 1, 2, 5000):
            data = (await client.call_tool("read_log", {"name": "postgres-ha.log",
                                                       "max_lines": n})).data
            print(f"  max_lines={n:<5} -> lines={data['lines']:<3} "
                  f"first={data['content'].splitlines()[0][11:25]!r}")
        print("  max_lines is clamped into 1..1000 inside the tool — the clamp is not a request")

        print("\n=== 7. the allowlist, attacked ===")
        attempts = ["../../etc/passwd", "..\\..\\windows\\win.ini", "/etc/passwd",
                    "postgres-ha.log; rm -rf /", "$(id)", "", "nope.log"]
        print(f"  {'input':34} {'error':18} hint")
        for attempt in attempts:
            data = (await client.call_tool("read_log", {"name": attempt})).data
            print(f"  {attempt!r:34} {data['error']:18} {data['hint'][:52]}")

        print("\n=== 8. what a good assistant reports from here ===")
        print("  1 evidence   : the four ERROR lines, quoted exactly")
        print("  2 first event: the replication-lag WARN, not the connection errors")
        print("  3 runbook    : runbook://postgres-ha step 2 — check lag before anything else")
        print("  4 falsifier  : read the WARN line as a client-side retry, not a lag problem")
        print("  5 next action: smallest change that tests the explanation, not a restart")


if __name__ == "__main__":
    asyncio.run(main())
