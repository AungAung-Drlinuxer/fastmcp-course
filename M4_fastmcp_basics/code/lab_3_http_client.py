"""LAB 3 (driver) — reach a server over HTTP instead of spawning it.

Two servers, one client. The tool code is identical between them; what differs is the URL
the client dials and who started the process.

Terminal A — start the HTTP server and LEAVE IT RUNNING:
    uv run python -m M4_fastmcp_basics.code.lab_1_echo_server --http

Terminal B — run this file:
    uv run python -m M4_fastmcp_basics.code.lab_3_http_client

This exact HTTP URL form was NOT executed in the course repository (the course VM had no
network port free at verification time). If it is rejected by your version, ask the CLI what
the right form is — it prints the transport it resolved:
    uv run fastmcp inspect http://127.0.0.1:8001/mcp
"""
from __future__ import annotations

import asyncio

from fastmcp import Client

# The streamable-HTTP endpoint is served under /mcp. Nothing else about this client changes:
# list_tools and call_tool are the same calls as over stdio.
HTTP_URL = "http://127.0.0.1:8001/mcp"


async def main() -> None:
    async with Client(HTTP_URL) as client:
        tools = await client.list_tools()
        print("=== over HTTP: the server is a process someone else started ===")
        print("  discovered:", [t.name for t in tools])
        print("  ping      ->", (await client.call_tool("ping", {})).data)
        print("  echo      ->", (await client.call_tool("echo", {"message": "over http"})).data)

        result = await client.call_tool("word_count", {"text": "one two\nthree"})
        print("  word_count->", result.data)
        # structured_content is the machine-readable half of the same result; see the
        # lesson file 10 for the full anatomy of a CallToolResult.
        print("  structured:", result.structured_content)
        print("  is_error  :", result.is_error)

    print()
    print("=== what did NOT change ===")
    print("  the tool functions, their names, their schemas, their return values")
    print("=== what DID change ===")
    print("  the client did not spawn anything; it dialled a port")
    print("  anything else that can reach that port can call these tools")
    print("  your print() statements are harmless here — stdout is not the protocol")


if __name__ == "__main__":
    asyncio.run(main())
