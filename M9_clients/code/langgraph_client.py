"""Lesson 3.2 (part 2) — LangGraph orchestrating an MCP server.

The loop from tool_loop.py, with a model choosing instead of a hand-written dispatch. What is
new is only the chooser; the discovery and invocation are the same calls.

Two paths, because a lab may be air-gapped:
    --offline   runs a scripted chooser, so the graph and the MCP wiring are demonstrated with
                no API key. This is the default.
    --model     uses an LLM via langchain-openai. Needs OPENAI_API_KEY (or a compatible
                base_url) in the environment.

Run:
    uv run python -m M9_clients.code.langgraph_client
    OPENAI_API_KEY=... uv run python -m M9_clients.code.langgraph_client --model
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import Annotated, TypedDict

from fastmcp import Client
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import StructuredTool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

SERVER = Path(__file__).parents[2] / "M4_fastmcp_basics" / "code" / "hello_server.py"
USE_MODEL = "--model" in sys.argv


class AgentState(TypedDict):
    """The graph's state. `add_messages` is a REDUCER: without it each node would overwrite
    the whole list and the model would lose every previous tool result."""

    messages: Annotated[list[BaseMessage], add_messages]


def mcp_tool_to_langchain(name: str, description: str, schema: dict, client: Client) -> StructuredTool:
    """Adapt one MCP tool into a LangChain tool.

    `langchain-mcp-adapters` does this in one call (`load_mcp_tools`), and in a real project you
    would use it. Doing it by hand once shows that an "adapter" is only a name, a description,
    a schema and an async function — there is no magic to be intimidated by.
    """

    async def _call(**kwargs):
        result = await client.call_tool(name, kwargs)
        return result.data

    return StructuredTool.from_function(
        coroutine=_call,
        name=name,
        description=description,
        args_schema=None,          # the JSON Schema travels in the docs to the model
    )


async def build_graph(client: Client, tools: list[StructuredTool], chooser):
    async def agent(state: AgentState) -> dict:
        last = state["messages"][-1]
        decision = await chooser(last, tools)
        return {"messages": [decision]}

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent)
    graph.add_node("tools", ToolNode(tools))
    graph.add_edge(START, "agent")
    # tools_condition routes to "tools" if the last message carries tool_calls, else END
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")
    # MemorySaver gives every thread_id its own conversation history. Without a checkpointer
    # each invoke would start from nothing.
    return graph.compile(checkpointer=MemorySaver())


def scripted_chooser(*calls: tuple[str, dict]):
    """A deterministic 'model': emits the tool calls it was handed, one per turn."""
    remaining = list(calls)

    async def choose(_last: BaseMessage, _tools: list[StructuredTool]) -> AIMessage:
        if not remaining:
            return AIMessage(content="Done.")
        name, args = remaining.pop(0)
        return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": f"call_{name}"}])

    return choose


def model_chooser(model):
    async def choose(last: BaseMessage, tools: list[StructuredTool]) -> AIMessage:
        return await model.bind_tools(tools).ainvoke([last])

    return choose


async def main() -> None:
    async with Client(SERVER) as client:
        discovered = await client.list_tools()
        print("=== discovered over MCP ===")
        for t in discovered:
            print(f"  {t.name:8} {(t.description or '').splitlines()[0][:60]}")

        tools = [mcp_tool_to_langchain(t.name, t.description or "", t.parameters or {}, client)
                 for t in discovered]

        if USE_MODEL:
            from langchain_openai import ChatOpenAI
            if not os.environ.get("OPENAI_API_KEY"):
                print("\n  --model needs OPENAI_API_KEY; falling back to the scripted chooser")
                chooser = scripted_chooser(("add", {"a": 7, "b": 5}))
            else:
                chooser = model_chooser(ChatOpenAI(model="gpt-4o-mini", temperature=0))
        else:
            print("\n=== scripted chooser (no API key needed) ===")
            chooser = scripted_chooser(("add", {"a": 7, "b": 5}))

        app = await build_graph(client, tools, chooser)
        config = {"configurable": {"thread_id": "lesson-3-2"}}
        out = await app.ainvoke({"messages": [HumanMessage("What is 7 + 5?")]}, config)

        print("\n=== the run, step by step ===")
        for message in out["messages"]:
            kind = type(message).__name__
            if isinstance(message, AIMessage) and message.tool_calls:
                for call in message.tool_calls:
                    print(f"  {kind:12} -> calls {call['name']}({call['args']})")
            elif isinstance(message, ToolMessage):
                print(f"  {kind:12} <- {message.content}")
            else:
                print(f"  {kind:12} {str(message.content)[:60]}")

        print("\n=== checkpointing: a second turn sees the first ===")
        second = await app.ainvoke({"messages": [HumanMessage("And 1 + 1?")]}, config)
        print(f"  messages retained in thread lesson-3-2: {len(second['messages'])}")

        print("\n=== --offline vs --model ===")
        print("  The graph, the MCP wiring and the checkpointer are IDENTICAL in both modes.")
        print("  Only the chooser differs. That is the point of the lesson: the model is one")
        print("  replaceable node, not the architecture.")


if __name__ == "__main__":
    asyncio.run(main())
