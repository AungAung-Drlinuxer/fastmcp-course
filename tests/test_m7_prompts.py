"""M7 — a prompt that registers is not a prompt that renders.

The failure this file exists for: returning a custom type registers fine, list_prompts()
succeeds, and the error only appears when a client retrieves the prompt —
  "messages[0] must be Message or str, got GuidedStep".
"""
from __future__ import annotations

from fastmcp import Client

from M7_prompts.code.highlight import GuidedStep, mcp


async def test_prompts_are_discoverable_with_their_arguments():
    async with Client(mcp) as client:
        prompts = {p.name: p for p in await client.list_prompts()}
    assert {"dns_lookup_failure", "rca_over_logs", "highlight_sections"} <= set(prompts)
    assert {a.name for a in prompts["rca_over_logs"].arguments} == {"service", "window_minutes"}


async def test_a_plain_string_prompt_renders():
    async with Client(mcp) as client:
        result = await client.get_prompt("rca_over_logs",
                                        {"service": "postgres-ha", "window_minutes": 30})
    text = result.messages[0].content.text
    assert "postgres-ha" in text and "30" in text
    assert "insufficient evidence" in text          # the anti-hallucination instruction survives


async def test_arguments_are_injected():
    async with Client(mcp) as client:
        result = await client.get_prompt("highlight_sections", {"article": "Kubernetes", "count": 3})
    assert "Kubernetes" in result.messages[0].content.text


async def test_a_custom_type_must_be_wrapped_in_Message():
    async with Client(mcp) as client:
        result = await client.get_prompt("dns_lookup_failure", {"hostname": "git.drlinuxer.com"})
    # One Message per guided step, because the code wraps each GuidedStep.
    assert len(result.messages) == 5
    assert all(m.content.text for m in result.messages)
    assert "git.drlinuxer.com" in result.messages[0].content.text


def test_the_dataclass_is_the_thing_that_would_break():
    step = GuidedStep("t", "i")
    assert not isinstance(step, str), "a bare dataclass is exactly what the wrapper is for"
