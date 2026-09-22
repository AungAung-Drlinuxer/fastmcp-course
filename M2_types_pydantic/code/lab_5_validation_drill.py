"""LAB 5 — read a ValidationError like a debugger, not like a stack trace.

Eight bad payloads, one table. For each: where the error happened (`loc`), which rule it broke
(`type`), and the value that broke it (`input`). Once you can read this table, a schema bug in a
tool call stops being mysterious in Phase 2.

Run:
    uv run python -m M2_types_pydantic.code.lab_5_validation_drill
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, ValidationError


class Disk(BaseModel):
    """One attached disk."""

    size_gb: int = Field(ge=1, le=4096, description="Disk size in GB (1-4096)")
    kind: Literal["ssd", "hdd"] = Field(default="ssd", description="Disk technology")


class VMProvisionSchema(BaseModel):
    """A request to provision a virtual machine."""

    vm_name: str = Field(description="Name of the virtual machine")
    cpu_cores: int = Field(default=2, ge=1, le=16, description="Virtual cores to assign (1-16)")
    os_type: Literal["ubuntu", "rocky", "windows"] = Field(description="Operating System")
    memory_gb: int | None = Field(default=None, ge=1, description="Memory in GB. Omit for default.")
    disks: list[Disk] = Field(default_factory=list, description="Disks to attach")


DRILLS: list[tuple[str, dict]] = [
    ("over the maximum", {"vm_name": "kasm-agent1", "cpu_cores": 99, "os_type": "ubuntu"}),
    ("under the minimum", {"vm_name": "kasm-agent1", "cpu_cores": 0, "os_type": "ubuntu"}),
    ("not in the Literal", {"vm_name": "kasm-agent1", "os_type": "Ubuntu 24.04"}),
    ("required field missing", {"cpu_cores": 2, "os_type": "ubuntu"}),
    ("wrong scalar type", {"vm_name": 123, "os_type": "ubuntu"}),
    ("string that looks like an int", {"vm_name": "x", "os_type": "ubuntu", "cpu_cores": "eight"}),
    ("optional field present but too small", {"vm_name": "x", "os_type": "ubuntu", "memory_gb": 0}),
    ("error inside a nested model", {"vm_name": "x", "os_type": "ubuntu", "disks": [{"size_gb": 0}]}),
    ("three errors at once", {"cpu_cores": 99, "os_type": "nope", "memory_gb": 0}),
]


def main() -> None:
    print("=== the drill: one bad payload per row ===")
    print(f"  {'case':36} {'loc':22} {'type':24} input")
    for label, payload in DRILLS:
        try:
            VMProvisionSchema(**payload)
            print(f"  {label:36} {'ACCEPTED':22} {'-':24} -")
        except ValidationError as exc:
            first = exc.errors()[0]
            loc = ".".join(str(p) for p in first["loc"])
            print(f"  {label:36} {loc:22} {first['type']:24} {first.get('input')!r}")

    print()
    print("=== how many errors are raised at once ===")
    try:
        VMProvisionSchema(cpu_cores=99, os_type="nope", memory_gb=0)
    except ValidationError as exc:
        print("  error_count() =", exc.error_count())
        for err in exc.errors():
            print(f"    loc={err['loc']} type={err['type']} msg={err['msg']}")

    print()
    print("=== the full dict for ONE error — every key you can rely on ===")
    try:
        VMProvisionSchema(vm_name="kasm-agent1", cpu_cores=99, os_type="ubuntu")
    except ValidationError as exc:
        print("  ", exc.errors()[0])

    print()
    print("=== the same failure as a human reads it ===")
    try:
        VMProvisionSchema(vm_name="kasm-agent1", cpu_cores=99, os_type="ubuntu")
    except ValidationError as exc:
        print(str(exc))

    print()
    print("=== ValidationError is a ValueError, so `except ValueError` catches it ===")
    print("  MRO:", [c.__name__ for c in ValidationError.__mro__[:3]])

    print()
    print("=== coercion: what Pydantic accepts without being asked ===")
    for value in ("8", 8.0, True, "eight"):
        try:
            model = VMProvisionSchema(vm_name="x", os_type="ubuntu", cpu_cores=value)
            print(f"  cpu_cores={value!r:10} -> accepted as {model.cpu_cores!r}")
        except ValidationError as exc:
            print(f"  cpu_cores={value!r:10} -> rejected ({exc.errors()[0]['type']})")


if __name__ == "__main__":
    main()
