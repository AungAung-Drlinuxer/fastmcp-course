"""M8 — elicitation, including the mode requirement that old tutorials do not mention."""
from __future__ import annotations

from fastmcp import Client

from M8_elicitation.code.booking import mcp, make_handler


async def test_elicitation_requires_the_legacy_protocol_era():
    """Measured: the default `auto` negotiates 2026-07-28, which is sessionless and rejects
    server-initiated requests with 'elicitation ... unavailable on 2026-07-28 connections'."""
    async with Client(mcp, elicitation_handler=make_handler("accept")) as client:
        try:
            await client.call_tool("book_flight", {"destination": "Yangon"})
        except Exception as exc:
            assert "unavailable on 2026-07-28" in str(exc)
        else:
            raise AssertionError(
                "the default mode now supports elicitation — update VERIFIED.md and M8")


async def test_legacy_mode_enables_it():
    async with Client(mcp, mode="legacy", elicitation_handler=make_handler("accept")) as client:
        # the handshake era, not the sessionless modern one
        assert client.protocol_version != "2026-07-28"
        result = await client.call_tool("book_flight", {"destination": "Yangon"})
        assert result.data["ok"] is True
        assert result.data["booking"]["destination"] == "Yangon"
        assert result.data["booking"]["date"] == "2026-10-01"


async def test_decline_is_not_an_error_and_is_reported_as_a_decision():
    import M8_elicitation.code.booking as booking

    booking.BOOKINGS.clear()                    # module-level state; the test owns it
    async with Client(mcp, mode="legacy", elicitation_handler=make_handler("decline")) as client:
        data = (await client.call_tool("book_flight", {"destination": "Yangon"})).data

    assert data["ok"] is False
    assert data["status"] == "decline"          # distinct from "cancel" and from an error
    assert "hint" in data
    # The decisive assertion: a declined booking recorded NOTHING.
    assert booking.BOOKINGS == []


async def test_cancel_is_distinct_from_decline():
    async with Client(mcp, mode="legacy", elicitation_handler=make_handler("cancel")) as client:
        data = (await client.call_tool("book_flight", {"destination": "Yangon"})).data
    assert data["status"] == "cancel"


async def test_a_protected_service_asks_and_an_ordinary_one_does_not():
    async with Client(mcp, mode="legacy", elicitation_handler=make_handler("accept")) as client:
        protected = (await client.call_tool("maintenance_window", {"service": "postgres-ha"})).data
        ordinary = (await client.call_tool("maintenance_window", {"service": "gitea"})).data
    assert protected["status"] == "scheduled"
    assert ordinary["status"] == "scheduled" and "confirmation" in ordinary["note"]
