"""LAB 6 — URL mode: send the user to a browser for the sensitive part.

Some questions must never be typed into a form: an API key, an OAuth consent, a
card number. URL mode hands the user a link, the browser does the sensitive
part out of band, and the tool resumes with only the outcome.

Measured in FastMCP 4.0.5:
  * `ctx.elicit(...)` is FORM mode only — it has no `url` parameter.
  * URL mode is reached with `await ctx.session.elicit_url(...)`, which returns a
    plain `ElicitResult` (`action` + `content=None`), not an `AcceptedElicitation`.
  * the host handler receives params with `mode == "url"` and `response_type is None`.

Run:
    uv run python -m M8_elicitation.code.lab_6_url_flow
"""
from __future__ import annotations

import asyncio
from typing import Any

from fastmcp import Client, Context, FastMCP
from fastmcp.client.elicitation import ElicitResult

mcp = FastMCP("url-flow")

CREDENTIALS: dict[str, str] = {}


@mcp.tool
async def connect_calendar(ctx: Context) -> dict:
    """Ask the user to authorise calendar access, out of band, in a browser."""
    result = await ctx.session.elicit_url(
        message=("Calendar access needs your authorisation. Open the link below, "
                 "approve the request, then come back."),
        url="https://auth.example.com/oauth/authorize?client=assistant&scope=calendar",
        elicitation_id="calendar-consent-001",
        related_request_id=ctx.request_id,
    )
    if result.action != "accept":
        return {"ok": False, "status": result.action,
                "note": "no credential was stored"}

    # The browser did the sensitive part; the server never saw the secret.
    CREDENTIALS["calendar"] = "oauth-handshake-completed"
    return {"ok": True, "status": "authorised", "scope": "calendar"}


@mcp.tool
async def credential_status(ctx: Context) -> dict:
    """Only the fact of authorisation is ever readable — never the token."""
    return {"authorised": sorted(CREDENTIALS)}


def make_handler(action: str):
    async def handler(message: str, response_type: Any, params: Any = None,
                      context: Any = None) -> Any:
        mode = getattr(params, "mode", "?")
        print(f"    [host] mode={mode!r} response_type={response_type!r}")
        print(f"    [host] message={message}")
        if mode == "url":
            print(f"    [host] url={params.url!r}")
            print(f"    [host] elicitation_id={params.elicitation_id!r}")
        if action == "accept":
            return ElicitResult(action="accept")
        return ElicitResult(action=action)

    return handler


async def main() -> None:
    for action in ("accept", "decline", "cancel"):
        print(f"=== the user {action}s the browser flow ===")
        async with Client(mcp, mode="legacy",
                          elicitation_handler=make_handler(action)) as client:
            print("  ->", (await client.call_tool("connect_calendar", {})).data)
            print("  ->", (await client.call_tool("credential_status", {})).data)
        print()


if __name__ == "__main__":
    asyncio.run(main())
