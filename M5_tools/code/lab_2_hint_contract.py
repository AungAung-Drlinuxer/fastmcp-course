"""M5_tools LAB 2 — the hint field, and what an agent does without it.

No model is called here. The "agent" is a scripted chooser that follows one rule: read the
result, and if it contains a `hint`, do what the hint says; if it does not, repeat the call.
A scripted chooser makes the retry behaviour measurable instead of a story.

Run:
    uv run python -m M5_tools.code.lab_2_hint_contract
"""
from __future__ import annotations

import asyncio
import json

from fastmcp import Client, FastMCP

mcp = FastMCP("lab2-hint-contract")

SENSORS = {
    "boiler-01": {"temp_c": 81.4, "state": "nominal"},
    "boiler-02": {"temp_c": 94.9, "state": "high"},
    "pump-07": {"temp_c": 42.0, "state": "nominal"},
}


def _closest(name: str) -> str | None:
    """Cheap 'did you mean' — the server already knows the vocabulary, so say it."""
    lowered = name.lower().strip()
    for known in SENSORS:
        if lowered in known or known.split("-")[0] in lowered:
            return known
    return None


@mcp.tool
def read_sensor(sensor_id: str) -> dict:
    """Read the latest sample from a plant sensor.

    Args:
        sensor_id: The sensor identifier, one of boiler-01, boiler-02, pump-07.
    """
    if sensor_id not in SENSORS:
        suggestion = _closest(sensor_id)
        return {
            "ok": False,
            "error": "unknown_sensor",
            "hint": (f"'{sensor_id}' is not a sensor. Available: {', '.join(sorted(SENSORS))}. "
                     + (f"Did you mean '{suggestion}'?" if suggestion else "Pick one of those.")),
            "available": sorted(SENSORS),
            "did_you_mean": suggestion,
        }
    return {"ok": True, "sensor_id": sensor_id, **SENSORS[sensor_id]}


@mcp.tool
def read_sensor_bare(sensor_id: str) -> dict:
    """Read a sensor, failing without a hint — the pattern that wastes agent turns.

    Args:
        sensor_id: The sensor identifier.
    """
    if sensor_id not in SENSORS:
        return {"ok": False, "error": "unknown_sensor"}
    return {"ok": True, "sensor_id": sensor_id, **SENSORS[sensor_id]}


async def scripted_agent(client: Client, tool: str, first_call: dict, max_turns: int = 3) -> dict:
    """A deterministic stand-in for a model: obey the hint, or repeat the call verbatim."""
    args = dict(first_call)
    attempts = []
    for turn in range(1, max_turns + 1):
        result = await client.call_tool(tool, args, raise_on_error=False)
        body = result.structured_content or {}
        attempts.append({"turn": turn, "args": dict(args), "error": body.get("error")})
        if body.get("ok"):
            return {"turns": turn, "succeeded": True, "attempts": attempts}
        if "did_you_mean" in body and body["did_you_mean"]:
            args = {"sensor_id": body["did_you_mean"]}
            continue
        # No hint to act on: the scripted agent has nothing to change, so it retries as-is.
    return {"turns": max_turns, "succeeded": False, "attempts": attempts}


async def main() -> None:
    async with Client(mcp) as client:
        print("=== the failure body, verbatim ===")
        result = await client.call_tool("read_sensor", {"sensor_id": "boiler1"},
                                        raise_on_error=False)
        print(json.dumps(result.structured_content, indent=2))
        print(f"is_error={result.is_error}")

        print("\n=== scripted agent WITH a hint ===")
        with_hint = await scripted_agent(client, "read_sensor", {"sensor_id": "boiler1"})
        print(f"    succeeded   {with_hint['succeeded']}")
        print(f"    turns       {with_hint['turns']}")
        for attempt in with_hint["attempts"]:
            print(f"      turn {attempt['turn']}  args={attempt['args']}  "
                  f"error={attempt['error']}")

        print("\n=== scripted agent WITHOUT a hint ===")
        without = await scripted_agent(client, "read_sensor_bare", {"sensor_id": "boiler1"})
        print(f"    succeeded   {without['succeeded']}")
        print(f"    turns       {without['turns']}")
        for attempt in without["attempts"]:
            print(f"      turn {attempt['turn']}  args={attempt['args']}  "
                  f"error={attempt['error']}")
        print("\n    The identical call, three times. That is the cost of a missing hint.")


if __name__ == "__main__":
    asyncio.run(main())
