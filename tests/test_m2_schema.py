"""M2 — the schema is generated, and the constraints are real.

These assertions are the VERIFIED.md table turned into checks, so the lesson cannot drift from
the API: if a future FastMCP changes how `Field(ge=…, le=…)` is rendered, this fails here
instead of surprising a student.
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from M2_types_pydantic.code.schema_demo import VMProvisionSchema


def test_schema_is_generated_with_constraints_and_enum():
    schema = VMProvisionSchema.model_json_schema()
    props = schema["properties"]

    assert props["cpu_cores"]["minimum"] == 1
    assert props["cpu_cores"]["maximum"] == 16
    assert props["cpu_cores"]["default"] == 2
    assert props["os_type"]["enum"] == ["ubuntu", "rocky", "windows"]
    # descriptions travel to the model; they are part of the contract, not decoration
    assert props["vm_name"]["description"]
    assert props["os_type"]["description"]


def test_required_versus_optional_follows_the_defaults():
    required = set(VMProvisionSchema.model_json_schema()["required"])
    assert required == {"vm_name", "os_type"}          # no default -> required
    assert "cpu_cores" not in required                 # default -> optional
    assert "memory_gb" not in required                 # default=None -> optional


@pytest.mark.parametrize("payload,expected_field", [
    ({"vm_name": "x", "cpu_cores": 99, "os_type": "ubuntu"}, "cpu_cores"),
    ({"vm_name": "x", "cpu_cores": 0, "os_type": "ubuntu"}, "cpu_cores"),
    ({"vm_name": "x", "os_type": "Ubuntu 24.04"}, "os_type"),
])
def test_invalid_input_is_rejected_and_names_the_field(payload, expected_field):
    with pytest.raises(ValidationError) as excinfo:
        VMProvisionSchema(**payload)
    assert expected_field in str(excinfo.value.errors()[0]["loc"])


def test_a_missing_required_field_is_rejected():
    with pytest.raises(ValidationError):
        VMProvisionSchema(cpu_cores=2, os_type="ubuntu")
