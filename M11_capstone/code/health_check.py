"""Health check — exit non-zero when the capstone's promises no longer hold.

A self-test is for a human: it prints what the server can do. A health check is for a machine:
it prints NOTHING when all is well and exits 0, and exits 1 with named failures when it is not.
That distinction is what makes it usable from cron, CI, or a Kubernetes liveness probe.

Run:
    uv run python -m M11_capstone.code.health_check ; echo "exit code: $?"
"""
from __future__ import annotations

import asyncio
import sys

from fastmcp import Client

from M11_capstone.code.devops_assistant import mcp

EXPECTED_TOOLS = {"system_metrics", "list_logs", "read_log", "list_runbooks", "restart_service"}
EXPECTED_TEMPLATES = {"config://{host}", "runbook://{name}"}


async def check() -> list[str]:
    """Return a list of FAILURES; an empty list means every promise held."""
    failures: list[str] = []
    async with Client(mcp) as client:
        names = {t.name for t in await client.list_tools()}
        if not EXPECTED_TOOLS <= names:
            failures.append(f"missing tools: {sorted(EXPECTED_TOOLS - names)}")

        templates = {t.uri_template for t in await client.list_resource_templates()}
        missing = EXPECTED_TEMPLATES - templates
        if missing:
            failures.append(f"missing templates: {sorted(missing)}")

        metrics = (await client.call_tool("system_metrics", {})).data
        if metrics.get("cpu_count") is None:
            failures.append("system_metrics returned no cpu_count")
        if not metrics.get("data_disk_total_gb"):
            failures.append("system_metrics returned no disk total")

        # The important check: an attack must fail with the RIGHT code. A refusal that says
        # 'not_found' means the allowlist never refused anything — the file simply was absent.
        attack = (await client.call_tool("read_log", {"name": "../../etc/passwd"})).data
        if attack.get("error") != "path_not_allowed":
            failures.append(f"the allowlist no longer refuses traversal: {attack}")

        # A missing file must teach the caller what exists, or an agent will guess forever.
        absent = (await client.call_tool("read_log", {"name": "nope.log"})).data
        if not absent.get("available"):
            failures.append("a missing log no longer lists what is available")
    return failures


def main() -> int:
    failures = asyncio.run(check())
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("OK: every promise held")
    return 0


if __name__ == "__main__":
    sys.exit(main())
