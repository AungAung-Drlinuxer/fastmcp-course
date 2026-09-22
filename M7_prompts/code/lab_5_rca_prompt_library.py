"""LAB 5 — a prompt library: forced ordering, stop conditions, no speculation.

Three prompts that share one house style: a numbered procedure, an explicit stop condition,
and the insufficient-evidence clause. The point of a library is that every engineer who
picks any of these gets the SAME shape of answer.

Run:
    uv run python -m M7_prompts.code.lab_5_rca_prompt_library
"""
from __future__ import annotations

import asyncio

from fastmcp import Client, FastMCP

mcp = FastMCP("lab5-rca-library")

NO_SPECULATION = (
    "If the evidence does not support a conclusion, answer 'insufficient evidence' and list "
    "what you would need. Do not speculate."
)


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
        f"{NO_SPECULATION}"
    )


@mcp.prompt
def rca_over_deploy(service: str, version: str) -> str:
    """Root-cause analysis scoped to a deploy, with a stop condition.

    Args:
        service: The service that was deployed.
        version: The version that shipped.
    """
    return (
        f"The deploy of {service} {version} is suspect. Work in this order:\n"
        "1. State the exact time the new version started serving traffic.\n"
        "2. List every symptom that began within five minutes of it.\n"
        "3. Confirm or reject the deploy as cause, with one piece of evidence.\n"
        "4. If rejected, stop and say so — do not search for another cause in this pass.\n\n"
        f"{NO_SPECULATION}"
    )


@mcp.prompt
def rca_over_incident(service: str, incident_id: str, severity: str = "sev3") -> str:
    """Post-incident review skeleton, severity-scoped.

    Args:
        service: The service involved.
        incident_id: The incident identifier.
        severity: One of sev1, sev2, sev3.
    """
    detail = {"sev1": "minute by minute", "sev2": "five-minute buckets"}.get(severity, "hourly summary")
    return (
        f"Write the review for incident {incident_id} on {service} at severity {severity}. "
        f"Use a {detail} timeline.\n"
        "1. Impact, stated in user-visible terms.\n"
        "2. Timeline, as chosen above.\n"
        "3. Contributing factors, at least two.\n"
        "4. What detection was missing.\n"
        "Stop after the timeline if the record has gaps; list the gaps instead of filling them.\n\n"
        f"{NO_SPECULATION}"
    )


async def main() -> None:
    async with Client(mcp) as client:
        print("=== the library as a host would list it ===")
        for prompt in await client.list_prompts():
            print(f"  {prompt.name:18} args={[a.name for a in (prompt.arguments or [])]}")
            print(f"    {prompt.description}")

        print("\n=== every prompt carries the same house style ===")
        calls = [
            ("rca_over_logs", {"service": "postgres-ha", "window_minutes": 30}),
            ("rca_over_deploy", {"service": "checkout", "version": "2.14.0"}),
            ("rca_over_incident", {"service": "auth", "incident_id": "INC-4412", "severity": "sev1"}),
        ]
        for name, arguments in calls:
            rendered = await client.get_prompt(name, arguments)
            text = rendered.messages[0].content.text
            numbered = text.count("\n1.") + text.count("\n2.")
            has_stop = "stop" in text.lower() or "do not skip" in text
            print(f"  {name:18} numbered_steps={numbered}"
                  f" no_speculation={'insufficient evidence' in text}"
                  f" stop_condition={has_stop}")

        print("\n=== one full render ===")
        rendered = await client.get_prompt("rca_over_logs", {"service": "postgres-ha"})
        print(rendered.messages[0].content.text)


if __name__ == "__main__":
    asyncio.run(main())
