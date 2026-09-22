"""LAB 5 — the reducer, measured. 4 messages or 1, depending on one annotation.

Also measures what happens when the chooser names a tool that does not exist: the graph does NOT
crash. `ToolNode` turns the unknown name into a `ToolMessage` containing the error text, and the
model gets to read it and try again. That is the single most important behaviour to know before
you let a real model drive a real server.

Run:
    uv run python -m M9_clients.code.lab_5_state_reducer
"""
from __future__ import annotations

import asyncio
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import StructuredTool
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition


async def echo(text: str) -> str:
    """Echo the text back.

    Args:
        text: Any text.
    """
    return f"echo:{text}"


ECHO = StructuredTool.from_function(coroutine=echo, name="echo", description="Echo the text back.")


class WithReducer(TypedDict):
    """messages is a LIST plus a rule for merging. add_messages appends (and de-duplicates by id)."""

    messages: Annotated[list[BaseMessage], add_messages]


class NoReducer(TypedDict):
    """messages is just a list. Nothing says how to combine two of them, so the last write wins."""

    messages: list[BaseMessage]


def make_agent(report_state: bool = False):
    async def agent(state) -> dict:
        if report_state:
            print(f"    [agent sees {len(state['messages'])} message(s), "
                  f"last={type(state['messages'][-1]).__name__}]")
        last = state["messages"][-1]
        if isinstance(last, ToolMessage):
            return {"messages": [AIMessage(content="final")]}
        return {"messages": [AIMessage(content="", tool_calls=[
            {"name": "echo", "args": {"text": "hi"}, "id": "call_echo"}])]}

    return agent


def build(state_cls, agent, tools: list[StructuredTool], node: ToolNode | None = None):
    graph = StateGraph(state_cls)
    graph.add_node("agent", agent)
    graph.add_node("tools", node or ToolNode(tools))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")
    return graph.compile()


async def main() -> None:
    print("=== same graph, two state definitions ===")
    for state_cls, label in ((WithReducer, "Annotated[list[BaseMessage], add_messages]"),
                             (NoReducer, "list[BaseMessage]")):
        print(f"\n  --- {label} ---")
        app = build(state_cls, make_agent(report_state=(state_cls is NoReducer)), [ECHO])
        out = await app.ainvoke({"messages": [HumanMessage("go")]})
        print(f"    final message count = {len(out['messages'])}")
        for message in out["messages"]:
            print(f"      {type(message).__name__:12} {str(message.content)[:36]!r}")
    print("\n  The reducer version keeps the whole transcript. The plain list version keeps ONE")
    print("  message, because the tools node's return replaced the list the agent had written.")
    print("  With a real model that means the model re-asks for a tool it already ran — forever.")

    print("\n=== what the chooser's unknown tool name actually does ===")
    async def bad_agent(state) -> dict:
        last = state["messages"][-1]
        if isinstance(last, ToolMessage):
            return {"messages": [AIMessage(content="giving up: " + str(last.content)[:52])]}
        return {"messages": [AIMessage(content="", tool_calls=[
            {"name": "delete_everything", "args": {}, "id": "call_nope"}])]}

    for label, node in (("ToolNode([echo])", ToolNode([ECHO])),
                        ("ToolNode([echo], handle_tool_errors=True)", ToolNode([ECHO], handle_tool_errors=True))):
        app = build(WithReducer, bad_agent, [ECHO], node=node)
        out = await app.ainvoke({"messages": [HumanMessage("go")]})
        print(f"\n  --- {label} ---")
        for message in out["messages"]:
            print(f"    {type(message).__name__:12} {str(message.content)[:80]}")

    print("\n  No exception. The unknown name became data in the transcript:")
    print("    Error: delete_everything is not a valid tool, try one of [echo].")
    print("  That is why a client must reject unknown names ITSELF when the choice came from a")
    print("  script (see lab 1) — and why the model-driven path can be left to ToolNode.")

    print("\n=== tools_condition, called directly ===")
    no_calls = {"messages": [AIMessage(content="hi")]}
    with_calls = {"messages": [AIMessage(content="", tool_calls=[
        {"name": "echo", "args": {"text": "x"}, "id": "1"}])]}
    print(f"  tools_condition(no tool_calls)   -> {tools_condition(no_calls)!r}")
    print(f"  tools_condition(with tool_calls) -> {tools_condition(with_calls)!r}")
    print("  '__end__' is what END equals; you never write it by hand.")


if __name__ == "__main__":
    asyncio.run(main())
