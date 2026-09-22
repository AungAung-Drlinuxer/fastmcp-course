"""LAB 4 — the LangGraph orchestrator, offline first.

`langgraph_client.py` with the two client-side defects fixed (`.parameters` -> `.input_schema`,
and `args_schema=None` -> a real argument model). What is left is the lesson: ONE graph, TWO
choosers. The scripted chooser runs with no API key; `--model` swaps in a real model and changes
nothing else.

Run:
    uv run python -m M9_clients.code.lab_4_graph_offline
    OPENAI_API_KEY=... uv run python -m M9_clients.code.lab_4_graph_offline --model
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import Annotated, Any, Callable, TypedDict

from fastmcp import Client
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.tools import StructuredTool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import Field, create_model

ROOT = Path(__file__).parents[2]
HELLO = ROOT / "M4_fastmcp_basics" / "code" / "hello_server.py"
USE_MODEL = "--model" in sys.argv
THREAD = {"configurable": {"thread_id": "lesson-3-2"}}

JSON_TO_PY: dict[str, Callable[..., Any]] = {
    "string": str, "number": float, "integer": int, "boolean": bool,
    "array": list, "object": dict,
}


class AgentState(TypedDict):
    """The graph's state.

    `add_messages` is a REDUCER, not a type. It tells LangGraph how to COMBINE the value a node
    returns with the value already in state. Without it the key is overwritten, and the model
    loses every previous tool result on every hop.
    """

    messages: Annotated[list[BaseMessage], add_messages]


def args_model_from_schema(tool_name: str, schema: dict) -> type:
    required = set(schema.get("required") or [])
    fields: dict[str, tuple] = {}
    for key, spec in (schema.get("properties") or {}).items():
        annotation = JSON_TO_PY.get(spec.get("type", "string"), Any)
        default = ... if key in required else spec.get("default", None)
        fields[key] = (annotation, Field(default=default,
                                         description=spec.get("description", "")))
    return create_model(f"{tool_name}_args", **fields)


def mcp_tool_to_langchain(tool, client: Client) -> StructuredTool:
    """One MCP tool -> one LangChain tool. Four things travel: name, description, schema, call."""
    name = tool.name

    async def _call(**kwargs: Any) -> Any:
        result = await client.call_tool(name, kwargs)
        return result.data

    return StructuredTool.from_function(
        coroutine=_call,
        name=name,
        description=(tool.description or "").strip(),
        args_schema=args_model_from_schema(name, tool.input_schema),
    )


def scripted_chooser(*calls: tuple[str, dict]) -> Callable:
    """A deterministic stand-in for a model: it emits the tool calls it was handed, one per turn."""
    remaining = list(calls)

    async def choose(_last: BaseMessage, _tools: list[StructuredTool]) -> AIMessage:
        if not remaining:
            return AIMessage(content="Done.")
        name, args = remaining.pop(0)
        return AIMessage(content="",
                         tool_calls=[{"name": name, "args": args, "id": f"call_{name}"}])

    return choose


def model_chooser(model) -> Callable:
    """The real chooser. Identical contract: (last message, tools) -> AIMessage."""

    async def choose(last: BaseMessage, tools: list[StructuredTool]) -> AIMessage:
        return await model.bind_tools(tools).ainvoke([last])

    return choose


def build_graph(tools: list[StructuredTool], chooser: Callable, *, checkpoint: bool = True):
    async def agent(state: AgentState) -> dict:
        decision = await chooser(state["messages"][-1], tools)
        return {"messages": [decision]}

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent)
    graph.add_node("tools", ToolNode(tools))
    graph.add_edge(START, "agent")
    # tools_condition: last message has tool_calls -> "tools", otherwise -> END
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")
    if not checkpoint:
        return graph.compile()
    return graph.compile(checkpointer=MemorySaver())


def transcript(messages: list[BaseMessage]) -> None:
    for message in messages:
        kind = type(message).__name__
        if isinstance(message, AIMessage) and message.tool_calls:
            for call in message.tool_calls:
                print(f"  {kind:12} -> calls {call['name']}({call['args']})")
        else:
            print(f"  {kind:12} {str(message.content)[:60]}")


async def main() -> None:
    async with Client(HELLO) as client:
        discovered = await client.list_tools()
        print("=== discovered over MCP ===")
        for tool in discovered:
            print(f"  {tool.name:8} {(tool.description or '').strip()[:56]}")

        tools = [mcp_tool_to_langchain(t, client) for t in discovered]
        print(f"  adapted  {[(t.name, sorted(t.args)) for t in tools]}")

        if USE_MODEL:
            if not os.environ.get("OPENAI_API_KEY"):
                print("\n  --model needs OPENAI_API_KEY; falling back to the scripted chooser")
                print("  (the offline path is the one that runs in an air-gapped lab)")
                chooser = scripted_chooser(("add", {"a": 7, "b": 5}))
            else:
                from langchain_openai import ChatOpenAI
                chooser = model_chooser(ChatOpenAI(model="gpt-4o-mini", temperature=0))
                print("\n=== model chooser (temperature=0, tools bound) ===")
        else:
            print("\n=== scripted chooser (no API key needed) ===")
            chooser = scripted_chooser(("add", {"a": 7, "b": 5}))

        app = build_graph(tools, chooser)

        print("\n=== turn 1: the run, step by step ===")
        out = await app.ainvoke({"messages": [HumanMessage("What is 7 + 5?")]}, THREAD)
        transcript(out["messages"])
        print(f"  messages after turn 1: {len(out['messages'])}")

        print("\n=== turn 2: a checkpointer keeps the thread's history ===")
        second = await app.ainvoke({"messages": [HumanMessage("And 1 + 1?")]}, THREAD)
        print(f"  messages retained in thread lesson-3-2: {len(second['messages'])}")
        print("  the first human message is still there:")
        print(f"    {second['messages'][0].content!r}")

        print("\n=== a different thread_id sees none of it ===")
        fresh = await app.ainvoke({"messages": [HumanMessage("Other thread")]},
                                  {"configurable": {"thread_id": "someone-else"}})
        print(f"  messages in thread someone-else: {len(fresh['messages'])}")

        state = await app.aget_state(THREAD)
        print(f"\n  aget_state(THREAD).values keys = {list(state.values)}")
        print(f"  next nodes pending              = {state.next}")

        print("\n=== the same graph with NO checkpointer ===")
        bare = build_graph(tools, scripted_chooser(("add", {"a": 7, "b": 5})), checkpoint=False)
        r1 = await bare.ainvoke({"messages": [HumanMessage("first")]})
        r2 = await bare.ainvoke({"messages": [HumanMessage("second")]})
        print(f"  run 1 messages: {len(r1['messages'])}   run 2 messages: {len(r2['messages'])}")
        print("  Nothing is remembered between invokes — every run starts from your input only.")
        try:
            await bare.aget_state(THREAD)
        except Exception as exc:
            print(f"  aget_state -> {type(exc).__name__}: {exc}")
        print("\n  And the reverse mistake — compiled WITH a checkpointer, invoked WITHOUT a")
        print("  thread_id — fails before any node runs:")
        try:
            await app.ainvoke({"messages": [HumanMessage("no thread")]})
        except Exception as exc:
            print(f"    {type(exc).__name__}: {str(exc)[:96]}")

        print("\n=== scripted chooser vs model chooser ===")
        print("  Same graph. Same nodes. Same MCP calls. Only the chooser function differs,")
        print("  which is the point: the model is one replaceable node, not the architecture.")


if __name__ == "__main__":
    asyncio.run(main())
