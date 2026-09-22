# M9 — အဖြေများ (solution.md)

## LAB 1 — client loop ကိုကိုယ်တိုင်ရေးခြင်း (LLM မပါဘဲ)

``python
# lab_1_client_loop.py — a client loop with no model at all
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server = StdioServerParameters(command="python", args=["server.py"])
    # three surfaces in one loop: list, call, read
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = [t.name for t in tools.tools]
            print("tools:", names)
            result = await session.call_tool(names[0], {})
            print("result:", result.content[0].text)

asyncio.run(main())
``

**အဓိကအယူအဆ** — LLM မပါပဲနဲ့ပဲ `list_tools` နဲ့ `call_tool` ကို loop တစ်ခုအဖြစ် ခေါ်နိုင်တယ်ဆိုတာ client ဆိုတာ သာမာန် programming သာဖြစ်တယ်။

## LAB 2 — မျက်နှာလေးဖက်ကို server သုံးခုနဲ့ တွေ့ဆုံခြင်း

``python
# lab_2 — discover all four surfaces from a real server
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def probe(command: str, args: list[str]):
    params = StdioServerParameters(command=command, args=args)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("tools:", (await session.list_tools()).tools)
            print("resources:", (await session.list_resources()).resources)
            print("templates:", (await session.list_resource_templates()).resourceTemplates)
            print("prompts:", (await session.list_prompts()).prompts)

asyncio.run(probe("python", ["server.py"]))
``

**အဓိကအယူအဆ** — client method လေးခုဖြစ်တဲ့ `list_tools`, `list_resources`, `list_resource_templates`, `list_prompts` ကနေ server ရဲ့ မျက်နှာလေးဖက်ကို အတိအကျ မြင်နိုင်တယ်။

## LAB 3 — ခေါ်မခေါ်မှ ငြင်းတတ်တဲ့ dispatcher

``python
# lab_7_dispatch_table.py — validate before you call
import json

def dispatch(session, emission: str):
    # a model emits: name + arguments as a JSON string
    parsed = json.loads(emission)
    name = parsed.get("name")
    args = parsed.get("arguments", {})
    schema = DISPATCH_TABLE[name]  # each entry holds the schema
    for key, spec in schema["properties"].items():
        if key in spec.get("required", []) and key not in args:
            return f"refused: missing required key '{key}'"
    return session.call_tool(name, args)
``

**အဓိကအယူအဆ** — dispatcher တစ်ခြောက်က JSON Schema အတိုင်း arguments ကို စစ်ပြီးမှ ခေါ်ရတဲ့အတွက် model ရဲ့ emission မှားရင် server ဆီ မရောက်မီ ငြင်းနိုင်တယ်။

## LAB 4 — host ရဲ့ settings ကို audit လုပ်ခြင်း

``python
# lab_2_cline_settings.py — audit cline_mcp_settings.json
import json

with open("cline_mcp_settings.json", encoding="utf-8") as f:
    settings = json.load(f)

for name, entry in settings.get("mcpServers", {}).items():
    # every stdio entry needs at least command and args to launch
    print(name, "->", entry.get("command"), entry.get("args", []))
    if "command" not in entry:
        print(f"  BROKEN: '{name}' has no command")
``

**အဓိကအယူအဆ** — `cline_mcp_settings.json` ထဲက `mcpServers` entry တစ်ခုစီက stdio transport အတွက် `command` နဲ့ `args` ပါရင် launch လုပ်နိုင်တယ်ဆိုတာ settings ဖိုင်ကို FastMCP code အဖြစ် ပြန်ဘာသာပြန်ပြီး စစ်ဆေးနိုင်တယ်။

## LAB 5 — adapter ကို လက်ဖြင့်ရေးခြင်း

``python
# lab_3_hand_adapter.py — MCP schema -> LangChain tool, by hand
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool

class AddInput(BaseModel):
    a: float = Field(description="first number")
    b: float = Field(description="second number")

def _add(a: float, b: float) -> str:
    return str(a + b)  # replace with a real session.call_tool(...)

add_tool = StructuredTool.from_function(func=_add, name="add",
    description="add two numbers", args_schema=AddInput)
``

**အဓိကအယူအဆ** — MCP schema ကို Pydantic model အဖြစ် ပြောင်းပြီး `StructuredTool.from_function` နဲ့ LangChain tool ဆောက်တဲ့ လက်ဖြင့်ရေးထားတဲ့ adapter က one-liner ထက် ပိုတိကျပြီး မှားစရာနည်းတယ်။

## LAB 6 — reducer ကို တိုင်းတာခြင်း

``python
# lab_5_state_reducer.py — add_messages appends, it does not overwrite
from langgraph.graph import MessagesState

class State(MessagesState):
    counter: int  # keys without a reducer are simply overwritten

state = {"messages": [("user", "hi")], "counter": 0}
first = StateSchema.apply(state, [("ai", "hello")])
``

**အဓိကအယူအဆ** — `add_messages` reducer က message list ကို အစားထိုးတာမဟုတ်ဘဲ တန်းစာ ထပ်ထည့်တယ်၊ reducer မပါတဲ့ key တွေကတော့ အစားထိုးတယ်။

## LAB 7 — stop condition မဲ့ loop နဲ့ budget

``python
# lab_6_stop_condition.py — a step budget guards the cycle
from langgraph.graph import StateGraph, MessagesState, START, END

def agent(state: MessagesState):
    budget = state.get("step_budget", 3) - 1
    if budget <= 0:
        return {"messages": [("ai", "budget exhausted")], "step_budget": 0}
    # otherwise keep the cycle going with one more tool call
    return {"messages": [("ai", "call again")], "step_budget": budget}
``

**အဓိကအယူအဆ** — graph ထဲက cycle တစ်ခုဟာ `tools_condition` ဆီ ပြန်လှည့်နေတာကြောင့် state ထဲမှာ step budget ထားပြီး stop condition မလိုမခင် ရပ်ရတယ်။

## LAB 8 — thread တစ်ခုကို ကိုယ်တိုင်တိုင်းခြင်း

``python
# checkpointing: turn 2 remembers turn 1 via thread_id
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, START, END

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)
config = {"configurable": {"thread_id": "lab-8"}}
graph.invoke({"messages": [("user", "my name is Aung")]}, config)
second = graph.invoke({"messages": [("user", "what is my name?")]}, config)
print(second["messages"][-1].content)  # the model still knows turn 1
``

**အဓိကအယူအဆ** — checkpointer နဲ့ `thread_id` ပါတဲ့ `config` ရှိရင် graph run တိုင်း မမှတ်တဲ့ state အသစ် မဟုတ်ဘဲ အရင် turn ကို ပြန်မှတ်တယ်။

## LAB 9 — chooser နှစ်မျိုးကို တွဲပြခြင်း

``python
# one graph, two brains: the chooser is swappable
def scripted_chooser(state):
    # deterministic: pick the tool by simple rules, no API key needed
    if "add" in state["messages"][-1].content:
        return {"messages": [("ai", "tool_call:add")]}

def model_chooser(state):
    # ask the model which tool fits, requires an API key
    response = model.invoke(state["messages"])
    return {"messages": [response]}
``

**အဓိကအယူအဆ** — chooser က graph ထဲက swap လုပ်နိုင်တဲ့ အစိတ်အပိုင်းတစ်ခုသာဖြစ်လို့ scripted chooser နဲ့ API key မလိုပဲ test လုပ်ပြီး model chooser နဲ့ ပြောင်းနိုင်တယ်။

## LAB 10 — server နှစ်ခု၊ graph တစ်ခု

``python
# lab_8_two_servers.py — one host, two servers, one graph
async def main():
    async with connect("python", ["server_a.py"]) as a, connect("python", ["server_b.py"]) as b:
        tools = a_tools + b_tools  # merged tool list for the graph
        # use an allowlist so the model only sees the tools you chose
        allowlist = [t for t in tools if t.name in ALLOWED]
        print("merged tools:", [t.name for t in allowlist])
``

**အဓိကအယူအဆ** — host တစ်ခုက server အများအပြားကနေ tool တွေကို ပေါင်းစည်းပြီး allowlist နဲ့ ကန့်သတ်နိုင်တာကြောင့် server တစ်ခုကို host များစွာက ဝေမျှသလို host တစ်ခုက server များစွာကို ဦးစီးနိုင်တယ်။
