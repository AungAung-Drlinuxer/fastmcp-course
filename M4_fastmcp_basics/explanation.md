# explanation.md — M4: FastMCP အခြေခံ — Server, Transport နှင့် Inspector

## အပိုင်း ၁ — FastMCP Server ဆိုတာ ဘာလဲ

### ဘာကို ဆိုလိုတာလဲ

FastMCP သည် Python code ကို MCP server အဖြစ် ပြောင်းပေးသည့် framework ဖြစ်သည်။ `FastMCP("name")` ဖြင့် server object တစ်ခု ဖန်တီးပြီး `@mcp.tool` decorator ဖြင့် ကျွနု်ပ်တို့၏ function များကို client များ ခေါ်ဆိုနိုင်သည့် tool များအဖြစ် မှတ်ပုံတင်ပေးသည်။ Server နာမည်သည် client ဘက်မှ တွေ့ရမည့် အချက်အလက်တစ်ခု ဖြစ်သည်။

### ဘာကြောင့် လဲ

MCP protocol သည် JSON-RPC 2.0 အပေါ် အခြေခံသည်။ protocol အရ ဆိုလျှင် host, client, server ဟူ၍ အခန်းကဏ္ဍ သုံးမျိုး ရှိပြီး၊ server က tools, prompts, resources ဟူ၍ သုံးမျိုး ထုတ်ပြနိုင်သည်။ ဤ handshake နှင့် message format အားလုံးကို FastMCP က ကိုယ်စားလုပ်ပေး၍၊ ကျွနု်ပ်တို့သည် စီးပွားရေး logic ကိုသာ ရေးရမည်။

### ဘယ်လို အလုပ်လုပ်လဲ

Server object ကို ဖန်တီးသည့်အခါ FastMCP က အတွင်းပိုင်း registry တစ်ခု ထားသည်။ `@mcp.tool` ကို function တစ်ခုပေါ်တွင် တပ်သည့်အခါ FastMCP က function ၏ signature နှင့် type hints များကို ဖတ်ပြီး JSON Schema အဖြစ် ပြောင်းသည်။ ထို schema သည် `initialize` handshake အပြီးတွင် client ထံ ရောက်သွားသည်။

### ဥပမာ

``python
from fastmcp import FastMCP

# Create a server with a name reported to clients
mcp = FastMCP("course-hello")

# Register a tool from a plain function
@mcp.tool
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

# Inspect what the server publishes
print(mcp.name)
# Expected output: course-hello
``

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Server နာမည်နှင့် tool စာရင်းသည် client များက server ကို မှန်ကန်စွာ ရှာဖွေနိုင်ရန် အခြေခံ ဖြစ်သည်။ `main()` function အတွင်းတွင် transport ကို ရွေးချယ်ပြီး `mcp.run()` ဖြင့် စတင်သည်။ နာမည်မှားလျှင် client ဘက်တွင် server ကို ခွဲခြားရ ခက်သည်။

## အပိုင်း ၂ — stdio Transport

### ဘာကို ဆိုလိုတာလဲ

stdio transport သည် client က server ကို child process တစ်ခုအဖြစ် ဖွင့်ပြီး `stdin` / `stdout` လိုင်းများဖြင့် JSON-RPC message များ ဖလှယ်သည့် နည်းလမ်း ဖြစ်သည်။ Client က `Client(Path)` ကို server ဖိုင် path ဖြင့် ဖန်တီးလျှင် အလိုအလျောက် ထို process ကို စတင်ပေးသည်။

### ဘာကြောင့် လဲ

Editor များသည် server ကို process တစ်ခုအဖြစ် တိုက်ရိုက် ဖွင့်လိုသည်။ stdio တွင် ဆက်သွယ်ရန် port သို့မဟုတ် network မလိုဘဲ OS ၏ process pipe များသာ အသုံးပြုသည်။ ထို့ကြောင့် local tool များအတွက် အလွယ်ကျဆုံး ဖြစ်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

Client က server command ကို ဖွင့်သည်။ Server ၏ `stdin` တွင် client က request ရေးသည်။ Server က `stdout` တွင် response ပြန်ရေးသည်။ `stderr` တွင်မူ log များသာ ရေးရသည်။ ဆက်သွယ်မှု အဆုံးတွင် child process လည်း ပိတ်သွားသည်။

### ဥပမာ

``python
from pathlib import Path
from fastmcp import Client

async def main():
    # Point the client at the server file; stdio is the default
    async with Client(Path("hello_server.py")) as client:
        tools = await client.list_tools()
        print([t.name for t in tools])
# Expected output: ['add']
``

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

stdio တွင် `stdout` သည် protocol လိုင်း ဖြစ်သည်။ ထို့ကြောင့် server code ထဲတွင် `print()` တစ်ကြောင်း ရေးလိုက်လျှင် protocol message ကို ဖျက်၍ client ကို ထောင်ချောက်တွင် ကျစေသည်။ stdout ထဲ ဘာမှ မရေးရန် တင်းကျပ်စွာ သတိထားရမည်။

## အပိုင်း ၃ — HTTP Transport

### ဘာကို ဆိုလိုတာလဲ

HTTP transport သည် server ကို network ပေါ်တွင် ရောက်နိုင်စေသည့် နည်းလမ်း ဖြစ်သည်။ Server က တစ်နေရာတွင် စောင့်ပြီး၊ client က နောက်မှ dial လုပ်သည်။ Streamable HTTP ကို အသုံးပြုပြီး SSE ကိုလည်း အထောက်အကူ ပြုသည်။

### ဘာကြောင့် လဲ

တစ်ခါတစ်ရံ server ကို process တစ်ခုအဖြစ် မဟုတ်ဘဲ service တစ်ခုအဖြစ် တည်ရှိစေလိုသည်။ HTTP ဖြင့် ဆိုလျှင် server တစ်ခုကို client များစွာက ခေါ်ဆိုနိုင်သည်။ stdio ကဲ့သို့ ဖွင့်/ပိတ် အသီးသီး မလုပ်ရပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

Server က `host` နှင့် `port` တွင် စောင့်သည်။ `host="127.0.0.1"` ဖြင့် ဆိုလျှင် machine တစ်ခုတည်းအတွင်းသာ ရောက်နိုင်ပြီး၊ `0.0.0.0` ဖြင့် ဆိုလျှင် network အပြင်ဘက်မှ ရောက်နိုင်သည်။ Client က HTTP ဖြင့် ချိတ်ဆက်၍ JSON-RPC message များ ပို့သည်။

### ဥပမာ

``python
# Server side: run over HTTP on localhost
def main():
    # transport="http", host and port decide who can reach us
    mcp.run(transport="http", host="127.0.0.1", port=8000)

# Expected output: server listens at http://127.0.0.1:8000
``

### လက်တွေ့မှာ ဘာကြောင်း အရေးကြီးလဲ

HTTP တွင် `stdout` သည် protocol လိုင်း မဟုတ်တော့သောကြောင့် `print()` ရေးလို့ရသည်။ သို့သော် network ပေါ်တွင် ဖွင့်လိုက်လျှင် ခွင့်ပြုချက် (auth) မရှိဘဲ လုံးဝ မထုတ်ပြရန် သတိထားရမည်။ `0.0.0.0` ကို ရွေးချယ်ခြင်းသည် တကယ့် အန္တရာယ် ဖြစ်သည်။

## အပိုင်း ၄ — Tool ရှာဖွေခြင်း နှင့် Result

### ဘာကို ဆိုလိုတာလဲ

Client က `list_tools()` ဖြင့် server တွင် ရှိသည့် tool များကို ရှာပြီး၊ `call_tool()` ဖြင့် ခေါ်ဆိုသည်။ ခေါ်ဆိုမှု အဆုံးတွင် result object တစ်ခု ပြန်ရ၍ ၎င်းထဲတွင် `structured_content` နှင့် `is_error` တို့ ပါဝင်သည်။

### ဘာကြောင့် လဲ

Server က tool တစ်ခုကို ထုတ်ပြသည့်အခါ သူ့ function ၏ type hints မှ JSON Schema ဖြစ်လာသည်။ Client ဘက်တွင် tool object ၏ `.parameters` ဟု မြင်ရပြီး၊ server ဘက်တွင် `.input_schema` ဟု ခေါ်သည်။ နာမည် ကွဲခြားかလောက်စွာ ရှိသည်မှာ အမှားအများဆုံး နေရာ ဖြစ်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

`call_tool()` က tool နာမည်နှင့် argument dict ကို လက်ခံသည်။ Tool အတွင်းတွင် error ဖြစ်လျှင် `raise` လုပ်သည့်အစား result ထဲတွင် `is_error=True` ဖြင့် ပြန်လာသည်။ ထို့ကြောင့် client က ခေါ်ဆိုပြီးတိုင်း `is_error` ကို စစ်ရမည်။

### ဥပမာ

``python
async def main():
    async with Client(Path("hello_server.py")) as client:
        result = await client.call_tool("add", {"a": 2, "b": 3})
        print(result.is_error)
        print(result.structured_content)
# Expected output:
# False
# {'result': 5}
``

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

`is_error=False` ဖြစ်လျှင်ပင် အလုပ်က ကျရှုံးနိုင်သည် — ဥပမာ argument တန်ဖိုး မှားနေလျှင် result ထဲတွင် မှားယွင်းမှု ပါလာသည်။ ဤ pattern ကို နောင် module များတွင်လည်း တူညီစွာ တွေ့ရမည်ဖြစ်၍၊ result ကို အခြေခံ၍ ဆုံးဖြတ်သည့် အလေ့အက ခုကတည်း စတင်ထားသင့်သည်။

## အနှစ်ချုပ်

- **FastMCP** က MCP protocol ၏ JSON-RPC အသေးစိတ်ကို ကိုယ်စားလုပ်ပေး၍ `FastMCP("name")` နှင့် `@mcp.tool` သာ ရေးရမည်။
- **stdio transport** တွင် client က server ကို child process အဖြစ် ဖွင့်ပြီး `stdout` သည် protocol လိုင်းဖြစ်၍ `print()` လုံးဝ မရေးရ။
- **HTTP transport** တွင် server က စောင့်ပြီး client က dial လုပ်သည်။ `0.0.0.0` ကို ရွေးလျှင် အပြင်မှ ရောက်နိုင်သဖြင့် အန္တရာယ် ရှိသည်။
- **Transport ရွေးချယ်ရာ**တွင် — ဘယ်သူ စသလဲ၊ ဘယ်သူ ရောက်နိုင်သလဲ၊ auth ဘယ်မှာလဲ၊ stdout ဘယ်လို အသုံးပြုလဲ — ဆိုသည့် မေးခွန်းများကို မေးရမည်။
- **Inspector** သည် server ထုတ်ပြသည့် tool များကို မြင်ရန် အသုံးဝင်သော်လည်း tool အတွင်းရှိ စီးပွားရေး logic ၏ မှန်ကန်မှုကို မပြနိုင်ပါ။
- **Result object** တွင် `structured_content` နှင့် `is_error` ကို တွေ့ရ၍ ခေါ်ဆိုပြီးတိုင်း `is_error` ကို စစ်ရမည်။
- **Schema နာမည်** သည် server ဘက်တွင် `.input_schema`၊ client ဘက်တွင် `.parameters` ဟု ကွဲခြားသည်။
