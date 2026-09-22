"""LAB 8 — write your own prompt: forced step order plus an anti-hallucination clause.

The capstone's `rca_error_log` is the template. This lab writes a second one for a different
job and adds the three things a guide needs to be usable:

  1. A FORCED ORDER. "Work in this order and do not skip a step" is not politeness: the order
     is the reasoning method. Reading the runbook AFTER recommending is a different (worse)
     procedure than reading it before.

  2. A GROUNDING STEP BEFORE GENERATION. Step 4 reads the estate's own runbook. General
     knowledge is not the estate's knowledge: `synchronous_standby_names` and "never restart
     two instances together" are this organisation's rules, and only the runbook has them.

  3. AN EXIT FOR "I DO NOT KNOW". Without a stated way to answer 'insufficient evidence',
     a model under pressure to answer WILL answer. The clause is what makes honesty legal.

Deliberately written WITHOUT f-strings on the lines that must not be substituted, and WITH them
where the argument belongs — because the capstone's `capacity_review` shows the opposite mistake
in the wild: `config://{host}` sits there as a literal in a prompt whose whole purpose is to name
a host. This lab ends by rendering its own prompt so you can see the difference.

Run:
    uv run python -m M11_capstone.code.lab_8_incident_review_prompt
"""
from __future__ import annotations

import asyncio

from fastmcp import Client

# Attaches this prompt to the capstone's server object — no edit to devops_assistant.py.
from M11_capstone.code.devops_assistant import mcp


@mcp.prompt
def incident_review(service: str, minutes: int = 60) -> str:
    """Walk a service incident to a testable conclusion, with the estate's rules first.

    Args:
        service: The service to review, e.g. 'postgres-ha'.
        minutes: How far back the incident window extends.
    """
    return (
        f"Review the last {minutes} minutes of {service}. Work in this order and do not "
        "skip a step:\n\n"
        "1. Call `list_logs` and pick the log whose name matches the service. Say which one "
        "you picked and why. Do not guess a filename.\n"
        "2. Call `read_log` with `errors_only=true` and quote every line you rely on.\n"
        "3. Name the FIRST anomalous event — the earliest one by timestamp, not the most "
        "frequent one. State its timestamp explicitly.\n"
        f"4. Read `runbook://{service}` BEFORE you recommend anything. If that URI is "
        "unknown, call `list_runbooks` and pick the closest match. Quote the step that "
        "applies to your conclusion.\n"
        "5. State one observation that would DISPROVE your explanation.\n"
        "6. Recommend the smallest change that would test it, and say what you expect to "
        "see if you are right.\n\n"
        "If the logs do not support a conclusion, answer 'insufficient evidence' and list "
        "exactly which lines or fields you would need. Do not speculate, and do not invent "
        "log lines or runbook steps."
    )


async def main() -> None:
    async with Client(mcp) as client:
        print("=== 1. the prompt is registered beside the capstone's own ===")
        for prompt in await client.list_prompts():
            print(f"  {prompt.name:18} args={[a.name for a in (prompt.arguments or [])]}")

        print("\n=== 2. render it and READ it — this is the step people skip ===")
        rendered = await client.get_prompt("incident_review",
                                          {"service": "postgres-ha", "minutes": 45})
        text = rendered.messages[0].content.text
        print(text)

        print("\n=== 3. substitution check, the capstone's own bug in reverse ===")
        print(f"  'postgres-ha' appears : {'postgres-ha' in text}")
        print(f"  '{{service}}' remains   : {'{service}' in text}")
        print(f"  '{{minutes}}' remains   : {'{minutes}' in text}")
        print(f"  '45 minutes' appears  : {'the last 45 minutes' in text}")
        print("  For comparison, the capstone's capacity_review renders")
        print("    '1. Read `config://{host}` for its declared resources.'")
        print("  with the literal placeholder intact, because that line is not an f-string.")

        print("\n=== 4. runbook://{service} is a REAL uri here ===")
        runbook = (await client.read_resource("runbook://postgres-ha"))[0].text
        quoted = [line for line in text.splitlines() if "synchronous_standby_names" in line
                  or "replication lag" in line]
        print(f"  the runbook the prompt points at says: "
              f"{runbook.splitlines()[2].strip()!r}")
        print(f"  the prompt's grounding step is step 4: "
              f"{[l for l in text.splitlines() if l.startswith('4.')][0][:70]}...")
        print("  Matching them up is the whole point: the runbook is the estate's rules, not")
        print("  general knowledge, and the prompt forces it to be read before advice.")


if __name__ == "__main__":
    asyncio.run(main())
