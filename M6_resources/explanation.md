# M6 — Read-Only Data Resources (`@mcp.resource`) — ရှင်းလင်းချက်

ဒီ module မှာ MCP ရဲ့ primitive ဒုတိယမျိုးဖြစ်တဲ့ **resource** အကြောင်းကို လေ့လာရမှာ ပါတယ်။ Tool က action ဖြစ်ပြီး resource က thing (ဖတ်ရုံပဲရတဲ့ data) ဖြစ်တယ်။ သင်စိတ်ဝင်စားရမှာတွေက — resource နဲ့ tool ခွဲပုံ၊ URI scheme နဲ့ template၊ `mime_type`၊ enumeration နဲ့ read လုပ်ပုံ၊ pathlib၊ error ကို ရှင်းရှင်းလင်းလင်း ပြောပုံ၊ path confinement တွေပါ။

---

## Resource ဆိုတာ ဘာကို ဆိုလိုတာလဲ

### ဘာကို ဆိုလိုတာလဲ
Resource ဆိုတာ — URI တစ်ခုနဲ့ လိပ်စာပေးထားတဲ့၊ ဖတ်ရုံပဲရတဲ့ (read-only) data ပါတယ်။ URI ဆိုတာ — data တစ်ခုရဲ့ လိပ်စာလေးပါ။ `@mcp.resource` decorator နဲ့ သတ်မှတ်ပြီး client က `read_resource` နဲ့ ဖတ်ယူတယ်။ စာကြည့်တိုက်ထဲက စာအုပ်တစ်အုပ်လိုပါ — ဖတ်လို့ရတယ်၊ ပြင်လို့မရပါဘူး။

### ဘာကြောင့် လဲ
MCP မှာ primitive နှစ်မျိုးရှိတယ် — **action** (tool) နဲ့ **thing** (resource) ပါ။ "server status ကို ပြပါ" ဆိုတာ action မဟုတ်ပါဘူး၊ ဖတ်ခြင်းသာပါ။ Tool နဲ့ လုပ်ရင် LLM က status ပြောင်းတဲ့ command လို့ မှာယူလိုက်မိပြီး မှားနိုင်တယ်။ ဒါကို resource အဖြစ် သတ်မှတ်ရင် ဖတ်ရုံပဲရလို့ ဘာမှမပျက်ပါဘူး။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ Server ဘက်မှာ function တစ်ခုရေးတယ်။
၂။ `@mcp.resource` နဲ့ အဲဒီ functionကို URI တစ်ခုနဲ့ ချိတ်ပေးတယ်။
၃။ Client က URI တစ်ခုကို တောင်းလာတယ်။
၄။ Server က function ကို run တယ်။
၅။ ရတဲ့ တန်ဖိုးကို client ကို ပြန်ပေးတယ်။

### ဥပမာ
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("m6-demo")

@mcp.resource("inventory://hosts")
def host_inventory() -> str:
    # A static resource: a fixed URI, read-only data
    return "web-01: online\nweb-02: offline"
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
Configuration၊ runbook၊ log လို ဖတ်စရာ data တွေအတွက် tool ကို မှားသုံးရင် ပြဿနာ ဖြစ်တယ်။ Client က action လုပ်မယ်လို့ မှားထင်ပြီး side effect ရှိမယ်လို့ ထင်ပါတယ်။ Resource က data ကို သူ့နာမည်နဲ့ အမှန်ပြပါတယ်။ ဒါကြောင့် client က အရင်ကလို ကြိုပြီး ယူဖို့လည်း ရပါတယ်။

---

## Resource or Tool? — မေးခွန်း ၄ ခု

### ဘာကို ဆိုလိုတာလဲ
Function တစ်ခုကို resource လား tool လား ဆုံးဖြတ်ဖို့ မေးခွန်း ၄ ခုနဲ့ စစ်တဲ့ နည်းပါ။ ဆရာဝန်က လူနာကို မေးခွန်း ၄ ခုမေးပြီး ရောဂါ ခွဲသလိုမျိုးပါ။

### ဘာကြောင့် လဲ
မှားရွေးရင် နာမည်တပ်တာ၊ error ပြတာ၊ client အလုပ်လုပ်ပုံ အားလုံး ရှုပ်လာတယ်။ ရှုပ်ပြီးမှ ပြင်ရတော့ debug ချိန် ကြာပါတယ်။ ဒါကြောင့် စစ်ဆေးတဲ့ ပုံစံ တစ်ခု လိုတာပါ။

### ဘယ်လို အလုပ်လုပ်လဲ
မေးခွန်း ၄ ခုကို အစဉ်လိုက် စစ်ပါ —
၁။ ဒါက ဖတ်ရုံလား၊ ပြောင်းလဲစေလို့လား။
၂။ တစ်ခါတည်း အတုံးအသင်း ရနိုင်လား။
၃။ ဖတ်ဖို့သက်သက် လိုအပ်လား။
၄။ ကမ်းလှမ်းချက်က လက်တွေ့ဘက် သက်ရောက်လား။
ဖတ်ရုံ၊ တစ်ခါတည်းရနိုင်၊ data ဘက်သက်သက် ဖြစ်ရင် resource ပါ။

### ဥပမာ
ဒီ snippet မှာ မေးခွန်း ၄ ခုနဲ့ ဥပမာ function တွေကို စစ်ပြထားတာ ဖြစ်ပါတယ်။ ဖတ်ရုံလား ပြောင်းလဲလား ဆိုတဲ့ အဖြေကို သတိထားကြည့်ပါ။
```python
# Reading the runbook = resource (a thing)
@mcp.resource("runbook://{service}")
def get_runbook(service: str) -> str:
    return f"runbook for {service}"

# Restarting the service = tool (an action)
@mcp.tool()
def restart_service(service: str) -> str:
    # An action that changes state: must be a tool
    return f"restarted {service}"
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
`runbooks.py` မှာ ဆုံးဖြတ်ချက် တစ်ခု ရှိပါတယ် — ဖတ်စရာအမျိုးအစား (runbook၊ config၊ inventory) က resource ဖြစ်ပါတယ်။ ပြောင်းလဲမှု လုပ်ဆောင်စရာ (restart၊ deploy) က tool ဖြစ်ပါတယ်။ ဒီ စည်းမျဉ်းလေးက server တစ်ခုလုံးရဲ့ ဖွဲ့စည်းပုံကို ရှင်းရှင်းလင်းလင်း မြင်စေပါတယ်။ စည်းမျဉ်း မရှိရင် အသင်းထဲမှာ ဘယ်အရာက resource ဘယ်အရာက tool ဆိုတာ တစ်ယောက်နဲ့ တစ်ယောက် မတူဘဲ ရှုပ်ထွေးသွားပါတယ်။

---

## URI Schemes နှင့် Templates

### ဘာကို ဆိုလိုတာလဲ
URI ဆိုတာ — resource တစ်ခုရဲ့ လိပ်စာလေးပါ။ `scheme://path` ပုံစံ ရှိပါတယ် — ဥပမာ `runbook://postgres` ပါ။ Static resource က URI အတိအကျ တစ်ခုတည်းပါ။ Template resource က `runbook://{service}` လို variable ပါတဲ့ ပုံစံပါ။ မှတ်တမ်းစာအုပ်ကို စာမျက်နှာနံပါတ်နဲ့ ရှာသလိုမျိုးပါ။

### ဘာကြောင့် လဲ
URI က လိပ်စာသာ မဟုတ်ဘူး — resource ရဲ့ အမျိုးအစားကိုပါ ပြပါတယ်။ ကိုယ်ပိုင် scheme (`runbook://`, `config://`, `db://`) သုံးရင် client က URI ကို မြင်တဲ့အခါပဲ ဒါက ဘာအမျိုးအစားလဲဆိုတာ သိပါတယ်။ scheme မသိရင် client က resource တွေကို မှားယွင်းစွာ နားလည်ပြီး မှားတဲ့ အရာကို ခေါ်မိနိုင်ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ Static resource ကို URI အတိအကျနဲ့ ချိတ်ပါတယ်။
၂။ Template resource မှာ `{service}` လို variable တစ်ခု ထည့်ပါတယ်။
၃။ Client က URI ပုံစံနဲ့ ကိုက်ညီတဲ့ URI တစ်ခုကို ခေါ်ပါတယ်။
၄။ Server က URI ထဲက variable တန်ဖိုးကို ညှပ်ယူပါတယ်။
၅။ ညှပ်ယူထားတဲ့ တန်ဖိုးကို function parameter အဖြစ် ပေးလိုက်ပါတယ်။

### ဥပမာ
ဒီ snippet မှာ static resource နဲ့ template resource နှစ်မျိုးလုံး ဘယ်လို ရေးရမလဲဆိုတာ ပြထားပါတယ်။ URI ထဲက `{service}` က function parameter အဖြစ် ရောက်သွားပုံကို သတိထားကြည့်ပါနော်။
```python
from pathlib import Path

@mcp.resource("runbook://{service}")
def runbook_for(service: str) -> str:
    # Template variable {service} becomes a function parameter
    p = Path("runbooks") / f"{service}.md"
    if not p.is_file():
        raise FileNotFoundError(f"no runbook for '{service}'")
    return p.read_text()
# Expected output: client calls read_resource("runbook://postgres")
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
data မတူတာတွေကို URI template တစ်ခုတည်းနဲ့ ဖန်တီးလို့ ရပါတယ်။ ဒါပေမယ့် **enumeration ထောင်ချောက်** တစ်ခု ရှိပါတယ် — LAB 4 မှာ တွေ့ရမယ်နော်။ `list_resources()` က static resources ကိုပဲ ပြပါတယ်။ template တွေကတော့ `list_resource_templates()` နဲ့ သီးသန့် ရယူရပါတယ်။

---

## `mime_type` နှင့် Return Shape

### ဘာကို ဆိုလိုတာလဲ
`mime_type` ဆိုတာ — bytes တွေရဲ့ အမျိုးအစားကို ဖော်ပြတဲ့ ကြေညာချက်လေးပါ။ ဥပမာ `text/plain`, `application/json` ဆိုတဲ့ စာသားတွေပါ။ default ကတော့ `text/plain` ပါတယ်။ ဒါက စာလုံးပေါ်မှာ ဘာအရောင်နဲ့ ရေးထားလဲ ပြတဲ့ မှတ်စုလေးနဲ့ တူပါတယ်။

### ဘာကြောင့် လဲ
`mime_type` မပေးရင် client က content အမျိုးအစား မသိပါဘူး။ JSON အဖြစ် ဆက်ဆံရမလား၊ text အဖြစ် ပြရမလား နားမလည်တော့ပါဘူး။ အဲဒါဆို JSON ကို text အတိုင်း ပြတတ်ပြီး user က အဓိပ္ပာယ် မှားယွင်းသွားတတ်ပါတယ်။ `mime_type` ပေးလိုက်ရင် client က မှန်ကန်တဲ့ ပုံစံနဲ့ ဆက်ဆံနိုင်ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ `str` ပြန်ရင် content က `text/plain` အဖြစ် သတ်မှတ်ပါတယ်။
၂။ `dict` ဒါမှမဟုတ် `list` ပြန်ရင် JSON content ဖြစ်ပါတယ်။
၃။ `mime_type` ပေးလို့ရတဲ့နေရာ သုံးခု ရှိပါတယ် — decorator ထဲမှာ၊ function ထဲကနေ `Resource` object ပြန်တဲ့အခါ၊ client ဘက်က ကြည့်တဲ့အခါ။
၄။ Template တစ်ခုကိုတော့ `mime_type` တစ်ခုတည်းပဲ သတ်မှတ်လို့ရပါတယ်။

### ဥပမာ
အောက်မှာ code က `mime_type` ချင်းကွဲပြီး resource တွေ ဘယ်လိုပြန်လဲ ပြပါတယ်။ ကျွန်တော်တို့ ကြည့်ရမှာက — return လုပ်တဲ့ ပုံစံအလိုက် content type ဘယ်လို ပြောင်းသွားလဲ ဆိုတာပါ။
```python
import json

@mcp.resource("inventory://hosts.json", mime_type="application/json")
def hosts_json() -> dict:
    # Declaring the type: the client can parse it as JSON
    return {"web-01": "online", "web-02": "offline"}
# Expected output: client sees mime_type="application/json"
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
အရေးကြီးဆုံး အချက်က — `mime_type` ဆိုတာ **ကြေညာတဲ့ စာသားပါပဲ၊ content ကို တကယ်မပြောင်းပါဘူး**။ မှားပြီး ကြေညာရင် client က လှည့်စားခံရတယ်။ LAB 8 မှာ return shape အမျိုးမျိုးကို တိုင်းတာကြည့်ကြပါမယ်။

---

## Read၊ Enumerate နှင့် Failing Loudly

### ဘာကို ဆိုလိုတာလဲ
Client ဘက်ကနေ `read_resource(uri)` နဲ့ resource ဖတ်တယ်။ `list_resources()` နဲ့ `list_resource_templates()` နဲ့ စာရင်းယူတယ်။ Resource မှာ tool လို structured error channel မရှိလို့ **raise လုပ်ပြီး ဘာဖြစ်ကြောင်း ပြောပြရတယ်**။

### ဘာကြောင့် လဲ
Resource က read-only ဖြစ်တဲ့အတွက် error ပြောဖို့ နေရာကျဉ်းတယ်။ `None` ကို တိတ်တိတ်ပြန်ရင် (silent failure) client က လမ်းလွဲသွားတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ
File မတွေ့ရင် `FileNotFoundError` ချတယ်။ message ထဲမှာ ဘယ် service တွေအတွက် runbook ရနိုင်လဲ စာရင်းထည့်ပြတယ်။ LAB 9 မှာ failure အမျိုးအစား ၄ မျိုးကို တိုင်းတာကြည့်ကြပါမယ်။

### ဥပမာ
```python
available = "postgres, redis, nginx"

@mcp.resource("runbook://{service}")
def runbook_for(service: str) -> str:
    p = Path("runbooks") / f"{service}.md"
    if not p.is_file():
        # Fail loudly AND name what IS available
        raise FileNotFoundError(
            f"no runbook for '{service}'. available: {available}"
        )
    return p.read_text()
# Expected output: FileNotFoundError: no runbook for 'kafka'. available: postgres, redis, nginx
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
LAB 5 ရဲ့ reader loop မှာ မြင်ရတဲ့အတိုင်းပါ — client က server ပေးသမျှ လက်ခံဖို့သာ ရှိတယ်။ Error message ကောင်းရင် user က နောက်တစ်ဆင့် ဘာလုပ်ရမလဲဆိုတာ ချက်ချင်း မြင်ပါတယ်။ Path confinement (LAB 6) ကလည်း `Path.resolve()` နဲ့ ဖိုင်က ချိတ်ပေးထားတဲ့ ဖိုဒါထဲမှာပဲ ရှိတယ်ဆိုတာ စစ်ပေးတယ် — အပြည့်အစုံကိုတော့ M10 မှာ ဆက်သင်ပါမယ်နော်။

---

## အနှစ်ချုပ်

- MCP မှာ primitive နှစ်မျိုး ရှိပါတယ် — **action** (tool) နဲ့ **thing** (resource) ပါ။ Resource ဆိုတာ URI လိပ်စာ ပေးထားတဲ့ read-only data ပါ။
- မေးခွန်း ၄ ခုနဲ့ resource/tool ခွဲပါတယ် — ဖတ်ရုံလား၊ တစ်ခါတည်း ရလား၊ data သက်သက်လား၊ သက်ရောက်မှု ရှိလားပါ။
- Static resource က URI အတိအကျပါ။ Template resource က `{service}` လို variable ပါတယ် — variable က function parameter အဖြစ် ဖြစ်လာပါတယ်။
- ကိုယ်ပိုင် scheme (`runbook://`, `config://`) သုံးတာ တရားဝင်ပြီး၊ documentation အဖြစ်လည်း အသုံးဝင်ပါတယ်။
- `mime_type` က ကြေညာချက်သာပါ။ Default က `text/plain` ပါ — content ကို မပြောင်းပေးပါဘူး။
- Enumeration ထောင်ချောက် ရှိပါတယ် — `list_resources()` က static ကိုပဲ ပြပါတယ်။ Template တွေအတွက် `list_resource_templates()` လိုအပ်ပါတယ်။
- pathlib ရဲ့ `Path`, `glob`, `is_file`, `read_text` တွေနဲ့ ဖိုင်တွေကို URI စာရင်းအဖြစ် ပြောင်းနိုင်ပါတယ်။
- Error ကို raise လုပ်ပြီး ဘာ ဖြစ်နိုင်လဲဆိုတာ နာမည်တပ် ပြောပါ — silent failure ကို ရှောင်ပါနော်။
- Path confinement ရဲ့ အလွှာ ၂ ခု (URI router + `Path.resolve()` containment) ကို ဒီ module မှာ မိတ်ဆက်ပြီး M10 မှာ အပြည့်အစုံံ သင်ပါမယ်။