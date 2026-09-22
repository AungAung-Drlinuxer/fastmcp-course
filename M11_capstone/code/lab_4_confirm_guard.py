"""LAB 4 — the confirmation guard: four client behaviours, four different outcomes.

A guard that only has a "yes" path is not a guard. This lab drives the SAME tool with four
different client handlers and prints what the server returned each time:

    accept   -> the user approved        -> status 'confirmed'
    refuse   -> the user answered no     -> status 'refused_by_user'  (a DECISION)
    decline  -> the user said "don't ask"-> status 'decline'          (a REFUSAL, not a failure)
    cancel   -> the user walked away     -> status 'cancel'           (STOP cleanly)

`accept` and `refuse` are both the same protocol outcome: the user answered. `decline` and
`cancel` are the user NOT answering, and the distinction matters because one means "ask again
later" and the other means "never ask again in this flow".

TWO THINGS THIS LAB PROVES ABOUT THE API, both measured on fastmcp 4.0.5:

  1. `Client(mcp)` — the DEFAULT mode — negotiates the 2026-07-28 era, where a server may not
     initiate a request. The call fails with:
         ToolError: elicitation via server-initiated requests is unavailable on
                    2026-07-28 connections.
     `mode="legacy"` pins the 2025-11-25 handshake and elicitation works.

  2. Inside the handler, `response_type` is NOT your Pydantic class. It is a dataclass rebuilt
     from the schema, living in a synthetic module named `types`. `response_type.__name__` is
     'Confirm' and `response_type.__module__` is 'types'; it has `__dataclass_fields__` and it
     does NOT have pydantic's `model_fields`. Read the fields from `__dataclass_fields__`.

Run:
    uv run python -m M11_capstone.code.lab_4_confirm_guard
"""
from __future__ import annotations

import asyncio
from typing import Any

from fastmcp import Client
from fastmcp.client.elicitation import ElicitResult

from M11_capstone.code.devops_assistant import mcp

SERVICE = "postgres-ha"


def make_handler(label: str):
    """Build a client-side handler that behaves the way `label` says.

    FOUR parameters. The callback does `await handler(...)`, so the function MUST be async —
    a sync `def` that returns a perfectly good dict dies on the await with
        ToolError: Error calling tool 'restart_service': object dict can't be used in 'await'
    """

    async def handler(message: str, response_type: Any, params: Any = None,
                      context: Any = None) -> Any:
        print(f"    [client] asked: {message}")
        print(f"    [client] response_type={response_type.__name__} "
              f"module={response_type.__module__} "
              f"fields={list(response_type.__dataclass_fields__)}")
        print(f"    [client] raw params type: {type(params).__name__}")
        if label == "accept":
            return {"proceed": True, "reason": "approved during the lab"}
        if label == "refuse":
            return {"proceed": False, "reason": "change board has not approved a window"}
        if label == "decline":
            return ElicitResult(action="decline")
        return ElicitResult(action="cancel")

    return handler


async def main() -> None:
    print("=== 1. the unprotected service never elicits at all ===")
    async with Client(mcp) as client:
        ordinary = (await client.call_tool("restart_service", {"service": "gitea"})).data
        print(f"  gitea -> {ordinary}")
        print("  no prompt was shown: the guard is scoped to PROTECTED_SERVICES, so the")
        print("  common case stays fast and no user is trained to click through dialogs.")

    print("\n=== 2. the protected service with the DEFAULT client ===")
    async with Client(mcp) as client:
        try:
            await client.call_tool("restart_service", {"service": SERVICE})
            print("  unexpectedly succeeded")
        except Exception as exc:
            print(f"  {type(exc).__name__}: {str(exc).splitlines()[0][:120]}")
    print("  This is the trap: the tool is correct and the CLIENT is wrong.")

    print("\n=== 3. the four outcomes, with mode='legacy' ===")
    for label in ("accept", "refuse", "decline", "cancel"):
        print(f"\n  --- {label} ---")
        async with Client(mcp, mode="legacy",
                          elicitation_handler=make_handler(label)) as client:
            print(f"    protocol era: {client.protocol_version}")
            data = (await client.call_tool("restart_service",
                    {"service": SERVICE, "reason": "replication lag 3.1s"})).data
            print(f"    server returned: {data}")
        if label in ("decline", "cancel"):
            print("    -> the user did not answer. Do not retry inside this flow.")

    print("\n=== 4. what the tool did to the host ===")
    print("  'action_taken': 'none — this capstone server does not modify the host'")
    print("  Read that literally. The GUARD is real; the restart is not. A capstone that")
    print("  really restarted postgres-ha on the machine running the course would be a")
    print("  liability, and a course that pretended otherwise would be teaching a lie.")

    print("\n=== 5. the handler contract, one more time ===")
    print("  async def handler(message, response_type, params, context) -> T | dict | ElicitResult")
    print("  4 positional args     : fewer -> MCPError 'takes from 2 to 3 positional arguments'")
    print("  async, always         : sync -> ToolError \"object dict can't be used in 'await'\"")
    print("  return a dict or model: ACCEPT (validated against the schema)")
    print("  ElicitResult('decline')/('cancel'): the user's answer, not an exception")
    print("  return None           : MCPError 'Invalid request parameters' — don't")


if __name__ == "__main__":
    asyncio.run(main())
