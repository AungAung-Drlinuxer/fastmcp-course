"""LAB 4 — the protected-service gate: confirmation before anything risky.

One set of protected names, one Confirmation model, one audit trail. The gate
answers four questions every risky action needs: did the user consent, did they
refuse with a reason, did they walk away, or was the action never risky at all?

Run:
    uv run python -m M8_elicitation.code.lab_4_protected_gate
"""
from __future__ import annotations

import asyncio
from typing import Any

from fastmcp import Client, Context, FastMCP
from fastmcp.client.elicitation import ElicitResult
from pydantic import BaseModel, Field

mcp = FastMCP("protected-gate")

CLUSTER_PROTECTED = {"postgres-ha", "redis", "kasm-app"}


class Confirmation(BaseModel):
    """A yes/no confirmation before an irreversible action."""

    proceed: bool = Field(description="True to continue, false to stop")
    reason: str = Field(default="", description="Optional note explaining the decision")
    change_ticket: str = Field(default="", description="Change ticket reference, if any")


AUDIT: list[dict[str, Any]] = []


@mcp.tool
async def maintenance_window(service: str, ctx: Context) -> dict:
    """Confirm before touching a protected service.

    Args:
        service: The service the maintenance is for.
    """
    if service not in CLUSTER_PROTECTED:
        AUDIT.append({"service": service, "gate": "skipped", "status": "scheduled"})
        return {"ok": True, "status": "scheduled", "service": service,
                "note": "not a protected service, no confirmation required"}

    answer = await ctx.elicit(
        message=(f"About to schedule maintenance for the PROTECTED service {service!r}. "
                 "This affects live traffic. Proceed?"),
        response_type=Confirmation,
    )

    action = getattr(answer, "action", "accept")
    if action != "accept":
        AUDIT.append({"service": service, "gate": action, "status": action})
        return {"ok": False, "status": action, "service": service,
                "hint": "Nothing was scheduled."}

    if not answer.data.proceed:
        AUDIT.append({"service": service, "gate": "refused", "status": "refused_by_user"})
        return {"ok": False, "status": "refused_by_user", "service": service,
                "reason": answer.data.reason or "no reason given"}

    AUDIT.append({"service": service, "gate": "confirmed", "status": "scheduled",
                  "ticket": answer.data.change_ticket})
    return {"ok": True, "status": "scheduled", "service": service,
            "ticket": answer.data.change_ticket or "none"}


@mcp.tool
async def audit_log(ctx: Context) -> dict:
    """What actually reached the system, and through which gate."""
    return {"entries": list(AUDIT)}


def make_handler(proceed: bool | None, reason: str = "", ticket: str = "",
                 action_override: str | None = None):
    async def handler(message: str, response_type: Any, params: Any = None,
                      context: Any = None) -> Any:
        print(f"    [host] confirmation form: {message}")
        if action_override:
            return ElicitResult(action=action_override)
        return {"proceed": bool(proceed), "reason": reason, "change_ticket": ticket}

    return handler


async def main() -> None:
    cases = [
        ("protected, user agrees", "postgres-ha", make_handler(True, ticket="CHG-1041")),
        ("protected, user refuses", "redis", make_handler(False, reason="during peak")),
        ("protected, user declines the prompt", "kasm-app",
         make_handler(None, action_override="decline")),
        ("protected, user cancels the prompt", "postgres-ha",
         make_handler(None, action_override="cancel")),
        ("not protected, gate skipped", "gitea", make_handler(True)),
    ]

    for label, service, handler in cases:
        print(f"=== {label} ===")
        async with Client(mcp, mode="legacy", elicitation_handler=handler) as client:
            print("  ->", (await client.call_tool(
                "maintenance_window", {"service": service})).data)
        print()

    async with Client(mcp, mode="legacy", elicitation_handler=make_handler(True)) as client:
        print("=== audit trail ===")
        for entry in (await client.call_tool("audit_log", {})).data["entries"]:
            print("  ", entry)


if __name__ == "__main__":
    asyncio.run(main())
