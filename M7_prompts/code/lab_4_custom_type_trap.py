"""LAB 4 — the custom-type trap, reproduced and then fixed.

Returning a dataclass from `@mcp.prompt` registers without complaint and `list_prompts()`
succeeds. The failure appears only when a client renders it:

    MCPError: Error rendering prompt 'bare_steps': messages[0] must be Message or str,
              got GuidedStep. Use Message(GuidedStep(...)) to wrap the value.

This lab captures that error, then shows the two working forms.

Run:
    uv run python -m M7_prompts.code.lab_4_custom_type_trap
"""
from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass

from fastmcp import Client, FastMCP
from fastmcp.prompts import Message

mcp = FastMCP("lab4-custom-type-trap")


@dataclass
class GuidedStep:
    """One step of a guided procedure."""

    title: str
    instruction: str


def build_steps(hostname: str, symptom: str) -> list[GuidedStep]:
    """The steps themselves are shared by both prompts below."""
    return [
        GuidedStep("Confirm the failure", f"Reproduce the lookup for {hostname}: {symptom!r}."),
        GuidedStep("Check the record", f"Query the authoritative server for {hostname}."),
        GuidedStep("Check the resolver", "Read /etc/resolv.conf and confirm port 53 is reachable."),
        GuidedStep("Report", "Name the faulty layer, or say it is still unknown."),
    ]


@mcp.prompt
def bare_steps(hostname: str, symptom: str = "name or service not known") -> list[GuidedStep]:
    """BROKEN ON PURPOSE: returns the dataclass unwrapped."""
    return build_steps(hostname, symptom)


@mcp.prompt
def dropped_steps(hostname: str, symptom: str = "name or service not known") -> list[str]:
    """FIX 1: flatten each step into a string yourself."""
    return [f"{step.title}: {step.instruction}" for step in build_steps(hostname, symptom)]


@mcp.prompt
def wrapped_steps(hostname: str, symptom: str = "name or service not known") -> list[Message]:
    """FIX 2: keep the structure and wrap each step in a Message."""
    return [Message(step) for step in build_steps(hostname, symptom)]


async def main() -> None:
    async with Client(mcp) as client:
        print("=== registration succeeds for all three ===")
        for prompt in await client.list_prompts():
            print(f"  {prompt.name:16} args={[a.name for a in (prompt.arguments or [])]}")

        print("\n=== retrieval is where the difference shows ===")
        for name in ("bare_steps", "dropped_steps", "wrapped_steps"):
            try:
                rendered = await client.get_prompt(name, {"hostname": "git.drlinuxer.com"})
                print(f"  {name:16} OK  messages={len(rendered.messages)}")
                print(f"    first message: {rendered.messages[0].content.text[:96]}")
            except Exception as exc:  # noqa: BLE001 — printing the error is the point
                print(f"  {name:16} {type(exc).__name__}: {exc}")

        print("\n=== what a wrapped step actually serialises to ===")
        rendered = await client.get_prompt("wrapped_steps", {"hostname": "git.drlinuxer.com"})
        first = rendered.messages[0]
        print(f"  role:            {first.role}")
        print(f"  content type:    {type(first.content).__name__}")
        print(f"  content.text:    {first.content.text}")
        print(f"  model_dump():    {first.content.model_dump()}")
        print(f"  one Message per step, so the host can render {len(rendered.messages)} items")

        print("\n=== the same dataclass, flattened by hand, is still valid ===")
        for step in build_steps("git.drlinuxer.com", "name or service not known")[:1]:
            print(f"  asdict: {asdict(step)}")


if __name__ == "__main__":
    asyncio.run(main())
