# M0 — Orientation: MCP ဆိုတာ ဘာလဲ

## အပိုင်း ၁ — ပြဿနာကို အရင် မြင်ပါ

### ဘာကို ဆိုလိုတာလဲ

AI model တစ်ခုကို ပြင်ပ tool တွေ (database, API, file system) နဲ့ ချိတ်ဆက်ပေးချင်တဲ့အခါ MCP မရှိခင်က တစ်ခုချင်းစီအတွက် သီးသန့် integration ရေးရတာကို ဆိုလိုတယ်။

### ဘာကြောင့် လဲ

Model တစ်မျိုးချင်းစီ၊ tool တစ်ခုချင်းစီအတွက် ချိတ်ဆက်နည်း မတူပါ။ OpenAI format တစ်မျိုး၊ အခြား provider format တစ်မျိုးဆိုသလို ရှိနေတော့ တစ်ခုပြောင်းရင် တစ်ခု ပြန်ရေးရတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

Integration တိုင်းက custom code ဖြစ်နေပြီး အရေအတွက် များလာတာနဲ့ အမျှ စျေးကြီးလာပြီး ပြန်ထိန်းရခက်လာတယ်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

ပြဿနာကို မြင်ရင် MCP က ဘာကြောင့် ဖန်တီးထားလဲဆိုတာ နားလည်လာမယ်။ USB port မရှိခင် စက်တစ်ခုချင်းစီကို ကြိုးအမျိုးမျိုးနဲ့ ချိတ်ရတဲ့ ပြဿနာနဲ့ တူတယ်။

## အပိုင်း ၂ — MCP ဆိုတာ တကယ် ဘာလဲ

### ဘာကို ဆိုလိုတာလဲ

MCP (Model Context Protocol) ဆိုတာ AI application တွေကို ပြင်ပ data source တွေနဲ့ tool တွေဆီ ချိတ်ဆက်ပေးတဲ့ ဖွင့်လှစ်ထားတဲ့ protocol တစ်ခုဖြစ်တယ်။

### ဘာကြောင့် လဲ

တစ်ခါတည်း protocol စံနှုန်းတစ်ခု သတ်မှတ်ပေးလိုက်တာကြောင့် model တိုင်း၊ tool တိုင်း တစ်ပြေးညီ အလုပ်လုပ်နိုင်တယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

MCP က JSON-RPC ဆိုတဲ့ message format ကို အသုံးပြုပြီး client နဲ့ server ကြားမှာ စံနှုန်းတူ message တွေ ပြောင်းလဲကြတယ်။ ဒါကို LAB 1 မှာ ကိုယ်တိုင် မြင်ရမယ်။

### ဥပမာ

MCP မှာ client က server ဆီ request ပို့တဲ့ JSON format က ဒီလိုမျိုးဖြစ်တယ် (`../code/lab_1_see_the_protocol.py` မှာ အပြည့်အစုံ မြင်နိုင်သည်):

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

JSON-RPC message တွေကို မြင်နိုင်ရင် MCP က magic မဟုတ်ဘဲ သာမန် JSON message တွေပဲဆိုတာ နားလည်လာပြီး debug လုပ်ရတာလည်း လွယ်လာမယ်။

## အပိုင်း ၃ — Host / Client / Server

### ဘာကို ဆိုလိုတာလဲ

MCP architecture မှာ အဓိက အစိတ်အပိုင်း သုံးခု ရှိတယ် — Host (AI application), Client (ချိတ်ဆက်ပေးသည့် အလယ်တန်း), Server (tool တွေကို ဖော်ထုတ်ပေးသည့် ဘက်)။

### ဘာကြောင့် လဲ

တာဝန်တွေကို ခွဲခြားထားတာကြောင့် တစ်ခု ပြောင်းလဲရင် အခြားတစ်ခုကို မသက်ရောက်တော့ဘူး။ Host application တစ်ခုပြောင်းလို့ server တွေ ပြန်ရေးစရာ မလိုဘူး။

### ဘယ်လို အလုပ်လုပ်လဲ

Host (ဥပမာ AI chat app) ထဲမှာ Client တွေ ပါဝင်တယ်။ Client တစ်ခုက Server တစ်ခုနဲ့ ချိတ်ဆက်ပြီး Host နဲ့ Server ကြားမှာ protocol အတိုင်း message ပို့ပေးတယ်။

### ဥပမာ

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

ဘယ်တစ်ခုမှာ code ရေးရမလဲ၊ ဘယ်တစ်ခုမှာ debug လုပ်ရမလဲဆိုတာ သိနိုင်ဖို့ ဒီ သုံးခု ခွဲနိုင်ဖို့ အရေးကြီးတယ်။

## အပိုင်း ၄ — Server က ဖော်ထုတ်သည့် အရာ ၄ မျိုး

### ဘာကို ဆိုလိုတာလဲ

MCP Server တစ်ခုက protocol ကတဆင့် ဖော်ထုတ်ပေးနိုင်တဲ့ surface ၄ မျိုး ရှိတယ် — tools, resources, prompts နဲ့ အခြား server capability များ။

### ဘာကြောင့် လဲ

တစ်ခုတည်း surface ပဲရှိရင် အသုံးပြုမှု ကန့်သတ်ခံရတယ်။ အမျိုးမျိုးသော လိုအပ်ချက် (လုပ်ဆောင်ချက်၊ data ဖတ်ချင်ခြင်း၊ prompt template သုံးချင်ခြင်း) အတွက် သင့်တင့်တဲ့ surface က မတူတဲ့အတွက် ၄ မျိုး ခွဲထားတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

Client က server ဆီ "ဘာရှိလဲ" လို့ မေးရင် server က ကိုယ်ဖော်ထုတ်တဲ့ surface တွေရဲ့ စာရင်းကို ပြန်ပေးတယ်။ ဒါကို LAB 2 (`../code/lab_2_four_surfaces.py`) မှာ လက်တွေ့ စမ်းကြည့်ရမယ်။

### ဥပမာ

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

မိမိရဲ့ server ကို ဒီဇိုင်းရဖို့ ဘယ် feature က ဘယ် surface မှာ ဆင်သင့်လဲဆိုတာ ရွေးနိုင်ဖို့ ၄ မျိုးလုံးကို နားလည်ဖို့ လိုတယ်။

## အပိုင်း ၅ — `FastMCP` က ဘာလုပ်ပေးသလဲ

### ဘာကို ဆိုလိုတာလဲ

`FastMCP` ဆိုတာ Python နဲ့ MCP server တွေကို အလွယ်တကူ ရေးနိုင်စေဖို့ ဆောက်ထားတဲ့ high-level layer တစ်ခုဖြစ်တယ်။

### ဘာကြောင့် လဲ

အခြေခံ protocol code (JSON-RPC message ဖန်တီးခြင်း၊ transport စီမံခြင်း) တွေကို `FastMCP` က ဖုံးကွယ်ပေးထားတာကြောင့် လုပ်ဆောင်ချက် logic အပေါ်မှာတည်း အာရုံစိုက်နိုင်တယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

Python function တစ်ခုကို `@mcp.tool` ဆိုတဲ့ decorator နဲ့ အမှတ်အသားပြုလိုက်ရင် `FastMCP` က ဒါကို MCP tool အဖြစ် အလိုအလျောက် မှတ်ပုံတင်ပြီး JSON Schema နဲ့ ဖော်ပြပေးတယ်။

### ဥပမာ

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

ဒီ course တလျှောက်လုံးမှာ server တွေကို `FastMCP` နဲ့ ရေးမှာဖြစ်တဲ့အတွက် ဒီ pattern ကို ကျွမ်းကျင်ဖို့ အရေးကြီးတယ်။

## အနှစ်ချုပ်

- MCP မရှိခင် integration တိုင်းက custom ဖြစ်ပြီး စျေးကြီးတယ်
- MCP က open protocol တစ်ခုဖြစ်ပြီး JSON-RPC ကို အသုံးပြုတယ်
- Host / Client / Server ဆိုတဲ့ အစိတ်အပိုင်း သုံးခုရဲ့ တာဝန်တွေ ကွဲပြားတယ်
- Server က surface ၄ မျိုး ဖော်ထုတ်ပေးတယ်
- `FastMCP` က protocol အသေးစိတ်ကို ဖုံးကွယ်ပြီး Python နဲ့ ရေးရတာကို လွယ်ကူစေတယ်
- LAB 1 နဲ့ LAB 2 က protocol ကို ကိုယ်တိုင် မြင်ရဖို့ အခွင့်အရေးပေးတယ်
