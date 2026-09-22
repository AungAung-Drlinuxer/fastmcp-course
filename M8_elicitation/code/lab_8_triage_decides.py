"""LAB 8 — deciding whether to elicit at all.

The hardest skill in this lesson is not the API call, it is the decision: has the
question moved the server's work onto the user? This lab makes the decision an
explicit, testable function and shows the difference between a tool that looks
something up and a tool that asks.

Run:
    uv run python -m M8_elicitation.code.lab_8_triage_decides
"""
from __future__ import annotations

import asyncio
from typing import Any

from fastmcp import Client, Context, FastMCP
from fastmcp.client.elicitation import ElicitResult
from pydantic import BaseModel, Field

mcp = FastMCP("triage")

CLUSTERS: dict[str, dict[str, Any]] = {
    "prod-sg": {"region": "ap-southeast-1", "nodes": 6},
    "staging-sg": {"region": "ap-southeast-1", "nodes": 3},
    "prod-eu": {"region": "eu-west-1", "nodes": 4},
}


class RemediationChoice(BaseModel):
    """What to do about a failing service — the user's call, not the server's."""

    action: str = Field(description="One of: restart, scale, page_oncall, ignore")
    ticket: str = Field(default="", description="Change ticket reference")


@mcp.tool
async def cluster_list(ctx: Context) -> dict:
    """The server's own lookup. Exists so that NOTHING must be asked to find it."""
    return {"clusters": sorted(CLUSTERS)}


def needs_the_user(tool_name: str, service: str, action: str = "") -> tuple[bool, str]:
    """The decision rule, written down so it can be reviewed and tested."""
    if action in {"restart", "scale"}:
        return True, "the effect is irreversible and only the operator owns it"
    if service in {"postgres-ha", "redis"}:
        return True, "the target is protected"
    return False, "the server can resolve this itself — look it up"


@mcp.tool
async def triage(service: str, cluster: str, ctx: Context) -> dict:
    """Diagnose a service, asking the user only when the decision is theirs.

    Args:
        service: The failing service.
        cluster: The cluster it runs in, exactly as `cluster_list` reports it.
    """
    if cluster not in CLUSTERS:
        # The server can check this itself: it must NOT ask the user to spell it.
        return {"ok": False, "error": "unknown_cluster", "cluster": cluster,
                "known": sorted(CLUSTERS),
                "hint": "call cluster_list; do not ask the user for a name"}

    nodes = CLUSTERS[cluster]["nodes"]
    diagnosis = {"service": service, "cluster": cluster,
                 "region": CLUSTERS[cluster]["region"],
                 "likely_cause": "memory pressure" if service != "redis" else "eviction storm"}

    ask, why = needs_the_user("triage", service)
    if not ask:
        return {"ok": True, "status": "diagnosed", "why_no_prompt": why,
                "diagnosis": diagnosis, "nodes": nodes}

    result = await ctx.elicit(
        message=(f"{service} on {cluster} looks unhealthy ({diagnosis['likely_cause']}). "
                 "Which remediation should I apply?"),
        response_type=RemediationChoice,
    )
    action = getattr(result, "action", "accept")
    if action != "accept":
        return {"ok": False, "status": action, "why_prompted": why,
                "diagnosis": diagnosis}

    return {"ok": True, "status": "remediation_chosen",
            "chosen": result.data.action, "ticket": result.data.ticket or "none",
            "why_prompted": why, "diagnosis": diagnosis}


def make_handler(decision: str = "accept"):
    async def handler(message: str, response_type: Any, params: Any = None,
                      context: Any = None) -> Any:
        print(f"    [host] asked: {message}")
        if decision == "accept":
            return {"action": "restart", "ticket": "CHG-2077"}
        return ElicitResult(action=decision)

    return handler


async def main() -> None:
    print("=== the decision rule, enumerated ===")
    for tool_name, service, action in (("triage", "nginx", ""),
                                       ("triage", "postgres-ha", ""),
                                       ("triage", "nginx", "restart")):
        ask, why = needs_the_user(tool_name, service, action)
        print(f"  service={service:12} action={action or '-':8} elicit={str(ask):5} {why}")

    async with Client(mcp, mode="legacy", elicitation_handler=make_handler()) as client:
        print("\n=== the server resolves what it can ===")
        print("  cluster_list ->", (await client.call_tool("cluster_list", {})).data)
        print("  nginx (asks) ->", (await client.call_tool(
            "triage", {"service": "nginx", "cluster": "prod-sg"})).data)
        print("  redis (asks) ->", (await client.call_tool(
            "triage", {"service": "redis", "cluster": "prod-sg"})).data)

        print("\n=== and refuses to bother the user about its own bookkeeping ===")
        print("  typo cluster ->", (await client.call_tool(
            "triage", {"service": "nginx", "cluster": "prod-sg-typo"})).data)


if __name__ == "__main__":
    asyncio.run(main())
