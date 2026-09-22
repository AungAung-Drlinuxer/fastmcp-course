# M0 — Orientation: MCP ဆိုတာ ဘာလဲ

## အပိုင်း ၁ — ပြဿနာကို အရင် မြင်ပါ

### ဘာကို ဆိုလိုတာလဲ

ဒီအပိုင်းမှာ ပြဿနာကို အရင် ပြပါမယ်။ AI model ကို ပြင်ပ tool တွေနဲ့ ချိတ်ချင်ရင် ဘာတွေ ခံရလဲဆိုတာ မြင်ရမယ်။ Tool ဆိုတာ — database၊ API၊ file system လို model အပြင်ဘက်က အကူအညီပေးတဲ့ အရာတွေကို ဆိုလိုတာပါ။

### ဘာကြောင့် လဲ

MCP မရှိခင် တစ်ခုချင်းစီအတွက် သီးသန့် integration ရေးရတယ်။ Integration ဆိုတာ — နှစ်ခုကို ချိတ်ပေးတဲ့ ချိတ်ဆက် code လေးပါ။ Model တစ်မျိုးချင်းစီ၊ tool တစ်ခုချင်းစီ ချိတ်နည်း မတူပါဘူး။ OpenAI format တစ်မျိုး၊ အခြား provider format တစ်မျိုး ရှိနေတယ်။ ဒါကြောင့် တစ်ခုပြောင်းရင် တစ်ခု ပြန်ရေးရတာပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Model အသစ်တစ်ခု ထည့်ချင်တယ်။
၂။ ရှိပြီး tool အားလုံးနဲ့ ချိတ်ဖို့ code အသစ် ပြန်ရေးရတယ်။
၃။ Tool အသစ်တစ်ခု ထည့်ချင်ရင်လည်း အပြန်အလှန် ရေးရပြန်တယ်။
၄။ ချိတ်ဆက် code တွေ ပိုများလာတယ်။
၅။ များလာတဲ့အမျှ စျေးကြီးလာပြီး ပြန်ထိန်းရခက်လာတယ်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

ဒီပြဿနာ မြင်ရင် MCP က ဘာကြောင့် ဖန်တီးထားလဲ နားလည်လာမယ်။ တကယ်လည်း အလုပ်မှာ model ပြောင်းရုံနဲ့ tool ချိတ် code တွေ တစ်သမတ်တည်း ရေးပြန်ရရင် အချိန်ကုန် ကျောပိုးတာပဲ ဖြစ်တယ်နော်။ USB port မရှိခင် စက်တစ်ခုချင်းစီကို ကြိုးအမျိုးမျိုးနဲ့ ချိတ်ရတာနဲ့ တူတယ်။

## အပိုင်း ၂ — MCP ဆိုတာ တကယ် ဘာလဲ

### ဘာကို ဆိုလိုတာလဲ

MCP (Model Context Protocol) ဆိုတာ — AI application တွေကို ပြင်ပ data source တွေနဲ့ tool တွေဆီ ချိတ်ပေးတဲ့ ဖွင့်လှစ်ထားတဲ့ စံ protocol တစ်ခုပါ။ Protocol ဆိုတာ — ဘယ်လို စကားပြောရမလဲဆိုတဲ့ သဘောတူညီချက် စည်းမျဉ်းလေးပါ။ USB port လိုပဲ — ဘယ်ကြိုးနဲ့မဆို တစ်ပြေးညီ ချိတ်လို့ရအောင် သတ်မှတ်ပေးလိုက်တာပါ။

### ဘာကြောင့် လဲ

စံ protocol တစ်ခုတည်း ရှိလိုက်တာနဲ့ model တိုင်း၊ tool တိုင်း တစ်ပြေးညီ အလုပ်လုပ်နိုင်ပါတယ်။ Model ပြောင်းရင် tool code ပြန်ရေးစရာ မလိုတော့ဘူး။ Tool အသစ် ထည့်ရင်လည်း အရင်လို ထပ်ရေးစရာ မရှိတော့ပါဘူး။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ MCP က JSON-RPC ဆိုတဲ့ message format ကို သုံးတယ်။
၂။ JSON-RPC ဆိုတာ — request နဲ့ response ကို JSON အဖြစ် ရေးတဲ့ စနစ်လေးပါ။
၃။ Client ဆိုတာ — program က server ကို ခေါ်တဲ့အခါ သုံးတဲ့ အလွှာလေး။
၄။ Server ဆိုတာ — tool တွေကို အမှန်တကယ် အလုပ်လုပ်ပေးတဲ့ ဘက်ပါ။
၅။ ဒီနှစ်ခုကြားမှာ စံတူ message တွေနဲ့ ပြောင်းလဲကြတယ်။
၆။ ဒီအလုပ်ကို LAB 1 မှာ ကိုယ်တိုင် မြင်ရမယ်။

### ဥပမာ

ဒီ snippet မှာ client က server ဆီ request ပို့တဲ့ JSON format အစစ်ကို ပြထားပါတယ်။ JSON ထဲမှာ method နာမည်နဲ့ parameter တွေ ဘယ်လို ပါလဲဆိုတာ ဂရုစိုက်ကြည့်ပါ (`../code/lab_1_see_the_protocol.py` မှာ အပြည့်အစုံ မြင်နိုင်ပါတယ်):
```python
# A simplified JSON-RPC request that an MCP client sends to a server
import json

request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
}

print(json.dumps(request, indent=2))
# Expected output:
# {
#   "jsonrpc": "2.0",
#   "id": 1,
#   "method": "tools/list"
# }
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

JSON-RPC message တွေကို မြင်နိုင်ရင် MCP က magic မဟုတ်ဘူးဆိုတာ သိလာတယ်။ ဒါက သာမန် JSON message တွေပါပဲ။ ဒါကြောင့် ဘာဖြစ်နေလဲဆိုတာကို အလွယ်တကူ ရှာတွေ့ပြီး debug ချိန် တိုသွားတယ်။

## အပိုင်း ၃ — Host / Client / Server

### ဘာကို ဆိုလိုတာလဲ

MCP architecture မှာ အဓိက အစိတ်အပိုင်း သုံးခု ရှိတယ်။ Host ဆိုတာ — AI app အကြီးကြီး၊ ဥပမာ chat app လိုမျိုး။ Client ဆိုတာ — Host ထဲကနေ server ကို ခေါ်တဲ့ အလယ်တန်း အလွှာလေး။ Server ဆိုတာ — tool တွေကို အပြင်ကို ဖော်ပြပေးတဲ့ ဘက်။ မိုဘိုင်းဆိုင် ရှိတယ်၊ အလယ်မှာ broker ရှိတယ်၊ နောက်ဆုံးမှာ ကုန်ပစ္စည်း စီမံတဲ့ store ရှိတယ်ဆိုတဲ့ ပုံစံမျိုးပါ။

### ဘာကြောင့် လဲ

ဒီသုံးခု မခွဲထားရင် အားလုံးကို တစ်နေရာတည်း ရေးရတယ်။ ဒါဆို Host အသစ်တစ်ခု လုပ်တိုင်း server code အားလုံး ပြန်ရေးရတယ်။ တာဝန်ခွဲထားရင်တော့ Host တစ်ခုပြောင်းလို့ server တွေ မပါဘူး။ တစ်ခုပျက်လည်း အခြားတစ်ခု မပျက်တော့ပါဘူး။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ User က Host (AI chat app) ကို ဖွင့်တယ်။
၂။ Host ထဲမှာ Client တွေ တည်ရှိတယ်။
၃။ Client တစ်ခုက Server တစ်ခုနဲ့ ချိတ်ဆက်တယ်။
၄။ Client က Host ဘက်ကနေ ယူလိုက်တဲ့ တောင်းဆိုမှုကို JSON-RPC message အဖြစ် ပြောင်းတယ်။
၅။ Server က tool ရလဒ်ကို ပြန်ပို့တယ်။
၆။ Client က ဒီအဖြေကို Host ဆီ ပြန်ပို့ပေးတယ်။

### ဥပမာ

ဒီ snippet မှာ Host တစ်ခုထဲမှာ Client ဘယ်လောက် ပါလို့ရလဲ၊ Client တစ်ခုက Server တစ်ခုနဲ့ ဘယ်လို တွဲတယ်ဆိုတာ ပြထားတယ်။ Client နဲ့ Server က တစ်ကိုယ်တော မဟုတ်ဘဲ အတွဲလိုက် ချိတ်နေပုံကို သတိထားကြည့်ပါ။
```python
# Conceptual map of the three MCP roles
roles = {
    "Host": "the AI application the user interacts with (e.g. a chat app)",
    "Client": "lives inside the Host, maintains a 1:1 connection to one Server",
    "Server": "exposes tools, resources and prompts over the protocol",
}

for name, description in roles.items():
    print(f"{name}: {description}")
# Expected output:
# Host: the AI application the user interacts with (e.g. a chat app)
# Client: lives inside the Host, maintains a 1:1 connection to one Server
# Server: exposes tools, resources and prompts over the protocol
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Client နဲ့ server ပြဿနာ ၃ မျိုးကို ခွဲခြားနိုင်ဖို့ ဒီ သုံးခု အရေးကြီးတယ်။ ခွဲမသိရင် code ရေးရမဲ့နေရာနဲ့ debug လုပ်ရမဲ့နေရာ မှားတတ်ပါတယ်။ မှားရင် error က ဘယ်ဘက်ကဖြစ်တယ်ဆိုတာ ရှာရတာ အချိန်ကုန်ပါတယ်။

## အပိုင်း ၄ — Server က ဖော်ထုတ်သည့် အရာ ၄ မျိုး

### ဘာကို ဆိုလိုတာလဲ

Server — ဆိုတာ client ရဲ့ တောင်းဆိုမှုတွေကို လက်ခံပြီး အဖြေပြန်ပေးတဲ့ ဘက်ပါ။ ဒီ server က protocol ကတဆင့် ဖော်ထုတ်ပေးလို့ရတဲ့ အရာ ၄ မျိုး ရှိတယ် — tools, resources, prompts နဲ့ အခြား server capability တွေပါ။ စားပွဲပေါ်မှာ မုန့် ၄ မျိုး တင်ပေးထားတဲ့ ပွဲစားလိုမျိုးပါပဲ။

### ဘာကြောင့် လဲ

surface တစ်မျိုးပဲရှိရင် လုပ်စရာတွေ ကန့်သတ်ခံရတယ်။ ဥပမာ — လုပ်ဆောင်ချက်လိုချင်တာ၊ data ဖတ်ချင်တာ၊ prompt template သုံးချင်တာ စသဖြင့် လိုအပ်ချက် မတူကြပါ။ ဒါကြောင့် လိုအပ်ချက်အလိုက် သင့်တော်တဲ့ surface ၄ မျိုး ခွဲပေးထားတာပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Client က server ဆီ "မင်းမှာ ဘာတွေရှိလဲ" လို့ မေးပါတယ်။
၂။ Server က မိမိဖော်ထုတ်ထားတဲ့ surface စာရင်းကို စုစည်းပါတယ်။
၃။ အဲဒီ စာရင်းကို protocol ကတဆင့် client ဆီ ပြန်ပေးပါတယ်။
၄။ Client က ရရှိတဲ့ စာရင်းအတိုင်း သင့်တင့်တဲ့ surface ကို ရွေးသုံးပါတယ်။
၅။ LAB 2 (`../code/lab_2_four_surfaces.py`) မှာ ဒီ အဆင့်တွေကို လက်တွေ့ စမ်းကြည့်ရမယ်။

### ဥပမာ

ဒီ snippet မှာ server တစ်ခုက surface ၄ မျိုး ဘယ်လို ဖော်ထုတ်လဲဆိုတာ ပြထားပါတယ်။ tools, resources, prompts ဆိုတဲ့ နာမည်တွေကို အတိအကျ သတိထားကြည့်ပါနော်။
```python
# The four surfaces an MCP server can expose
surfaces = [
    "tools",     # actions the model can call, e.g. query a database
    "resources", # data the model can read, e.g. file contents
    "prompts",   # reusable prompt templates the user can invoke
]

for surface in surfaces:
    print(f"Server exposes: {surface}")
# Expected output:
# Server exposes: tools
# Server exposes: resources
# Server exposes: prompts
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Server ကို ဒီဇိုင်းရတဲ့အခါ ဘယ် feature ကို ဘယ် surface မှာ တင်ရမလဲဆိုတာ ရွေးရတယ်။ ဒါကြောင့် ၄ မျိုးလုံးကို နားလည်ထားဖို့ လိုပါတယ်။ မနားလည်ရင် သင့် tool ကို client က မမြင်ဘူး။ ဒါဆို debug ချိန် ကြာရပြီး အချိန်ဆုံးရှုံးတယ်။

## အပိုင်း ၅ — `FastMCP` က ဘာလုပ်ပေးသလဲ

### ဘာကို ဆိုလိုတာလဲ

`FastMCP` ဆိုတာ Python နဲ့ MCP server ရေးဖို့ သုံးတဲ့ အလွှာတစ်ခုပါ။ ခက်ခဲတဲ့ အောက်ခံ code တွေကို ဖုံးပြီး လွယ်လွယ်နဲ့ ရေးလို့ရတော့မယ်။ ဒါက ကားမောင်းတုန်း စက်ပိုင်းကို မစဉ်းစားဘဲ steering ပဲကိုင်ရသလိုနော်။

### ဘာကြောင့် လဲ

`FastMCP` မရှိရင် JSON-RPC message တွေကို ကိုယ်တိုင် လက်ဖြင့် ရေးရတယ်။ Transport ကြောင်းလည်း ကိုယ်တိုင် စီမံရတယ်။ အမှားရှိရင် protocol လိုင်းတစ်ခုလုံး ပျက်သွားတယ်။ `FastMCP` က ဒီအလုပ်တွေကို လုပ်ပေးတာကြောင့် သင့် logic အပေါ်ပဲ အာရုံစိုက်လို့ရတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Python function တစ်ခု ရေးပါ။
၂။ Function ရှေ့မှာ `@mcp.tool` ဆိုတဲ့ decorator ထည့်ပါ — decorator ဆိုတာ function ရှေ့မှာတပ်ပြီး အလုပ်အကူညီပေးတဲ့ အမှတ်အသားလေးပါ။
၃။ `FastMCP` က ဒီ function ကို MCP tool အဖြစ် အလိုအလျောက် မှတ်ပါတယ်။
၄။ Input/output အတွက် JSON Schema လည်း အလိုအလျောက် ဆောက်ပေးပါတယ်။
၅။ Server အလုပ်လုပ်တာနဲ့ client က ဒီ tool ကို မြင်ပြီး ခေါ်လို့ရပါပြီ။

### ဥပမာ

ဒီ snippet မှာ function ရှေ့မှာ `@mcp.tool` တပ်ပြီး tool တစ်ခုဖန်တီးပြထားတယ်။ Decorator တပ်ထားတာနဲ့ မတပ်ထားတာ — tool list ထဲ ပေါ်မပေါ်ကို သတိထားကြည့်ပါ။
```python
# Minimal pattern of a FastMCP tool (concept, matches the labs' style)
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

if __name__ == "__main__":
    # Start the server (transport handling is done for you)
    mcp.run()
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

ဒီ course တလျှောက်လုံးမှာ server တွေကို `FastMCP` နဲ့ ရေးရမှာပါ။ ဒီ pattern ကို ကျွမ်းကျင်ဖို့ အရေးကြီးပါတယ်။

## အနှစ်ချုပ်

- MCP မရှိခင် integration တိုင်းက custom ဖြစ်ပြီး စျေးကြီးတယ်
- MCP က open protocol တစ်ခုပါ။ JSON-RPC ကို အသုံးပြုတယ်
- Host / Client / Server ဆိုတဲ့ အစိတ်အပိုင်း သုံးခုရဲ့ တာဝန်တွေ ကွဲပြားတယ်
- Server က surface ၄ မျိုး ဖော်ထုတ်ပေးတယ်
- `FastMCP` က protocol အသေးစိတ်ကို ဖုံးကွယ်ပေးတယ်။ Python နဲ့ ရေးရတာ လွယ်ကူသွားတယ်
- LAB 1 နဲ့ LAB 2 က protocol ကို ကိုယ်တိုင် မြင်ရဖို့ အခွင့်အရေးပေးတယ်