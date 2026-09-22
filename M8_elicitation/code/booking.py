"""Lesson 3.1 — elicitation: the server asking the client a question.

Every other capability flows client -> server. Elicitation is the reverse: the server pauses
mid-tool and asks for information it does not have. For an IT assistant this is the difference
between "I cannot help without a date" and a tool that asks for the date and then books.

THREE THINGS YOU MUST GET RIGHT IN FASTMCP 4.x — all verified, see ../VERIFIED.md:

  1. mode="legacy" on the Client. The default (`mode="auto"`) negotiates the modern
     `2026-07-28` protocol era, which is sessionless, and elicitation then fails with:
        ToolError: elicitation via server-initiated requests is unavailable on
                   2026-07-28 connections.
     Pin the handshake era and it works.

  2. The handler takes FOUR arguments and may be async:
        async def handler(message, response_type, params, context) -> T | dict | ElicitResult

  3. The three outcomes are expressed by the RETURN VALUE:
        return {...} or a model        -> accept
        ElicitResult(action="decline") -> decline   (the user said no: do not retry)
        ElicitResult(action="cancel")  -> cancel    (the user walked away: stop cleanly)

Run:
    uv run python -m M8_elicitation.code.booking
"""
from __future__ import annotations

import asyncio
from typing import Any

from fastmcp import Client, Context, FastMCP
from fastmcp.client.elicitation import ElicitResult
from pydantic import BaseModel, Field

mcp = FastMCP("booking")


class BookingDetails(BaseModel):
    """The information needed to complete a booking."""

    date: str = Field(description="Travel date, ISO format (YYYY-MM-DD)")
    seat: str = Field(default="any", description="Seat preference: window, aisle, or any")


class Confirmation(BaseModel):
    """A yes/no confirmation before an irreversible action."""

    proceed: bool = Field(description="True to continue, false to stop")
    reason: str = Field(default="", description="Optional note explaining the decision")


BOOKINGS: list[dict[str, Any]] = []


@mcp.tool
async def book_flight(destination: str, ctx: Context) -> dict:
    """Book a flight, asking for the missing details before committing.

    Args:
        destination: Where the traveller is going.
    """
    # The schema is a Pydantic model, so the host renders a NATIVE FORM rather than asking the
    # user to type free text. That is the advantage of elicitation over a tool that simply
    # demands more arguments up front: the question appears only when it is needed.
    result = await ctx.elicit(
        message=f"What date and seat would you like for the flight to {destination}?",
        response_type=BookingDetails,
    )

    # Ask the RESULT what happened rather than importing a version-specific class name. In
    # FastMCP 2.x this was a single `ElicitationResult` type; in 4.x the accepted case carries
    # `.data` and declined/cancelled are separate classes. (`ElicitationResult` no longer
    # exists at all — the first thing an old tutorial gets wrong.)
    action = getattr(result, "action", "accept")
    if action != "accept":
        return {"ok": False, "status": action,
                "hint": "The booking was not made. Ask the user whether to try again."}

    details = result.data
    record = {"destination": destination,
              "date": getattr(details, "date", None),
              "seat": getattr(details, "seat", "any")}
    BOOKINGS.append(record)
    return {"ok": True, "status": "booked", "booking": record}


CLUSTER_PROTECTED = {"postgres-ha", "redis", "kasm-app"}


@mcp.tool
async def maintenance_window(service: str, ctx: Context) -> dict:
    """Confirm before touching a protected service — the pattern for any risky action.

    Args:
        service: The service the maintenance is for.
    """
    if service not in CLUSTER_PROTECTED:
        return {"ok": True, "status": "scheduled", "service": service,
                "note": "not a protected service, no confirmation required"}

    answer = await ctx.elicit(
        message=(f"About to schedule maintenance for the PROTECTED service {service!r}. "
                 "This affects live traffic. Proceed?"),
        response_type=Confirmation,
    )

    action = getattr(answer, "action", "accept")
    if action != "accept":
        return {"ok": False, "status": action, "service": service,
                "hint": "Nothing was scheduled."}
    if not answer.data.proceed:
        return {"ok": False, "status": "refused_by_user", "service": service,
                "reason": answer.data.reason or "no reason given"}
    return {"ok": True, "status": "scheduled", "service": service}


def make_handler(decision: str):
    """A client-side handler, i.e. what a HOST application implements.

    Four parameters, and it may be async — verified against fastmcp 4.0.5. In a real client this
    opens a form (form mode) or an external browser (URL mode). Here it is deterministic so the
    lesson can demonstrate all three outcomes.

    Declining is `ElicitResult(action="decline")`, NOT an exception and NOT `None`: the protocol
    distinguishes "no" from "failed", and a server that conflates them retries a user who has
    already said no.
    """
    async def handler(message: str, response_type: Any, params: Any = None,
                      context: Any = None) -> Any:
        print(f"    [client] the server asks: {message[:78]}{'...' if len(message) > 78 else ''}")
        if decision == "accept":
            return {"date": "2026-10-01", "seat": "window", "proceed": True, "reason": ""}
        if decision == "decline":
            return ElicitResult(action="decline")
        return ElicitResult(action="cancel")
    return handler


async def main() -> None:
    for decision in ("accept", "decline", "cancel"):
        print(f"=== client behaviour: {decision} ===")
        # mode="legacy" is REQUIRED for elicitation — see the module docstring.
        async with Client(mcp, mode="legacy", elicitation_handler=make_handler(decision)) as client:
            print(f"  protocol era: {client.protocol_version}")
            outcome = await client.call_tool("book_flight", {"destination": "Yangon"})
            print("  ->", outcome.data)
        print()

    print("=== the risky-action pattern ===")
    async with Client(mcp, mode="legacy", elicitation_handler=make_handler("accept")) as client:
        print("  protected:", (await client.call_tool("maintenance_window",
                                                      {"service": "postgres-ha"})).data)
        print("  ordinary :", (await client.call_tool("maintenance_window",
                                                      {"service": "gitea"})).data)

    print("\n=== the three outcomes are NOT the same failure ===")
    print("  accept  -> proceed with result.data")
    print("  decline -> the user said no. Do not retry; report it.")
    print("  cancel  -> the user abandoned the flow. Stop cleanly; keep no partial state.")
    print("  A server that retries on decline, or treats cancel as an error, trains users to")
    print("  stop answering prompts.")

    print("\n=== when to elicit, and when not to ===")
    print("  elicit for: a decision only the user can make (a date, a choice, a confirmation).")
    print("  do NOT elicit for: anything the server can find out itself. An assistant that")
    print("  stops to ask for the cluster name when it could have called cluster_list has moved")
    print("  its own work onto the user.")


if __name__ == "__main__":
    asyncio.run(main())
