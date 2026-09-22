"""LAB 8 — one graph, two servers, and the name-collision problem that follows.

A host rarely talks to one server. Cline's own settings file declares two (`cline_mcp_settings.json`),
and the moment you adapt tools from more than one server you meet the first real integration problem:

    every tool name from every server lands in ONE flat namespace,
    and two servers are free to use the same name for different things.

This lab solves it the way it is solved in practice: a server PREFIX on the LangChain tool name,
while the MCP-side call keeps the server's own name. The scripted chooser then drives both servers
in one run: the hardened log server for evidence, the hello server for arithmetic.

Run:
    uv run python -m M9_clients.code.lab_8_two_servers
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Annotated, Any, Callable, TypedDict

from fastmcp import Client
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.tools import StructuredTool
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import Field, create_model

ROOT = Path(__file__).parents[2]
HELLO = ROOT / "M4_fastmcp_basics" / "code" / "hello_server.py"

JSON_TO_PY: dict[str, Callable[..., Any]] = {
    "string": str, "number": float, "integer": int, "boolean": bool,
    "array": list, "object": dict,
}


def args_model_from_schema(tool_name: str, schema: dict) -> type:
    required = set(schema.get("required") or [])
    fields: dict[str, tuple] = {}
    for key, spec in (schema.get("properties") or {}).items():
        annotation = JSON_TO_PY.get(spec.get("type", "string"), Any)
        default = ... if key in required else spec.get("default", None)
        fields[key] = (annotation, Field(default=default,
                                         description=spec.get("description", "")))
    return create_model(f"{tool_name}_args", **fields)


def adapt(tool, client: Client, prefix: str) -> StructuredTool:
    """One MCP tool -> one LangChain tool, namespace-safe.

    Two names are in play and they are deliberately different:
      * the LangChain name  -> f"{prefix}__{tool.name}"  (what the model sees and emits)
      * the MCP tool name   -> tool.name                 (what the server is asked for)
    """
    lc_name = f"{prefix}__{tool.name}"
    mcp_name = tool.name

    async def _call(**kwargs: Any) -> Any:
        result = await client.call_tool(mcp_name, kwargs)
        return result.data

    return StructuredTool.from_function(
        coroutine=_call,
        name=lc_name,
        description=f"[{prefix}] {(tool.description or '').strip()}",
        args_schema=args_model_from_schema(lc_name, tool.input_schema),
    )


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def scripted_chooser(*calls: tuple[str, dict]) -> Callable:
    remaining = list(calls)

    async def choose(_last: BaseMessage, _tools: list[StructuredTool]) -> AIMessage:
        if not remaining:
            return AIMessage(content="Done.")
        name, args = remaining.pop(0)
        return AIMessage(content="",
                         tool_calls=[{"name": name, "args": args, "id": f"call_{name}"}])

    return choose


async def main() -> None:
    from M10_security.code.path_validation import mcp as log_server

    async with Client(HELLO) as hello_client, Client(log_server) as logs_client:
        hello_tools = await hello_client.list_tools()
        log_tools = await logs_client.list_tools()

        print("=== two servers, discovered separately ===")
        print(f"  hello_server        {[t.name for t in hello_tools]}")
        print(f"  path_validation     {[t.name for t in log_tools]}")

        tools = ([adapt(t, hello_client, "hello") for t in hello_tools]
                 + [adapt(t, logs_client, "logs") for t in log_tools])
        print("\n=== one flat namespace, made unambiguous ===")
        for tool in tools:
            print(f"  {tool.name:24} args={sorted(tool.args)}")

        print("\n=== the same adapter, two connections ===")
        print("  both tool lists are in ONE ToolNode; each coroutine closes over its OWN client,")
        print("  so a call never goes to the wrong server. That is the whole trick.")

        chooser = scripted_chooser(
            ("logs__list_logs", {}),
            ("logs__read_log", {"name": "postgres.log", "max_lines": 3}),
            ("logs__grep_log", {"name": "postgres.log", "pattern": "ERROR"}),
        )
        tools_by_name = {t.name: t for t in tools}

        async def agent(state: AgentState) -> dict:
            return {"messages": [await chooser(state["messages"][-1], tools)]}

        graph = StateGraph(AgentState)
        graph.add_node("agent", agent)
        graph.add_node("tools", ToolNode(tools))
        graph.add_edge(START, "agent")
        graph.add_conditional_edges("agent", tools_condition)
        graph.add_edge("tools", "agent")
        app = graph.compile()

        out = await app.ainvoke({"messages": [HumanMessage("What do the logs say?")]})
        print("\n=== the run: three calls, two servers, one transcript ===")
        for message in out["messages"]:
            kind = type(message).__name__
            if isinstance(message, AIMessage) and message.tool_calls:
                for call in message.tool_calls:
                    print(f"  {kind:12} -> {call['name']}({call['args']})")
            elif kind == "ToolMessage":
                first = str(message.content).splitlines()[0]
                print(f"  {kind:12} <- {first[:74]}")
            else:
                print(f"  {kind:12} {str(message.content)[:60]}")

        print("\n=== the collision this prevents ===")
        print("  Two servers may both ship a tool called `read_log`. Unprefixed, one would")
        print("  silently shadow the other in ToolNode's name lookup, and the wrong server")
        print("  would answer — with no error anywhere. The prefix is cheap insurance.")
        print(f"  names in this graph: {sorted(tools_by_name)}")

        print("\n=== a call BEFORE the tool is chosen ===")
        payload = json.dumps({"tool": "logs__list_logs", "arguments": {}})
        incoming = json.loads(payload)
        if incoming["tool"] in tools_by_name:
            data = await tools_by_name[incoming["tool"]].ainvoke(incoming["arguments"])
            print(f"  dispatched {incoming['tool']} -> {str(data)[:60]}")
        print("  A LangChain tool is directly awaitable — the graph is a convenience, not a")
        print("  requirement. The MCP round trip is the same either way.")


if __name__ == "__main__":
    asyncio.run(main())
