"""Extra: a render self-test — the CI gate that catches the custom-type trap.

`list_prompts()` succeeding proves nothing about whether a prompt can be rendered. This
script renders EVERY prompt with sample arguments and fails loudly, which is the check that
turns "it registered" into "it works".

Run:
    uv run python -m M7_prompts.code.extra_render_selftest
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass

from fastmcp import Client, FastMCP
from fastmcp.prompts import Message

mcp = FastMCP("render-selftest")


@dataclass
class GuidedStep:
    """One step of a guided procedure."""

    title: str
    instruction: str


@mcp.prompt
def plain_text(service: str) -> str:
    """Returns a str: always renders."""
    return f"Analyse {service} in five ordered steps."


@mcp.prompt
def many_strings(service: str) -> list[str]:
    """Returns list[str]: one message per item."""
    return [f"First check {service}.", f"Then report on {service}."]


@mcp.prompt
def wrapped_steps(service: str) -> list[Message]:
    """Returns list[Message]: renders, and the host can read roles."""
    return [Message(GuidedStep("Check", f"health of {service}"), role="user")]


@mcp.prompt
def un_wrapped_steps(service: str) -> list[GuidedStep]:
    """Return the custom type UNWRAPPED: registers, lists, and fails to render."""
    return [GuidedStep("Check", f"health of {service}")]


SAMPLE_ARGUMENTS: dict[str, dict] = {
    "plain_text": {"service": "postgres-ha"},
    "many_strings": {"service": "postgres-ha"},
    "wrapped_steps": {"service": "postgres-ha"},
    "un_wrapped_steps": {"service": "postgres-ha"},
}


async def main() -> None:
    failures: list[str] = []
    async with Client(mcp) as client:
        listed = await client.list_prompts()
        print(f"list_prompts() returned {len(listed)} prompts")
        print("  " + ", ".join(p.name for p in listed))

        print("\nrendering each one with sample arguments:")
        for prompt in listed:
            arguments = SAMPLE_ARGUMENTS.get(prompt.name, {})
            try:
                rendered = await client.get_prompt(prompt.name, arguments)
                first = rendered.messages[0].content.text[:70]
                print(f"  OK    {prompt.name:16} messages={len(rendered.messages)} "
                      f"role={rendered.messages[0].role} {first}")
            except Exception as exc:  # noqa: BLE001 — reporting the failure is the point
                failures.append(prompt.name)
                print(f"  FAIL  {prompt.name:16} {type(exc).__name__}: {exc}")

    print(f"\n{len(failures)} prompt(s) failed to render: {failures}")
    print("A registration-only check would have reported 4 OK. That is the trap.")


if __name__ == "__main__":
    asyncio.run(main())
