"""LAB 2 (driver) — talk to the deliberately broken server and read the failure.

A client does not tell you "your server printed something". It tells you it could not parse
what came back. The skill this lab teaches is mapping that message back to the print().

Run:
    uv run python -m M4_fastmcp_basics.code.lab_2_client_demo
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from fastmcp import Client

# Path(...) rather than a plain string: string paths still work but emit
# FastMCPDeprecationWarning on 4.0.5 and will be removed in FastMCP 5 (see VERIFIED.md).
BROKEN = Path(__file__).with_name("lab_2_stdout_trap.py")


async def main() -> None:
    print("=== discovering tools from a server with a stray print() ===")
    try:
        async with Client(BROKEN) as client:
            tools = await client.list_tools()
            print("  discovered:", [t.name for t in tools])
            print("  add(2, 3) ->", (await client.call_tool("add", {"a": 2, "b": 3})).data)
    except Exception as exc:
        # The class name is the diagnostic. A JSONDecodeError / parse error here means the
        # stream was corrupted, and the only thing that corrupts a stdio stream is a write to
        # stdout from outside the protocol.
        print(f"  {type(exc).__name__}: {str(exc).splitlines()[0][:120]}")
        print("  -> the server, not your tool, wrote to stdout. Remove the print().")

    print()
    print("=== the fix ===")
    print("  Replace print(...) with sys.stderr.write(...) or ctx.info(...).")
    print("  stdout is the protocol. stderr is for humans.")


if __name__ == "__main__":
    asyncio.run(main())
