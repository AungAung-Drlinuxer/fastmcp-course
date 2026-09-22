"""M6 — a template is not a resource, and the distinction is observable."""
from __future__ import annotations

import pytest
from fastmcp import Client

from M6_resources.code.runbooks import mcp


async def test_static_and_templated_resources_are_listed_separately():
    static = await mcp.list_resources()
    templates = await mcp.list_resource_templates()
    assert [str(r.uri) for r in static] == ["inventory://hosts"]
    # A URI-templated resource does NOT appear in list_resources() — this is the trap.
    assert [t.uri_template for t in templates] == ["runbook://{service}"]


async def test_attribute_is_snake_case_in_4x():
    (template,) = await mcp.list_resource_templates()
    assert hasattr(template, "uri_template")
    assert not hasattr(template, "uriTemplate"), "camelCase was 2.x; if this passes, the API moved"


async def test_reading_each_kind():
    async with Client(mcp) as client:
        inventory = await client.read_resource("inventory://hosts")
        assert "pve01" in inventory[0].text

        for service in ("postgres", "redis"):
            contents = await client.read_resource(f"runbook://{service}")
            assert contents[0].text.startswith("#")


async def test_an_unknown_resource_fails_loudly_and_lists_alternatives():
    """Returning "" would read to a model as 'this runbook is empty' — worse than 'unknown'."""
    async with Client(mcp) as client:
        with pytest.raises(Exception) as excinfo:
            await client.read_resource("runbook://nginx")
        message = str(excinfo.value)
        assert "nginx" in message
        assert "postgres" in message and "redis" in message
