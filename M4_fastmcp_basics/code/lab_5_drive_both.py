"""LAB 5 (part 2) — drive the SAME server over BOTH transports and compare.

Step 1: the in-process view. No transport at all — `Client(mcp)` talks to the server object
        inside this same Python process. This is how the test suite checks lesson code.
Step 2: stdio. The client spawns the server file as a child process.
Step 3: HTTP. The client dials a port; the server must already be running.

Steps 1 and 2 need nothing running. Step 3 prints an instruction and skips cleanly if the
server is not up, so this file is runnable at any moment.

Run:
    uv run python -m M4_fastmcp_basics.code.lab_5_drive_both

HTTP server for step 3 (separate terminal, leave it running):
    uv run python -m M4_fastmcp_basics.code.lab_5_currency_server --http
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastmcp import Client

from M4_fastmcp_basics.code.lab_5_currency_server import mcp

SERVER = Path(__file__).with_name("lab_5_currency_server.py")
HTTP_URL = "http://127.0.0.1:8002/mcp"

CALLS = [
    ("add", {"a": 2, "b": 3}),
    ("divide", {"a": 1, "b": 0}),
    ("convert", {"amount": 100.0, "source": "USD", "target": "MMK"}),
    ("convert", {"amount": 0.0, "source": "USD", "target": "MMK"}),
]


async def exercise(client: Client, label: str) -> None:
    """The same five lines work for every transport — that is the point of the comparison."""
    print(f"=== {label} ===")
    tools = await client.list_tools()
    print("  tools:", [t.name for t in tools])
    for name, arguments in CALLS:
        result = await client.call_tool(name, arguments)
        print(f"  {name:8} {json.dumps(arguments)} -> is_error={result.is_error} "
              f"data={result.data}")


async def main() -> None:
    print("=== 1. in-process: no transport, no child process ===")
    print("  server name reported by the object:", mcp.name)
    server_tools = await mcp.list_tools()
    print("  server-side schema lives at .parameters:",
          sorted(server_tools[0].parameters["properties"]))

    async with Client(mcp) as client:
        await exercise(client, "in-process client")

    print()
    print("=== 2. stdio: the client spawns the server ===")
    async with Client(SERVER) as client:
        await exercise(client, "stdio client")

    print()
    print("=== 3. http: the client dials a port ===")
    try:
        async with Client(HTTP_URL) as client:
            await exercise(client, "http client")
    except Exception as exc:
        print(f"  {type(exc).__name__}: {str(exc).splitlines()[0][:100]}")
        print("  nothing is listening on port 8002 — start it with:")
        print("    uv run python -m M4_fastmcp_basics.code.lab_5_currency_server --http")
        print("  and run this file again. This URL form over HTTP was not executed in the")
        print("  course repo; if your version rejects it, ask the CLI:")
        print("    uv run fastmcp inspect http://127.0.0.1:8002/mcp")

    print()
    print("=== what stayed identical ===")
    print("  tool names, arguments, schemas, return payloads, error shape")
    print("=== what changed ===")
    print("  who started the process, who can reach it, where logs may go")


if __name__ == "__main__":
    asyncio.run(main())
