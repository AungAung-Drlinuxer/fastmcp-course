"""Extra: a template is testable WITHOUT a model — check the text it produces.

Every phrasing of the request must produce the same skeleton. This script is the
consistency check used in tutorial file 03.

Run:
    uv run python -m M7_prompts.code.extra_consistency_check
"""
from __future__ import annotations

import asyncio

from fastmcp import Client, FastMCP

mcp = FastMCP("consistency-check")


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


FINGERPRINT = [
    "in this order",
    "1. State what you actually observed",
    "2. Name the first anomalous event, not the loudest one.",
    "3. Give the causal chain",
    "4. Say what evidence would DISPROVE",
    "5. Recommend the smallest change",
    "insufficient evidence",
    "Do not speculate",
]


async def main() -> None:
    phrasings = [
        {"service": "postgres-ha"},
        {"service": "postgres-ha", "window_minutes": 600},
        {"service": "checkout-api", "window_minutes": 5},
    ]
    async with Client(mcp) as client:
        rendered = []
        for arguments in phrasings:
            result = await client.get_prompt("rca_over_logs", arguments)
            text = result.messages[0].content.text
            rendered.append(text)
            missing = [marker for marker in FINGERPRINT if marker not in text]
            print(f"  {arguments} -> missing={missing}")

        steps = ("1.", "2.", "3.", "4.", "5.")
        structure = [line for line in rendered[0].splitlines() if line.startswith(steps)]
        same = all(
            [line for line in other.splitlines() if line.startswith(steps)] == structure
            for other in rendered
        )
        print(f"\n  the five ordered steps are identical in every phrasing: {same}")
        print(f"  step 2 forbids the loudest-event shortcut: {'not the loudest one' in rendered[0]}")
        print(f"  the template is {len(rendered[0])} characters, whatever the arguments were")


if __name__ == "__main__":
    asyncio.run(main())
