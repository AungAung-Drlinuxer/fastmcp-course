"""LAB 2 — the same parameter declared two ways: `str` versus `Literal`.

Both models accept a string. Only one of them tells the model which strings are legal. This
lab prints the two schemas side by side and then feeds the SAME bad value to each, so the
difference is visible as behaviour rather than as an opinion.

Run:
    uv run python -m M2_types_pydantic.code.lab_2_literal_contract
"""
from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, Field, ValidationError


class VagueRequest(BaseModel):
    """os_type is a free string: the contract says nothing useful."""

    vm_name: str = Field(description="Name of the virtual machine")
    os_type: str = Field(description="Operating System")


class PreciseRequest(BaseModel):
    """os_type is an enum: the contract names the legal values."""

    vm_name: str = Field(description="Name of the virtual machine")
    os_type: Literal["ubuntu", "rocky", "windows"] = Field(description="Operating System")


# The values a model plausibly sends for "which operating system".
SENT_BY_MODEL = [
    "ubuntu",
    "rocky",
    "Ubuntu 24.04",
    "ubuntu-server",
    "Ubuntu",
    "Windows Server 2022",
]


def try_model(model: type[BaseModel], payload: dict) -> str:
    """Return 'accepted' or the pydantic error type for one payload."""
    try:
        model(**payload)
        return "accepted"
    except ValidationError as exc:
        return exc.errors()[0]["type"]


def main() -> None:
    print("=== property schema: `str` vs `Literal` ===")
    vague = VagueRequest.model_json_schema()["properties"]["os_type"]
    precise = PreciseRequest.model_json_schema()["properties"]["os_type"]
    print("  str     :", json.dumps(vague))
    print("  Literal :", json.dumps(precise))

    print()
    print("=== what happens to the values a model actually sends ===")
    print(f"  {'value sent':24} {'os_type: str':22} {'os_type: Literal[...]'}")
    for value in SENT_BY_MODEL:
        left = try_model(VagueRequest, {"vm_name": "kasm-agent1", "os_type": value})
        right = try_model(PreciseRequest, {"vm_name": "kasm-agent1", "os_type": value})
        print(f"  {value:24} {left:22} {right}")

    print()
    print("=== the lesson in one line ===")
    print("  With `str` the bad value passes validation and fails later, inside YOUR code,")
    print("  where the error message no longer mentions the parameter.")
    print("  With `Literal` the bad value is rejected at the boundary and the schema told")
    print("  the caller the legal set BEFORE it ever called.")

    print()
    print("=== how the enum reaches the schema ===")
    print(f"  required: {PreciseRequest.model_json_schema()['required']}")
    print("  Field(description=...) still travels with the enum:")
    print("   ", json.dumps(precise.get("description")))


if __name__ == "__main__":
    main()
