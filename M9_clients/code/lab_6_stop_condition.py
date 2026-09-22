"""LAB 6 — the cycle needs a stop condition: GraphRecursionError, and the step budget that fixes it.

An agent<->tools edge is a LOOP. `tools_condition` ends it when the model stops asking for tools —
but a chooser that always asks (a buggy model, a scripted chooser with a typo, a model stuck on a
failing tool) has no natural end. LangGraph stops it for you at a recursion limit, and the message
you get is the one below. The fix is a budget carried in STATE and enforced by a router, which is
also what lets you say "this run may spend at most N tool calls".

Run:
    uv run python -m M9_clients.code.lab_6_stop_condition
"""
from __future__ import annotations

import asyncio
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.tools import StructuredTool
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

STEP_BUDGET = 3


async def echo(text: str) -> str:
    """Echo the text back.

    Args:
        text: Any text.
    """
    return f"echo:{text}"


ECHO = StructuredTool.from_function(coroutine=echo, name="echo", description="Echo the text back.")


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    # NO reducer on steps: every node writes the absolute new value, which is what a counter
    # wants. `add_messages` on `messages` is the opposite case: a list that must accumulate.
    steps: int


def always_echo(state: State) -> dict:
    """A chooser that never decides to stop — the bug this lab is about."""
    return {"messages": [AIMessage(content="", tool_calls=[
        {"name": "echo", "args": {"text": "again"}, "id": f"call_{len(state['messages'])}"}])],
        "steps": state.get("steps", 0) + 1}


def router(state: State) -> str:
    """Where the agent goes next: run one more tool, or stop."""
    last = state["messages"][-1]
    if not getattr(last, "tool_calls", None):
        return "stop"
    if state.get("steps", 0) >= STEP_BUDGET:
        return "stop"
    return "tools"


async def main() -> None:
    print("=== 1. no stop condition: let LangGraph catch it ===")
    graph = StateGraph(State)
    graph.add_node("agent", always_echo)
    graph.add_node("tools", ToolNode([ECHO]))
    graph.add_edge(START, "agent")
    graph.add_edge("agent", "tools")
    graph.add_edge("tools", "agent")
    app = graph.compile()
    try:
        await app.ainvoke({"messages": [HumanMessage("go")], "steps": 0},
                          {"recursion_limit": 6})
    except Exception as exc:
        print(f"  {type(exc).__name__}:")
        for line in str(exc).splitlines()[:2]:
            print(f"    {line}")
    print("  The default limit is 10007 steps, which is a long way from any useful answer:")
    print("  you find out after minutes of tool calls, not after three.")

    print("\n=== 2. a budget in state, enforced by a router ===")
    graph = StateGraph(State)
    graph.add_node("agent", always_echo)
    graph.add_node("tools", ToolNode([ECHO]))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", router, {"tools": "tools", "stop": "__end__"})
    graph.add_edge("tools", "agent")
    app = graph.compile()

    out = await app.ainvoke({"messages": [HumanMessage("go")], "steps": 0})
    print(f"  steps used: {out['steps']}   messages: {len(out['messages'])}")
    for message in out["messages"]:
        kind = type(message).__name__
        calls = getattr(message, "tool_calls", None)
        detail = f"calls {calls[0]['name']}" if calls else str(message.content)[:24]
        print(f"    {kind:12} {detail}")
    print("  The loop ended on the budget, not on luck, and the count is visible in the")
    print("  returned state — so a caller can say 'this run was truncated'.")

    print("\n=== 3. the same router with a chooser that does stop ===")
    def one_shot(state: State) -> dict:
        if state["steps"] >= 1:
            return {"messages": [AIMessage(content="Done.")], "steps": state["steps"]}
        return {"messages": [AIMessage(content="", tool_calls=[
            {"name": "echo", "args": {"text": "once"}, "id": "call_once"}])],
            "steps": state["steps"] + 1}

    graph = StateGraph(State)
    graph.add_node("agent", one_shot)
    graph.add_node("tools", ToolNode([ECHO]))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", router, {"tools": "tools", "stop": "__end__"})
    graph.add_edge("tools", "agent")
    out = await (graph.compile()).ainvoke({"messages": [HumanMessage("go")], "steps": 0})
    print(f"  final content: {out['messages'][-1].content!r}   steps: {out['steps']}")

    print("\n=== the rule ===")
    print("  tools_condition is the right router when the CHOOSER can be trusted to stop.")
    print("  A step budget is the right router when it cannot — every model call, every")
    print("  scripted chooser, and every unattended run. Keep the count in state so it is")
    print("  part of the transcript, not a variable in your head.")


if __name__ == "__main__":
    asyncio.run(main())
