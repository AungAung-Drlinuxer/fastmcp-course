# M9 — Host & Client Orchestration (ရှင်းလင်းချက်)

## အပိုင်း ၁ — Client loop ဆိုတာ ဘာလဲ

### ဘာကို ဆိုလိုတာလဲ
MCP client ဆိုတာ — model မပါတဲ့ program တစ်ခုပါ။ Server နဲ့ connection ဖွင့်ပြီး tool တွေကို ခေါ်တယ်။ ဒါပဲ မဟုတ်ဘူး — "ဘယ် tool ကို ဘယ် argument နဲ့ ခေါ်မလဲ" ဆိုတာကို ဆုံးဖြတ်တဲ့ loop လည်း အလုပ်လုပ်ရတယ်။ ဥပမာ — အခေါက်ဆက်တဲ့သူက အော်ဒါယူတာ၊ မီးဖိုချောင်က ချက်ပေးတာလိုမျိုးပါ။ ဒါက သာမန် programming ပါ၊ magic မဟုတ်ပါနော်။

### ဘာကြောင့် လဲ
Model မပါရင် ပြဿနာက ရှင်းမပြနိုင်တာ ဖြစ်တယ်။ Tool မအလုပ်လုပ်ရင် — tool ဘက်ကြောင့်လား၊ chooser ဘက်ကြောင့်လား၊ server ဘက်ကြောင့်လား — မခွဲနိုင်ဘူး။ Model နဲ့ client ကို ခွဲထားရင် ဒီသုံးခုကို ခွဲခြားနိုင်တယ်။ ဒါကြောင့် model မပါဘဲ client loop ကို ကိုယ်တိုင်ရေးကြည့်တာက orchestration ရဲ့ အခြေခံအုတ်မြစ်ဖြစ်တယ်။

### ဘယ်လို အလုပ်လုပ်လဲ
`Client` ကို server နဲ့ တွဲဖွင့်ပြီး အောက်က လှည့်ကွက်လေးကို လည်ပတ်စေတာပါ။
၁။ Server ရဲ့ surface တွေကို အရင် စစ်တယ်။
၂။ Chooser က tool တစ်ခု ရွေးတယ်။
၃။ ရွေးထားတဲ့ tool ကို ခေါ်တယ်။
၄။ ရလဒ်ကို ကြည့်တယ်။
၅။ ဆက်လုပ်စရာ ရှိရင် နောက်တစ်ဆင့် ထပ်ရွေးတယ်။
Module ရဲ့ `tool_loop.py` နဲ့ `lab_1_client_loop.py` က ဒီ loop ရဲ့ အသေးစိတ်ပါ။

### ဥပမာ
နောက်မှာ ပါလာမယ့် code က model မပါဘဲ client loop တစ်ခု ဘယ်လို လည်ပတ်လဲ ဆိုတာ ပြထားတယ်။ Surface စစ်တဲ့အဆင့်နဲ့ chooser ရွေးတဲ့အဆင့်ကို အထူး သတိထားကြည့်ပါ။
```python
from mcp import Client
from client import choose_next_call

with Client(server) as c:
    tools = c.list_tools()
    while True:
        call = choose_next_call(tools)
        if call is None:
            break
        result = c.call_tool(call.name, call.args)
        print(result)
# Expected output:
# tool call: get_weather {"city": "Yangon"} -> sunny
# loop finished
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
MCP ကို model မပါဘဲ စစ်လို့ရရင် debugging လည်း လွယ်သွားပါတယ်၊ testing လည်း လွယ်သွားပါတယ်။ Model မပါရင် ဘာဖြစ်နေလဲ ဆိုတာကို တိုက်ရိုက်ကြည့်လို့ရတယ်။ `test_m9_client_loop.py` က client loop ကို model မပါဘဲ စစ်ပေးတဲ့ နမူနာ ဖြစ်ပါတယ်။ ဒါမျိုး စစ်နိုင်ဖို့က production မှာ အချိန်အများကြီး ချွေတာပေးပါတယ်။

## အပိုင်း ၂ — Surface လေးမျိုးနဲ့ dispatch

### ဘာကို ဆိုလိုတာလဲ
Client မှာ အပြင်အဆင် လေးမျိုးရှိပါတယ် — tools, resources, templates (resource templates), prompts။ Surface ဆိုတာက server က ပြချင်တဲ့ အလုပ်တွေရဲ့ စာရင်းလို့ မှတ်နော်။ Model က tool တစ်ခုခေါ်မယ်ဆို JSON ထဲမှာ နာမည်နဲ့ arguments ထည့်ပြီး ထုတ်လိုက်တာပါ။ Dispatcher ဆိုတာက အဲဒီ JSON ကိုယူပြီး တကယ့် function call အဖြစ် ပြောင်းပေးတဲ့ အလွှာလေးပါ။

### ဘာကြောင့် လဲ
Host တစ်ခုက server ရဲ့ surface လေးမျိုးလုံးကို မြင်ရပါတယ်။ Model ထုတ်လိုက်တဲ့ JSON က schema နဲ့ မကိုက်ရင် ဘာမှမလုပ်ဘဲ ငြင်းပယ်ရပါတယ်။ ဒါမှမှ tool မှားခေါ်မိတာ၊ အချက်အလက်ပျက်စီးတာကနေ ကာကွယ်လို့ရပါတယ်။ Dispatcher က ခေါ်ခင် စစ်ပြီးမှ ခေါ်တာဆိုလို့ အန္တရာယ်ကို ကာကွယ်ပေးတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ `Client` ကို ဖွင့်တဲ့နည်းနှစ်မျိုးရှိပါတယ်။
၂။ Model က tool နာမည်နဲ့ arguments ပါတဲ့ JSON ထုတ်လိုက်ပါတယ်။
၃။ Dispatcher က schema အရ arguments တွေမှန်လား စစ်ပါတယ်။
၄။ မှန်ရင် function ကို ခေါ်ပါတယ်၊ မှားရင် ငြင်းပယ်ပါတယ်။
၅။ `read_resource` က form မှန်ကန်မှ အလုပ်လုပ်လို့ အမှားများတဲ့နေရာပါ၊ သတိထားနော်။
၆။ တစ်လှည့်ထဲမှာ tool နှစ်ခု ခေါ်တာလည်း ဖြစ်နိုင်ပါတယ်။

### ဥပမာ
```python
def dispatch(emission, registry):
    # Refuse before calling when the name is unknown or args fail the schema
    tool = registry.get(emission["name"])
    if tool is None:
        raise KeyError("unknown tool: " + emission["name"])
    tool.validate_args(emission["arguments"])
    return tool.run(emission["arguments"])
# Expected output:
# KeyError: unknown tool: delete_everything
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
Model က တစ်ခါတစ်ရံ မှားတဲ့ tool ကို ခေါ်လိုက်တတ်ပါတယ်။ ဒါကို မယုံရပါနော်။
ဒါကြောင့် schema အရ ငြင်းပယ်တတ်တဲ့ dispatcher (`lab_7_dispatch_table.py`) လိုမျိုး လိုအပ်တာပါ။
ဒီလို စစ်တဲ့ အလွှာမှာမရှိရင် — မရှိတဲ့ tool ကို ခေါ်မိပြီး program ပျက်နိုင်ပါတယ်။
Production မှာဆို မှားတဲ့ tool ခေါ်မိရင် data ပျက်စေတာ ဒါမှမဟုတ် downtime ဖြစ်စေနိုင်ပါတယ်။

## အပိုင်း ၃ — Host နဲ့ Cline settings

### ဘာကို ဆိုလိုတာလဲ
Host ဆိုတာ — client loop နဲ့ chooser ကို တစ်နေရာတည်း ပေါင်းထားတဲ့ အက်ပလီကေးရှင်းပါ။
Client loop ဆိုတာ server နဲ့ စကားပြောတဲ့ အလုပ်ကို လုပ်တဲ့ အပိုင်းလေးပါ။ Chooser ဆိုတာ — များသောအားဖြင့် model က ဘယ် tool ကို ခေါ်မလဲ ဆုံးဖြတ်တဲ့ အပိုင်းပါ။
Cline လို host တွေက server စာရင်းကို `cline_mcp_settings.json` ဖိုင်ထဲ သိမ်းထားပါတယ်။ အဲဒါကို stdio transport နဲ့ ချိတ်ပါတယ်။

### ဘာကြောင့် လဲ
Server တစ်ခု ရေးပြီးပေမယ့် host က မှတ်တမ်းသွင်းမထားရင် သူများတွေ မမြင်ရပါ။
ဆိုလိုတာက — ဘယ်သူမှ အဲဒီ server ကို သုံးလို့မရပါဘူး။
Settings entry တစ်ခုက `command`, `args`, `env` တွေနဲ့ ဘယ် process ကို ဘယ်လို စတင်ရမလဲ ပြောပြပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ
Settings entry မှာ သိမ်းတဲ့ အချက်အလက်တွေက FastMCP code နဲ့ အတူတူပါပဲ။
ကွာခြားတာက — တစ်ခုက code နဲ့ရေးတာ၊ တစ်ခုက config ဖိုင်နဲ့ရေးတာပါ။
၁။ Settings ဖိုင်ထဲမှာ server တစ်ခုရဲ့ entry ကို ဖတ်ပါတယ်။
၂။ `command` နဲ့ `args` ကို ယူပြီး ဘယ် program ကို run ရမလဲ သိပါတယ်။
၃။ `env` က environment variable တွေ ထည့်ပေးပါတယ်။
၄။ အဲဒါတွေနဲ့ server process ကို stdio နဲ့ စတင်ပါတယ်။
၅။ Server ပြန်လာရင် ချိတ်ပြီး သုံးလို့ရပါပြီ။

### ဥပမာ
အောက်က code က `lab_2_cline_settings.py` က settings ဖိုင်ကို ဖတ်ပြီး entry တစ်ခုစီကို စစ်ပြထားတာပါ။ ဘယ် entry က တကယ် launch လုပ်လို့ရမလဲ ဆိုတာကို သတိထားကြည့်ပါနော်။
```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["server.py"],
      "env": {},
      "disabled": false
    }
  }
}
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Host တစ်ခုရဲ့ settings ကို စစ်ကြည့်နိုင်တာက အရေးကြီးပါတယ်။ Settings စစ်တယ်ဆိုတာ — ဘယ် server တွေ ပါလဲ၊ ဘယ် environment variable တွေ သုံးလဲ ဆိုတာကို မြင်တာပါ။ ဒါက security (M10) ရဲ့ ပထမဆုံး စတင်စစ်ရတဲ့ နေရာလည်း ဖြစ်ပါတယ်။ ဒီအဆင့်ကို မစစ်ဘူးဆိုရင် မသိတဲ့ server တွေ ဝင်နေတာကို မမြင်ရတော့ပါဘူး။

## အပိုင်း ၄ — MCP → LangChain adapter နဲ့ LangGraph state

### ဘာကို ဆိုလိုတာလဲ

Adapter ဆိုတာ — တစ်ဘက် format ကို တစ်ဘက် format ပြောင်းပေးတဲ့ ချိတ်ဆက်ပစ္စည်းလေးပါ။ ဒီနေရာမှာတော့ MCP tool တစ်ခုကို LangChain သုံးလို့ရအောင် ပြောင်းပေးတာပါ။ ပြောင်းရင် schema ကို Pydantic model အဖြစ် ရေးရပါတယ်။ Pydantic model ဆိုတာ — field တွေရဲ့ အမျိုးအစားကို သတ်မှတ်ပေးထားတဲ့ Python class လေးပါ။ ပြီးရင် LangGraph graph ရဲ့ state ကို သတ်မှတ်ရပါတယ်။ State ထဲမှာ message list တွေ ပါပြီး `add_messages` reducer နဲ့ ပေါင်းရပါတယ်။ Reducer ဆိုတာ — state update လုပ်တဲ့အခါ အသစ်နဲ့ အဟောင်းကို ဘယ်လိုပေါင်းမလဲ ဆိုတဲ့ ဖန်ရှင်ပါ။

### ဘာကြောင့် လဲ

MCP က schema ကို JSON Schema ပုံစံနဲ့ ပေးပါတယ်။ ဒါပေမယ့် LangChain က Pydantic model ကိုပဲ ခံယူပါတယ်။ ဒါကြောင့် ကြားမှာ ပြောင်းပေးဖို့ လိုအပ်ပါတယ်။ "လွယ်တဲ့နည်း" ဆိုပြီး schema ကို ရှင်းပဲ pass လုပ်တာမျိုး ရေးမိရင် အလုပ်မလုပ်ပါဘူး။ Error တက်ပြီး tool ခေါ်လို့ မရတော့တာနဲ့ တူပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ MCP server ဆီက tool ရဲ့ schema ကို ယူပါတယ်။

၂။ JSON Schema ကို Pydantic model အဖြစ် ပြောင်းပါတယ်။

၃။ Pydantic model ကို LangChain tool ထဲထည့်ပြီး သုံးလို့ရအောင် လုပ်ပါတယ်။

၄။ LangGraph graph ရဲ့ state မှာ `messages` key ကို `add_messages` reducer နဲ့ သတ်မှတ်ပါတယ်။

၅။ Reducer လိုတဲ့ key နဲ့ မလိုတဲ့ key က အပြုအမူ မတူတာကို သတိပြုပါ။

### ဥပမာ

ဒီ snippet မှာ adapter နှစ်မျိုးကို နှိုင်းယှဉ်ပြထားပါတယ် — one-liner နည်းနဲ့ လက်ဖြင့်ရေးတဲ့နည်း (`lab_3_hand_adapter.py`) ပါ။ Reducer က list နှစ်ခုကို ပေါင်းတာမျိုး မဟုတ်ဘဲ ယူငင်တဲ့သဘောနဲ့ အလုပ်လုပ်တဲ့ နေရာကို ကြည့်ပါနော်။
```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class State(TypedDict):
    # add_messages merges new messages into the existing list instead of replacing
    messages: Annotated[list, add_messages]
    budget: int  # keys without a reducer are simply overwritten
# Expected output:
# State(messages=[...appended...], budget=3)
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
Adapter ကို ကိုယ်တိုင် တစ်ခေါက် ရေးကြည့်ရင် auto-conversion က တကယ် ဘာလုပ်နေသလဲ သိလာပါတယ်။ ဒါဆို အလုပ်မလုပ်တဲ့အခါ ကိုယ်တိုင် ပြင်တတ်ပါတယ်။ မဟုတ်ရင်တော့ error ထွက်တာနဲ့ နာရီပေါင်းများစွာ debug လုပ်ရပါလိမ့်မယ်။ `lab_5_state_reducer.py` က reducer ရဲ့ တိကျတဲ့ အပြုအမူကို တိုင်းပြပါတယ်။

## အပိုင်း ၅ — Graph cycle, stop condition, checkpointing နဲ့ chooser နှစ်မျိုး

### ဘာကို ဆိုလိုတာလဲ
LangGraph graph မှာ node တွေ၊ edge တွေနဲ့ cycle တစ်ခု ပါပါတယ်။ Node ဆိုတာ — အလုပ်တစ်ခု လုပ်ပေးတဲ့ အဆင့်လေးပါ။ Cycle ဆိုတာ — node တွေက အလှည့်ကျ ပြန်ခေါ်နေတဲ့ ပတ်လမ်းပါ။ ပတ်လမ်းထဲမှာ ဘယ်အချိန် ရပ်မယ်ဆိုတာ stop condition က သတ်မှတ်ပါတယ်။ Checkpointer နဲ့ `thread_id` က run အလှည့်များကြား state ကို မှတ်ထားပေးပါတယ်။ Chooser နှစ်မျိုးရှိပါတယ် — scripted chooser နဲ့ model chooser ပါ။ ဒီနှစ်ခုက တူညီတဲ့ graph ထဲမှာ ပုံစံနှစ်မျိုးနဲ့ အလုပ်လုပ်ပါတယ်။

### ဘာကြောင့် လဲ
Stop condition မပါတဲ့ cycle က ဘယ်တုန်းမှ မရပ်ပါဘူး။ ဒါကြောင့် budget (step အရေအတွက် ကန့်သတ်ချက်) ကို state ထဲ ထည့်ပြီး ကာကွယ်ရပါတယ်။ မကာကွယ်ရင် API bill တက်သွားပြီး app က ဆက်လက် မဆုံးပါ။ `tools_condition` က model reply ထဲမှာ tool call ရှိမရှိ အရ လမ်းကြောင်း ရွေးပေးပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ `tools_condition` က model message ထဲ `ToolMessage`/tool call ရှိလား အရင်စစ်ပါတယ်။
၂။ ရှိရင် `ToolNode` ဆီ၊ မရှိရင် END ဆီ လမ်းပြပါတယ်။
၃။ Checkpointer (`MemorySaver` အသုံးအများဆုံး) က state ကို process memory ထဲ မှတ်ပါတယ် — durable မဟုတ်ပါဘူး။
၄။ `thread_id` မပါဘဲ checkpointer နဲ့ run ရင် error တက်ပါတယ်။
၅။ Scripted chooser က API key မလိုပါဘူး — ရေးထားတဲ့ စည်းမျဉ်းအရ tool ရွေးပါတယ်။
၆။ Model chooser က LLM ကနေ ရွေးတာမို့ key မရှိရင် run မလုပ်နိုင်ပါဘူး။

### ဥပမာ
ဒီ snippet မှာ stop condition ပါတဲ့ cycle၊ checkpointer၊ `thread_id` သုံးပုံနဲ့ chooser နှစ်မျိုး ပြထားပါတယ်။ Run နှစ်ခုကြား အလှည့်ကျ state ပြန်ရမလား၊ `thread_id` မပါရင် error တက်မလား ဆိုတာကို ကြည့်ပါနော်။
```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

builder = StateGraph(State)
builder.add_node("model", model_chooser)
builder.add_node("tools", tool_node)
builder.set_entry_point("model")
builder.add_conditional_edges("model", tools_condition)
builder.add_edge("tools", "model")
graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "demo-1"}}
# Expected output:
# turn 1: tool call -> tool result -> final answer
# turn 2 (same thread_id): state from turn 1 is still present
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
`lab_6_stop_condition.py` မှာ stop condition မပါတဲ့ loop နဲ့ budget ထည့်ထားတဲ့ version ကို နှိုင်းယှဉ်ပြထားပါတယ်။ stop condition မပါရင် loop က မရပ်တော့ဘူးဆိုတာ မြင်ရမယ်။ `lab_4_graph_offline.py` နဲ့ `lab_8_two_servers.py` က graph တစ်ခုနဲ့ server နှစ်ခု တွဲနည်းပြပါတယ်။ Chooser နှစ်မျိုးကို နှိုင်းနိုင်ရင် API key မရှိတဲ့ environment မှာလည်း test လုပ်နိုင်တဲ့ စနစ် ဆောက်နိုင်ပါတယ်။ နောက်တစ်ခု — server တစ်ခုကို host များစွာက ချိတ်လို့ရသလို host တစ်ခုကလည်း server များစွာကို ချိတ်လို့ရပါတယ်။ ဒါပေမယ့် host ဘက်က tool list ကို allowlist — ခွင့်ပြုထားတဲ့ tool စာရင်း — အဖြစ် စစ်ပြီးမှ ချိတ်သင့်ပါတယ်။ မစစ်ရင် လိုအပ်တဲ့ tool အစား မှားတဲ့ tool ခေါ်မိပြီး debug အချိန် ကြာသွားနိုင်ပါတယ်။

## အနှစ်ချုပ်

- **Client loop က ordinary programming ပါ** — model မပါဘဲ ရေးနိုင်ပြီး test လုပ်နိုင်ပါတယ်။
- **Surface လေးမျိုး** — tools, resources, templates, prompts — ကို client method တွေနဲ့ တိတိကျကျ စစ်နိုင်ပါတယ်။
- **Dispatcher က ခေါ်ခင် schema အရ ငြင်းရမယ်** — model ရဲ့ JSON emission က အမြဲမှန်နေမယ် မဟုတ်ပါ။ မစစ်ရင် မှားတဲ့ argument နဲ့ tool ပြေးမိပြီး error ထွက်ပါတယ်။
- **Host registration က config ပါ** — `cline_mcp_settings.json` entry တစ်ခုက FastMCP server တစ်ခုရဲ့ launch အချက်အလက် ဖြစ်ပါတယ်။ config မှားရင် server တက် မှာ မဟုတ်ပါ။
- **Adapter က schema ကို Pydantic model အဖြစ် ပြောင်းရတယ်** — လက်ဖြင့် ရေးတဲ့ လွယ်လွယ်နည်းက မှားလွယ်ပါတယ်။
- **State ထဲက `messages` key က `add_messages` reducer နဲ့ ပေါင်းတယ်** — အခြား key တွေက overwrite ဖြစ်ပါတယ်။ reducer မသိရင် အဖြစ်အပျက် တစ်ခုကို နောက်တစ်ခုက ဖုံးလွှမ်းပြီး ပျောက်သွားနိုင်ပါတယ်။
- **Cycle တိုင်းမှာ stop condition လိုပါတယ်** — step budget က loop မရပ်တာကို ရပ်တန့်စေတဲ့ တစ်ခုတည်းသော နည်းလမ်းပါ။ budget မထည့်ရင် agent က အလုပ်ချောင်သွားရင်တောင် ရပ်ပေးမှာ မဟုတ်ပါ။