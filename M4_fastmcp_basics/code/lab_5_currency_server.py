"""LAB 5 (part 1) — Calculator + Currency Converter, one server, two transports.

The server does not know or care how a client reaches it. Everything transport-specific
lives in `main()`, which is the whole lesson of file 06.

Rates are FIXED on purpose: a course lab must not depend on a network API, and the lesson
here is the transport, not the forex feed. Say so in the docstring so a model reading the
tool description is not misled — a tool that pretends to be live is worse than one that says
it is a fixture.

Run (stdio):
    uv run python -m M4_fastmcp_basics.code.lab_5_currency_server

Run (HTTP, port 8002):
    uv run python -m M4_fastmcp_basics.code.lab_5_currency_server --http
"""
from __future__ import annotations

import sys
from typing import Literal

from fastmcp import FastMCP

mcp = FastMCP("lab-calculator-fx")

# Fixed fixture rates, quoted as "units of the currency per 1 USD". Real deployments should
# read a rate table with an explicit timestamp; an unlabelled price is a trap for a model.
RATES_PER_USD: dict[str, float] = {
    "USD": 1.0,
    "MMK": 2100.0,
    "THB": 36.5,
    "EUR": 0.92,
    "SGD": 1.34,
}

Currency = Literal["USD", "MMK", "THB", "EUR", "SGD"]


def _ok(**payload: object) -> dict:
    return {"ok": True, **payload}


def _fail(code: str, hint: str) -> dict:
    """A structured failure the agent can act on. Same shape as M5's calculator."""
    return {"ok": False, "error": code, "hint": hint}


@mcp.tool
def add(a: float, b: float) -> dict:
    """Add two numbers.

    Args:
        a: The first number.
        b: The second number.
    """
    return _ok(result=a + b)


@mcp.tool
def divide(a: float, b: float) -> dict:
    """Divide a by b, reporting a zero denominator as data instead of raising.

    Args:
        a: The numerator.
        b: The denominator. Must not be zero.
    """
    if b == 0:
        return _fail("division_by_zero", "The denominator must be non-zero; try a different b.")
    return _ok(result=a / b)


@mcp.tool
def convert(amount: float, source: Currency, target: Currency) -> dict:
    """Convert an amount between two currencies using fixed fixture rates.

    Args:
        amount: How much to convert. Must be positive.
        source: The currency the amount is quoted in.
        target: The currency to convert into.
    """
    if amount <= 0:
        return _fail("non_positive_amount", "The amount must be greater than zero.")
    usd = amount / RATES_PER_USD[source]
    return _ok(result=round(usd * RATES_PER_USD[target], 4),
               source=source, target=target, rate_table="fixed fixture values per 1 USD")


@mcp.tool
def list_rates() -> dict:
    """List the fixed fixture rates this server will use."""
    return _ok(base="USD", rates=RATES_PER_USD, note="fixture values; not a live feed")


def main() -> None:
    if "--http" in sys.argv:
        mcp.run(transport="http", host="127.0.0.1", port=8002)
    else:
        mcp.run(transport="stdio", show_banner=False)


if __name__ == "__main__":
    main()
