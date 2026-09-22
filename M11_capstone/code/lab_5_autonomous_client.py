"""LAB 5 — an autonomous client driving the whole capstone, with no model in the loop.

The capstone's promise is that a client can:  discover the surface, pick the right prompt, follow
the steps that prompt prescribes, read the resources it names, and stop for a human before a
protected action. This lab does all of that in ordinary Python. Nothing here needs an API key,
which is the point — you should not have to pay for a model to find out whether your server's
CONTRACT is sound.

Two phases:

  phase A  a hand-written scripted agent over one connection: prompt -> tools -> resource ->
           guarded action. Deterministic, so the output is comparable between runs.
  phase B  (--graph) the SAME work with a LangGraph StateGraph, where the only thing that
           changes is WHO chooses the next tool. This is M9's lesson applied to M11's server.

Run:
    uv run python -m M11_capstone.code.lab_5_autonomous_client
    uv run python -m M11_capstone.code.lab_5_autonomous_client --graph
"""
from __future__ import annotations

import asyncio
import sys
from typing import Annotated, Any, TypedDict

from fastmcp import Client

from M11_capstone.code.devops_assistant import mcp

USE_GRAPH = "--graph" in sys.argv
LOG = "postgres-ha.log"

# The graph state must live at MODULE level, not inside a function. With
# `from __future__ import annotations` the annotations are strings, and LangGraph resolves them
# against the module globals: a TypedDict declared inside `phase_b` fails with
#     NameError: name 'Annotated' is not defined
# at `StateGraph(GraphState)`, which is a long way from the actual mistake.
try:  # langgraph is a course dependency, but the scripted phase must run without it
    from langchain_core.messages import BaseMessage
    from langgraph.graph.message import add_messages

    class GraphState(TypedDict):
        """The reducer matters: without `add_messages` each node REPLACES the list, so the
        graph loses every tool result the moment the next node runs."""

        messages: Annotated[list[BaseMessage], add_messages]

    GRAPH_AVAILABLE = True
except ImportError:  # pragma: no cover - only on a machine without langgraph
    GraphState = dict  # type: ignore[assignment,misc]
    GRAPH_AVAILABLE = False


async def phase_a() -> None:
    """The scripted agent: every decision written out, so the contract is what is under test."""

    async def approve(message: str, response_type: Any, params: Any = None,
                      context: Any = None) -> Any:
        print(f"  [human] {message}")
        return {"proceed": True, "reason": "approved by the lab operator"}

    async with Client(mcp, mode="legacy", elicitation_handler=approve) as client:
        print("=== A1. discover, do not assume ===")
        tools = [t.name for t in await client.list_tools()]
        templates = [t.uri_template for t in await client.list_resource_templates()]
        prompts = [p.name for p in await client.list_prompts()]
        print(f"  tools     {tools}")
        print(f"  templates {templates}")
        print(f"  prompts   {prompts}")

        print("\n=== A2. pick the prompt whose JOB matches the request ===")
        rendered = await client.get_prompt("rca_error_log",
                                           {"log_name": LOG, "window_minutes": 30})
        plan = rendered.messages[0].content.text
        print("  the server's own instructions, step by step:")
        for line in plan.splitlines():
            if line[:2].strip().rstrip(".").isdigit():
                print(f"    {line}")

        print("\n=== A3. step 1 — read the log with the filter the prompt asks for ===")
        evidence = (await client.call_tool("read_log",
                    {"name": LOG, "errors_only": True, "max_lines": 100})).data
        if not evidence["ok"]:
            print(f"  cannot proceed: {evidence['error']} — {evidence['hint']}")
            return
        quoted = evidence["content"].splitlines()
        for line in quoted:
            print(f"    {line}")

        print("\n=== A4. step 2 — the FIRST anomalous event ===")
        first = quoted[0]
        print(f"  first  : {first}")
        print(f"  loudest: the 'could not connect to host kasm-app' group "
              f"(x{sum('could not connect' in line for line in quoted)})")
        print("  The prompt forces the first one. Without that instruction the loudest wins.")

        print("\n=== A5. step 4 — read the runbook BEFORE recommending anything ===")
        candidates = (await client.call_tool("list_runbooks", {})).data["runbooks"]
        print(f"  runbooks available: {candidates}")
        name = LOG.removesuffix(".log")
        if name not in candidates:
            name = candidates[0]
            print(f"  no runbook literally named {LOG!r}; using {name!r} — say this out loud")
        runbook = (await client.read_resource(f"runbook://{name}"))[0].text
        print(f"  runbook://{name}:")
        for line in [l for l in runbook.splitlines() if l.strip()][:6]:
            print(f"    {line}")
        print("  the runbook's step 2 is 'check replication lag before anything else' —")
        print("  which is exactly what the FIRST anomalous event was about. The order stands.")

        print("\n=== A6. steps 3 + 5 — causal chain and the falsifier ===")
        print("  chain      : lag WARN (02:01:50) -> client retries to kasm-app (02:02:12)")
        print("               -> failover candidate withheld because a sync standby is missing")
        print("  falsifier  : if the lag warning is sampled from a replica rather than the")
        print("               primary, the whole chain collapses. Read the emitting instance.")

        print("\n=== A7. step 6 — the smallest change, and the guard ===")
        review = await client.get_prompt("capacity_review", {"host": "pve01"})
        print("  the second prompt demands a NUMBER before any upgrade:")
        last_line = [l for l in review.messages[0].content.text.splitlines() if l.strip()][-1]
        print(f"    {last_line}")
        metrics = (await client.call_tool("system_metrics", {})).data
        if metrics["data_disk_total_gb"]:
            pct = round((metrics["data_disk_total_gb"] - metrics["data_disk_free_gb"])
                        / metrics["data_disk_total_gb"] * 100, 1)
            print(f"  number: data disk at {pct}% — "
                  f"{'above 70%, act' if pct > 70 else 'below 70%, say there is nothing to do'}")
        if metrics["memory_total_gb"] is None:
            print("  memory: UNKNOWN on this platform — report it as unknown, not as 0%")

        print("\n=== A8. the guarded action ===")
        decision = (await client.call_tool("restart_service",
                    {"service": "postgres-ha", "reason": "replication lag 3.1s"})).data
        print(f"  {decision}")
        print("  The tool asked, the human answered, and the tool then said plainly that it")
        print("  changed nothing. A client in production must surface that 'action_taken' field")


async def phase_b() -> None:
    """The same server, driven by a LangGraph graph with a scripted chooser."""
    from langchain_core.messages import AIMessage, HumanMessage
    from langchain_core.tools import StructuredTool
    from langgraph.graph import END, START, StateGraph
    from langgraph.prebuilt import ToolNode, tools_condition
    from pydantic import Field, create_model

    if not GRAPH_AVAILABLE:
        print("  langgraph is not installed in this environment; skipping phase B.")
        return

    # JSON Schema type -> Python type. This is the M2 payoff: the schema the server GENERATED
    # from its type hints is enough to build a callable tool on the other side of the wire.
    PYTHON_TYPE = {"string": str, "integer": int, "boolean": bool, "number": float,
                   "array": list, "object": dict}

    def args_model(tool_name: str, schema: dict) -> type:
        """Turn a tool's JSON Schema into a Pydantic model LangChain can validate against.

        Skipping this step is the classic LangGraph+MCP mistake: a coroutine declared as
        `async def call(**kwargs)` infers an EMPTY argument schema, so ToolNode strips the
        arguments the model supplied and the server answers
            ToolError: 1 validation error for call[read_log]
            name  Missing required argument [type=missing_argument, input_value={}]
        """
        required = set(schema.get("required") or [])
        fields: dict[str, tuple] = {}
        for key, spec in (schema.get("properties") or {}).items():
            annotation = PYTHON_TYPE.get(spec.get("type", "string"), str)
            default = ... if key in required else spec.get("default", None)
            fields[key] = (annotation,
                           Field(default=default, description=spec.get("description", "")))
        return create_model(f"{tool_name}_args", **fields)

    async with Client(mcp) as client:
        discovered = await client.list_tools()
        print(f"=== B1. discovered {len(discovered)} tools over MCP ===")

        def adapt(tool) -> StructuredTool:
            async def call(**kwargs: Any) -> Any:
                return (await client.call_tool(tool.name, kwargs)).data

            return StructuredTool.from_function(
                coroutine=call,
                name=tool.name,
                description=(tool.description or "")[:200],
                args_schema=args_model(tool.name, tool.input_schema),
            )

        # Only the read-only tools: a scripted chooser has no judgement, and giving it
        # `restart_service` would be handing a loaded gun to a for-loop.
        safe = [t for t in discovered
                if t.name in {"system_metrics", "list_logs", "read_log", "list_runbooks"}]
        tools = [adapt(t) for t in safe]
        print(f"  adapted: {[t.name for t in tools]}")
        read_log_tool = next(t for t in tools if t.name == "read_log")
        print(f"  read_log args schema: {sorted(read_log_tool.args.keys())}")

        async def agent(state: GraphState) -> dict:
            last = state["messages"][-1]
            if getattr(last, "tool_calls", None):
                return {"messages": [AIMessage(content="done")]}
            return {"messages": [AIMessage(
                content="",
                tool_calls=[{"name": "read_log",
                             "args": {"name": LOG, "errors_only": True},
                             "id": "call_read_log"}])]}

        graph = StateGraph(GraphState)
        graph.add_node("agent", agent)
        graph.add_node("tools", ToolNode(tools))
        graph.add_edge(START, "agent")
        graph.add_conditional_edges("agent", tools_condition)
        graph.add_edge("tools", END)
        app = graph.compile()

        out = await app.ainvoke({"messages": [HumanMessage("What is wrong with postgres?")]})
        print("\n=== B2. the graph's transcript ===")
        for message in out["messages"]:
            kind = type(message).__name__
            if isinstance(message, AIMessage) and message.tool_calls:
                for call in message.tool_calls:
                    print(f"  {kind:12} -> {call['name']}({call['args']})")
            elif kind == "ToolMessage":
                first = str(message.content).splitlines()[0]
                print(f"  {kind:12} <- {first[:96]}")
            else:
                print(f"  {kind:12} {str(message.content)[:100]}")
        print("\n  The graph is M9's. The server is M11's. Neither knows about the other, and")
        print("  that is the whole value of MCP: the same server serves Cline, a LangGraph")
        print("  graph, or a 40-line script, with no server-side change at all.")


async def main() -> None:
    print("=== PHASE A — scripted agent, no model, no API key ===")
    await phase_a()
    if USE_GRAPH:
        print("\n=== PHASE B — LangGraph drives the same server ===")
        await phase_b()
    else:
        print("\n  (re-run with --graph to see a LangGraph StateGraph drive the same server)")


if __name__ == "__main__":
    asyncio.run(main())
