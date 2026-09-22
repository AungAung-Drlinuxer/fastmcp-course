"""Mini-exercise: reproduce the trap with your own dataclass, and predict the index.

Question before running: does the error report messages[0] or messages[1]?

Run:
    uv run python -m M7_prompts.code.mini_exercise_trap
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass

from fastmcp import Client, FastMCP
from fastmcp.prompts import Message

mcp = FastMCP("mini-exercise-trap")


@dataclass
class Finding:
    """One finding from a review."""

    severity: str
    detail: str


def build_findings(target: str) -> list[Finding]:
    """The findings, shared by the broken and the fixed prompt."""
    return [Finding("high", "missing timeout"), Finding("low", "unused import")]


@mcp.prompt
def review_findings(target: str) -> list:
    """BROKEN ON PURPOSE: a str at index 0, a bare dataclass at index 1."""
    return [
        "Findings for " + target,
        Finding("high", "missing timeout"),
        Finding("low", "unused import"),
    ]


@mcp.prompt
def review_findings_fixed(target: str) -> list[Message]:
    """Fixed: keep the structure, wrap each finding."""
    return [Message(finding) for finding in build_findings(target)]


async def main() -> None:
    async with Client(mcp) as client:
        print(f"listed: {[p.name for p in await client.list_prompts()]}\n")

        for name in ("review_findings", "review_findings_fixed"):
            try:
                rendered = await client.get_prompt(name, {"target": "checkout-api"})
                print(f"{name}: OK messages={len(rendered.messages)}")
                for message in rendered.messages:
                    print(f"   ({message.role}) {message.content.text}")
            except Exception as exc:  # noqa: BLE001 — the error is the answer
                print(f"{name}: {type(exc).__name__}: {exc}")

        print("\nThe annotation says `list` on the broken prompt and `list[Message]` on the")
        print("fixed one — but the runtime does not check annotations. Only the actual")
        print("Message(...) wrapping changes the outcome.")


if __name__ == "__main__":
    asyncio.run(main())
