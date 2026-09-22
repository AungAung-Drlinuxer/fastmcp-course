"""Lesson 2.1 — the smallest server that is still a real server.

Four lines of substance. Everything the rest of the course adds is either a capability
(@mcp.tool / .resource / .prompt) or a transport decision (how the client reaches it).

Run it three ways:
    uv run python -m M4_fastmcp_basics.code.hello_server          # stdio, for an editor
    uv run fastmcp dev inspector M4_fastmcp_basics/code/hello_server.py
    uv run python -m M4_fastmcp_basics.code.hello_server --http   # HTTP, for the network
"""
from __future__ import annotations

import sys

from fastmcp import FastMCP

# The name is not decoration: it is reported to the client and appears in the banner, in the
# Inspector, and in every error the server returns. Use the system the server fronts.
mcp = FastMCP("course-hello")


@mcp.tool
def ping() -> str:
    """Return a fixed string, to prove the round trip works."""
    return "pong"


@mcp.tool
def add(a: float, b: float) -> float:
    """Add two numbers.

    Args:
        a: The first number.
        b: The second number.
    """
    return a + b


def main() -> None:
    if "--http" in sys.argv:
        # HTTP transport: reachable across the network, which is what a containerised server
        # in a lab needs. Streamable HTTP is the current transport; the older SSE transport is
        # still accepted for clients that predate it.
        mcp.run(transport="http", host="0.0.0.0", port=8000)
    else:
        # stdio: the server is a child process of the client. Nothing listens on a port, and
        # stdout belongs to the protocol — which is why every print() in a stdio server is a
        # bug. Diagnostics go to stderr or to ctx.info().
        mcp.run(transport="stdio", show_banner=False)


if __name__ == "__main__":
    main()
