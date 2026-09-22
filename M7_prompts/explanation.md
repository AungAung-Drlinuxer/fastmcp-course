# M7 — Workflow Steering Prompts (`@mcp.prompt`) — explanation.md

## မိတ်ဆက်

ဒီ module မှာ MCP server တစ်ခုရဲ့ ပစ္စည်းသုံးမျိုးအနက် တတိယမြောက်ဖြစ်သော **prompt** အကြောင်းကို လေ့လာမည်။ Tool က model က ခေါ်သည်၊ resource က application က ဖတ်သည် — prompt ကတော့ **user က task စမှိုင်းခင် host မှတစ်ဆင့် ရွေးချယ်သည့် template** ဖြစ်သည်။ Duration ၂ နာရီ၊ Phase 2 — MCP Core Surfaces ဖြစ်သည်။

---

## Topic 1 — Prompt ဆိုတာ ဘာလဲ

### ဘာကို ဆိုလိုတာလဲ

Prompt ဆိုသည်မှာ server က declare လုပ်ထားပြီး host (client) က menu အဖြစ် ပြသည့် **အကြို-စာသား template** ဖြစ်သည်။ Function တစ်ခုကို `@mcp.prompt` decorator နှင့် အမှတ်အသားပြုပြီး argument များကို လက်ခံရရှိသည်။ Render လုပ်သောအခါ message list တစ်ခု ပြန်ထွက်လာပြီး host က conversation ရဲ့ အစတွင် ထည့်သွင်းရန် ဖြစ်သည်။

### ဘာကြောင့် လဲ

Model တစ်ခုကို တစ်နေ့တာလုံး တူညီသော အလုပ်မျိုးကို ထပ်ခါထပ်ခါ တောင်းဆိုသောအခါ user တိုင်းက မတူညီသော စာသားဖြင့် မေးလေ့ရှိသည်။ ရလဒ်မှာလည်း တစ်ခါနှင့်တစ်ခါ မတူညီတော့သည် — တစ်ခါက structure ကောင်းသည်၊ တစ်ခါက step တွေ ချန်လျက် အဖြေပေးသည်။ Prompt သည် ဒီ "ဘယ်လိုမေးမေး" ခြားနားမှုကို ဖျက်ပြီး **consistency** ကို အာမခံပေးသည်။ ဒါကြောင့် prompt ရဲ့ တန်ဖိုးအားလုံးဟာ consistency ပင်ဖြစ်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

Server ဘက်မှာ Python function တစ်ခုကို `@mcp.prompt` (bare) သို့မဟုတ် `@mcp.prompt("name")` (named) နှင့် သတ်မှတ်သည်။ Docstring သည် description ဖြစ်လာပြီး function signature ရဲ့ parameter တိုင်းသည် prompt ရဲ့ argument ဖြစ်လာသည်။ Host က `list_prompts()` ဖြင့် စာရင်းယူပြီး `get_prompt(name, arguments)` ဖြင့် render လုပ်သည်။ Server က declare၊ host က surface — ဒါသည် ကွဲပြားခြင်းနှစ်ရပ်ဖြစ်သည်။ Prompt မရှိလျှင် server ပျက်သည်မဟုတ် — မြင်ကွင်းထဲမှာ menu တစ်ခု ရှိမနေတော့သည်သာဖြစ်သည်။

### ဥပမာ

``python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("m7")

@mcp.prompt
def rca_prompt(service: str) -> str:
    """Guide a five-step root cause analysis for a service."""
    return (
        f"Perform a root cause analysis for the service '{service}'.\n"
        "Follow these numbered steps in order:\n"
        "1. State the observed symptom.\n"
        "2. List the facts you actually have.\n"
        "3. List what you do NOT know.\n"
        "4. Propose the most likely cause.\n"
        "5. State how to verify it."
    )
# Expected output: a prompt registered in the server's registry,
# visible to the host via list_prompts() under the name "rca_prompt".
``

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

ပထမဆုံး "LAB 1 — Prompt Anatomy" ကို လုပ်ရင်း prompt တစ်ခုရဲ့ အစိတ်အပိုင်းဖြစ်သော name, description, arguments, return value တို့ကို သီးသန့် မြင်ရမည်။ ဒါက prompt တစ်ခုကို ဘယ်လိုဖန်တီးမလဲဆိုသည့် အခြေခံ နားလည်မှုကို ပေးသည်။ အဲဒါမရှိလျှင် နောက်ပိုင်း topic အားလုံး — argument injection, multi-turn guidance, host contract — တွေကို ဆက်လက်လေ့လာဖို့ ခက်ခဲသွားမည်။

---

## Topic 2 — Tool vs Resource vs Prompt — ဘယ်သူက ရွေးသလဲ

### ဘာကို ဆိုလိုတာလဲ

သုံးမျိုးလုံး server က declare လုပ်သည်မှာ တူသော်လည်း **ဘယ်သူက ရွေးလဲ** (model, application, user) နှင့် **ဘယ်အချိန်မှာ ရွေးလဲ** (task အတွင်း / task မစခင်) ကွာသည်။ ရွေးသူသည် ဒီဇိုင်းဆုံးဖြတ်ချက်ဖြစ်သည်။ Timing အရ tool က task အတွင်း model က ဆုံးဖြတ်သည်၊ resource က application က ဖတ်သည်၊ prompt က task မစခင် user က host မှတစ်ဆင့် ရွေးသည်။

### ဘာကြောင့် လဲ

ရွေးမှားလျှင် အလုပ်လုပ်သည့်ပုံစံ ပြောင်းသွားသည် — ဥပမာအားဖြင့် anti-hallucination clause တစ်ခုကို tool ရဲ့ description ထဲမှာ ထည့်လိုက်လျှင် tool ကို model က ခေါ်သည့်အချိန်မှသာ အာရုံစိုက်မည်။ ဒါကြောင့် နှိုင်းယှဉ်ကြည့်ရန် `highlight.py` lab file က comparison output ထုတ်ပေးသည် — တစ်ခုတည်းသော အလုပ်ကို သုံးမျိုးနှင့် အသီးသီး လုပ်ကြည့်ပြီး ကွာခြားချက်ကို တိုင်းတာသည်။

### ဘယ်လို အလုပ်လုပ်လဲ

ဆုံးဖြတ်ချက်ဇယား (decision table) အရ — action လိုသည် (effect) လျှင် tool၊ data ဖတ်ရမည် (read) ဆိုလျှင် resource၊ workflow ဦးတည်မှု (steering) ကို task မစခင် ထည့်ချင်လျှင် prompt ဖြစ်သည်။ Server-side object နှင့် client-side object ကလည်း ကွာသည် — server က Python object (function, return value) ကို ကိုင်သည်၊ client ဘက်မှာ protocol အရ JSON-like object ဖြစ်သည်။

### ဥပမာ

``python
# The same task exposed through all three surfaces, for comparison.

@mcp.tool
def summarize_tool(log: str) -> str:
    """Model calls this DURING the task, when it decides an action is needed."""
    return f"Summary: {log[:50]}"

@mcp.resource("logs://{name}")
def read_log(name: str) -> str:
    """Application reads this DURING the task; no model decision required."""
    return f"raw log for {name}"

@mcp.prompt
def triage_prompt(service: str) -> str:
    """User picks this BEFORE the task starts; the host renders it into the chat."""
    return f"Triage the service '{service}' step by step. Do not guess."
# Expected output: three registered surfaces; highlight.py prints a
# comparison table showing who chooses each one and when.
``

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

ဒီဇိုင်းဆုံးဖြတ်ချက်ကို မှားလိုက်လျှင် နောက်ပိုင်းမှာ prompt ထဲမှာ action ထည့်တာ၊ tool ထဲမှာ စာသားရှည် ထည့်တာ မျိုး ဖြစ်လာပြီး user ရဲ့ မျှော်လင့်ချက်နှင့် ကိုက်ညီတော့မည် မဟုတ်။ Module ရဲ့ LAB 5 (RCA Prompt Library) မှာ ဒီဇယားကို အသုံးချပြီး prompt library တစ်ခု တည်ဆောက်ရမည်။

---

## Topic 3 — Argument Injection — Signature သည် Prompt ရဲ့ Argument များ ဖြစ်လာသည်

### ဘာကို ဆိုလိုတာလဲ

`@mcp.prompt` ဖြင့် သတ်မှတ်ထားသော function ရဲ့ parameter တိုင်းသည် host က `get_prompt` ဖြင့် render လုပ်ရန် ထည့်ပေးရမည့် argument တစ်ခု ဖြစ်လာသည်။ Type hint တစ်မျိုးစီအတွက် JSON Schema တစ်ခု ထွက်လာသည် — required ဖြစ်မဖြစ်က default ရှိမရှိအပေါ် မူတည်သည်။

### ဘာကြောင့် လဲ

User က prompt တစ်ခုကို ရွေးလိုက်သောအခါ host က argument form တစ်ခု ဆွဲပြရမည်။ ဒါကို ဖြစ်စေရန် server က signature မှ `prompt.arguments` (name, required, schema) များကို ထုတ်ပေးရသည်။ Complex type များကို JSON string အဖြစ် ပို့ရမည် — list သို့ dict ကို argument အဖြစ် တိုက်ရိုက်မပေးရ။

### ဘယ်လို အလုပ်လုပ်လဲ

Required argument ကို host က မထည့်လျှင် render ချို့ယွင်းသည်၊ defaulted argument ကို မထည့်လျှင် default တန်ဖိုးနှင့် ဆက်လုပ်သည်၊ missing argument ကို `None` အဖြစ် coercion လုပ်ခြင်း၊ extra argument ကို ဖြတ်တောက်ခံရခြင်း (ignored) — ဒီလေးမျိုးကို LAB 2 နှင့် `extra_argument_tests.py` မှာ အသီးသီး တိုင်းတာသည်။ Mutable default (ဥပမာ `def f(items: list = [])`) ရဲ့ အန္တရာယ်ကိုလည်း သတိပြုရသည် — prompt တစ်ခုကို render တိုင်း default object အတူတူ နောက်ကျော်သွားနိုင်သောကြောင့် ဖြစ်သည်။ Argument ထည့်သည့်နေရာကို template ထဲမှာ တိုက်ရိုက် ဆုံးဖြတ်ရသည် — ထိပ်မှာလား၊ အလယ်မှာလဲ။

### ဥပမာ

``python
@mcp.prompt
def report_prompt(service: str, max_steps: int = 3, tags: str = "") -> str:
    """Build a structured report prompt. 'tags' is a JSON string."""
    tag_line = f"\nTags: {tags}" if tags else ""
    return (
        f"Write an incident report for '{service}'.{tag_line}\n"
        f"Keep it to at most {max_steps} numbered steps."
    )

# Host renders with all three arguments:
#   get_prompt("report_prompt", {"service": "auth", "max_steps": 5,
#                               "tags": '["prod", "sev2"]'})
# Host renders with defaults (max_steps=3, tags=""):
#   get_prompt("report_prompt", {"service": "auth"})
# Expected output: two different rendered strings, both valid;
# extra unknown arguments are ignored, missing 'service' is an error.
``

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Host ဘက်မှ မဖြစ်မနေ ကိုင်တွယ်ရမည့် error လေးမျိုးထဲက သုံးမျိုး (missing required, bad coercion, extra argument) သည် argument injection အတွင်းမှ လာသည်။ Prompt တစ်ခုကို user က လွယ်ကူစွာ ဖြည့်နိုင်ရန် argument ဒီဇိုင်းကို အစပိုင်းမှာပင် မှန်ကန်စွာ ထည့်သွင်းရမည်။

---

## Topic 4 — Multi-Turn Guidance နှင့် Anti-Hallucination Clause

### ဘာကို ဆိုလိုတာလဲ

Multi-turn guidance ဆိုသည်မှာ prompt တစ်ခုက model ကို အလှည့်များစွာ (multiple turns) ဖြတ်သနား၍ လိုက်နာစေသည့် ဦးတည်မှုဖြစ်သည် — numbered procedure (အဆင့် ၁, ၂, ၃…)၊ forced ordering (အဆင့်များကို စဉ်စီးချက်ပေးခြင်း)၊ stop conditions (ဘယ်အချိန်ရပ်မလဲ သတ်မှတ်ခြင်း) ဟူ၍ ပုံစံသုံးမျိုး ရှိသည်။ Anti-hallucination clause ကတော့ "မသိလျှင် မဖန်တီးနှင့်၊ အချက်အလက် မရှိလျှင် အသိအမှတ်ပြု၍ ပြောပါ" ဟူသည့် စာသားတစ်ခုကို prompt ရဲ့ အစိတ်အပိုင်းအဖြစ် ထည့်ခြင်းဖြစ်သည်။

### ဘာကြောင့် လဲ

Model သည် အဖြေတစ်ခု အမြဲပေးလိုသည့် သဘာဝရှိသည်။ အချက်အလက် မလုံလောက်စဉ်တွင်ပင် ဖန်တီးဖြေရှင်းမှု တစ်ခုခု ထုတ်ပေးတတ်သည်။ ဒီ clause ကို tool ရဲ့ docstring ထဲမှာ ထားလျှင် tool ကို ခေါ်သည့်အချိန်မှသာ အသက်ဝင်မည် — task တစ်ခုလုံးရဲ့ အစတွင် model ကို ဦးစားပေးရန် နောက်ကျသွားသည်။ ဒါကြောင့် prompt သည် ဒီ clause အတွက် အမှန်တကယ် သင့်လျော်သည့်နေရာဖြစ်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

Numbered procedure ကို အသုံးချလျှင် အဆင့်များကို နံပါတ်တပ်၍ ရေးသည်၊ forced ordering က အဆင့်အားလုံး မပြီးခင် နောက်တစ်ဆင့်ကို မလုပ်နှင့်ဟု တားမြစ်သည်၊ stop condition က "ဒီအချက်ကို အတည်ပြုလို့မရလျှင် ရပ်တန့်ပြီး မသိကြောင်း ဖော်ပြပါ" ဟု သတ်မှတ်သည်။ Clause မလိုက်နာလျှင် ဘာလုပ်မလဲကိုပါ စာ
