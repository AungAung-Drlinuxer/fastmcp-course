"""Lesson 2.1 (part 2) — what changes between stdio and HTTP.

The tool code does not change at all. What changes is who can reach the server, how the
process is supervised, and where your logging is allowed to go. Those three differences decide
which transport a deployment should use, so they are worth writing down before choosing.

This file is a reference, not a server: it runs a stdio server in a SUBPROCESS and talks to it
exactly the way an editor does, so the mechanism is visible rather than described.

Run:
    uv run python -m M4_fastmcp_basics.code.transports
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from fastmcp import Client

SERVER = Path(__file__).with_name("hello_server.py")


async def main() -> None:
    print("=== stdio: the client owns the process ===")
    print(f"  spawning: {sys.executable} -m M4_fastmcp_basics.code.hello_server")
    # A PythonStdioTransport launches the server as a child process and speaks JSON-RPC over
    # its stdin/stdout. This is exactly what Cline does with a `command` entry in its settings.
    async with Client(SERVER) as client:
        tools = await client.list_tools()
        print("  discovered:", [t.name for t in tools])
        print("  ping ->", (await client.call_tool("ping", {})).data)
        print("  add  ->", (await client.call_tool("add", {"a": 2, "b": 3})).data)

    print()
    print("=== the comparison ===")
    rows = [
        ("who starts it", "the client spawns a child process", "an operator/service manager"),
        ("reachable by", "that client only, on that machine", "anything that can reach the port"),
        ("auth", "the OS process boundary", "you must add it (M10)"),
        ("stdout", "IS the protocol — never print", "free for logs"),
        ("best for", "an editor on a laptop", "a shared or containerised server"),
    ]
    width = max(len(r[0]) for r in rows)
    for label, stdio, http in rows:
        print(f"  {label:<{width}}  stdio: {stdio:<34} http: {http}")

    print()
    print("=== the trap that costs the most time ===")
    print("  A stray print() in a stdio server corrupts the JSON-RPC stream. The client then")
    print("  reports a parse error and the student blames their tool. Use sys.stderr.write()")
    print("  or ctx.info(); never print() in a stdio server.")


if __name__ == "__main__":
    asyncio.run(main())
