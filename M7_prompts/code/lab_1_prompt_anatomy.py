"""LAB 1 — the smallest possible prompt: declare it, list it, render it.

A prompt is a TEMPLATE. The server declares it; the host lists it and renders it with
arguments. Nothing is called in the middle of a task the way a tool is.

Run:
    uv run python -m M7_prompts.code.lab_1_prompt_anatomy
"""
from __future__ import annotations

import asyncio

from fastmcp import Client, FastMCP

mcp = FastMCP("lab1-prompt-anatomy")


@mcp.prompt
def summarise_release(service: str, version: str = "unknown") -> str:
    """Summarise a release note into operational impact.

    Args:
        service: The service that was released.
        version: The version string that shipped.
    """
    return (
        f"Read the release notes for {service} version {version} and answer in this order:\n"
        "1. Which behaviour changed for callers?\n"
        "2. What breaks if nobody reads this note?\n"
        "3. One sentence a on-call engineer can act on tonight.\n"
        "If the note does not say something, write 'not stated' instead of guessing."
    )


async def main() -> None:
    async with Client(mcp) as client:
        print("=== list prompts: names and declared arguments ===")
        for prompt in await client.list_prompts():
            arguments = [(a.name, a.required) for a in (prompt.arguments or [])]
            print(f"  {prompt.name}  args={arguments}")
            print(f"    description: {prompt.description}")

        print("\n=== render it with both arguments ===")
        rendered = await client.get_prompt(
            "summarise_release",
            {"service": "billing-api", "version": "2.14.0"},
        )
        print(f"  messages={len(rendered.messages)} role={rendered.messages[0].role}")
        print(rendered.messages[0].content.text)

        print("\n=== render it with the default left out ===")
        rendered = await client.get_prompt("summarise_release", {"service": "billing-api"})
        print(rendered.messages[0].content.text.splitlines()[0])

        print("\n=== the prompt was never a tool and never a resource ===")
        print(f"  tools on the server:     {[t.name for t in await client.list_tools()]}")
        print(f"  resources on the server: {[r.uri for r in await client.list_resources()]}")


if __name__ == "__main__":
    asyncio.run(main())
