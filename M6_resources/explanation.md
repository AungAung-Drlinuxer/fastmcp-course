# M6 — Read-Only Data Resources (`@mcp.resource`) — ရှင်းလင်းချက်

ဒီ module တွင် MCP ၏ primitive ဒုတိယမျိုးဖြစ်သည့် **resource** အကြောင်းကို သင်မည်။ Tool က action ဖြစ်ပြီး resource က thing (ဖတ်ရုံသာရနိုင်သော data) ဖြစ်သည်။ သင်စိတ်ဝင်စားရမည့် အချက်များမှာ — resource နှင့် tool ခွဲခြားနည်း၊ URI scheme နှင့် template၊ `mime_type`၊ enumeration နှင့် read လုပ်ခြင်း၊ pathlib၊ error ကို ရှင်းရှင်းလင်းလင်း ပြောခြင်း၊ path confinement တို့ဖြစ်သည်။

---

## Resource ဆိုတာ ဘာကို ဆိုလိုတာလဲ

### ဘာကို ဆိုလိုတာလဲ
Resource ဆိုသည်မှာ URI တစ်ခုဖြင့် လိပ်စာပေးထားသော၊ ဖတ်ရုံသာရနိုင်သည့် (read-only) data ဖြစ်သည်။ `@mcp.resource` decorator ဖြင့် သတ်မှတ်ပြီး client က `read_resource` ဖြင့် ဖတ်ယူသည်။

### ဘာကြောင့် လဲ
MCP တွင် primitive နှစ်မျိုးရှိသည် — **action** (tool) နှင့် **thing** (resource)။ "server status ကို ပြပါ" ဆိုသည်မှာ action မဟုတ်၊ ဖတ်ခြင်းသာဖြစ်သည်။ ထို့ကြောင့် ၎င်းကို resource အဖြစ် သတ်မှတ်ရခြင်းဖြစ်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ
Server ဘက်တွင် function တစ်ခုကို `@mcp.resource` ဖြင့် URI ချိတ်ပေးသည်။ Client က URI ကို တောင်းလာသောအခါ server က function ကို run ပြီး တန်ဖိုးကို ပြန်ပေးသည်။

### ဥပမာ
``python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("m6-demo")

@mcp.resource("inventory://hosts")
def host_inventory() -> str:
    # A static resource: a fixed URI, read-only data
    return "web-01: online\nweb-02: offline"
``

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
Configuration၊ runbook၊ log ကဲ့သို့ ဖတ်စရာ data များအတွက် tool မှားသုံးပါက action ထင်စေမည်။ Resource က ကျွန်ုပ်တို့ကို အဓိပ္ပာယ်မှန်ကန်စွာ ခွဲခြားစေပြီး client က ကြိုတင်ရယူနိုင်ရန်လည်း ဖြစ်စေသည်။

---

## Resource or Tool? — မေးခွန်း ၄ ခု

### ဘာကို ဆိုလိုတာလဲ
Function တစ်ခုကို resource လား tool လား ဆုံးဖြတ်ရန် မေးခွန်း ၄ ခုဖြင့် စစ်နည်းဖြစ်သည်။

### ဘာကြောင့် လဲ
မှားရွေးပါက နာမည်ပေးခြင်း၊ error ပြောခြင်း၊ client အလုပ်လုပ်ပုံ အားလုံး ရှုပ်ထွေးလာမည်။ ခွဲခြားနိုင်ဖို့ စစ်ဆေးတံပုံစံတစ်ခု လိုအပ်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ
မေးခွန်း ၄ ခုကို စဉ်းစားပါ — (၁) ဒါက ဖတ်ရုံလား၊ ပြောင်းလဲလား (၂) တစ်ခါတည်း အတုံးအသင်း ရနိုင်လား (၃) ဖတ်ဖို့သက်သက် လိုအပ်လား (၄) ကမ်းလှမ်းချက်က လက်တွေ့ဘက် သက်ရောက်လား။ ဖတ်ရုံ၊ တစ်ခါတည်းရနိုင်၊ data ဘက် သက်သက် ဖြစ်ပါက resource ဖြစ်သည်။

### ဥပမာ
``python
# Reading the runbook = resource (a thing)
@mcp.resource("runbook://{service}")
def get_runbook(service: str) -> str:
    return f"runbook for {service}"

# Restarting the service = tool (an action)
@mcp.tool()
def restart_service(service: str) -> str:
    # An action that changes state: must be a tool
    return f"restarted {service}"
``

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
`runbooks.py` ၏ ဆုံးဖြတ်ချက်များကို ကြည့်ပါက — ဖတ်စရာများ (runbook၊ config၊ inventory) သည် resource ဖြစ်ပြီး၊ ပြောင်းလဲသည့်အရာများ (restart၊ deploy) သည် tool ဖြစ်သည်။ ဒီ စည်းမျဉ်းက server တစ်ခုလုံး၏ ဖွဲ့စည်းပုံကို သိသာစေသည်။

---

## URI Schemes နှင့် Templates

### ဘာကို ဆိုလိုတာလဲ
URI သည် `scheme://path` ပုံစံရှိသည် — ဥပမာ `runbook://postgres`။ Static resource က URI အတိအကျတစ်ခုဖြစ်ပြီး template resource က `runbook://{service}`ကဲ့သို့ variable ပါသည့် ပုံစံဖြစ်သည်။

### ဘာကြောင့် လဲ
URI က resource ၏ လိပ်စာသာမက၊ အမျိုးအစားကိုလည်း ဖော်ပြသည်။ ကိုယ်ပိုင် scheme (`runbook://`, `config://`, `db://`) သုံးခြင်းက တရားဝင်ဖြစ်ပြီး client က အဓိပ္ပာယ် နားလည်ရန် documentation အဖြစ်လည်း ဆောင်ရွက်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ
Static resource တွင် URI အတိအကျဖြင့် ချိတ်သည်။ Template တွင် `{service}` ကဲ့သို့ variable တစ်ခုသည် function parameter တစ်ခုဖြစ်လာသည် — server က URI ထဲက တန်ဖိုးကို ညှပ်ယူပြီး parameter အဖြစ် ပေးလိုက်သည်။

### ဥပမာ
``python
from pathlib import Path

@mcp.resource("runbook://{service}")
def runbook_for(service: str) -> str:
    # Template variable {service} becomes a function parameter
    p = Path("runbooks") / f"{service}.md"
    if not p.is_file():
        raise FileNotFoundError(f"no runbook for '{service}'")
    return p.read_text()
# Expected output: client calls read_resource("runbook://postgres")
``

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
မတူညီသော data များကို URI တစ်ခုတည်းသော template ဖြင့် ဖန်တီးနိုင်သည်။ သို့သော် LAB 4 တွင် တွေ့ရမည့် **enumeration ထောင်ချောက်** ရှိသည် — `list_resources()` က static resources ကိုသာ ပြပြီး template များကို `list_resource_templates()` ဖြင့် သီးသန့်ရယူရသည်။

---

## `mime_type` နှင့် Return Shape

### ဘာကို ဆိုလိုတာလဲ
`mime_type` ဆိုသည်မှာ bytes များ၏ အမျိုးအစားကို ဖော်ပြသည့် ကြေညာချက်ဖြစ်သည် (ဥပမာ `text/plain`, `application/json`)။ Default မှာ `text/plain` ဖြစ်သည်။

### ဘာကြောင့် လဲ
Client က ရရှိလာသော content ကို မှန်ကန်စွာ ဆက်ဆံရန် မျိုးအစား သိရန် လိုအပ်သည် — JSON အဖြစ် ဖန်တီးမလား၊ text အဖြစ် ပြမလား။

### ဘယ်လို အလုပ်လုပ်လဲ
`str` ပြန်ပါက `text/plain`၊ `dict`/`list` ပြန်ပါက JSON content ဖြစ်သည်။ `mime_type` ပေးနိုင်သည့် နေရာ ၃ ခုရှိသည် — decorator ထဲ၊ function ထဲတွင် `Resource` object ပြန်ခြင်းဖြင့်၊ client ဘက်တွင် ကြည့်ခြင်းဖြင့်။ Template တစ်ခုတည်းအတွက် `mime_type` တစ်ခုတည်းသာ ရှိသည်။

### ဥပမာ
``python
import json

@mcp.resource("inventory://hosts.json", mime_type="application/json")
def hosts_json() -> dict:
    # Declaring the type: the client can parse it as JSON
    return {"web-01": "online", "web-02": "offline"}
# Expected output: client sees mime_type="application/json"
``

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
အရေးကြီးဆုံး အချက်မှာ — `mime_type` သည် **ကြေညာချက်သာဖြစ်ပြီး content ကို ပြောင်းလဲမပေး**။ မှားကြေညာပါက client လှည့်ဖြင့် ချရမည်။ LAB 8 တွင် return shape အမျိုးမျိုးကို တိုင်းတာကြည့်မည်။

---

## Read၊ Enumerate နှင့် Failing Loudly

### ဘာကို ဆိုလိုတာလဲ
Client ဘက်တွင် `read_resource(uri)` ဖြင့် ဖတ်ပြီး `list_resources()` နှင့် `list_resource_templates()` ဖြင့် စာရင်းရယူသည်။ Resource တွင် tool လို structured error channel မရှိသောကြောင့် **raise လုပ်ပြီး ဘာရနိုင်ကြောင်း ပြောရ**သည်။

### ဘာကြောင့် လဲ
Resource က read-only ဖြစ်သောကြောင့် error ပြောရန် နေရာကျဉ်းသည်။ တိတ်ဆိတ်စွာ `None` ပြန်ခြင်း (silent failure) က client ကို လမ်းလွဲစေမည်။

### ဘယ်လို အလုပ်လုပ်လဲ
File မတွေ့ပါက `FileNotFoundError` ချပြီး message ထဲတွင် ဘယ် service များအတွက် runbook ရနိုင်ကြောင်း စာရင်းထည့်သည်။ LAB 9 တွင် failure အမျိုးအစား ၄ မျိုးကို တိုင်းတာမည်။

### ဥပမာ
``python
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
``

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
LAB 5 ၏ reader loop တွင် တွေ့ရမည့်အတိုင်း — client တစ်ခုက server ပေးသမျှ ကိုင်တွယ်ရသည်။ Error message ကောင်းလျှင် user က ဘာဆက်လုပ်ရမည်ကို ချက်ချင်း မြင်နိုင်သည်။ Path confinement (LAB 6) ကလည်း `Path.resolve()` ဖြင့် ဖိုင်ကို ချိတ်ပိတ်ထားသည့် ဖိုဒါထဲမှာသာ ရှိမကြောင်း စစ်သည် — အပြည့်အစုံကို M10 တွင် ဆက်သင်မည်။

---

## အနှစ်ချုပ်

- MCP တွင် primitive နှစ်မျိုး — **action** (tool) နှင့် **thing** (resource)။ Resource က URI လိပ်စာပေးထားသော read-only data ဖြစ်သည်။
- မေးခွန်း ၄ ခုဖြင့် resource/tool ခွဲသည် — ဖတ်ရုံလား၊ တစ်ခါတည်းရလား၊ data သက်သက်လား၊ သက်ရောက်မှုရှိလား။
- Static resource က URI အတိအကျ၊ template resource က `{service}` ကဲ့သို့ variable ပါသည် — variable က function parameter ဖြစ်လာသည်။
- ကိုယ်ပိုင် scheme (`runbook://`, `config://`) သုံးခြင်းက တရားဝင်ပြီး documentation အဖြစ်လည်း အသုံးဝင်သည်။
- `mime_type` က ကြေညာချက်သာဖြစ်ပြီး default မှာ `text/plain` — content ကို ပြောင်းလဲမပေး။
- Enumeration ထောင်ချောက် — `list_resources()` က static ကိုသာပြသည်၊ template များအတွက် `list_resource_templates()` လိုအပ်သည်။
- pathlib ၏ `Path`, `glob`, `is_file`, `read_text` တို့ဖြင့် ဖိုင်များကို URI စာရင်းအဖြစ် ပြောင်းနိုင်သည်။
- Error ကို raise လုပ်ပြီး ဘာရနိုင်ကြောင်း အမည်တပ် ပြောရသည် — silent failure ရှောင်ပါ။
- Path confinement ၏ အလွှာ ၂ ခု (URI router + `Path.resolve()` containment) ကို ဒီ module တွင် မိတ်ဆက်ပြီး M10 တွင် အပြည့်အစုံ သင်မည်။
