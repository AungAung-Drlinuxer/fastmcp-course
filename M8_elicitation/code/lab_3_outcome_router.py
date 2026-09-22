"""LAB 3 — the three outcomes, and the policy each one demands.

accept, decline and cancel are three different futures. This lab encodes the
policy next to the tool, counts the prompts, and proves with a counter that a
declined elicitation is NOT re-asked.

Run:
    uv run python -m M8_elicitation.code.lab_3_outcome_router
"""
from __future__ import annotations

import asyncio
from typing import Any

from fastmcp import Client, Context, FastMCP
from fastmcp.client.elicitation import ElicitResult

mcp = FastMCP("outcome-router")

PROMPTS_SENT = 0
AUDIT: list[dict[str, Any]] = []


# The policy belongs next to the outcome, not in the tool body. One table, one meaning.
OUTCOME_POLICY: dict[str, dict[str, Any]] = {
    "accept":  {"ok": True,  "retry": False, "keep_state": True,
                "message": "The user consented: proceed with result.data."},
    "decline": {"ok": False, "retry": False, "keep_state": False,
                "message": "The user said no. Do NOT ask again; report the refusal."},
    "cancel":  {"ok": False, "retry": False, "keep_state": False,
                "message": "The user walked away. Stop cleanly; leave no partial state."},
}


def classify(result: Any) -> str:
    """Read the outcome off the result object instead of an isinstance chain."""
    return getattr(result, "action", "accept")


@mcp.tool
async def delete_snapshot(snapshot_id: str, ctx: Context) -> dict:
    """Delete a snapshot — irreversible, so it asks first.

    Args:
        snapshot_id: The snapshot to delete.
    """
    global PROMPTS_SENT
    PROMPTS_SENT += 1
    result = await ctx.elicit(
        message=f"Delete snapshot {snapshot_id!r}? This cannot be undone.",
        response_type=bool,
    )
    action = classify(result)
    policy = OUTCOME_POLICY[action]
    AUDIT.append({"snapshot_id": snapshot_id, "action": action, "retry": policy["retry"]})

    if action != "accept":
        return {"ok": False, "status": action, "policy": policy["message"],
                "deleted": False}

    # Only here — after acceptance — is any state changed.
    return {"ok": True, "status": "deleted", "snapshot_id": snapshot_id,
            "confirmed": result.data}


@mcp.tool
async def prompt_counter(ctx: Context) -> dict:
    """How many times has a human been asked? A decline must not raise this twice."""
    return {"prompts_sent": PROMPTS_SENT, "audit": list(AUDIT)}


def make_handler(decision: str):
    async def handler(message: str, response_type: Any, params: Any = None,
                      context: Any = None) -> Any:
        print(f"    [host] prompt #{PROMPTS_SENT}: {message}")
        if decision == "accept":
            return {"value": True}
        return ElicitResult(action=decision)

    return handler


async def main() -> None:
    print("=== one tool, three client behaviours ===")
    for decision in ("accept", "decline", "cancel"):
        async with Client(mcp, mode="legacy",
                          elicitation_handler=make_handler(decision)) as client:
            outcome = await client.call_tool("delete_snapshot", {"snapshot_id": "snap-42"})
            print(f"  {decision:8} -> {outcome.data}")
        print()

    print("=== the policy table, printed as the tool applies it ===")
    for action, policy in OUTCOME_POLICY.items():
        print(f"  {action:8} ok={policy['ok']!s:5} retry={policy['retry']!s:5} "
              f"keep_state={policy['keep_state']!s:5} | {policy['message']}")

    print("\n=== the counter proves no retry happened ===")
    async with Client(mcp, mode="legacy",
                      elicitation_handler=make_handler("decline")) as client:
        await client.call_tool("delete_snapshot", {"snapshot_id": "snap-99"})
        print("  after a declined call ->", (await client.call_tool(
            "prompt_counter", {})).data)


if __name__ == "__main__":
    asyncio.run(main())
