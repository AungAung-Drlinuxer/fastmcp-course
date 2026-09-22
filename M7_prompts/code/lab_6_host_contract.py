"""LAB 6 — the host contract: list with arguments, render by name, fail loudly.

This is the exact code a host application runs. Nothing here calls a tool and nothing here
reads a resource; a prompt is offered to the user before the task starts, so the host needs
the list plus a rendering call.

Run:
    uv run python -m M7_prompts.code.lab_6_host_contract
"""
from __future__ import annotations

import asyncio

from fastmcp import Client, FastMCP

mcp = FastMCP("lab6-host-contract")


@mcp.prompt
def explain_failure(symptom: str, depth: int = 2) -> str:
    """Explain a failure at a chosen depth.

    Args:
        symptom: The symptom the user reported.
        depth: 1 = one paragraph, 2 = causes and checks.
    """
    if depth <= 1:
        return f"Explain the likely cause of {symptom!r} in one paragraph. Say 'unclear' if it is."
    return (
        f"Explain the failure {symptom!r} as:\n"
        "1. The cause, if known.\n"
        "2. The two checks that would confirm it.\n"
        "3. The check to run first, and why.\n"
        "If no cause is supported, say 'insufficient evidence' and list what is missing."
    )


@mcp.prompt
def weekly_report(team: str) -> str:
    """Draft a weekly report skeleton.

    Args:
        team: The team the report is for.
    """
    return f"Draft the weekly report for {team}: shipped, blocked, next, risks."


async def main() -> None:
    async with Client(mcp) as client:
        prompts = await client.list_prompts()

        print("=== the form the host draws ===")
        for prompt in prompts:
            print(f"[{prompt.name}] {prompt.description}")
            arguments = prompt.arguments or []
            if not arguments:
                print("  (no arguments)")
            for argument in arguments:
                flag = "required" if argument.required else "optional"
                print(f"  --{argument.name:<10} ({flag})")

        print("\n=== render each one exactly as a menu pick would ===")
        picks = [
            ("explain_failure", {"symptom": "connection reset by peer", "depth": 2}),
            ("explain_failure", {"symptom": "connection reset by peer", "depth": 1}),
            ("weekly_report", {"team": "platform"}),
        ]
        for name, arguments in picks:
            rendered = await client.get_prompt(name, arguments)
            texts = [message.content.text for message in rendered.messages]
            print(f"  {name}({arguments}) -> {len(texts)} message(s), {len(texts[0])} chars")
            print(f"    {texts[0].splitlines()[0]}")

        print("\n=== a host must handle these two failures ===")
        failures = [
            ("unknown name", "no_such_prompt", {}),
            ("missing required", "explain_failure", {}),
        ]
        for label, name, arguments in failures:
            try:
                await client.get_prompt(name, arguments)
                print(f"  {label:18} -> unexpectedly succeeded")
            except Exception as exc:  # noqa: BLE001 — the error text is the lesson
                print(f"  {label:18} -> {type(exc).__name__}: {exc}")

        print("\n=== listing worked the whole time: that is the trap in one line ===")
        print(f"  list_prompts() returned {len(prompts)} prompts even though some calls fail")


if __name__ == "__main__":
    asyncio.run(main())
