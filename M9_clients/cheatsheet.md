# Cheatsheet — M9 clients, hosts and orchestration

## ဒီဖိုင်မှာ ဘာသင်မလဲ

- Module တစ်ခုလုံးရဲ့ API စာရင်း (method အတိအကျ)
- ⭐ **တိုင်းထားသည့် error message များ** — ရှာရာတွင် ပထမဆုံး ကြည့်ရမည့် ဇယား
- ကူးယူလို့ရသည့် code skeleton လေးခု (client loop, adapter, graph, budget router)
- ဘယ်အခါ ဘာသုံးမလဲ (decision tables)
- ဖိုင် ၁၀ ခုရဲ့ မြေပုံ — ပြဿနာတစ်ခု ရှိလျှင် ဘယ်ဖိုင်ကို ပြန်ကြည့်ရမလဲ
- Lab တစ်ခုစီရဲ့ တစ်လိုင်း အကျဉ်း

---

## အပိုင်း ၁ — Client API (အတိအကျ)

```python
from fastmcp import Client
from fastmcp.client.transports import StdioTransport, UvStdioTransport
```

### Discovery — လေးခု

| Method | ပြန်သည့်အရာ | ဘယ် field ကို ဖတ်ရမလဲ |
|---|---|---|
| `list_tools()` | `list[Tool]` | `.name`, `.description`, **`.input_schema`** |
| `list_resources()` | `list[Resource]` | `.uri` |
| `list_resource_templates()` | `list[ResourceTemplate]` | `.uri_template` |
| `list_prompts()` | `list[Prompt]` | `.name`, `.arguments` (`or []`) |

### Invocation — သုံးခု

| Method | ပြန်သည့်အရာ | value ကို ဘယ်လိုယူမလဲ |
|---|---|---|
| `call_tool(name, args)` | `CallToolResult` | **`.data`** (`.is_error` ကိုပါ စစ်ပါ) |
| `read_resource(uri)` | `list[ReadResourceContents]` | **`[0].text`** |
| `get_prompt(name, args)` | `GetPromptResult` | **`.messages[0].content.text`** |

### Connection — ပုံစံများ

```python
async with Client(Path("M4_fastmcp_basics/code/hello_server.py")) as client:   # stdio subprocess
async with Client(mcp) as client:                                              # in-process (fast)
async with Client(mcp, mode="legacy", elicitation_handler=handler) as client:  # elicitation
async with Client(StdioTransport(command="uv", args=[...], keep_alive=False)) as client:
async with Client(UvStdioTransport(command="python", args=["-m", MOD],
                                  project_directory=ROOT, keep_alive=False)) as client:
```

⭐ `Client(str(path))` က deprecated — `Path` ပေးပါ။

---

## အပိုင်း ၂ — ⭐ Error ဇယား (တိုင်းထားသည့်အတိုင်း)

### Client-side attribute များ

| Error | အကြောင်းရင်း | ဖြေရှင်းနည်း |
|---|---|---|
| `AttributeError: 'Tool' object has no attribute 'parameters'` | client-side `Tool` မှာ server-side နာမည် | `.input_schema` |
| `FastMCPDeprecationWarning: Accessing Tool.inputSchema is deprecated` | အလယ်နာမည် | `.input_schema` |
| `AttributeError` on `uriTemplate` | 2.x နာမည် | `.uri_template` |
| `AttributeError: 'list' object has no attribute 'text'` | `read_resource` က list | `[0].text` |
| `AttributeError: 'Message' object has no attribute 'text'` | `content` ကျော်သွားသည် | `.messages[0].content.text` |

⭐ **ဖိုင် 01 က `tool_loop.py` ရဲ့ line 38 မှာ ဒီ error ကို တကယ်တွေ့သည်။**

### Call နှင့် validation

| Error | အကြောင်းရင်း | ဖြေရှင်းနည်း |
|---|---|---|
| `ToolError: 1 validation error for call[add]` | argument အမျိုးအစား မှား | schema ဖတ်ပါ |
| `ToolError: 2 validation errors for call[add]` | argument မပါ (၂ ခု) | required field ဖြည့်ပါ |
| `4 validation errors` (missing 2 + unexpected 2) | argument name နှစ်ခုလုံး မှား | `properties` ထဲက နာမည် သုံးပါ |
| `MCPError: Error reading resource '...'` | ထို URI မရှိ | server ရဲ့ "available:" စာရင်းကို ဖတ်ပါ |
| `Error: <name> is not a valid tool, try one of [...]` | ToolNode က unknown name | tools list ကို စစ်ပါ (exception မဟုတ်) |
| server log: `Invalid arguments for tool 'add': {'error_count': 4, 'error_types': ['missing_argument', 'unexpected_keyword_argument']}` | schema `additionalProperties: false` | ပိုတဲ့ key ကို ဖယ်ပါ |

### LangGraph

| Error | အကြောင်းရင်း | ဖြေရှင်းနည်း |
|---|---|---|
| `GraphRecursionError: Recursion limit of 10007 reached without hitting a stop condition` | stop condition မရှိ | budget router (ဖိုင် 07) |
| `ValueError: Checkpointer requires one or more of the following 'configurable' keys: thread_id, ...` | checkpointer ရှိပြီး thread_id မပေး | `{"configurable": {"thread_id": "..."}}` |
| `ValueError: No checkpointer set` | `compile()` တွင် checkpointer မပါ | `compile(checkpointer=MemorySaver())` |
| `ValueError: Graph must have an entrypoint: add at least one edge from START to another node` | `add_edge(START, ...)` မရှိ | START မှ edge ဆွဲပါ |
| `ValueError: At 'agent' node, 'tools_condition' branch found unknown target 'tools'` | node က `"tools"` မဟုတ် | node ကို `"tools"` အမည်ပေးပါ |
| `wrote to unknown channel branch:to:nonsense, ignoring it.` | mapping မပါဘဲ မသိတဲ့ route | `add_conditional_edges(..., {mapping})` |
| reducer မပါလို့ message ၁ ခုသာ ကျန် | `Annotated[..., add_messages]` မရှိ | reducer ထည့်ပါ (Measured: 4 → 1) |

### Adapter နှင့် model path

| Error | အကြောင်းရင်း | ဖြေရှင်းနည်း |
|---|---|---|
| `ToolError: ... Missing required argument [type=missing_argument, input_value={}]` | `args_schema=None` → arguments ဖျောက်ခံရသည် | MCP schema ဖြင့် Pydantic model ဆောက်ပါ |
| `ValidationError: 1 validation error for add_args` | local validation (wire မရောက်) | ဒါက ကောင်းတာ — argument ကို ပြင်ပါ |
| `ModuleNotFoundError: No module named 'mcp.server.fastmcp'` | `langchain_mcp_adapters.tools` vs mcp 2.x | hand-written adapter သုံးပါ |
| `ImportError: cannot import name 'RequestContext' from 'mcp.shared.context'` | `langchain_mcp_adapters.client` vs mcp 2.2.0 | အထက်နှင့် တူ |
| `ModuleNotFoundError: No module named 'langchain_openai'` | model path အတွက် package မထည့်ရသေး | `uv add langchain-openai` (သင့်ဆုံးဖြတ်ချက်) |
| `AttributeError: 'str' object has no attribute 'exists'` | `project_directory` ကို str ပေးနေသည် | `Path` ပေးပါ |
| `AttributeError: 'tuple' object has no attribute 'pop'` | `remaining = list(calls)` မလုပ်ပါ | `list(calls)` ဖြင့် စပါ |
| `ToolError: elicitation via server-initiated requests is unavailable on 2026-07-28 connections.` | `mode="auto"` | `mode="legacy"` |

---

## အပိုင်း ၃ — Code skeletons (ကူးယူလို့ရသည်)

### Skeleton 1 — client loop (model မပါ)

```python
async def main() -> None:
    async with Client(Path("path/to/server.py")) as client:
        tools = await client.list_tools()
        known = {t.name for t in tools}
        for emission in [{"tool": "add", "arguments": {"a": 2, "b": 3}}]:
            if emission["tool"] not in known:
                print(f"reject: unknown tool {emission['tool']!r}")
                continue
            try:
                result = await client.call_tool(emission["tool"], emission["arguments"])
                print("ok:", result.data)
            except Exception as exc:
                print("failed:", type(exc).__name__, str(exc).splitlines()[0])
```

### Skeleton 2 — adapter (MCP tool → LangChain tool)

```python
JSON_TO_PY = {"string": str, "number": float, "integer": int, "boolean": bool,
              "array": list, "object": dict}


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
    lc_name, mcp_name = f"{prefix}__{tool.name}", tool.name

    async def _call(**kwargs: Any) -> Any:
        return (await client.call_tool(mcp_name, kwargs)).data

    return StructuredTool.from_function(coroutine=_call, name=lc_name,
                                        description=f"[{prefix}] {(tool.description or '').strip()}",
                                        args_schema=args_model_from_schema(lc_name, tool.input_schema))
```

### Skeleton 3 — the graph

```python
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]     # ⭐ reducer


async def agent(state: AgentState) -> dict:
    return {"messages": [await chooser(state["messages"][-1], tools)]}


graph = StateGraph(AgentState)
graph.add_node("agent", agent)
graph.add_node("tools", ToolNode(tools))                     # the name must be "tools"
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", tools_condition)
graph.add_edge("tools", "agent")
app = graph.compile(checkpointer=MemorySaver())
await app.ainvoke({"messages": [HumanMessage("...")]}, {"configurable": {"thread_id": "t1"}})
```

### Skeleton 4 — budget router (stop condition)

```python
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    steps: int                                   # no reducer — counter


def router(state: State) -> str:
    if not getattr(state["messages"][-1], "tool_calls", None):
        return "stop"
    if state.get("steps", 0) >= STEP_BUDGET:
        return "stop"
    return "tools"


graph.add_conditional_edges("agent", router, {"tools": "tools", "stop": END})
```

---

## အပိုင်း ၄ — Decision tables

### ဘယ် chooser ကို သုံးမလဲ

| အခြေအနေ | သုံးသင့်သည် |
|---|---|
| CI test, contract regression | scripted chooser (key မလို၊ ၆ စက္ကန့်) |
| Demo, teaching | scripted chooser |
| ဈေး/အချိန် စောင့်ကြည့်တဲ့ internal tool | rule-based chooser (deterministic) |
| တကယ့် user request (မပြတ်တဲ့ input) | model chooser |
| Air-gapped lab | scripted (တစ်ခုတည်း) |

### ဘယ် checkpointer ကို သုံးမလဲ

| အခြေအနေ | သုံးသင့်သည် |
|---|---|
| Lab, test, single-process demo | `MemorySaver` |
| Process restart ကို ခံနိုင်ရမည် | persistent (Sqlite/Postgres) |
| Worker များစွာ | shared persistent |
| Audit/legal လိုသည် | persistent + M10 ရဲ့ audit log |

### Resource လား Tool လား Prompt လား

| အရာ | အမျိုးအစား | ဘယ်သူ ရွေးသည် |
|---|---|---|
| runbook (ဖတ်ရန်) | resource | host (prompt က လမ်းညွှန်သည်) |
| host inventory | resource | host |
| restart a service | tool | model + approval |
| search the wiki | tool (query ရှိလို့) | model |
| RCA ပုံစံ | prompt | **လူ** (အလုပ် မစခင်) |

### ကာကွယ်မှု အလွှာများ

| အလွှာ | ဘာကာကွယ်သည် | ဘယ်မှာ |
|---|---|---|
| tool list ကျဉ်း (allowlist) | model က မခေါ်နိုင် | ဖိုင် 10 (M11 lab_5) |
| `autoApprove` explicit | လူက review လုပ်သည် | ဖိုင် 04 |
| server-side validation (`additionalProperties: false`) | မှားတဲ့ input | M5 / M10 |
| path confinement, allowlist dir | traversal | M10 |
| step budget | အဆုံးမရှိ loop | ဖိုင် 07 |
| audit log | ဘာဖြစ်ခဲ့လဲ | M10 |
| elicitation (`mode="legacy"`) | action မတိုင်မှီ ခွင့်ပြုချက် | M8 / ဖိုင် 10 |

---

## အပိုင်း ၅ — တိုင်းထားသည့် အချက်ရှစ်ခု (ဒီ module မှာ သင် ကိုယ်တိုင်မြင်ရမည်)

```text
၁. tool_loop.py line 38  → AttributeError: 'Tool' object has no attribute 'parameters'
   fix: .input_schema                            [ဖိုင် 01, 02]

၂. hello_server မှာ resources/templates/prompts = []   [ဖိုင် 02]

၃. read_resource → list, [0].text; get_prompt → .messages[0].content.text   [ဖိုင် 02]

၄. args_schema=None → schema {"kwargs": {...}} → server က {} ရသည် → ToolError   [ဖိုင် 05]

၅. load_mcp_tools / MultiServerMCPClient → import မရ (mcp 2.2.0)   [ဖိုင် 05]

၆. reducer ပါ → message 4 ခု; မပါ → 1 ခု   [ဖိုင် 06]

၇. thread တူတူ turn 2 → 6 messages; thread အသစ် → 2; checkpointer မရှိ → 2 နှင့် 2   [ဖိုင် 08]

၈. no stop condition → GraphRecursionError (default 10007); budget=3 → steps 3, messages 6   [ဖိုင် 07]
```

---

## အပိုင်း ၆ — ဖိုင်မြေပုံ (ပြဿနာ → ဖိုင်)

| ပြဿနာ | ဖိုင် |
|---|---|
| "Tool object has no attribute parameters" | 01 |
| "resources/templates/prompts က ဗလာ" | 02 |
| "read_resource ရဲ့ ရလဒ်ကို ဘယ်လိုယူမလဲ" | 02 |
| "model က ဘာထုတ်လဲ၊ unknown name ကို ဘယ်လိုတားမလဲ" | 03 |
| "Cline settings ထဲ ဘယ်လို ထည့်မလဲ၊ autoApprove က ဘာလဲ" | 04 |
| "adapter က arguments မပို့ဘူး" | 05 |
| "message history ပျောက်တယ်" | 06 |
| "Recursion limit reached" / "loop မရပ်ဘူး" | 07 |
| "turn 2 က turn 1 ကို မမှတ်မိဘူး" | 08 |
| "API key လိုလား၊ model ကို ဘယ်လိုထည့်မလဲ" | 09 |
| "server နှစ်ခုကို ဘယ်လိုချိတ်မလဲ" | 10 |

---

## အပိုင်း ၇ — Lab များ (တစ်လိုင်း အကျဉ်း)

| Lab | ဖိုင် | ရည်မှန်းချက် | မိနစ် |
|---|---|---|---|
| LAB 1 | `lab_1_client_loop.py` (§A) | client loop, `.input_schema` bug ကို ကိုယ်တိုင်တွေ့/ပြင် | ၂၅ |
| LAB 2 | `lab_1_client_loop.py` (§B/C) | surface လေးခု၊ `[0].text`, `.messages[0].content.text` | ၃၀ |
| LAB 3 | `lab_7_dispatch_table.py` | emission ၈ ခုကို dispatch၊ unknown ကို ငြင်း၊ count ကို code ဖြင့်တွက် | ၃၀ |
| LAB 4 | `lab_2_cline_settings.py` | settings audit + wildcard၊ entry ကို တကယ် launch | ၃၀ |
| LAB 5 | `lab_3_hand_adapter.py` | adapter နှစ်မျိုး၊ one-liner ရဲ့ တိုင်းထားသည့် ပျက်ကွက်မှု | ၃၅ |
| LAB 6 | `lab_5_state_reducer.py` | reducer 4 vs 1၊ unknown tool = data | ၂၅ |
| LAB 7 | `lab_6_stop_condition.py` | GraphRecursionError + budget router | ၃၀ |
| LAB 8 | `lab_4_graph_offline.py` | checkpointer/thread measurements + `--model` | ၂၅ |
| LAB 9 | `lab_4_graph_offline.py` (chooser အပိုင်း) | chooser နှစ်မျိုး၊ `[last]` vs `state[...]` | ၂၀ |
| LAB 10 | `lab_8_two_servers.py` | server နှစ်ခု၊ prefix၊ graph တစ်ခု | ၃၅ |

**စုစုပေါင်း:** ~၄ နာရီ ၂၅ မိနစ် (သင်ခန်းစာ ၃.၅ နာရီနှင့် ကိုက်ညီ)

---

## အပိုင်း ၈ — Command reference

```bash
# run a module
uv run python -m M9_clients.code.tool_loop
uv run python -m M9_clients.code.langgraph_client
uv run python -m M9_clients.code.langgraph_client --model

# the labs
uv run python -m M9_clients.code.lab_1_client_loop
uv run python -m M9_clients.code.lab_2_cline_settings
uv run python -m M9_clients.code.lab_3_hand_adapter
uv run python -m M9_clients.code.lab_4_graph_offline
uv run python -m M9_clients.code.lab_5_state_reducer
uv run python -m M9_clients.code.lab_6_stop_condition
uv run python -m M9_clients.code.lab_7_dispatch_table
uv run python -m M9_clients.code.lab_8_two_servers

# the offline test (no key, ~6s)
uv run pytest tests/test_m9_client_loop.py -q

# the Inspector (a host you did not write)
uv run fastmcp dev inspector M4_fastmcp_basics/code/hello_server.py
```

⚠️ **`--model` အတွက်:** `OPENAI_API_KEY` **နှင့်** `langchain-openai` (ဒီ environment တွင်
မရှိပါ)။ Key မရှိလျှင် scripted chooser ကို ပြန်ကျသည်။

---

## အပိုင်း ၉ — စကားလုံး သတ်မှတ်ချက်များ (တိကျစွာ)

| စကားလုံး | အဓိပ္ပာယ် |
|---|---|
| **host** | server နှင့် လူ အကြားမှာ ရပ်တဲ့ application (transport, UI, approval ကို ပိုင်) |
| **client** | MCP session တစ်ခုကို ကိုင်တဲ့ object (`Client`) |
| **transport** | ချိတ်ဆက်မှု နည်းလမ်း: stdio (child process), HTTP |
| **capability** | server ကြေညာသည့် surface (tools, resources, prompts, logging စသည်) |
| **chooser** | ဘယ် tool ကို ခေါ်မလဲ ဆုံးဖြတ်တဲ့ function (model (သို့) script) |
| **adapter** | MCP tool → LangChain tool (name + description + args_schema + async callable) |
| **reducer** | state key တစ်ခုရဲ့ value များကို ပေါင်းတဲ့ function (`add_messages`) |
| **checkpointer** | run တစ်ခုစီရဲ့ state ကို thread တစ်ခုစီအတွက် သိမ်းတဲ့ object (`MemorySaver`) |
| **thread_id** | စကားပြောခန်း တစ်ခုရဲ့ အမည် (checkpointer အတွက် မဖြစ်မနေ) |
| **allowlist** | ခွင့်ပြုသည့် tool/ path စာရင်း (security boundary) |
| **emission** | model ထုတ်တဲ့ structured request: `{"name": ..., "args": ...}` |
| **stop condition** | loop/cycle ရပ်စေတဲ့ အကြောင်းရင်း (chooser ရပ် (သို့) budget ကုန်) |

---

## အပိုင်း ၁၀ — နောက်သင်ခန်းစာများသို့

```text
M10 security  — ဒီ module ရဲ့ ကာကွယ်မှုများ (allowlist, confinement, audit, attack matrix)
M11 capstone  — host တစ်ခု ကိုယ်တိုင်ရေးခြင်း (lab_5: phase A scripted, phase B graph)
              ⭐ M11 lab_5 သည် M9 ရဲ့ lesson ကို M11 ရဲ့ server ပေါ် တကယ် အသုံးချထားသည်
```

⭐ နောက်တစ်ဆင့်ကို ကိုယ်တိုင် စမ်းရန်:

```text
၁. သင့်ကိုယ်ပိုင် server တစ်ခု ရေးပါ (tool ၃ ခု၊ resource ၁ ခု၊ prompt ၁ ခု)
၂. lab_1_client_loop.py ကို သင့် server ပေါ် ချိတ်ပါ — surface လေးခု ရှာပါ
၃. lab_3_hand_adapter.py ရဲ့ adapter ဖြင့် tool တွေကို LangChain အဖြစ် ပြောင်းပါ
၄. lab_6_stop_condition.py ရဲ့ budget router ကို ထည့်ပါ
၅. Cline settings ထဲ သင့် server ကို ထည့်ပြီး lab_2 ဖြင့် launch စမ်းပါ
   → ဒီငါးဆင့်သည် ဒီ module တစ်ခုလုံးရဲ့ အကျဉ်းချုပ် ဖြစ်သည်
```

## ကိုးကား

- [`../code/`](code/) — module ရဲ့ code ဖိုင်အားလုံး
- [`../code/cline_mcp_settings.json`](code/cline_mcp_settings.json) — host setting
- [`../../VERIFIED.md`](../VERIFIED.md) — တိုင်းထားသည့် API အချက်အားလုံး
- `01-client-loop-is-ordinary-programming.md` — မူရင်းဖိုင် ၁
- [`../M11_capstone/code/lab_5_autonomous_client.py`](../M11_capstone/code/lab_5_autonomous_client.py) — နောက်တစ်ဆင့်
