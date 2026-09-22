"""Capstone — an Enterprise DevOps / Knowledge Assistant MCP server.

Everything from M2 to M10, in one server that actually works on the machine it runs on:

  tools      real host metrics (CPU / memory / disk) from the standard library, plus log reads
  resources  server configuration and Markdown runbooks, addressed by URI
  prompts    a guided root-cause-analysis template over an error log
  elicitation  confirmation before a change to a protected service

DELIBERATE DESIGN CHOICE: the metrics are REAL — read from the host the server runs on with
`os`, `shutil` and `time` only. A capstone that returns invented numbers teaches students to
accept fabricated data, which is the habit this whole course argues against. Point it at a lab
VM in M8's environment and the numbers are that VM's.

Run:
    uv run python -m M11_capstone.code.devops_assistant          # self-test, no client needed
    uv run fastmcp dev inspector M11_capstone/code/devops_assistant.py
"""
from __future__ import annotations

import asyncio
import json
import os
import shutil
import time
from pathlib import Path
from typing import Any, Literal

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("devops-assistant")

# ------------------------------------------------------------------ configuration paths
HOME = Path(__file__).parent
DATA = HOME / "data"
LOGS = DATA / "logs"
CONF = DATA / "conf"
RUNBOOKS = DATA / "runbooks"
for directory in (LOGS, CONF, RUNBOOKS):
    directory.mkdir(parents=True, exist_ok=True)

# The allowlist IS the security boundary (M10). Everything below resolves paths against these
# three roots and refuses anything that escapes them.
PROTECTED_SERVICES = {"postgres-ha", "redis-sentinel", "kasm-app"}
MAX_BYTES = 48 * 1024


def _seed() -> None:
    """Write the sample estate, so the capstone runs on a fresh checkout."""
    (CONF / "pve01.yaml").write_text(
        "host: pve01\nrole: hypervisor\ncpu_cores: 72\nmemory_gb: 270\n"
        "storage:\n  - name: data\n    type: lvmthin\n    free_tb: 6.1\n",
        encoding="utf-8")
    (CONF / "kasm-agent1.yaml").write_text(
        "host: kasm-agent1\nrole: lab-agent\ncpu_cores: 16\nmemory_gb: 48\n"
        "runtime: docker\nsessions_max: 20\n", encoding="utf-8")
    (RUNBOOKS / "postgres-ha.md").write_text(
        "# postgres-ha runbook\n\n1. `cnpg status postgres-ha` — three instances, one primary.\n"
        "2. Check replication lag before anything else.\n"
        "3. Failover only after confirming `synchronous_standby_names`.\n"
        "4. Never restart two instances together.\n", encoding="utf-8")
    (RUNBOOKS / "kasm-agent.md").write_text(
        "# kasm-agent runbook\n\n1. `docker ps` — the agent and its proxy must both be up.\n"
        "2. A session that will not start usually means the agent is not Enabled in the UI.\n"
        "3. Disk fills with workspace images: check `docker system df` weekly.\n", encoding="utf-8")
    (LOGS / "postgres-ha.log").write_text("\n".join([
        "2026-09-19 02:00:00 INFO  checkpoint starting: time",
        "2026-09-19 02:00:04 INFO  checkpoint complete: wrote 1,204 buffers",
        "2026-09-19 02:01:50 WARN  replication lag 3.1s on postgres-ha-3",
        "2026-09-19 02:02:12 ERROR could not connect to host kasm-app:5432",
        "2026-09-19 02:02:13 ERROR connection retry 1 of 3",
        "2026-09-19 02:02:19 ERROR could not connect to host kasm-app:5432",
        "2026-09-19 02:02:20 ERROR connection retry 2 of 3",
        "2026-09-19 02:02:31 WARN  failover candidate withheld: sync standby missing",
    ]), encoding="utf-8")
    (LOGS / "kasm-agent.log").write_text("\n".join([
        "2026-09-19 02:10:01 INFO  agent check-in ok",
        "2026-09-19 02:11:44 WARN  workspace image pull slow: 12.4 MB/s",
        "2026-09-19 02:12:02 ERROR session start failed: agent not enabled in UI",
    ]), encoding="utf-8")


_seed()


# ------------------------------------------------------------------ shared helpers
def _resolve(root: Path, name: str) -> Path:
    """Resolve `name` inside `root`, refusing anything that escapes it (M10).

    `.resolve()` collapses `..` AND follows symlinks before the check, so both the traversal
    and the symlink bypass are closed. Comparing raw strings would miss both.
    """
    candidate = (root / name).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"path escapes {root.name}/: {name!r}")
    return candidate


def _fail(code: str, hint: str, **extra: Any) -> dict:
    """Structured failure (M5): the model reads `hint`, the client branches on `error`."""
    return {"ok": False, "error": code, "hint": hint, **extra}


# ------------------------------------------------------------------ TOOLS: metrics
@mcp.tool
def system_metrics() -> dict:
    """Report CPU count and load, memory, and disk usage for the host this server runs on.

    Real values from the standard library — no simulated numbers.
    """
    load: list[float] | None = None
    if hasattr(os, "getloadavg"):
        try:
            load = [round(x, 2) for x in os.getloadavg()]
        except OSError:                      # can fail on some platforms
            load = None
    mem_total = mem_available = None
    meminfo = Path("/proc/meminfo")
    if meminfo.is_file():
        fields = {}
        for line in meminfo.read_text().splitlines():
            key, _, rest = line.partition(":")
            fields[key.strip()] = rest.strip()
        def _kb(key: str) -> float | None:
            value = fields.get(key)
            return round(float(value.split()[0]) / 1024 / 1024, 2) if value else None
        mem_total = _kb("MemTotal")
        mem_available = _kb("MemAvailable")
    usage = shutil.disk_usage(HOME)
    return {
        "ok": True,
        "host": os.uname().nodename if hasattr(os, "uname") else os.environ.get("COMPUTERNAME", "unknown"),
        "cpu_count": os.cpu_count(),
        "load_average": load,
        "memory_total_gb": mem_total,
        "memory_available_gb": mem_available,
        "data_disk_total_gb": round(usage.total / 1e9, 2),
        "data_disk_free_gb": round(usage.free / 1e9, 2),
        "note": "null means the platform does not expose it (e.g. /proc on non-Linux)",
    }


@mcp.tool
def list_logs() -> dict:
    """List the log files this server may read."""
    return {"ok": True, "files": sorted(p.name for p in LOGS.glob("*") if p.is_file())}


@mcp.tool
def read_log(name: str, max_lines: int = 100, errors_only: bool = False) -> dict:
    """Read the tail of a log file.

    Args:
        name: File name inside the log directory, e.g. 'postgres-ha.log'.
        max_lines: How many trailing lines to return, 1-1000.
        errors_only: Return only lines containing ERROR or WARN.
    """
    try:
        target = _resolve(LOGS, name)
    except ValueError as exc:
        return _fail("path_not_allowed", str(exc))
    if not target.is_file():
        return _fail("not_found", f"{name!r} is not a log file",
                     available=sorted(p.name for p in LOGS.glob("*") if p.is_file()))
    max_lines = max(1, min(1000, max_lines))
    lines = target.read_text(errors="replace").splitlines()
    if errors_only:
        lines = [line for line in lines if "ERROR" in line or "WARN" in line]
    body = "\n".join(lines[-max_lines:])
    return {"ok": True, "name": name, "lines": len(lines[-max_lines:]),
            "truncated": len(body) > MAX_BYTES, "content": body[:MAX_BYTES]}


@mcp.tool
def list_runbooks() -> dict:
    """List the available runbooks."""
    return {"ok": True, "runbooks": sorted(p.stem for p in RUNBOOKS.glob("*.md"))}


@mcp.tool
async def restart_service(service: str, ctx: Context, reason: str = "") -> dict:
    """Restart a service, requiring confirmation when it is protected.

    This tool does NOT really restart anything — it is a capstone, and a course server must not
    touch the host's real services. What IS real is the GUARD: the confirmation flow, the
    protected-service list and the audit trail are the parts the lesson is about. The body
    states plainly that it did not act, so a student cannot mistake it for a working admin tool.

    Args:
        service: The service to restart.
        reason: Why the restart is needed. Recorded with the decision.
    """
    known = sorted(p.stem for p in CONF.glob("*.yaml"))
    if service not in PROTECTED_SERVICES:
        return {"ok": True, "status": "would_restart", "service": service,
                "protected": False, "note": "not protected; no confirmation required",
                "action_taken": "none — this capstone server does not modify the host"}

    class Confirm(BaseModel):
        """Confirmation before an action that affects live traffic."""

        proceed: bool = Field(description="True to continue, false to stop")
        reason: str = Field(default="", description="Optional note explaining the decision")

    answer = await ctx.elicit(
        message=(f"About to restart the PROTECTED service {service!r}. Live traffic is "
                 f"affected. Proceed?  (reason given: {reason or 'none'})"),
        response_type=Confirm,
    )
    action = getattr(answer, "action", "accept")
    if action != "accept":
        return {"ok": False, "status": action, "service": service,
                "hint": "Nothing was restarted. Do not retry without asking the user."}
    if not answer.data.proceed:
        return {"ok": False, "status": "refused_by_user", "service": service,
                "reason": answer.data.reason or "no reason given"}
    return {"ok": True, "status": "confirmed", "service": service, "protected": True,
            "config_seen": known, "action_taken": "none — this capstone server does not modify the host"}


# ------------------------------------------------------------------ RESOURCES
@mcp.resource("config://{host}", mime_type="application/yaml")
def host_config(host: str) -> str:
    """The configuration file for a named host.

    Args:
        host: Host name without the extension, e.g. 'pve01'.
    """
    try:
        target = _resolve(CONF, f"{host}.yaml")
    except ValueError as exc:
        raise FileNotFoundError(str(exc)) from exc
    if not target.is_file():
        available = sorted(p.stem for p in CONF.glob("*.yaml"))
        raise FileNotFoundError(f"no config for {host!r}; available: {', '.join(available) or 'none'}")
    return target.read_text(encoding="utf-8")


@mcp.resource("runbook://{name}", mime_type="text/markdown")
def runbook(name: str) -> str:
    """The Markdown runbook for a service.

    Args:
        name: Runbook name without the extension, e.g. 'postgres-ha'.
    """
    try:
        target = _resolve(RUNBOOKS, f"{name}.md")
    except ValueError as exc:
        raise FileNotFoundError(str(exc)) from exc
    if not target.is_file():
        available = sorted(p.stem for p in RUNBOOKS.glob("*.md"))
        raise FileNotFoundError(f"no runbook for {name!r}; available: {', '.join(available) or 'none'}")
    return target.read_text(encoding="utf-8")


# ------------------------------------------------------------------ PROMPTS
@mcp.prompt
def rca_error_log(log_name: str, window_minutes: int = 30) -> str:
    """Guide a root-cause analysis over an error log, in a fixed order.

    Args:
        log_name: Which log to analyse.
        window_minutes: How far back to look.
    """
    return (
        f"Perform a root cause analysis of {log_name} over the last {window_minutes} "
        "minutes. Work in this order and do not skip a step:\n\n"
        "1. Call `read_log` with `errors_only=true` and quote the exact lines you rely on.\n"
        "2. Identify the FIRST anomalous event, not the loudest one.\n"
        "3. Give the causal chain from that event to the user-visible symptom.\n"
        "4. Read the matching runbook resource before recommending anything.\n"
        "5. State what evidence would DISPROVE your explanation.\n"
        "6. Recommend the smallest change that would test it.\n\n"
        "If the log does not support a conclusion, answer 'insufficient evidence' and list\n"
        "exactly what you would need. Do not speculate, and do not invent log lines."
    )


@mcp.prompt
def capacity_review(host: str) -> str:
    """Review a host's capacity against what it is running.

    Args:
        host: The host to review.
    """
    return (
        f"Review the capacity of {host}.\n\n"
        "1. Read `config://{host}` for its declared resources.\n"
        "2. Call `system_metrics` and compare declared against measured.\n"
        "3. Name anything already above 70% and say what that implies.\n"
        "4. Give one concrete next action, or say plainly that there is nothing to do.\n\n"
        "Do not recommend an upgrade without a number that justifies it."
    )


# ------------------------------------------------------------------ self-test
async def main() -> None:
    from fastmcp import Client

    async with Client(mcp) as client:
        print("=== the server's surface ===")
        print("  tools     :", [t.name for t in await client.list_tools()])
        print("  resources :", [t.uri_template for t in await client.list_resource_templates()])
        print("  prompts   :", [p.name for p in await client.list_prompts()])

        print("\n=== real host metrics ===")
        metrics = (await client.call_tool("system_metrics", {})).data
        print(json.dumps(metrics, indent=2))

        print("\n=== reading an error log, filtered at the tool boundary ===")
        out = (await client.call_tool("read_log",
               {"name": "postgres-ha.log", "errors_only": True})).data
        print(f"  {out['lines']} lines; truncated={out['truncated']}")
        print(" " + out["content"].splitlines()[0])

        print("\n=== a path that escapes the allowlist ===")
        bad = (await client.call_tool("read_log", {"name": "../../etc/passwd"})).data
        print(" ", {k: bad[k] for k in ("ok", "error", "hint")})

        print("\n=== resources ===")
        for uri in ("config://pve01", "runbook://postgres-ha"):
            text = (await client.read_resource(uri))[0].text
            print(f"  {uri:26} -> {text.splitlines()[0]}")

        print("\n=== the guided RCA prompt ===")
        prompt = await client.get_prompt("rca_error_log", {"log_name": "postgres-ha.log"})
        print("  " + prompt.messages[0].content.text.splitlines()[0])

        print("\n=== elicitation on a protected service ===")
        # mode="legacy" is required for elicitation in fastmcp 4.x; the default `auto`
        # negotiates the sessionless 2026-07-28 era where server-initiated requests are
        # unavailable. The handler takes four arguments. See M8 for the full explanation.
        async def handler(message: str, response_type: Any, params: Any = None,
                          context: Any = None) -> Any:
            print(f"  [client] {message[:88]}...")
            return {"proceed": True, "reason": "approved in the capstone demo"}

        async with Client(mcp, mode="legacy", elicitation_handler=handler) as confirming:
            print(" ", (await confirming.call_tool("restart_service",
                   {"service": "postgres-ha", "reason": "replication lag"})).data)
            print("  ordinary service:",
                  (await confirming.call_tool("restart_service", {"service": "gitea"})).data)


if __name__ == "__main__":
    asyncio.run(main())
