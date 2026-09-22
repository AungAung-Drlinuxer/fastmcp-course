"""M3 — decorator metadata, and the real cost of blocking I/O."""
from __future__ import annotations

import asyncio
import inspect

from M3_asyncio_decorators.code import async_io
from M3_asyncio_decorators.code.decorators import TOOLS, logged, naive_logger


def test_a_wrapper_without_functools_wraps_destroys_the_metadata_mcp_needs():
    def provision(vm_name: str, cpu_cores: int = 2) -> dict:
        """Provision a VM."""
        return {"vm_name": vm_name}

    wrapped = naive_logger(provision)
    # This is the failure the lesson is about: a tool registered from this has no name and no
    # parameters, so its generated schema is empty and nothing raises to say why.
    assert wrapped.__name__ == "wrapper"
    assert inspect.getdoc(wrapped) is None
    assert wrapped.__annotations__.get("return", None) is None

    preserved = logged(provision)
    assert preserved.__name__ == "provision"
    assert "Provision a VM" in (inspect.getdoc(preserved) or "")


def test_the_registry_decorator_captures_name_signature_and_docstring():
    # @register_tool is deliberately a stand-in for @mcp.tool: same three ingredients.
    assert "disk_usage" in TOOLS
    entry = TOOLS["disk_usage"]
    assert entry["description"].startswith("Report disk usage")
    assert set(entry["parameters"]) == {"path", "human"}
    assert entry["parameters"]["human"][1] is True          # the default survived


async def test_gather_is_faster_than_sequential():
    names = ["a", "b", "c", "d"]
    _, seq = await async_io.sequential(names)
    _, con = await async_io.concurrent(names)
    assert con < seq, "concurrent must beat sequential; if not, the await points are wrong"
    assert seq / con > 1.5


async def test_a_wait_for_timeout_is_caught_not_propagated_uncaught():
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(async_io.fetch("slow"), timeout=0.01)


import pytest  # noqa: E402  (kept below the module under test for readability)
