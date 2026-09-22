# explanation.md — M4: FastMCP အခြေခံ — Server, Transport နှင့် Inspector

## အပိုင်း ၁ — FastMCP Server ဆိုတာ ဘာလဲ

### ဘာကို ဆိုလိုတာလဲ

FastMCP ဆိုတာ — Python code ကို MCP server အဖြစ် အလိုအလျောက် ပြောင်းပေးတဲ့ framework ပါ။ `FastMCP("name")` နဲ့ server object တစ်ခု ဆောက်ပြီး `@mcp.tool` decorator နဲ့ function တွေကို tool အဖြစ် မှတ်ပုံတင်တယ်။ Decorator ဆိုတာ — function ရဲ့ အပေါ်မှာ တပ်ပြီး အဲဒီ function ကို အလိုအလျောက် ခြုံပေးထားတဲ့ အလွှာလေးပါ။ Server နာမည်က client ဘက်က မြင်ရမယ့် အချက်အလက်တစ်ခု ဖြစ်ပါတယ်။ စားသောက်ဆိုင် တစ်ခုနဲ့ တူတယ် — FastMCP က ဆိုင်အိမ်၊ `@mcp.tool` တွေက မီနူးစာရင်း သဘောပါ။

### ဘာကြောင့် လဲ

MCP protocol က JSON-RPC 2.0 အပေါ် အခြေခံထားပါတယ်။ JSON-RPC 2.0 ဆိုတာ — program တွေက တစ်ခုနဲ့တစ်ခု စာပို့ပေးပြီး စကားပြောနိုင်အောင် လုပ်ပေးတဲ့ စည်းမျဉ်းလေးပါ။ ဒီ protocol အရ host, client, server ဆိုပြီး အခန်းကဏ္ဍ သုံးမျိုး ရှိပါတယ်။ ဒီလို handshake နဲ့ message format အားလုံးကို ကိုယ်တိုင် ရေးရင် အချိန်ကုန်ပြီး မှားလွယ်ပါတယ်။ FastMCP က အဲဒါတွေကို ကိုယ်စားလုပ်ပေးလို့ ကျွန်ုပ်တို့က စီးပွားရေး logic ကိုသာ ရေးရတယ်။ Handshake ဆိုတာ — server နဲ့ client ပထမဆုံးမှ တစ်ခုကိုတစ်ခု အသိအမှတ်ပြုတဲ့ အဆင့်ပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ `FastMCP("name")` နဲ့ server object ဆောက်တဲ့အခါ အတွင်းပိုင်းမှာ tool registry တစ်ခု ထားပါတယ်။ Registry ဆိုတာ — tool တွေရဲ့ စာရင်းမှတ်စာအုပ်လေးပါ။

၂။ `@mcp.tool` ကို function တစ်ခုပေါ်မှာ တပ်တယ်။

၃။ FastMCP က function ရဲ့ signature နဲ့ type hints တွေကို ဖတ်ပြီး JSON Schema အဖြစ် ပြောင်းပါတယ်။ Signature ဆိုတာ — function နာမည်၊ လက်ခံတဲ့ အကြောင်းအရာတွေရဲ့ ပုံစံပါ။

၄။ အဲဒီ schema က `initialize` handshake အပြီးမှာ client ဆီ ရောက်သွားပါတယ်။

၅။ ဒါနဲ့ client က ဘယ် tool တွေ ရှိလဲ၊ ဘယ် data ပို့ရမလဲ ဆိုတာ သိသွားပါတယ်။

### ဥပမာ

အောက်မှာ code snippet ပြထားပါတယ် — server တစ်ခု ဆောက်ပြီး tool တစ်ခု မှတ်ပုံတင်တဲ့ ပုံစံပါ။ `@mcp.tool` အောက်က function ရဲ့ docstring နဲ့ type hints တွေကို ဂရုစိုက်ကြည့်ပါနော် — အဲဒါတွေကပဲ client ဆီ ရောက်မယ့် schema ဖြစ်လာတယ်။

```python
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

```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Server နာမည်နဲ့ tool စာရင်းက client တွေက server ကို ရှာဖို့ အခြေခံ အချက်အလက်တွေ ပါတယ်။ `main()` function ထဲမှာ transport ရွေးပြီး `mcp.run()` နဲ့ server ကို စတင်ရတယ်။ နာမည်မှားရင် client ဘက်က ဘယ် server ဘယ် tool လဲဆိုတာ မှန်ကန်စွာ ခွဲမရတော့ပါဘူး။ ဒါကြောင့် debug လုပ်ဖို့ အချိန် ပိုကုန်တယ်၊ မှားတဲ့ tool ကို ခေါ်မိလည်း ဖြစ်နိုင်ပါတယ်။

## အပိုင်း ၂ — stdio Transport

### ဘာကို ဆိုလိုတာလဲ

stdio transport ဆိုတာ — client က server ကို process သေးသေးလေးတစ်ခုအဖြစ် ဖွင့်ပြီး `stdin` / `stdout` လိုင်းတွေနဲ့ စကားပြောတဲ့ နည်းလေး ပါတယ်။ process ဆိုတာ computer ထဲမှာ အလုပ်လုပ်နေတဲ့ program တစ်ခုချင်းစီကို ဆိုလိုတာနော်။ Client က `Client(Path)` ကို server file path နဲ့ ဖန်တီးရင် အလိုအလျောက် server process စတင်သွားတယ်။ အခန်းနှစ်ခုကြားက တိုက်ရိုက် စကားပြောသလိုမျိုး တိုက်ရိုက် ဆက်တာပါ။

### ဘာကြောင့် လဲ

stdio မသုံးရင် server ကို ချိတ်ဖို့ port နဲ့ network လိုတယ်။ ဒါက local tool တွေအတွက် ရှုပ်ထွေးတယ်၊ လုံခြုံမှုလည်း စဉ်းစားရတယ်။ stdio က port နဲ့ network မလိုဘဲ OS process pipe လေးတွေနဲ့ပဲ ဆက်ပါတယ်။ ဒါကြောင့် local tool တွေအတွက် အလွယ်ကျဆုံး ဖြစ်ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Client က server command ကို ဖွင့်တယ်။
၂။ Client က server ရဲ့ `stdin` ထဲကို request ရေးတယ်။
၃။ Server က `stdout` ထဲကို response ပြန်ရေးတယ်။
၄။ `stderr` ထဲမှာတော့ log တွေပဲ ရေးရတယ်။
၅။ ဆက်သွယ်မှု ပြီးတာနဲ့ child process လည်း ပိတ်သွားတယ်။

### ဥပမာ

အောက်မှာ `Client(Path)` နဲ့ stdio server ကို ချိတ်ပြတဲ့ snippet ပါတယ်။ client က server file path ပေးလိုက်တာနဲ့ process အလိုအလျောက် စတင်သွားတာကို သတိထားကြည့်ပါနော်။

```python
from pathlib import Path
from fastmcp import Client

async def main():
    # Point the client at the server file; stdio is the default
    async with Client(Path("hello_server.py")) as client:
        tools = await client.list_tools()
        print([t.name for t in tools])
# Expected output: ['add']

```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

stdio မှာ `stdout` က protocol လိုင်းပါ။ ဒါကြောင့် server code ထဲမှာ `print()` တစ်ကြောင်း ရေးမိရင် protocol message ပျက်သွားပြီး client ကို ထောင်ချောက်ထဲ ကျစေတယ်။ ဘာဖြစ်လဲဆိုတာ မသိဘဲနဲ့ debug အချိန် ကြာရှယ်၊ server ကလည်း အလုပ်မလုပ်တော့ပါဘူး။ ဒါကြောင့် stdout ထဲ ဘာမှ မရေးရအောင် သတိထားရတယ်။ logging လုပ်ချင်ရင် `stderr` ကို ရေးပါ။

## အပိုင်း ၃ — HTTP Transport

### ဘာကို ဆိုလိုတာလဲ

HTTP transport ဆိုတာ — server ကို network ပေါ် တင်ပေးတဲ့ နည်းလမ်းပါ။ Server ကတစ်နေရာမှာ စောင့်နေပြီး၊ client တွေက နောက်မှ ခေါ်တာပေါ့။ ရုံးတစ်ခုမှာ ဖုန်းတစ်လှဲ ခံနေသလိုမျိုး — server က ဖုန်းခံစောင့်နေ၊ client က ဖုန်းဆက်လို့ရတယ်။ Streamable HTTP ကို သုံးပြီး SSE လည်း ပါဝင်ပါတယ်။

### ဘာကြောင့် လဲ

stdio နဲးဆိုရင် client တစ်ခု ခေါ်တိုင်း server process အသစ် တစ်ခါစ ဖွင့်ရတယ်။ Client များစွာ ပါရင် ဖွင့်/ပိတ် လုပ်ရတာ အလွန် ပင်ပန်းပါတယ်။ HTTP နဲ့ဆိုရင်တော့ server တစ်ခုတည်းကို client များစွာက တစ်ပြိုင်တည်း ခေါ်လို့ရတယ်။ Server က service တစ်ခုလို အမြဲ ရှိနေတာပေါ့။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Server က `host` နဲ့ `port` မှာ စောင့်နေတယ်။
၂။ `host="127.0.0.1"` ဆိုရင် ကွန်ပျူတာတစ်လုံး အတွင်းမှာပဲ ရောက်နိုင်တယ်။
၃။ `0.0.0.0` ဆိုရင် network အပြင်ဘက်ကနေ လာလို့ရတယ်။
၄။ Client က HTTP နဲ့ ချိတ်ဆက်တယ်။
၅။ ချိတ်ပြီးရင် JSON-RPC message တွေ ပို့တယ်။

### ဥပမာ

ဒီ snippet မှာ HTTP transport နဲ့ server ဖွင့်တာ ပြထားပါတယ်။ `host` setting က ဘယ်အထိ ရောက်နိုင်လဲဆိုတာ စောင့်ကြည့်ပါနော်။

```python
# Server side: run over HTTP on localhost
def main():
    # transport="http", host and port decide who can reach us
    mcp.run(transport="http", host="127.0.0.1", port=8000)

# Expected output: server listens at http://127.0.0.1:8000

```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

HTTP သုံးတဲ့အခါ `stdout` က protocol လိုင်း မဟုတ်တော့လို့ `print()` ရေးလို့ရပါတယ်။ ဒါပေမယ့် network ပေါ် ဖွင့်လိုက်ရင်တော့ auth (ခွင့်ပြုချက်စစ်တဲ့ စနစ်) မရှိဘဲ ဘာမှ မပြရဘူး။ `0.0.0.0` ကို ရွေးရင် အင်တာနက်က လူတိုင်း ဝင်လို့ရသွားတာပါ။ ဒါက data leak ဖြစ်တဲ့ အန္တရာယ် အစစ်ပါ။

## အပိုင်း ၄ — Tool ရှာဖွေခြင်း နှင့် Result

### ဘာကို ဆိုလိုတာလဲ

Client ဆိုတာ — program က server ကို ခေါ်တဲ့အခါ သုံးတဲ့ အလွှာလေး။ Client က `list_tools()` နဲ့ server မှာရှိတဲ့ tool တွေကို ရှာပါတယ်။ ပြီးရင် `call_tool()` နဲ့ ခေါ်ပါတယ်။ ခေါ်ပြီးတဲ့အခါ result object တစ်ခု ပြန်ရပါတယ်။ အဲ့ထဲမှာ `structured_content` နဲ့ `is_error` ဆိုတာတွေ ပါလာပါတယ်။

### ဘာကြောင့် လဲ

Server က tool တစ်ခု ထုတ်ပြောက်တဲ့အခါ သူ့ function ရဲ့ type hints က JSON Schema ဖြစ်သွားပါတယ်။ JSON Schema ဆိုတာ — "ဒီ tool ကို ဘယ် argument တွေနဲ့ ဘယ်ပုံခေါ်ရမလဲ" ဆိုတာ ဖော်ပြတဲ့ စာရွက်လေးပါ။ နာမည်ချင်း မတူတာက အမြဲမှားတဲ့ နေရာပါ။ Client ဘက်က `.parameters` လို့ မြင်ရပြီး၊ server ဘက်က `.input_schema` လို့ ခေါ်ပါတယ်။ တစ်ခုတည်းပေမယ့် နာမည် နှစ်မျိုးရှိလို့ ရှုပ်ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Client က `list_tools()` နဲ့ ရှိတဲ့ tool စာရင်း တောင်းပါတယ်။
၂။ ရလာတဲ့ tool object ထဲက `.parameters` ကို ကြည့်ပြီး argument တွေ စီမံပါတယ်။
၃။ `call_tool()` ကို tool နာမည်နဲ့ argument dict ပေးပြီး ခေါ်ပါတယ်။
၄။ Tool အထဲမှာ error ဖြစ်ရင် `raise` မလုပ်ဘဲ `is_error=True` နဲ့ ပြန်လာပါတယ်။
၅။ Client က result ရင်း `is_error` ကို စစ်ပြီး error လား ဆုံးဖြတ်ပါတယ်။

### ဥပမာ

ဒီ snippet မှာ `list_tools()` နဲ့ `call_tool()` ကို တွဲသုံးထားပုံ ပြထားပါတယ်။ `is_error` ကို မစစ်ဘဲ သွားရင် error ကို အောင်မြင်တယ်လို့ မှားယူင်နိုင်လို့ အဲ့အပိုင်းကို သတိထားကြည့်ပါ။

```python
async def main():
    async with Client(Path("hello_server.py")) as client:
        result = await client.call_tool("add", {"a": 2, "b": 3})
        print(result.is_error)
        print(result.structured_content)
# Expected output:
# False
# {'result': 5}

```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

`is_error=False` ဖြစ်နေရင်တောင် အလုပ်မှားနိုင်တယ် နော်။ ဥပမာ — argument တန်ဖိုး မှားနေရင် result ထဲမှာ အမှား ပါလာတယ်။ ဒီ pattern က နောင် module တွေမှာလည်း ထပ်တွေ့ရမယ်။ ဒါကြောင့် result ကိုကြည့်ပြီး ဆုံးဖြတ်တဲ့ အလေ့အကျင့်ကို အခုကတည်းက လေ့ကျင့်ထားသင့်ပါတယ်။

## အနှစ်ချုပ်

- **FastMCP** က MCP protocol ရဲ့ JSON-RPC အသေးစိတ်အပိုင်းတွေကို ကိုယ်စားလုပ်ပေးတယ်။ ဒါကြောင့် `FastMCP("name")` နဲ့ `@mcp.tool` ပဲ ရေးရပါတယ်။
- **stdio transport** မှာ client က server ကို child process အဖြစ် ဖွင့်ပေးတယ်။ `stdout` က protocol လိုင်းမို့ `print()` လုံးဝ မရေးရပါနဲ့။
- **HTTP transport** မှာ server က စောင့်ပြီး client က ချိတ်သွားတယ်။ `0.0.0.0` ရွေးရင် အပြင်ကလူတွေ ဝင်ရောက်လို့ရတာမို့ အန္တရာယ် ရှိတယ်။
- **Transport ရွေးရာ**မှာ မေးရမဲ့ မေးခွန်းတွေက — ဘယ်သူ စလဲ၊ ဘယ်သူ ရောက်နိုင်လဲ၊ auth ဘယ်မှာ ရှိလဲ၊ stdout ကို ဘယ်လို သုံးလဲ။
- **Inspector** က server မှ tool တွေကို ကြည့်ဖို့ အသုံးဝင်တယ်။ ဒါပေမဲ့ tool ထဲက logic မှန်မမှန်ကိုတော့ မပြနိုင်ပါဘူး။
- **Result object** ထဲမှာ `structured_content` နဲ့ `is_error` တွေ့ရတယ်။ ဒါကြောင့် ခေါ်တိုင်း `is_error` ကို စစ်ရမယ်။
- **Schema နာမည်** က ဘက်အလိုက် မတူပါဘူး။ server ဘက်မှာ `.input_schema`၊ client ဘက်မှာ `.parameters` လို့ ခေါ်တယ်။