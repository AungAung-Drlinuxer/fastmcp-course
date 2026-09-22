"""LAB 1 — a server you wrote yourself, four lines of substance.

The point of this file is that there is nothing in it you have not already read in
`hello_server.py`. You type it to prove to yourself that the shape is small: a name, a
decorator, a function, a `run()`.

Run (stdio — the way an editor starts it):
    uv run python -m M4_fastmcp_basics.code.lab_1_echo_server

Run (HTTP — the way the network reaches it):
    uv run python -m M4_fastmcp_basics.code.lab_1_echo_server --http
"""
from __future__ import annotations

import sys

from fastmcp import FastMCP

# The name is what the client is told this server IS. It is not the Python module name and it
# is not the file name; it is the label the host application shows a human.
mcp = FastMCP("lab-echo")


@mcp.tool
def ping() -> str:
    """Return a fixed string, to prove the round trip works."""
    return "pong"


@mcp.tool
def echo(message: str) -> str:
    """Return the message unchanged.

    Args:
        message: Any text. Returned verbatim so a client can verify the round trip.
    """
    return message


@mcp.tool
def word_count(text: str) -> dict:
    """Count characters, words and lines in a piece of text.

    Args:
        text: The text to measure. Newlines are significant.
    """
    return {
        "ok": True,
        "characters": len(text),
        "words": len(text.split()),
        "lines": len(text.splitlines()) or 1,
    }


def main() -> None:
    if "--http" in sys.argv:
        # Same three tools. Different transport: now anything on the network can reach them.
        mcp.run(transport="http", host="127.0.0.1", port=8001)
    else:
        # stdio. stdout belongs to the protocol, so no banner: the banner would be written
        # into the JSON-RPC stream. show_banner=False is the flag that keeps us honest.
        mcp.run(transport="stdio", show_banner=False)


if __name__ == "__main__":
    main()
