"""M5_tools LAB 3 — Pydantic validates the REQUEST; you never re-check types.

Every bad argument below is rejected before the function body runs. The tool never sees it,
so there is no `if not isinstance(x, float): raise` anywhere in this file — and that is the
lesson: type checking at the tool boundary is already done for you.

Run:
    uv run python -m M5_tools.code.lab_3_validate_the_boundary
"""
from __future__ import annotations

import asyncio
from typing import Annotated, Literal

from fastmcp import Client, FastMCP
from pydantic import Field

mcp = FastMCP("lab3-validate-the-boundary")


@mcp.tool
def set_fan_speed(
    fan_id: Annotated[str, Field(min_length=3, description="Fan identifier, e.g. 'fan-a1'.")],
    percent: Annotated[int, Field(ge=0, le=100, description="Target speed, 0-100.")],
    ramp: Literal["instant", "smooth"] = "smooth",
) -> dict:
    """Set a fan to a percentage of full speed.

    Args:
        fan_id: Which fan to change.
        percent: Target speed as a percentage.
        ramp: How to reach the target.
    """
    # There is no isinstance check here on purpose: Pydantic already refused anything that
    # is not an int in 0..100 before this line ran.
    return {"ok": True, "fan_id": fan_id, "percent": percent, "ramp": ramp}


@mcp.tool
def plan_window(count: Annotated[int, Field(ge=1, le=10)], label: str) -> dict:
    """Plan a number of maintenance windows.

    Args:
        count: How many windows to plan, 1-10.
        label: A short label for the plan.
    """
    return {"ok": True, "count": count, "label": label, "windows": list(range(1, count + 1))}


def error_codes(message: str) -> list[str]:
    """Pull the machine-readable error types out of a Pydantic message."""
    return sorted({part.split("type=")[1].split(",")[0]
                   for part in message.split()
                   if part.startswith("[type=") and "type=" in part})


async def try_call(client: Client, name: str, args: dict) -> tuple[str, str]:
    """Return (outcome, detail) — never raises, so the table always prints in full."""
    try:
        result = await client.call_tool(name, args)
        return "ACCEPTED", str(result.data)
    except Exception as exc:
        first = str(exc).splitlines()[0]
        return "REJECTED", f"{type(exc).__name__}: {first} | codes={error_codes(str(exc))}"


async def main() -> None:
    async with Client(mcp) as client:
        print("=== the schema the client sees (generated, never hand-written) ===")
        for tool in await client.list_tools():
            if tool.name == "set_fan_speed":
                for key, spec in tool.input_schema["properties"].items():
                    print(f"    {key:9} {spec}")
                print(f"    required  {tool.input_schema['required']}")

        cases = [
            ("set_fan_speed", {"fan_id": "fan-a1", "percent": 40}),
            ("set_fan_speed", {"fan_id": "fan-a1", "percent": 140}),
            ("set_fan_speed", {"fan_id": "fan-a1", "percent": -1}),
            ("set_fan_speed", {"fan_id": "fan-a1", "percent": 40.5}),
            ("set_fan_speed", {"fan_id": "fan-a1", "percent": "half"}),
            ("set_fan_speed", {"fan_id": "a1", "percent": 40}),
            ("set_fan_speed", {"percent": 40}),
            ("set_fan_speed", {"fan_id": "fan-a1", "percent": 40, "ramp": "warp"}),
            ("set_fan_speed", {"fan_id": "fan-a1", "percent": 40, "speed": 9}),
            ("plan_window", {"count": 3, "label": "q3"}),
            ("plan_window", {"count": 0, "label": "q3"}),
            ("plan_window", {"count": 3.0, "label": "q3"}),
        ]

        print("\n=== requests, as the client sends them ===")
        for name, args in cases:
            outcome, detail = await try_call(client, name, args)
            print(f"    {name}({args})")
            print(f"        -> {outcome}  {detail}")


if __name__ == "__main__":
    asyncio.run(main())
