"""LAB 6 — nested models: a list of objects, and where the error points.

A flat schema can describe `vm_name` and `cpu_cores`. It cannot describe "a list of disks, each
with a size and a technology" without nesting a model inside a model. Nested models are how a
tool takes a STRUCTURED argument instead of `dict[str, Any]`.

The second thing this lab shows: when the error is three levels deep, `loc` tells you the whole
path — `('disks', 0, 'size_gb')`.

Run:
    uv run python -m M2_types_pydantic.code.lab_6_nested_models
"""
from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, Field, ValidationError


class Disk(BaseModel):
    """One disk attached to a virtual machine."""

    size_gb: int = Field(ge=1, le=4096, description="Disk size in GB (1-4096)")
    kind: Literal["ssd", "hdd"] = Field(default="ssd", description="Disk technology")


class NetworkInterface(BaseModel):
    """One network interface."""

    bridge: str = Field(description="Bridge to attach to, e.g. vmbr0")
    vlan: int | None = Field(default=None, ge=1, le=4094, description="Optional VLAN tag")


class VMProvisionSchema(BaseModel):
    """A request to provision a virtual machine with disks and interfaces."""

    vm_name: str = Field(description="Name of the virtual machine")
    cpu_cores: int = Field(default=2, ge=1, le=16, description="Virtual cores to assign (1-16)")
    os_type: Literal["ubuntu", "rocky", "windows"] = Field(description="Operating System")
    disks: list[Disk] = Field(default_factory=list, description="Disks to attach, in order")
    interfaces: list[NetworkInterface] = Field(
        default_factory=list, description="Network interfaces to attach"
    )


BAD_CASES: list[tuple[str, dict]] = [
    ("nested field below the minimum",
     {"vm_name": "x", "os_type": "ubuntu", "disks": [{"size_gb": 0}]}),
    ("nested field is the wrong type",
     {"vm_name": "x", "os_type": "ubuntu", "disks": [{"size_gb": "big"}]}),
    ("nested enum is wrong",
     {"vm_name": "x", "os_type": "ubuntu", "disks": [{"size_gb": 40, "kind": "nvme"}]}),
    ("nested required field missing",
     {"vm_name": "x", "os_type": "ubuntu", "disks": [{"kind": "ssd"}]}),
    ("second element is the bad one",
     {"vm_name": "x", "os_type": "ubuntu",
      "disks": [{"size_gb": 40}, {"size_gb": 99999}]}),
    ("error in a different nested model",
     {"vm_name": "x", "os_type": "ubuntu",
      "interfaces": [{"bridge": "vmbr0", "vlan": 9999}]}),
]


def main() -> None:
    schema = VMProvisionSchema.model_json_schema()

    print("=== a nested model becomes a $ref, and the definition moves to $defs ===")
    print("  top-level keys :", list(schema.keys()))
    print("  $defs keys     :", list(schema["$defs"].keys()))
    print()
    print(json.dumps(schema["$defs"]["Disk"], indent=2))
    print()
    print("  disks.items    :", json.dumps(schema["properties"]["disks"]["items"]))
    print("  $ref target    :", schema["properties"]["disks"]["items"]["$ref"])
    print("  interfaces.items:", json.dumps(schema["properties"]["interfaces"]["items"]))

    print()
    print("=== required at every level ===")
    print("  VMProvisionSchema.required :", schema["required"])
    print("  Disk.required              :", schema["$defs"]["Disk"]["required"])
    print("  NetworkInterface.required  :", schema["$defs"]["NetworkInterface"]["required"])

    print()
    print("=== a valid nested call, and the dump ===")
    vm = VMProvisionSchema(
        vm_name="kasm-agent1",
        os_type="ubuntu",
        disks=[{"size_gb": 40}, {"size_gb": 200, "kind": "hdd"}],
        interfaces=[{"bridge": "vmbr0", "vlan": 20}],
    )
    print("  ", vm)
    print("  model_dump()      :", vm.model_dump())
    print("  model_dump_json() :", vm.model_dump_json())
    print("  nested object type:", type(vm.disks[0]).__name__)

    print()
    print("=== where the error points when it is nested ===")
    print(f"  {'case':34} {'loc':24} {'type':20} input")
    for label, payload in BAD_CASES:
        try:
            VMProvisionSchema(**payload)
            print(f"  {label:34} {'ACCEPTED':24} {'-':20} -")
        except ValidationError as exc:
            first = exc.errors()[0]
            loc = ".".join(str(p) for p in first["loc"])
            print(f"  {label:34} {loc:24} {first['type']:20} {first.get('input')!r}")

    print()
    print("=== the nested error message a human reads ===")
    try:
        VMProvisionSchema(vm_name="x", os_type="ubuntu", disks=[{"size_gb": 99999}])
    except ValidationError as exc:
        print(str(exc))

    print()
    print("=== why this matters for a tool parameter ===")
    print("  `disks: list[dict[str, Any]]` gives the model no shape at all:")
    print("   ", json.dumps(Shapes.model_json_schema()["properties"]["plain_map"]))
    print("  `disks: list[Disk]` gives it size_gb, kind, and their constraints.")
    print("  A model that is handed a shape makes fewer wrong calls.")


class Shapes(BaseModel):
    """A control group: the same data described with `dict` instead of a model."""

    plain_map: dict[str, object] = Field(description="Whatever you like")


if __name__ == "__main__":
    main()
