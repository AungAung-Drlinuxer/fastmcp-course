"""Lesson 2.4 — prompts: reusable instructions the client can offer by name.

A prompt is neither a tool nor data. It is a TEMPLATE the host application puts in front of the
user (or the model) as a starting point. The host decides how to surface it; the server just
declares it, with arguments that become its parameters.

The value is consistency: a root-cause analysis that always follows the same five steps,
however the user phrased the request.

Run:
    uv run python -m M7_prompts.code.highlight
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass

from fastmcp import Client, FastMCP
# Prompts may return str, or Message objects. A CUSTOM type must be wrapped: a bare
# dataclass raises "messages[0] must be Message or str, got GuidedStep" at render time —
# and only at render time, so it passes every list_prompts() call and fails in front of a
# user. Verified against FastMCP 4.0.5; see VERIFIED.md.
from fastmcp.prompts import Message

mcp = FastMCP("prompts-demo")


# A structured return value makes the prompt discoverable to a host that wants to render it
# differently (a form with a "next step" button, for instance). Plain strings are fine when
# there is nothing more to say.
@dataclass
class GuidedStep:
    """One step of a guided procedure."""

    title: str
    instruction: str


@mcp.prompt
def dns_lookup_failure(hostname: str, symptom: str = "name or service not known") -> list[Message]:
    """Walk through a DNS resolution failure, in order, without guessing.

    Args:
        hostname: The name that failed to resolve.
        symptom: The exact error text the user saw.
    """
    steps = [
        GuidedStep("Confirm the failure", f"Reproduce the lookup for {hostname} and capture the exact error: {symptom!r}."),
        GuidedStep("Check the record", f"Query the authoritative server for {hostname} and report what it returns."),
        GuidedStep("Check the resolver", "Read /etc/resolv.conf and confirm the nameserver is reachable on 53."),
        GuidedStep("Check the path", "Confirm UDP/TCP 53 is open between the client and the resolver."),
        GuidedStep("Report", "State which layer is at fault, and say so plainly if it is still unknown."),
    ]
    # One Message per step, so the host can render them as discrete items. Wrapping the whole
    # list in a single Message also works (the content is serialised) — the choice is about how
    # the host presents it, not about what the protocol allows.
    return [Message(step) for step in steps]


@mcp.prompt
def rca_over_logs(service: str, window_minutes: int = 15) -> str:
    """Produce a root-cause analysis outline over a service's recent logs.

    Args:
        service: The service to analyse.
        window_minutes: How far back to look.
    """
    return (
        f"You are performing a root cause analysis for `{service}` over the last "
        f"{window_minutes} minutes.\n\n"
        "Work in this order and do not skip a step:\n"
        "1. State what you actually observed, with the log lines that show it.\n"
        "2. Name the first anomalous event, not the loudest one.\n"
        "3. Give the causal chain from that event to the user-visible symptom.\n"
        "4. Say what evidence would DISPROVE your explanation.\n"
        "5. Recommend the smallest change that tests the explanation.\n\n"
        "If the logs do not support a conclusion, say 'insufficient evidence' and list what\n"
        "you would need. Do not speculate."
    )


@mcp.prompt
def highlight_sections(article: str, count: int = 3) -> str:
    """Ask for the most important sections of an article, and justify each choice.

    Args:
        article: The article title to summarise.
        count: How many sections to highlight.
    """
    return (
        f"Read the article {article!r}. Choose the {count} sections that matter most to "
        "someone who has ten minutes and needs the operative content — not the history, not "
        "the trivia.\n\n"
        "For each one, give: the section title, a two-sentence summary, and one line saying "
        "WHY it beats the sections you left out. If the article has fewer than "
        f"{count} substantive sections, say so instead of padding."
    )


async def main() -> None:
    async with Client(mcp) as client:
        print("=== the client can list prompts without calling them ===")
        for p in await client.list_prompts():
            args = [a.name for a in (p.arguments or [])]
            print(f"  {p.name:22} args={args}")
            print(f"    {p.description}")

        print("\n=== and render one with arguments ===")
        result = await client.get_prompt("rca_over_logs",
                                         {"service": "postgres-ha", "window_minutes": 30})
        print(result.messages[0].content.text[:420])

        print("\n=== a prompt with a structured return value ===")
        steps = await client.get_prompt("dns_lookup_failure",
                                        {"hostname": "git.drlinuxer.com"})
        print(f"  {len(steps.messages)} messages, one per guided step")
        for index, message in enumerate(steps.messages[:2], 1):
            print(f"  step {index}: {message.content.text[:110]}")
        print("  NOTE: returning the bare GuidedStep objects instead raises")
        print('    "messages[0] must be Message or str, got GuidedStep" — at RENDER time,')
        print("    so list_prompts() still succeeds and the failure only appears in front of")
        print("    a user. Verified against 4.0.5.")

    print("\n=== prompt vs tool vs resource ===")
    for kind, who_chooses, example in [
        ("tool", "the model, mid-task", "restart_service()"),
        ("resource", "the client, by reference", "runbook://postgres"),
        ("prompt", "the user, before the task", "rca_over_logs(service)"),
    ]:
        print(f"  {kind:9} chosen by {who_chooses:26} e.g. {example}")


if __name__ == "__main__":
    asyncio.run(main())
