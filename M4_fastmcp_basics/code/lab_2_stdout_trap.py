"""LAB 2 — the trap: one stray print() in a stdio server.

This file is DELIBERATELY BROKEN. Do not fix it until the lab tells you to. The bug is the
line marked `# <-- THE BUG`. It looks harmless, it is the first thing anyone writes while
debugging, and in a stdio server it destroys the protocol stream.

Run it under a client and read the error the CLIENT reports, not the error you expected:
    uv run python -m M4_fastmcp_basics.code.lab_2_stdout_trap
    uv run python -m M4_fastmcp_basics.code.lab_2_client_demo
"""
from __future__ import annotations

import sys

from fastmcp import FastMCP

mcp = FastMCP("lab-stdout-trap")


@mcp.tool
def add(a: float, b: float) -> float:
    """Add two numbers.

    Args:
        a: The first number.
        b: The second number.
    """
    print(f"add({a}, {b}) called")          # <-- THE BUG: this goes to stdout
    return a + b


@mcp.tool
def status() -> dict:
    """Report what the server thinks it is doing."""
    # This one is correct: diagnostics go to stderr, which is NOT the protocol stream.
    sys.stderr.write("status() called; writing to stderr, which is safe\n")
    return {"ok": True, "tools": ["add", "status"], "transport": "stdio"}


def main() -> None:
    mcp.run(transport="stdio", show_banner=False)


if __name__ == "__main__":
    main()
