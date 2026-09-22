"""LAB 4 — the README's hands-on task: write `ServerProvisionSchema` and prove it holds.

Five fields, four assertions. The point is that `required`, `minimum`, `maximum` and `enum` are
all GENERATED from the declarations — nothing is repeated, so nothing can drift.

Run:
    uv run python -m M2_types_pydantic.code.lab_4_server_schema
"""
from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, Field, ValidationError


class ServerProvisionSchema(BaseModel):
    """A request to provision a bare-metal server.

    Descriptions are written for the MODEL: they say what to put in the field, not what the
    field is called.
    """

    hostname: str = Field(description="Hostname of the server, e.g. web01")
    cpu_cores: int = Field(default=4, ge=1, le=64, description="Physical cores to assign (1-64)")
    memory_gb: int = Field(default=8, ge=2, description="Memory in GB (2 or more)")
    role: Literal["web", "db", "cache"] = Field(description="Role the server will play")
    tags: list[str] | None = Field(
        default=None,
        description="Optional labels, e.g. ['prod', 'eu-west']. Omit when the server is untagged.",
    )


REQUIREMENTS = {
    "hostname is the only string field": lambda s: s["properties"]["hostname"]["type"] == "string",
    "cpu_cores has minimum 1": lambda s: s["properties"]["cpu_cores"]["minimum"] == 1,
    "cpu_cores has maximum 64": lambda s: s["properties"]["cpu_cores"]["maximum"] == 64,
    "cpu_cores defaults to 4": lambda s: s["properties"]["cpu_cores"]["default"] == 4,
    "memory_gb has minimum 2": lambda s: s["properties"]["memory_gb"]["minimum"] == 2,
    "role is an enum of three": lambda s: s["properties"]["role"]["enum"] == ["web", "db", "cache"],
    "required is exactly {hostname, role}": lambda s: set(s["required"]) == {"hostname", "role"},
    "every field carries a description": lambda s: all(
        "description" in p for p in s["properties"].values()
    ),
}


def main() -> None:
    schema = ServerProvisionSchema.model_json_schema()

    print("=== ServerProvisionSchema.model_json_schema() ===")
    print(json.dumps(schema, indent=2))

    print()
    print("=== required vs optional, straight from the defaults ===")
    print(f"  required  : {schema['required']}")
    for name, field in ServerProvisionSchema.model_fields.items():
        print(f"  {name:12} is_required={field.is_required()!s:5} default={field.default!r}")

    print()
    print("=== the eight requirements ===")
    failed = 0
    for label, check in REQUIREMENTS.items():
        ok = check(schema)
        failed += 0 if ok else 1
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    print(f"  -> {len(REQUIREMENTS) - failed}/{len(REQUIREMENTS)} passed")

    print()
    print("=== a valid call, and what it dumps ===")
    server = ServerProvisionSchema(hostname="web01", role="web")
    print("  ", server)
    print("  model_dump()             :", server.model_dump())
    print("  model_dump(exclude_none=True):", server.model_dump(exclude_none=True))
    print("  model_dump_json()        :", server.model_dump_json())

    print()
    print("=== two rejected calls ===")
    for bad in (
        {"hostname": "web01", "role": "worker"},
        {"hostname": "web01", "role": "web", "cpu_cores": 128},
    ):
        try:
            ServerProvisionSchema(**bad)
            print("  ACCEPTED (should not have been):", bad)
        except ValidationError as exc:
            first = exc.errors()[0]
            print(f"  rejected loc={first['loc']} type={first['type']} input={first.get('input')!r}")


if __name__ == "__main__":
    main()
