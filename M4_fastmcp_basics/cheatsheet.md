# Cheatsheet — Lesson 2.1

> ဤဖိုင်သည် **ပြန်ကြည့်ရန်** ဖြစ်သည်။ Lesson 2.1 ကို ပြီးမြောက်လျှင် ဤဖိုင် တစ်ဖိုင်တည်းဖြင့်
> အလုပ်လုပ်နိုင်ရမည်။ ဖိုင်တိုင်း၏ အချက်အလက်များကို **ကျစ်လျစ်စွာ** ပြန်စုထားသည်။

## ဒီဖိုင်မှာ ဘာသင်မလဲ

- Lesson 2.1 ၏ **အရေးကြီးဆုံး အချက် ၁၀** (တစ်နေရာတည်း)
- Module တစ်ခုလုံး၏ command များ၊ file များ၊ port များ ဇယား
- ⭐ API နာမည် ဇယား — server-side vs client-side (အမှား အများဆုံး နေရာ)
- Error → အကြောင်းရင်း → ဖြေရှင်းနည်း (အမှားအများဆုံး ၁၀ ခု)
- သင့်ကိုယ်ပိုင် ဖြည့်ရမည့် အပိုင်း (CLI flag များ၊ သင့် deployment ၏ transport)
- နောက် module သို့ ကူးသည့် လမ်းကြောင်း

---

## အပိုင်း ၁ — Lesson 2.1 ၏ အချက် ၁၀ (တစ်နေရာတည်း)

```text
၁.  MCP သည် **protocol** တစ်ခု၊ framework မဟုတ် — wire format သည် JSON-RPC 2.0
     request: {jsonrpc, id, method, params}   |   response: {jsonrpc, id, result|error}
     notification တွင် `id` မပါ

၂.  **host / client / server** — ဆုံးဖြတ်ချက် အားလုံး host တွင်
     server က စာရင်း **ထုတ်ပြသည်** သာ၊ "ငါ့ tool ကို သုံးပါ" လို့ တောင်းဆိုလို့ မရ

၃.  Server တစ်ခုတွင် အပိုင်း သုံးပိုင်း: `FastMCP("name")` + `@mcp.tool` + `mcp.run(transport=...)`
     ⭐ နာမည်သည် `mcp.name`, `serverInfo.name`, banner, Inspector, error တွင် ပေါ်သည်

၄.  ⭐ stdio = client က **child process ဖောက်သည်**။ `stdin`→request, `stdout`→**protocol**,
     `stderr`→log။ stdio server တွင် `print()` တစ်လိုင်းက JSON-RPC stream ကို ဖျက်သည်

၅.  ⭐ HTTP = server က **port တွင် စောင့်**သည်, client က **dial** လုပ်သည်။
     `stdout` လွတ်လပ်၊ ဒါပေမယ့် **auth ကို သင်ထည့်ရမည်**

၆.  ⭐ ဇယားလိုင်း ၅ လိုင်းသည် အကြောင်းရင်းတစ်ခုတည်းမှ: **"ဘယ်သူ စသလဲ"**
     ဆုံးဖြတ်ချက်: "တစ်ဦး တစ်စက် → stdio ။ အများ/အဝေး → HTTP ။"

၇.  ⭐ Schema သည် annotations + docstring မှ **ထုတ်လုပ်**သည် —
     **server တွင် `.parameters`**၊ **client တွင် `.input_schema`** (`.inputSchema` = deprecated)

၈.  `Client` ၏ နည်း သုံးမျိုး: `Client(mcp)` (test)၊ `Client(Path(...))` (stdio)၊ `Client(url)` (HTTP)
     ⚠️ `Client("<str path>")` = deprecation warning → `Path` သုံးပါ

၉.  ⭐ `{"ok": false, "error": ..., "hint": ...}` သည် **`is_error=False`** — data, not a failure
     `raise` လုပ်လျှင် `ToolError` — model ဆီ "plan မပါသည့် error string" ရောက်သည်

၁၀. ⭐ Inspector = `fastmcp dev inspector <file>` (`inspector` သည် `dev` ၏ အောက်)
     Inspector သည် **ရှာဖွေမှု**၊ test သည် **အာမခံချက်** — နှစ်ခုလုံး လိုသည်
```

---

## အပိုင်း ၂ — File များနှင့် သူတို့၏ တာဝန်

| ဖိုင် | အမျိုးအစား | ဘာအတွက် | ဘယ်ဖိုင်တွင် ရှင်းထားသလဲ |
|---|---|---|---|
| `code/hello_server.py` | server | tool ၂ ခု (`ping`, `add`)၊ hybrid transport | 01, 02, 04, 05 |
| `code/transports.py` | reference | stdio ကို subprocess ဖြင့် + ဇယား ၅ လိုင်း | 04, 06 |
| `code/lab_1_echo_server.py` | lab server | tool ၃ ခု၊ port 8001 | 01, 02, 04, 05 |
| `code/lab_2_stdout_trap.py` | ⚠️ တမင် ကျိုးသည် | `print()` အန္တရာယ် (stdio) | 04, 06 |
| `code/lab_2_client_demo.py` | client | ကျိုးနေသည့် server ကို ချိတ်၊ error ဖတ် | 04 |
| `code/lab_3_http_client.py` | client | HTTP URL ဖြင့် ချိတ်သည် | 05 |
| `code/lab_4_discover_tools.py` | client | schema + ခေါ်ဆိုမှု သုံးမျိုး | 09 |
| `code/lab_5_currency_server.py` | lab server | tool ၄ ခု၊ port 8002 | 10, 11, 12 |
| `code/lab_5_drive_both.py` | driver | in-process + stdio + HTTP | 12 |
| `tests/test_m4_transport.py` | test | နာမည်၊ schema၊ round trip၊ validation | 02, 11 |

---

## အပိုင်း ၃ — Command များ (ကူးယူရန် အသင့်)

### Server ကို stdio ဖြင့် run

```bash
uv run python -m M4_fastmcp_basics.code.hello_server
uv run python -m M4_fastmcp_basics.code.lab_1_echo_server
uv run python -m M4_fastmcp_basics.code.lab_5_currency_server
```

⚠️ Output မရှိဘဲ terminal ရပ်နေလျှင် **ဒါက မှန်** — stdin စောင့်နေသည်။ `Ctrl+C`။

### Server ကို HTTP ဖြင့် run

```bash
uv run python -m M4_fastmcp_basics.code.hello_server --http            # port 8000, host 0.0.0.0
uv run python -m M4_fastmcp_basics.code.lab_1_echo_server --http       # port 8001, host 127.0.0.1
uv run python -m M4_fastmcp_basics.code.lab_5_currency_server --http   # port 8002, host 127.0.0.1
```

### Client များ

```bash
uv run python -m M4_fastmcp_basics.code.transports
uv run python -m M4_fastmcp_basics.code.lab_2_client_demo
uv run python -m M4_fastmcp_basics.code.lab_3_http_client
uv run python -m M4_fastmcp_basics.code.lab_4_discover_tools
uv run python -m M4_fastmcp_basics.code.lab_5_drive_both
```

### Test နှင့် Inspector

```bash
uv run pytest tests/test_m4_transport.py -v
uv run fastmcp dev inspector M4_fastmcp_basics/code/hello_server.py
uv run fastmcp dev inspector M4_fastmcp_basics/code/lab_1_echo_server.py
```

### စစ်ဆေးရေး command များ

```bash
uv run fastmcp version                # ⭐ first step when troubleshooting
uv run python -c "import fastmcp; print(fastmcp.__version__)"
uv run fastmcp inspect M4_fastmcp_basics/code/hello_server.py
uv run fastmcp inspect http://127.0.0.1:8002/mcp
uv run fastmcp --help
```

### Port လွတ်/မလွတ်

```bash
# Windows
netstat -ano | findstr :8000
tasklist | findstr python

# Linux/macOS
ss -ltnp | grep 8000
ps aux | grep hello_server
```

---

## အပိုင်း ၄ — ⭐ API နာမည် ဇယား (အမှား အများဆုံး နေရာ)

| ဘာကို လိုသလဲ | Server-side | Client-side | ⚠️ မသုံးရ |
|---|---|---|---|
| schema ဖတ် | `.parameters` (`FunctionTool`) | `.input_schema` (`Tool`) | ❌ `.inputSchema` (deprecated) |
| tool စာရင်း | `await mcp.list_tools()` | `await client.list_tools()` | ❌ `mcp.get_tools()` (2.x) |
| resource template | `await mcp.list_resource_templates()` | `await client.list_resource_templates()` | ❌ `template.uriTemplate` (2.x) |
| result ဖတ် | — | `result.data` / `.structured_content` / `.is_error` | — |
| elicitation result | `AcceptedElicitation` / `DeclinedElicitation` / `CancelledElicitation` | — | ❌ `ElicitationResult` (2.x) |

### 2.x → 4.0.5 (တိုင်းတာထားသည်)

| 2.x documentation says | 4.0.5 actually has | Old name သုံးလျှင် |
|---|---|---|
| `ElicitationResult` | `AcceptedElicitation` / `DeclinedElicitation` / `CancelledElicitation` | `ImportError` |
| `tool.inputSchema` | `tool.parameters` | `AttributeError: 'FunctionTool' object has no attribute 'inputSchema'` |
| `template.uriTemplate` | `template.uri_template` | `AttributeError` |
| `await mcp.get_tools()` | `await mcp.list_tools()` | `AttributeError: 'FastMCP' object has no attribute 'get_tools'` |

### ⭐ Object အမျိုးအစားကို အရင် စစ်ပါ

```python
print(type(tool).__name__)     # "FunctionTool" → .parameters
                               # "Tool"         → .input_schema
```

---

## အပိုင်း ၅ — ⚠️ Error → အကြောင်းရင်း → ဖြေရှင်းနည်း (၁၀ ခု)

| Error / လက္ခဏာ | အကြောင်းရင်း | ဖြေရှင်းနည်း |
|---|---|---|
| `JSONDecodeError` / parse error | stdio server ထဲ `print()` | `sys.stderr.write()` သို့ `ctx.info()` |
| `ModuleNotFoundError: fastmcp` (child ထဲ) | မှားသည့် Python (system) | `uv run` ဖြင့် run; M1 ၏ `.venv` စစ် |
| `AttributeError: 'Tool' object has no attribute 'parameters'` | client တွင် server နာမည် | `.input_schema` (file 11) |
| `AttributeError: 'FunctionTool' object has no attribute 'inputSchema'` | 2.x နာမည် | `.parameters` (server) |
| `FastMCPDeprecationWarning` | `.inputSchema` / `Client("str path")` | `.input_schema` / `Path(...)` |
| `ToolError: 1 validation error for call[...]` | argument type/enum မှား | schema ကို ဖတ်; model မြင်သည့် contract ပြင် |
| `ToolError: ... Unknown tool` | tool အမည် မှား | `known = {t.name for t in tools}` ဖြင့် ကြိုတင်စစ် |
| `Connection refused` / `ConnectError` | HTTP server run မနေသည် | `--http` ဖြင့် ဖွင့်; port စစ် |
| `Address already in use` | port ကို အခြား process ကိုင်ထားသည် | ဟောင်း process ရပ် / port ပြောင်း |
| `KeyError: 'result'` | structured failure တွင် `result` မရှိ | `payload["ok"]` ကို အရင် စစ် |
| tool အမည် `wrapper`၊ description `None` | ကိုယ်ပိုင် wrapper က `@mcp.tool` အပေါ်တွင် | `@functools.wraps` / အစီအစဉ် လှန် (file 03) |
| `pytest` hang | module အဆင့်တွင် `mcp.run()` | run ကို `main()` ထဲ ထည့် (file 02) |
| `Method not found (-32601)` | protocol/version မတူ | version စစ်; client က မမေးသင့်သည့်အရာ မေးနေသည် |
| `ToolError: elicitation ... unavailable on 2026-07-28 connections` | `mode="auto"` (sessionless era) | `Client(mcp, mode="legacy")` (M8) |

### ⭐ Error နှစ်မျိုးကို ခွဲခြားခြင်း

```text
Protocol အဆင့် (transport/handshake): parse error, connection refused, -32601
Tool အဆင့် (သင့် code):               validation error, ToolError, မှားသည့် data

⭐ ဒါကို ခွဲနိုင်လျှင် "ငါမှားလား API မှားလား" ဆိုသည့် အချိန်ကုန်ခြင်းကို ရှောင်နိုင်သည်
```

---

## အပိုင်း ၆ — Boilerplate (ကူးယူရန် အသင့်)

### Server ၏ အခြေခံပုံစံ

```python
"""One line saying what this server fronts.

Run:
    uv run python -m <module path>          # stdio, for an editor
    uv run python -m <module path> --http   # HTTP, for the network
"""
from __future__ import annotations

import sys

from fastmcp import FastMCP

mcp = FastMCP("lab-something")          # use the system the server fronts


@mcp.tool
def ping() -> str:
    """Return a fixed string, to prove the round trip works."""
    return "pong"


def main() -> None:
    if "--http" in sys.argv:
        mcp.run(transport="http", host="127.0.0.1", port=8000)
    else:
        mcp.run(transport="stdio", show_banner=False)


if __name__ == "__main__":
    main()
```

### Structured error ပုံစံ

```python
def _ok(**payload: object) -> dict:
    return {"ok": True, **payload}


def _fail(code: str, hint: str) -> dict:
    """A structured failure the agent can act on: a code for the client, a hint for the model."""
    return {"ok": False, "error": code, "hint": hint}
```

### Client ပုံစံ

```python
import asyncio
from pathlib import Path

from fastmcp import Client

SERVER = Path(__file__).with_name("lab_1_echo_server.py")


async def main() -> None:
    async with Client(SERVER) as client:            # Path -> stdio
        tools = await client.list_tools()
        print([t.name for t in tools])
        result = await client.call_tool("ping", {})
        print(result.is_error, result.data)


if __name__ == "__main__":
    asyncio.run(main())
```

### Schema ဖတ်သည့် snippet နှစ်ခု

```python
# server-side
t = next(t for t in await mcp.list_tools() if t.name == "add")
print(t.parameters)

# client-side
t = next(t for t in await client.list_tools() if t.name == "add")
print(t.input_schema)
```

---

## အပိုင်း ၇ — ရွေးချယ်မှု ဇယား (transport)

| မေးခွန်း | stdio | HTTP |
|---|---|---|
| ဘယ်သူ စသလဲ | client (child process) | operator / service manager |
| ဘယ်သူ ရောက်နိုင်သလဲ | ထို client၊ ထို machine | port ကို မြင်သူတိုင်း |
| auth | OS process boundary | ⭐ သင် ထည့်ရမည် (M10) |
| `stdout` | ⚠️ protocol — `print()` မဖြစ် | ✅ လွတ်လပ် |
| ဘာအတွက် | editor on a laptop | shared / containerised server |

```text
ဆုံးဖြတ်ချက်: မေးခွန်း ၁ — client သည် server နှင့် တူညီသည့် machine တွင် ရှိသလား?
  မဟုတ် → HTTP ။  ဟုတ် → client တစ်ခုတည်းလား? ဟုတ် → stdio
```

---

## အပိုင်း ၈ — ⭐ သင့်ကိုယ်ပိုင် ဖြည့်ရမည့် အပိုင်း

ဤနေရာတွင် နေရာ လွတ်ထားသည်။ Lesson 2.1 ကို run ပြီးလျှင် ဤဇယားကို **ကိုယ်တိုင်** ဖြည့်ပါ —
ဤအလေ့အကျင့်သည် `--help` ကို ဖတ်သည့် အလေ့အကျင့် (file 08) ကို အကျိုးရှိစေသည်။

### CLI flag များ (သင့် installation မှ)

| command | flag/argument | ဘာလုပ်သည် | တိုင်းတာထားသလား |
|---|---|---|---|
| `fastmcp version` | | | ✅ |
| `fastmcp dev inspector` | | | အမည် သာ |
| `fastmcp run` | `--reload`, `--module` | | ✅ |
| `fastmcp inspect` | | | ⬜ ဖြည့်ပါ |
| `fastmcp call` | | | ⬜ ဖြည့်ပါ |
| `fastmcp list` | | | ⬜ ဖြည့်ပါ |
| `fastmcp discover` | | | ⬜ ဖြည့်ပါ |
| `fastmcp ----` | | | ⬜ |

### သင့် deployment ၏ transport

```text
ကျွန်တော်၏ အခြေအနေ (ချရေးပါ):

  ခေါ်မည့် client:
  တူညီသည့် machine လား:
  client အရေအတွက်:
  network လိုသလား:
  auth လိုသလား:
  → ရွေးချယ်သည့် transport:
  → အကြောင်းရင်း (တစ်လိုင်း):
```

### Port စာရင်း (သင့် lab)

```text
8000  — hello_server.py (0.0.0.0)
8001  — lab_1_echo_server.py (127.0.0.1)
8002  — lab_5_currency_server.py (127.0.0.1)
----  — သင့်ကိုယ်ပိုင် server (ရွေးပါ)
```

---

## အပိုင်း ၉ — နောက် module သို့ ကူးခြင်း

```text
M4 (ဤ module) = server ဆောက်ခြင်း + transport
   ✅ server object၊ tool၊ stdio/HTTP၊ Inspector၊ CLI၊ client၊ result၊ schema

M5 — Tools (structured error ကို အသေးစိတ်)
   ကူးရန်: `M5_tools/code/calculator.py` (file 10 တွင် ဖတ်ထားပြီ)
   ⭐ M5 တွင် `{"ok": false, "hint": "..."}` ကို **စံ** အဖြစ် ချဲ့မည်

M6 — Resources (tool vs resource)
   ကူးရန်: `M6_resources/code/runbooks.py`
   ⭐ `list_rates` ကဲ့သို့ tool သည် အမှန်တကယ် resource ဖြစ်နိုင်သည်

M8 — Elicitation (protocol version ၏ သက်ရောက်မှု)
   ကူးရန်: `Client(mcp, mode="legacy", elicitation_handler=...)` (VERIFIED.md)

M9 — Clients (သင့်ကိုယ်ပိုင် agent loop)
   ကူးရန်: `M9_clients/code/tool_loop.py`, `cline_mcp_settings.json`

M10 — Security
   ကူးရန်: `M10_security/code/path_validation.py`, allowlist (file 05, 06)
```

---

## အပိုင်း ၁၀ — လေ့အကျင့် ၁၀ ခု (ဤ lesson မှ)

```text
၁.  `uv run` ကို အမြဲ သုံးပါ — `activate` မလုပ်ပါနဲ့
၂.  stdio server တွင် `print()` မရေးပါနဲ့ — `sys.stderr.write` / `ctx.info`
၃.  `mcp` object ကို module အဆင့်တွင်၊ `mcp.run()` ကို `main()` ထဲ
၄.  `if __name__ == "__main__":` ကို မမေ့ပါ
၅.  tool အသစ် ရေးတိုင်း Inspector ဖွင့်ပြီး schema ကို စစ်ပါ
၆.  schema မှန်လျှင် test တစ်ခု ရေးပါ (ရှာဖွေမှု → အာမခံချက်)
၇.  `is_error` ကို မစစ်ပါနဲ့ — tool ၏ `ok` field ကို စစ်ပါ
၈.  error တွင် `code` + `hint` နှစ်ခုလုံး ထည့်ပါ (M5/M11 ၏ ပုံစံ)
၉.  transport ကို tool logic မှ ခွဲထားပါ — `mcp.run(...)` တစ်နေရာတည်း
၁၀. lab ပြီးတိုင်း server ကို ရပ်ပါ — port လွတ်မှုသည် နောက် lab ၏ အခြေခံ
```

## နိဒါန်း

- ဤ cheatsheet ၏ အပိုင်း ၄ (API နာမည် ဇယား) ကို **အများဆုံး ပြန်ကြည့်မည်** — `.parameters` vs `.input_schema`
- အပိုင်း ၅ (error ဇယား) သည် ပြဿနာ ရှာသည့်အခါ ပထမဆုံး ဖတ်ရမည့် နေရာ
- အပိုင်း ၆ (boilerplate) ကို ကူးယူ၍ သင့် server အသစ်များ စတင်ပါ
- အပိုင်း ၈ (သင့်ကိုယ်ပိုင် ဖြည့်ရမည့်အပိုင်း) ကို `--help` ဖြင့် ဖြည့်ပါ — ပြီးမှ ရှေ့ဆက်
- ⭐ ဤ lesson ၏ အနှစ်သာရ: **tool code သည် transport ကို မသိ**၊ **schema သည် annotations မှ ထွက်သည်**၊ **error သည် data ဖြစ်နိုင်သည်**

## ကိုးကား

- `file 01 — what MCP is` · `file 02 — initializing` · `file 03 — the decorator`
- `file 04 — stdio` · `file 05 — HTTP` · `file 06 — choosing`
- `file 07 — Inspector` · `file 08 — CLI` · `file 09 — client discovery`
- `file 10 — results and errors` · `file 11 — schema end to end` · `file 12 — the big lab`
- [`../../VERIFIED.md`](../VERIFIED.md) — တိုင်းတာထားသည့် API အချက်များ (အာဏာရှိ)
- [`../TUTORIAL_SPEC.md`](../TUTORIAL_SPEC.md) — ဤ tutorial များအတွက် စည်းမျဉ်း
