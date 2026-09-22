# M4 — FastMCP Basics: Server, Transports & Inspector

> **ကြာမြင့်ချိန်:** 2 နာရီ · **Phase:** Phase 2 — MCP Core Surfaces

## ဤသင်ခန်းစာတွင် ဘာရမည်လဲ

- MCP protocol ဆိုတာ တကယ့်အားဖြင့် ဘာလဲ — JSON-RPC 2.0၊ host / client / server သုံးမျိုး၏ ကွာခြားချက်၊ `initialize` handshake အကြောင်း
- `FastMCP("name")` ဖြင့် server တစ်ခု စတင်ဖန်တီးခြင်းနှင့် `@mcp.tool` decorator ဖြင့် tool တစ်ခု register လုပ်ခြင်း
- transport နှစ်မျိုး — stdio (client က child process ကို ဖွင့်သည်) နှင့် HTTP (network ပေါ်မှ ချိတ်နိုင်သည်) — ဘယ်အခါ ဘယ်ဟာကို ရွေးရမလဲ
- stdio တွင် `print()` တစ်ကြောင်းက protocol ကို ဘာကြောင့် ဖျက်သလဲ၊ HTTP တွင် ဘာကြောင့် ရေးလို့ရသလဲ
- Inspector ဖြင့် server တစ်ခု ထုတ်ပြသည့်အရာများကို မျက်စိနှင့် မြင်ခြင်း၊ `fastmcp` CLI ၏ subcommand များကို tier အလိုက် သုံးတတ်ခြင်း
- Client ဘက်မှ `Client(path)`၊ `list_tools`၊ `call_tool` ဖြင့် server ကို ရှာဖွေခြင်း၊ result ၏ `structured_content` နှင့် `is_error` ကို ဖတ်တတ်ခြင်း
- JSON Schema သည် server မှ client ဆီ ဘယ်လို ရောက်သလဲ — `.parameters` နှင့် `.input_schema` ကွာခြားချက်

## သင်ခန်းစာများ

1. MCP protocol အခြေခံ — JSON-RPC 2.0၊ ဇာတ်ကောင်သုံးမျိုး၊ `initialize` handshake
2. `FastMCP("name")` ဖြင့် server ဖန်တီးခြင်း — အမည်သည် ဘယ်နေရာတွင် ပေါ်လဲ
3. `@mcp.tool` decorator — အပြင်ဘက်မှ ကြည့်ခြင်း၊ register ဖြစ်/မဖြစ် စစ်ခြင်း
4. stdio transport — child process ဘဝ၊ သုံးလိုင်း (`stdin` / `stdout` / `stderr`)၊ `print()` ထောင်ချောက်
5. HTTP transport — `host` ရွေးချယ်မှု (`0.0.0.0` vs `127.0.0.1`)၊ HTTP ၏ တကယ့်အန္တရာယ်
6. Transport ရွေးချယ်ရန် မေးခွန်း လေးခုနှင့် hybrid ပုံစံ
7. Inspector ဖြင့် စစ်ဆေးခြင်း — ပြနိုင်သည့်အရာ၊ **မပြနိုင်**သည့်အရာ
8. `fastmcp` CLI — TIER 1 (`run`, `inspect`, `dev`)၊ TIER 2 (`call`, `list`, `discover`)၊ TIER 3 (registry/account)
9. Client discovery — `Tool` object ဖတ်ခြင်း၊ မှားတတ်သည့် ခေါ်ဆိုမှု နှစ်မျိုး
10. Result ၏ အချက်အလက် — `is_error=False` ဖြစ်လျက်ပင် ကျရှုံးနိုင်ခြင်း
11. Schema အဆုံးစွန် — `Literal` က `enum` ဖြစ်လာပုံ၊ `required` ဖတ်ပုံ
12. LAB — Calculator + Currency converter ကို transport နှစ်မျိုးဖြင့် တစ်ပြိုင်တည်း ခေါ်ခြင်း

## လိုအပ်ချက်များ (Prerequisites)

- M3_asyncio_decorators ပြီးဆုံးထားရမည် — decorator အခြေခံနှင့် `async` / `await` ကို နားလည်ထားရမည်
- `mcp` / `fastmcp` package ကို install လုပ်ထားရမည် (ImportError မှ ကာကွယ်ရန်)
- `../code/` ဖိုလ်ဒါရှိ lab ဖိုင်များ (`hello_server.py`, `transports.py`, `lab_5_currency_server.py` အစရှိသည်) ကို အသင့်ရှိထားရမည်
- Terminal တစ်ခုတွင် Python ဖိုင် run တတ်ရမည်

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- သင့်ကိုယ်ပိုင် MCP server ကို ပထမဆုံး တည်ဆောက်လိုသည့်အခါ — server၊ tool၊ transport သုံးခုလုံး တစ်နေရာတည်းမှ စတင်နိုင်သည်
- Editor (host) တစ်ခုက သင့် server ကို ဘယ်လို ခေါ်သလဲ မျက်စိမြင်လိုသည့်အခါ — stdio က child process ဖြင့် အလုပ်လုပ်ပုံကို နားလည်ရန်
- stdio တွင် `print()` တစ်ကြောင်းကြောင့် ချိတ်ဆက်မှု ပျက်စီးပြီး ဘာမှမဖြစ်သကဲ့သို့ ထင်ရသည့်အခါ — အကြောင်းရင်းကို ချက်ချင်း သိနိုင်ရန်
- Server တစ်ခုက tool ဘယ်လောက် ထုတ်ပြနေလဲ၊ schema က client ဆီ ဘယ်ပုံ ရောက်လဲ စစ်ဆေးလိုသည့်အခါ — Inspector နှင့် `fastmcp` CLI ဖြင့် မိနစ်ပိုင်းအတွင်း ဖြေရှင်းနိုင်သည်
- Client ကို ရေးပြီး server ၏ အမှားများကို `is_error` ဖြင့် ခွဲခြားတတ်လိုသည့်အခါ — M5_tools နှင့် M11 အတွက် အခြေခံအုတ်မြစ် ဖြစ်သည်

## ဖိုင်ဖွဲ့စည်းပုံ

| ဖိုင် | တာဝန် |
|---|---|
| `explanation.md` | သင်ခန်းစာ၏ အဓိက ရှင်းလင်းချက် (condensed lesson) |
| `exercise.md` | လက်တွေ့ လေ့ကျင့်ခန်း ခြောက်ခု |
| `solution.md` | လေ့ကျင့်ခန်းများ၏ အဖြေများ |
| `cheatsheet.md` | အမြန်ကြည့်ရန် အချက်အလက် ဇယားများ |

## ကိုးကား

- အရင် module — [../M3_asyncio_decorators/README.md](../M3_asyncio_decorators/README.md)
- နောက် module — [../M5_tools/README.md](../M5_tools/README.md)
- ဤ module ၏ test — [../../tests/test_m4_transport.py](../tests/test_m4_transport.py)
