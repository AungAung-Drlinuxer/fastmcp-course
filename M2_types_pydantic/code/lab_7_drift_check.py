"""LAB 7 — drift, and why one declaration prevents it.

A hand-written validator has the rule in TWO places: the code that checks it, and the prose that
describes it. Change one and forget the other and the schema now lies. This lab makes that
happening visible: it changes the real limit and shows the hand-written description still
claiming the old one, while the Pydantic schema follows automatically.

Run:
    uv run python -m M2_types_pydantic.code.lab_7_drift_check
"""
from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

# ---------------------------------------------------------------------------------------------
# The hand-written version: the limit lives in the `if`, and again in the docstring.
# ---------------------------------------------------------------------------------------------

MAX_CORES_V1 = 16
MAX_CORES_V2 = 4


def hand_written_plan(vm_name: str, cpu_cores: int = 2, os_type: str = "ubuntu") -> dict:
    """Plan a virtual machine.

    Args:
        vm_name: Name of the virtual machine.
        cpu_cores: Virtual cores to assign (1-16).
        os_type: Which operating system image to use.
    """
    if not 1 <= cpu_cores <= MAX_CORES_V2:
        raise ValueError(f"cpu_cores must be between 1 and {MAX_CORES_V2}")
    if os_type not in ("ubuntu", "rocky", "windows"):
        raise ValueError(f"os_type must be one of ubuntu, rocky, windows (got {os_type!r})")
    return {"vm_name": vm_name, "cpu_cores": cpu_cores, "os_type": os_type}


HAND_WRITTEN_DESCRIPTION = "Virtual cores to assign (1-16)."

# ---------------------------------------------------------------------------------------------
# The Pydantic version: the number appears ONCE.
# ---------------------------------------------------------------------------------------------


class VMProvisionSchema(BaseModel):
    """A request to provision a virtual machine."""

    vm_name: str = Field(description="Name of the virtual machine")
    cpu_cores: int = Field(default=2, ge=1, le=MAX_CORES_V2,
                           description=f"Virtual cores to assign (1-{MAX_CORES_V2})")
    os_type: Literal["ubuntu", "rocky", "windows"] = Field(description="Operating System")


def main() -> None:
    print("=== the hand-written validator: the rule is written twice ===")
    print(f"  the `if` enforces        : 1..{MAX_CORES_V2}")
    print(f"  the docstring says       : {HAND_WRITTEN_DESCRIPTION}")
    print("  -> two statements of the same rule. They can disagree. Here they DO.")

    print()
    print("=== what the caller is told, versus what is enforced ===")
    print(f"  documented maximum : 16")
    print(f"  enforced maximum   : {MAX_CORES_V2}")
    for cores in (2, 4, 5, 16):
        try:
            hand_written_plan("kasm-agent1", cpu_cores=cores)
            print(f"  hand_written_plan(cpu_cores={cores:3}) -> accepted")
        except ValueError as exc:
            print(f"  hand_written_plan(cpu_cores={cores:3}) -> ValueError: {exc}")

    print()
    print("=== the same information, as a schema ===")
    print("  A hand-rolled schema can only print the text:")
    print(json.dumps({"cpu_cores": {"type": "integer", "default": 2,
                                    "description": HAND_WRITTEN_DESCRIPTION}}, indent=2))
    print("  A model caller with 5 cores reads `cpu_cores` as legal, and then gets a")
    print("  ValueError it cannot connect back to the parameter.")

    print()
    print("=== the Pydantic version: one declaration, two outputs ===")
    schema = VMProvisionSchema.model_json_schema()
    core_property = schema["properties"]["cpu_cores"]
    print("  schema cpu_cores :", json.dumps(core_property))
    print(f"  schema maximum   : {core_property['maximum']}")
    print(f"  schema description: {core_property['description']!r}")
    print("  -> the number in `le=` also produced the maximum AND the description text.")
    for cores in (2, 4, 5, 16):
        try:
            VMProvisionSchema(vm_name="kasm-agent1", cpu_cores=cores, os_type="ubuntu")
            print(f"  VMProvisionSchema(cpu_cores={cores:3}) -> accepted")
        except ValidationError as exc:
            first = exc.errors()[0]
            print(f"  VMProvisionSchema(cpu_cores={cores:3}) -> rejected "
                  f"loc={first['loc']} type={first['type']} ctx={first.get('ctx')}")

    print()
    print("=== prove the drift is real, not hypothetical ===")
    documented = 16
    enforced = MAX_CORES_V2
    print(f"  hand-written: documented={documented} enforced={enforced} "
          f"-> drift = {documented != enforced}")
    print(f"  pydantic    : maximum={core_property['maximum']} "
          f"enforced={MAX_CORES_V2} -> drift = "
          f"{core_property['maximum'] != MAX_CORES_V2}")

    print()
    print("=== change the constant and watch both move together ===")
    print("  Edit MAX_CORES_V2 = 4 to 8 and re-run this file.")
    print("  - hand-written: the `if` changes, the docstring text does NOT (you must edit it)")
    print("  - pydantic: the schema maximum AND the description change, because both are")
    print("    f-strings built from the same constant")


if __name__ == "__main__":
    main()
