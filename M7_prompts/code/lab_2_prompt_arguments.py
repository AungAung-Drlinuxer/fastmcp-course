"""LAB 2 — arguments: required, defaulted, coerced, missing, and extra.

The function signature IS the prompt's public contract. Whatever the host shows a user as a
form comes from these parameters, and nothing else.

Run:
    uv run python -m M7_prompts.code.lab_2_prompt_arguments
"""
from __future__ import annotations

import asyncio

from fastmcp import Client, FastMCP

mcp = FastMCP("lab2-prompt-arguments")


@mcp.prompt
def triage_alert(
    alert_name: str,
    service: str,
    window_minutes: int = 30,
    include_dashboards: bool = False,
) -> str:
    """Triage one alert with a fixed evidence order.

    Args:
        alert_name: The alert that fired.
        service: The service the alert belongs to.
        window_minutes: How far back the reviewer should look.
        include_dashboards: Whether to ask for dashboard links in the answer.
    """
    dashboards = "List the dashboards that would show this." if include_dashboards else "Skip dashboards."
    return (
        f"Triage the alert {alert_name!r} on {service!r} using only the last "
        f"{window_minutes} minutes of data.\n"
        "1. Restate the alert condition in one sentence.\n"
        "2. Say whether the condition is currently true, with evidence.\n"
        "3. Name the smallest safe action.\n"
        f"{dashboards}\n"
        "If the data is not available, answer 'insufficient evidence' and list what is missing."
    )


async def show(label: str, arguments: dict) -> None:
    """Render one call and print the first line, or print the exact error."""
    async with Client(mcp) as client:
        try:
            rendered = await client.get_prompt("triage_alert", arguments)
            headline = rendered.messages[0].content.text.splitlines()[0]
            print(f"{label:22} -> {headline}")
        except Exception as exc:  # noqa: BLE001 — we are printing the error on purpose
            print(f"{label:22} -> {type(exc).__name__}: {exc}")


async def main() -> None:
    async with Client(mcp) as client:
        print("=== what the host sees as the form ===")
        for prompt in await client.list_prompts():
            for argument in prompt.arguments or []:
                print(f"  {argument.name:20} required={argument.required}")
                print(f"    {argument.description}")

    print("\n=== the same prompt, called six different ways ===")
    await show("all args", {"alert_name": "HighErrorRate", "service": "checkout",
                            "window_minutes": 60, "include_dashboards": True})
    await show("defaults used", {"alert_name": "HighErrorRate", "service": "checkout"})
    await show("int sent as string", {"alert_name": "HighErrorRate", "service": "checkout",
                                      "window_minutes": "60"})
    await show("extra argument", {"alert_name": "HighErrorRate", "service": "checkout",
                                  "urgency": "high"})
    await show("missing required", {"alert_name": "HighErrorRate"})
    await show("wrong name", {"alert": "HighErrorRate", "service": "checkout"})


if __name__ == "__main__":
    asyncio.run(main())
