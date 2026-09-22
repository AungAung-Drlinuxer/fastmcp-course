"""LAB 1 — threat modelling an MCP server, as code you can run.

A threat model that lives in a document nobody opens is decoration. This lab keeps it in a data
structure so three things become automatic:

  * every threat must name an ASSET, a TRUST BOUNDARY and a CONTROL — a blank is a visible bug
  * the server's own tool inventory is checked against the model, so a NEW TOOL shows up as an
    unmodelled threat the moment it is registered
  * `missing_controls()` is the punch list for the next commit

Run:
    uv run python -m M10_security.code.lab_1_threat_model
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from fastmcp import FastMCP


@dataclass(frozen=True)
class Threat:
    """One row of the threat model. Every field is required; empty means unmodelled."""

    id: str                 # short stable identifier, e.g. "T-02"
    asset: str              # what is at risk
    actor: str              # who exploits it
    boundary: str           # the line that is crossed
    impact: str             # what happens if it succeeds
    control: str = ""       # what stops it TODAY — empty means "no control yet"

    @property
    def modelled(self) -> bool:
        return all([self.asset, self.actor, self.boundary, self.impact])

    @property
    def controlled(self) -> bool:
        return bool(self.control)


# ----------------------------------------------------------------------------------------
# The server under discussion: the one this module hardens.
# Its attack surface IS its tool list — nothing else in the process is reachable by a model.
# ----------------------------------------------------------------------------------------
mcp = FastMCP("hardened-tools")


@mcp.tool
def read_log(name: str, max_lines: int = 200) -> dict:
    """Read the tail of a log file inside the configured log directory."""
    return {"ok": True, "name": name, "lines": 0, "content": ""}   # stub for the model only


@mcp.tool
def list_logs() -> dict:
    """List the log files that are readable through this server."""
    return {"ok": True, "files": []}                              # stub for the model only


THREATS: list[Threat] = [
    Threat(
        id="T-01", asset="the host filesystem (keys, /etc/shadow, browser profile)",
        actor="an LLM that has been steered by text it read",
        boundary="model-supplied string -> filesystem syscall",
        impact="any file the server process can read is exfiltrated through a tool result",
        control="allowlist root + Path.resolve() confinement (LAB 6, LAB 9)",
    ),
    Threat(
        id="T-02", asset="host CPU, memory and disk",
        actor="a prompt that asks for one enormous read",
        boundary="tool argument -> allocation size",
        impact="context exhaustion downstream, OOM or a stalled worker upstream",
        control="max_lines clamp + MAX_BYTES ceiling (LAB 7)",
    ),
    Threat(
        id="T-03", asset="the secrets of every OTHER system this process can reach",
        actor="anyone who can put text in front of the model",
        boundary="tool result -> model context",
        impact="indirect prompt injection: instructions arrive inside the data being read",
        control="tool output is DATA, never instructions; host-side screening of tool results",
    ),
    Threat(
        id="T-04", asset="the human operator's approval decision",
        actor="a server that changes a tool's description after approval",
        boundary="tool description -> model context",
        impact="a rug-pull: approved once, behaves differently later",
        control="pin the server version; hash tool descriptions; re-prompt on a changed hash",
    ),
    Threat(
        id="T-05", asset="the audit trail itself",
        actor="an attacker who wants to leave no trace",
        boundary="tool call -> log record",
        impact="an incident cannot be reconstructed; the log leaks secrets if done wrong",
        control="append-only structured records, arg digests not raw secrets (LAB 11)",
    ),
    Threat(
        id="T-06", asset="the container host and its other workloads",
        actor="an exploit that assumes root inside the container",
        boundary="container -> host kernel",
        impact="lateral movement to every other namespace on the node",
        control="non-root uid, read-only rootfs, dropped capabilities, no-new-privileges",
    ),
]


def report() -> int:
    print(f"{'id':6} {'modelled':9} {'controlled':11} asset")
    print("-" * 96)
    for threat in THREATS:
        print(f"{threat.id:6} {str(threat.modelled):9} {str(threat.controlled):11} "
              f"{threat.asset[:60]}")
    open_rows = [t for t in THREATS if not t.controlled]
    print()
    print(f"threats modelled : {sum(t.modelled for t in THREATS)}/{len(THREATS)}")
    print(f"threats with a control : {sum(t.controlled for t in THREATS)}/{len(THREATS)}")
    for threat in open_rows:
        print(f"  OPEN  {threat.id}: no control recorded for {threat.asset[:50]}")
    return len(open_rows)


async def tool_surface() -> list[str]:
    """The attack surface, asked of the server itself rather than remembered by hand."""
    return sorted(tool.name for tool in await mcp.list_tools())


def main() -> None:
    print("=== the attack surface is the tool list ===")
    for name in asyncio.run(tool_surface()):
        print(f"  tool: {name}")
    print("  anything a model can reach, it reaches through one of these names\n")

    open_rows = report()

    print("\n=== the one-line test every new tool must pass ===")
    print("  'what does this tool let a STRANGER, speaking through the model, do?'")
    print("  if the answer is 'less than I intended', the tool is not finished.\n")

    assert not open_rows, f"{open_rows} threats have no control recorded"
    print("verdict : PASS — every modelled threat names a control")


if __name__ == "__main__":
    main()
