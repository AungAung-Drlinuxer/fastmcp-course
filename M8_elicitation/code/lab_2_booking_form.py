"""LAB 2 — the Flight Booking tool, in full.

A booking needs four facts. Two of them are worth asking for only when the user
actually wants the flight; two of them can be asked as a single native form.
This lab builds the tool, prints the JSON Schema the host would render, and
proves the schema is generated — never hand-written.

Run:
    uv run python -m M8_elicitation.code.lab_2_booking_form
"""
from __future__ import annotations

import asyncio
import json
from typing import Any, Literal

from fastmcp import Client, Context, FastMCP
from fastmcp.client.elicitation import ElicitResult
from pydantic import BaseModel, Field

mcp = FastMCP("booking-lab")


class BookingDetails(BaseModel):
    """The information needed to complete a booking."""

    date: str = Field(description="Travel date, ISO format (YYYY-MM-DD)")
    seat: Literal["window", "aisle", "any"] = Field(
        default="any", description="Seat preference"
    )
    meal: Literal["none", "vegetarian", "halal"] = Field(
        default="none", description="Meal preference"
    )
    contact_email: str = Field(description="Where the ticket should be sent")


BOOKINGS: list[dict[str, Any]] = []


@mcp.tool
async def book_flight(destination: str, ctx: Context) -> dict:
    """Book a flight, asking for the missing details before committing.

    Args:
        destination: Where the traveller is going.
    """
    result = await ctx.elicit(
        message=f"What date and seat would you like for the flight to {destination}?",
        response_type=BookingDetails,
    )

    action = getattr(result, "action", "accept")
    if action != "accept":
        return {"ok": False, "status": action,
                "made_up_detail": "no booking row was written"}

    details = result.data
    record = {
        "destination": destination,
        "date": getattr(details, "date", None),
        "seat": getattr(details, "seat", "any"),
        "meal": getattr(details, "meal", "none"),
        "contact_email": getattr(details, "contact_email", None),
    }
    BOOKINGS.append(record)
    return {"ok": True, "status": "booked", "booking": record}


@mcp.tool
async def list_bookings(ctx: Context) -> dict:
    """Show what is actually stored, so a declined booking is visibly absent."""
    return {"count": len(BOOKINGS), "bookings": list(BOOKINGS)}


def make_handler(decision: str):
    """A host implementation: one switch, three outcomes, no exceptions."""

    async def handler(message: str, response_type: Any, params: Any = None,
                      context: Any = None) -> Any:
        schema = getattr(params, "requested_schema", None)
        print(f"    [host] form fields: {list((schema or {}).get('properties', {}))}")
        print(f"    [host] required   : {(schema or {}).get('required')}")
        if decision == "accept":
            return {
                "date": "2026-10-01",
                "seat": "window",
                "meal": "vegetarian",
                "contact_email": "alice@example.com",
            }
        if decision == "decline":
            return ElicitResult(action="decline")
        return ElicitResult(action="cancel")

    return handler


def self_schema(tools) -> dict:
    """Read the tool's input schema with the SERVER-side attribute name."""
    for tool in tools:
        if tool.name == "book_flight":
            return tool.parameters          # server side: .parameters (not .inputSchema)
    return {}


async def main() -> None:
    # 1. The tool's OWN input schema — generated from the signature, never typed by hand.
    tools = await mcp.list_tools()
    print("registered tools:", [t.name for t in tools])
    print("book_flight parameters:",
          json.dumps(self_schema(tools), indent=2))
    print("(the FORM schema is a different thing — it is generated per elicit call)\n")

    for decision in ("accept", "decline", "cancel"):
        print(f"=== host behaviour: {decision} ===")
        async with Client(mcp, mode="legacy",
                          elicitation_handler=make_handler(decision)) as client:
            print("  protocol era:", client.protocol_version)
            print("  ->", (await client.call_tool(
                "book_flight", {"destination": "Yangon"})).data)
            print("  ->", (await client.call_tool("list_bookings", {})).data)
        print()


if __name__ == "__main__":
    asyncio.run(main())
