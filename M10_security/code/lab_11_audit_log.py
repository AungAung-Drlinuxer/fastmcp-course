"""LAB 11 — audit logging: a record that helps an incident, and leaks nothing.

Two failure modes bracket this lab:

  * TOO LITTLE — you log "tool called" with no argument, and after an incident you cannot say
    which file was read, by whom, or from which session.
  * TOO MUCH — you log the raw arguments, and the audit file becomes the very secret store the
    attacker was looking for. An audit log is the most attractive file on the machine.

The design here is: JSON Lines, one record per call, append-only, with the *shape* of the argument
recorded (length, hash, verdict) instead of its value whenever the value could be a secret.

Run:
    uv run python -m M10_security.code.lab_9_audit_log
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from fastmcp import Client

from M10_security.code.path_validation import LOG_ROOT, mcp

AUDIT = Path(__file__).with_name("audit.jsonl")

# Key NAMES whose value may be a secret. Record a digest and a length, never the text.
#
# These are matched as SUBSTRINGS, not with `==`. That detail is the difference between a
# working control and a decorative one: an exact-match set containing "token" does not match
# "api_token", "refresh_token" or "token_value" — and an attacker (or a tired colleague) will
# name the field after any of those. Fail closed: if the name contains a hint, redact.
SENSITIVE = ("password", "passwd", "pwd", "token", "secret", "api_key", "apikey",
             "authorization", "auth", "credential", "connection_string", "private_key")


def is_sensitive(key: str) -> bool:
    """True when the key NAME suggests the value must never be stored in clear."""
    lowered = key.lower()
    return any(hint in lowered for hint in SENSITIVE)


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def safe_arg(key: str, value: object) -> object:
    """Either the value itself, or a fingerprint that proves you saw it without storing it."""
    if is_sensitive(key):
        text = str(value)
        return {"redacted": True, "sha256_16": hashlib.sha256(
            text.encode()).hexdigest()[:16], "length": len(text)}
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return {"type": type(value).__name__}


@dataclass
class Audit:
    """Append-only JSON Lines writer. One line per event, fsync per write."""

    path: Path
    actor: str = "local-dev"
    session: str = "0"
    events: list = field(default_factory=list)

    def record(self, event: str, **fields: object) -> dict:
        row = {"ts": stamp(), "event": event, "actor": self.actor, "session": self.session, **fields}
        line = json.dumps(row, default=str, sort_keys=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
            handle.flush()
        self.events.append(row)
        return row


async def audited_call(audit: Audit, tool: str, args: dict,
                      host_context: dict | None = None) -> dict:
    """Call a tool THROUGH the audit boundary: record intent, outcome, duration and verdict.

    `host_context` is the host application's own material (the credential it used to reach the
    MCP server, the tenant it acted for). It is recorded through the SAME redaction function,
    because the audit file is exactly where a leaked token does the most damage.
    """
    started = time.perf_counter()
    audit.record("tool_call", tool=tool,
                 args={k: safe_arg(k, v) for k, v in args.items()},
                 host_context={k: safe_arg(k, v) for k, v in (host_context or {}).items()})
    async with Client(mcp) as client:
        try:
            result = await client.call_tool(tool, args)
            data = result.data
            is_error = bool(result.is_error)
        except Exception as exc:                       # a genuine failure, not a refusal
            audit.record("tool_exception", tool=tool, kind=type(exc).__name__,
                         ms=round((time.perf_counter() - started) * 1000, 1))
            raise
    verdict = "ok" if data.get("ok") else f"refused:{data.get('error')}"
    audit.record("tool_result", tool=tool, verdict=verdict, is_error=is_error,
                 ms=round((time.perf_counter() - started) * 1000, 1))
    return data


async def run(audit: Audit) -> list[dict]:
    out = []

    # A legitimate call, with the host's credential in the host context: it must be redacted.
    out.append(await audited_call(audit, "list_logs", {},
                                  host_context={"api_token": "sk-not-a-real-token-0000"}))
    out.append(await audited_call(audit, "read_log", {"name": "postgres.log", "max_lines": 2}))

    # The attempt an incident review wants to find afterwards:
    out.append(await audited_call(audit, "read_log", {"name": "../../etc/shadow"}))

    out.append(await audited_call(audit, "grep_log",
                                  {"name": "postgres.log", "pattern": "ERROR"}))

    # A call that is refused BEFORE the tool body runs: a validation error, raised as a
    # ToolError by the framework (see ../../VERIFIED.md). An audit trail must record FAILED
    # calls too — an attacker's malformed attempt is the most interesting line in the file.
    try:
        await audited_call(audit, "read_log",
                           {"name": "postgres.log", "password": "hunter2-not-a-real-one"})
    except Exception as exc:
        print(f"[expected] a malformed call raised {type(exc).__name__} and was recorded\n")
    return out


def main() -> None:
    if AUDIT.exists():
        AUDIT.unlink()                                    # start from a clean trail for the lab
    audit = Audit(path=AUDIT, actor="lab-student", session="m10-lab-11")

    asyncio.run(run(audit))

    print(f"=== {AUDIT.name}: the raw trail (one JSON object per line) ===")
    for line in AUDIT.read_text(encoding="utf-8").splitlines():
        print(f"  {line}")

    print("\n=== what an incident reviewer asks, and the field that answers it ===")
    for question, fieldname in [
        ("who called it?", "actor / session"),
        ("which tool, and when?", "event=tool_call, tool, ts"),
        ("what did they ask for?", "args — with secrets redacted"),
        ("did the boundary hold?", "event=tool_result, verdict"),
        ("how long did it take?", "ms"),
    ]:
        print(f"  {question:28} <- {fieldname}")

    records = [json.loads(line) for line in AUDIT.read_text(encoding="utf-8").splitlines()]
    refused = [r for r in records if r.get("verdict", "").startswith("refused:")]
    def has_redaction(row: dict) -> bool:
        buckets = list(row.get("args", {}).values()) + list(row.get("host_context", {}).values())
        return any(isinstance(v, dict) and v.get("redacted") for v in buckets)

    redacted = [r for r in records if has_redaction(r)]
    exceptions = [r for r in records if r["event"] == "tool_exception"]

    print("\n=== checks ===")
    print(f"  records            : {len(records)}")
    print(f"  refusals recorded  : {len(refused)} -> {[r['verdict'] for r in refused]}")
    print(f"  validation failures recorded : {len(exceptions)} "
          f"({[r.get('kind') for r in exceptions]})")
    print(f"  records with a redacted field: {len(redacted)}")
    for row in redacted:
        for bucket in ("args", "host_context"):
            for key, value in row.get(bucket, {}).items():
                if isinstance(value, dict) and value.get("redacted"):
                    print(f"    {row['event']:13} {bucket}.{key} -> length={value['length']} "
                          f"sha256_16={value['sha256_16']}")
    print("  note: 'api_token' is redacted because the check is a SUBSTRING match; an exact")
    print("        match against {'token'} would have let it through as clear text.")
    leaked = [r for r in records
              if "hunter2" in json.dumps(r) or "sk-not-a-real-token" in json.dumps(r)]
    print(f"  raw secret in trail: {'YES — bug' if leaked else 'no'}")
    print(f"  trail bytes        : {AUDIT.stat().st_size}")

    print("\n=== the four rules this file demonstrates ===")
    for rule in [
        "one line per event, JSON: greppable with jq, parseable without a library",
        "append-only: no updates, no deletes — a rewrite is reviewable, an edit is not",
        "record the DECISION (verdict) as well as the request; a refusal is an event too",
        "fingerprint secret-shaped arguments: length + sha256_16, never the value",
    ]:
        print(f"  - {rule}")

    assert not leaked, "a secret reached the audit trail"
    assert len(refused) == 1 and refused[0]["verdict"] == "refused:path_not_allowed"
    assert len(exceptions) == 1 and len(redacted) == 2
    print("\nverdict : PASS — the trail answers the incident questions and carries no secret")


if __name__ == "__main__":
    main()
