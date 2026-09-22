# M9 — Host & Client Orchestration (ရှင်းလင်းချက်)

## အပိုင်း ၁ — Client loop ဆိုတာ ဘာလဲ

### ဘာကို ဆိုလိုတာလဲ
MCP client ဆိုတာ model မပါတဲ့ program တစ်ခုပါ။ Server နဲ့ connection ဖွင့်ပြီး tool တွေကို ခေါ်ရုံသက်သက်မဟုတ်ဘူး — "ဘယ် tool ကို ဘယ် argument နဲ့ ခေါ်မလဲ" ဆုံးဖြတ်တဲ့ loop တစ်ခုလည်း အလုပ်လုပ်ရတယ်။ ဒါက ဗန်းကျတဲ့ programming ပါ၊ magic မဟုတ်ပါ။

### ဘာကြောင့် လဲ
Model နဲ့ client ကို ခွဲမြင်နိုင်မှ ပြဿနာတစ်ခုက tool ဘက်ကြောင့်လား၊ chooser ဘက်ကြောင့်လား၊ server ဘက်ကြောင့်လား ခွဲခြားနိုင်လို့ပါ။ Model မပါဘဲ client loop တစ်ခုကို ကိုယ်တိုင်ရေးကြည့်တာက orchestration ရဲ့ အခြေခံအုတ်မြစ်ပါ။

### ဘယ်လို အလုပ်လုပ်လဲ
`Client` ကို server နဲ့ တွဲဖွင့်ပြီး — (၁) surface တွေကို စစ်၊ (၂) chooser က tool တစ်ခု ရွေး၊ (၃) ခေါ်၊ (၄) ရလဒ်ကို ကြည့်ပြီး ထပ်ရွေး — ဆိုတဲ့ လှည့်ကွက်လေးကို လည်ပတ်စေတာပါ။ Module ရဲ့ `tool_loop.py` နဲ့ `lab_1_client_loop.py` က ဒီ loop ရဲ့ အသေးစိတ်ပါ။

### ဥပမာ
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
MCP ကို model မပါဘဲ စစ်မေးနိုင်ရင် debugging ရော၊ testing ရော သိသိသာသာ လွယ်သွားပါတယ်။ `test_m9_client_loop.py` က client loop ကို model မပါဘဲ စစ်ပေးတဲ့ နမူနာပါ။

## အပိုင်း ၂ — Surface လေးမျိုးနဲ့ dispatch

### ဘာကို ဆိုလိုတာလဲ
Client မှာ surface လေးမျိုးရှိပါတယ် — tools, resources, templates (resource templates), prompts။ Model က tool ခေါ်မယ်ဆိုတာက JSON ထဲမှာ နာမည်နဲ့ arguments ထုတ်တာပါ။ Dispatcher က အဲဒီ emission ကိုယူပြီး တကယ့် function call အဖြစ် ပြောင်းပေးရတယ်။

### ဘာကြောင့် လဲ
Host တစ်ခုက server ရဲ့ surface လေးမျိုးလုံးကို မြင်နိုင်ရပြီး၊ model ထုတ်လိုက်တဲ့ JSON က schema နဲ့ မကိုက်ရင် ခေါ်ခြင်းမခေါ်ဘဲ ငြင်းပယ်ဖို့လိုလို့ပါ။ "ခေါ်ခြင်းမခေါ်ခင် ငြင်းတတ်တဲ့" dispatcher က ဘေးအန္တရာယ်ကို ကာကွယ်ပေးတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ
`Client` ကို ဖွင့်တဲ့နည်းနှစ်မျိုးရှိပြီး၊ `read_resource` က form မှန်မှန်ကန်ကန် သုံးမှ အလုပ်လုပ်တတ်လို့ အမှားများတဲ့နေရာလို့ သတ်မှတ်ထားပါတယ်။ Dispatcher က schema အရ argument တွေကို စစ်ပြီးမှ ခေါ်တာပါ။ တစ်လှည့်ထဲမှာ tool နှစ်ခု ခေါ်တာလည်း ဖြစ်နိုင်ပါတယ်။

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
Model ရဲ့ ရွေးချယ်မှုက အမြဲမှန်ကန်မယ် ဆိုတာ မယုံရပါ။ Schema အရ ငြင်းတတ်တဲ့ dispatcher (`lab_7_dispatch_table.py`) က production system တိုင်းမှာ လိုအပ်တဲ့ လုံခြုံမှုတစ်ခုပါ။

## အပိုင်း ၃ — Host နဲ့ Cline settings

### ဘာကို ဆိုလိုတာလဲ
Host ဆိုတာ client loop နဲ့ chooser (များသောအားဖြင့် model) ကို တစ်နေရာတည်း ပေါင်းစပ်ထားတဲ့ အက်ပလီကေးရှင်းပါ။ Cline လို host တွေက server တွေကို `cline_mcp_settings.json` ဖိုင်ထဲမှာ stdio transport နဲ့ စာရင်းသွင်းထားပါတယ်။

### ဘာကြောင့် လဲ
Server တစ်ခု ရေးပြီးသားသားနဲ့ host တစ်ခုမှာ မှာတမ်းသွင်းမထားရင် သူများတွေ မမြင်ရပါ။ Settings entry တစ်ခုက `command`, `args`, `env` တွေနဲ့ ဘယ် process ကို ဘယ်လို စတင်ရမလဲ ဆိုတာ ပြောပြရတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ
Settings entry တစ်ခုစီက FastMCP code တစ်ခုနဲ့ တူညီတဲ့ အချက်အလက်တွေကို JSON အဖြစ် သိမ်းထားတာပါ — တစ်ခုက code၊ တစ်ခုက config။ `lab_2_cline_settings.py` က settings ဖိုင်ကို စစ်ပြီး entry တစ်ခုစီ တကယ် launch လုပ်နိုင်မှုကို သက်သေပြပါတယ်။

### ဥပမာ
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
Host တစ်ခုရဲ့ settings ကို audit လုပ်နိုင်စွမ်းက — ဘယ် server တွေ ပါဝင်သလဲ၊ ဘယ် environment variable တွေ သုံးသလဲ — ဆိုတာ မြင်နိုင်စွမ်းက security (M10) ရဲ့ အစပြုနေရာပါ။

## အပိုင်း ၄ — MCP → LangChain adapter နဲ့ LangGraph state

### ဘာကို ဆိုလိုတာလဲ
MCP tool တစ်ခုကို LangChain tool အဖြစ် ပြောင်းဖို့ schema ကို Pydantic model အဖြစ် ပြောင်းရပြီး၊ LangGraph graph တစ်ခုရဲ့ state က message list တွေပါဝင်ပြီး `add_messages` reducer နဲ့ ပေါင်းသည်။

### ဘာကြောင့် လဲ
"လွယ်တဲ့နည်း" (မှားတဲ့နည်း) က schema ကို မရှင်းပဲ pass လုပ်တာမျိုးမို့ — အလုပ်မလုပ်တတ်ပါ။ Schema က JSON Schema အဖြစ်ရှိပြီး LangChain က Pydantic model ကို မျှော်လင့်လို့ ကြားမှာ ပြောင်းပေးရတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ
Adapter နှစ်ခုမျိုးကို နှိုင်းယှဉ်နိုင်ပါတယ် — one-liner နည်းနဲ့ လက်ဖြင့်ရေးတဲ့နည်း (`lab_3_hand_adapter.py`)။ Graph state ထဲမှာ reducer လိုတဲ့ key (`messages`) နဲ့ မလိုတဲ့ key တွေ ကွဲပြားပြီး၊ reducer ကတော့ list နှစ်ခုကို ပေါင်းခြင်းအစား ယူငင်ခြင်းသဘောနဲ့ မတူတဲ့ အပြုအမူ ပြတယ်။

### ဥပမာ
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
Adapter ကို လက်ဖြင့်တစ်ခါ ရေးကြည့်ရင် auto-conversion က ဘာလုပ်နေသလဲ သိနိုင်ပြီး၊ အလုပ်မလုပ်တဲ့အခါ ကိုယ်တိုင် ပြင်နိုင်စွမ်း ရပါတယ်။ `lab_5_state_reducer.py` က reducer ရဲ့ တိကျတဲ့ အပြုအမူကို တိုင်းပြပါတယ်။

## အပိုင်း ၅ — Graph cycle, stop condition, checkpointing နဲ့ chooser နှစ်မျိုး

### ဘာကို ဆိုလိုတာလဲ
LangGraph graph တစ်ခုမှာ node တွေ (`ToolNode` အပါအဝင်)၊ edge တွေနဲ့ cycle တစ်ခုရှိပါတယ်။ Cycle တစ်ခုမှာ stop condition လိုပြီး၊ checkpointer နဲ့ `thread_id` က run အလှည့်များကြားမှာ state ကို မှတ်ထားပါတယ်။ Chooser နှစ်မျိုး — scripted chooser နဲ့ model chooser — ကတူညီတဲ့ graph မှာ အသွင်နှစ်မျိုးနဲ့ အလုပ်လုပ်ပါတယ်။

### ဘာကြောင့် လဲ
Stop condition မပါတဲ့ cycle က အဆုံးမသတ်နိုင်လို့ budget (step အရေအတွက် ကန့်သတ်ချက်) ကို state ထဲ ထည့်ပြီး ကာကွယ်ရပါတယ်။ `tools_condition` က model reply ထဲမှာ tool call ရှိမရှိအရ လမ်းကြောင်း ရွေးပေးတာပါ။

### ဘယ်လို အလုပ်လုပ်လဲ
`tools_condition` က model message ထဲ `ToolMessage`/tool call ရှိလားစစ်ပြီး `ToolNode` ဆီ သို့မဟုတ် END ဆီ လမ်းပြပါတယ်။ Checkpointer (`MemorySaver` အသုံးအများဆုံး) က state ကို process memory ထဲ မှတ်တယ် — durable မဟုတ်ပါ။ `thread_id` မပါဘဲ checkpointer နဲ့ run ရင် error တက်ပါတယ် (တိုင်းထားတဲ့ အချက်)။ Scripted chooser က API key မလိုပဲ ရေးသားထားတဲ့ စည်းမျဉ်းအရ tool ရွေးပြီး၊ model chooser က LLM အင်တာနက်ကနေ ရွေးတာမို့ key မရှိလျှင် run မလုပ်နိုင်ပါ။

### ဥပမာ
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
`lab_6_stop_condition.py` က stop condition မပါတဲ့ loop နဲ့ budget ထည့်ထားတဲ့ version ကို နှိုင်းပြီး၊ `lab_4_graph_offline.py` နဲ့ `lab_8_two_servers.py` က graph တစ်ခုနဲ့ server နှစ်ခု တွဲနည်းကို ပြပါတယ်။ Chooser နှစ်မျိုးကို နှိုင်းနိုင်ရင် API key မရှိတဲ့ environment မှာလည်း test ရနိုင်တဲ့ စနစ် ဆောက်နိုင်ပါတယ်။ တစ်ခုပြောရရင် — server တစ်ခုကို host များစွာက ချိတ်နိုင်သလို၊ host တစ်ခုကလည်း server များစွာကို tool list allowlist အဖြစ် စစ်ပြီး ချိတ်နိုင်ပါတယ်။

## အနှစ်ချုပ်

- **Client loop က ordinary programming ပါ** — model မပါဘဲ ရေးနိုင်ပြီး test နိုင်ပါတယ်။
- **Surface လေးမျိုး** — tools, resources, templates, prompts — ကို client method တွေနဲ့ တိတိကျကျ စစ်နိုင်ပါတယ်။
- **Dispatcher က ခေါ်ခြင်းမခေါ်ခင် schema အရ ငြင်းရမယ်** — model ရဲ့ JSON emission က အမြဲ မှန်မယ် မဟုတ်ပါ။
- **Host registration က config ပါ** — `cline_mcp_settings.json` entry တစ်ခုက FastMCP server တစ်ခုရဲ့ launch အချက်အလက် ဖြစ်ပါတယ်။
- **Adapter က schema ကို Pydantic model အဖြစ် ပြောင်းရတယ်** — လွယ်တဲ့နည်းက မှားတတ်ပါတယ်။
- **State ထဲက `messages` key က `add_messages` reducer နဲ့ ပေါင်းသည်** — အခြား key တွေက overwrite ဖြစ်ပါတယ်။
- **Cycle တိုင်းမှာ stop condition လိုပါ** — step budget က အဆုံးမသတ်တဲ့ loop တစ်ခုကို ရပ်တန့်စေတဲ့ တစ်ခုတည်းသော နည်းလမ်း ဖြစ်သည်။
