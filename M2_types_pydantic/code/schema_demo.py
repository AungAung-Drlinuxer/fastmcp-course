"""Lesson 1.2 (part 3) — Pydantic does the schema AND the validation.

The difference from the hand-rolled generator in introspect.py: Pydantic keeps the two in
sync. The same class produces the JSON Schema the model reads AND rejects bad input at the
boundary, so a schema that lies about the constraints is impossible by construction.

Run:
    uv run python -m M2_types_pydantic.code.schema_demo
"""
from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, Field, ValidationError


class VMProvisionSchema(BaseModel):
    """A request to provision a virtual machine.

    The docstring becomes the model-facing description of the whole object; each Field
    description becomes the description of that property. Write them for the MODEL, not for
    a human colleague — "Name of the virtual machine" is more useful to a model deciding what
    to put in the field than "vm name".
    """

    vm_name: str = Field(description="Name of the virtual machine")
    cpu_cores: int = Field(default=2, ge=1, le=16, description="Virtual cores to assign (1-16)")
    os_type: Literal["ubuntu", "rocky", "windows"] = Field(description="Operating System")
    memory_gb: int | None = Field(
        default=None,
        ge=1,
        description="Memory in GB. Omit to let the platform choose a default for the OS.",
    )


def main() -> None:
    print("=== the JSON Schema the model is shown (generated, never hand-written) ===")
    print(json.dumps(VMProvisionSchema.model_json_schema(), indent=2))

    print("\n=== valid input ===")
    ok = VMProvisionSchema(vm_name="kasm-agent1", cpu_cores=16, os_type="ubuntu")
    print(" ", ok)
    print("  model_dump():", ok.model_dump())

    print("\n=== invalid input, and what the model is told ===")
    for bad in (
        {"vm_name": "x", "cpu_cores": 99, "os_type": "ubuntu"},          # over the maximum
        {"vm_name": "x", "cpu_cores": 0, "os_type": "ubuntu"},           # under the minimum
        {"vm_name": "x", "os_type": "Ubuntu 24.04"},                     # not in the Literal
        {"cpu_cores": 2, "os_type": "ubuntu"},                           # required field missing
    ):
        try:
            VMProvisionSchema(**bad)
            print(f"  ACCEPTED (should not have been): {bad}")
        except ValidationError as exc:
            first = exc.errors()[0]
            loc = ".".join(str(p) for p in first["loc"])
            print(f"  rejected {loc:12} {first['type']:20} {first.get('input')!r}")

    print("\n=== why ge/le beats a manual if-statement ===")
    print("  A hand-written check has to be repeated in the docstring, and the two drift.")
    print("  Here the SAME field declaration produced the schema above and rejected the 99.")
    print("  In M5 you will see this ValidationError arrive as a ToolError the model can read.")


if __name__ == "__main__":
    main()
