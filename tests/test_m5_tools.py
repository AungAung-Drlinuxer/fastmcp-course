"""M5 — a structured failure is data; a raised exception is not."""
from __future__ import annotations

from fastmcp import Client

from M5_tools.code.calculator import mcp as calc
from M5_tools.code.wikipedia import mcp as wiki


async def test_structured_error_is_returned_as_success_with_a_plan():
    async with Client(calc) as client:
        result = await client.call_tool("divide", {"a": 1, "b": 0})
    data = result.data
    assert data["ok"] is False
    assert data["error"] == "division_by_zero"
    assert data["hint"], "the hint is the part the model reads"
    # It is NOT a protocol-level failure — the tool succeeded at reporting a situation.
    assert result.is_error is False


async def test_raising_gives_the_model_no_plan():
    async with Client(calc) as client:
        try:
            await client.call_tool("safe_divide", {"a": 1, "b": 0})
        except Exception as exc:
            assert "division" in str(exc).lower() or "zero" in str(exc).lower()
        else:
            raise AssertionError("expected a raised error")


async def test_successful_paths():
    async with Client(calc) as client:
        assert (await client.call_tool("divide", {"a": 9, "b": 3})).data["result"] == 3.0
        assert (await client.call_tool("sqrt_of", {"x": 16})).data["result"] == 4.0
        neg = (await client.call_tool("sqrt_of", {"x": -1})).data
        assert neg["ok"] is False and neg["error"] == "negative_input"


async def test_wikipedia_tools_work_offline_via_fixtures_and_say_so():
    """The lab may be air-gapped, so the source is reported rather than assumed."""
    async with Client(wiki) as client:
        search = (await client.call_tool("search_articles", {"query": "mcp"})).data
        assert search["ok"] is True
        assert search["source"] in {"live", "fixture"}
        assert search["count"] >= 1

        sections = (await client.call_tool("list_sections", {"article": "Model Context Protocol"})).data
        assert sections["count"] >= 1

        content = (await client.call_tool("get_content", {"article": "Model Context Protocol"})).data
        assert content["length"] >= len(content["content"])
        assert isinstance(content["truncated"], bool)


async def test_limit_is_clamped_rather_than_trusted():
    async with Client(wiki) as client:
        out = (await client.call_tool("search_articles", {"query": "x", "limit": 9999})).data
        assert out["ok"] is True
