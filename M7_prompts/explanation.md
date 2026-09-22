# M7 — Workflow Steering Prompts (`@mcp.prompt`) — explanation.md

## မိတ်ဆက်

ဒီ module မှာ MCP server ရဲ့ ပစ္စည်းသုံးမျိုးထဲက တတိယမြောက်ဖြစ်တဲ့ **prompt** အကြောင်းကို လေ့လာပါမယ်။ Tool က model က ခေါ်တာပါ။ Resource က application က ဖတ်တာပါ။ Prompt ကတော့ **user က task မစခင် host ကနေ ရွေးတဲ့ template** ပါ။ Duration ၂ နာရီ၊ Phase 2 — MCP Core Surfaces ဖြစ်ပါတယ်။

---

## Topic 1 — Prompt ဆိုတာ ဘာလဲ

### ဘာကို ဆိုလိုတာလဲ

Prompt ဆိုတာ — server က ကြိုပြီး ရေးထားတဲ့ **စာသား template** တစ်ခုပါ။ Host (ဆိုလိုတာ server ကို ခေါ်တဲ့ client အလွှာ) က ဒီ template တွေကို menu လို ပြပါတယ်။ ရနိုင်တဲ့ function တစ်ခုကို `@mcp.prompt` decorator နဲ့ အမှတ်အသားပြုပြီး argument တွေ လက်ခံပါတယ်။

### ဘာကြောင့် လဲ

တစ်နေ့တာလုံး တူတဲ့ အလုပ်မျိုးကို model ချက်ချင်း တောင်းရတိုင်း user တိုင်းရဲ့ စာသား မတူကြပါ။ ရလဒ်ကလည်း တစ်ခါက structure ကောင်းပေမယ့် တစ်ခါက step တွေ ကျော်လျက် အဖြေပေးတတ်ပါတယ်။ Prompt က ဒီ "ဘယ်လိုမေးသလဲ" ကွာခြားမှုကို ဖျက်ပြီး **consistency** — ဆိုလိုတာ အခါတိုင်း တူညီတဲ့ ရလဒ် — ကို အာမခံပေးပါတယ်။ ဒါကြောင့် prompt ရဲ့ တန်ဖိုးအားလုံးဟာ consistency ပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Server ဘက်မှာ Python function တစ်ခုကို `@mcp.prompt` (bare) ဒါမှမဟုတ် `@mcp.prompt("name")` (named) နဲ့ သတ်မှတ်ပါတယ်။
၂။ Docstring ရေးတဲ့ စာသားက prompt ရဲ့ description ဖြစ်သွားပါတယ်။
၃။ Function signature မှာရှိတဲ့ parameter တိုင်းက prompt ရဲ့ argument ဖြစ်လာပါတယ်။
၄။ Host က `list_prompts()` နဲ့ စာရင်းယူပါတယ်။
၅။ User ရွေးတဲ့အခါ host က `get_prompt(name, arguments)` နဲ့ render လုပ်ပါတယ်။
၆။ Render ထွက်လာတဲ့ message list ကို host က conversation ရဲ့ အစမှာ ထည့်ပါတယ်။

Server က declare တာပါ၊ host က surface လုပ်တာပါ — ဒါက ကွဲပြားခြင်းနှစ်ခုပါ။ Prompt မရှိရင် server ပျက်တာ မဟုတ်ပါ။ menu တစ်ခု မမြင်ရတော့တာပါ။

### ဥပမာ

ဒီ snippet မှာ `@mcp.prompt` နဲ့ function တစ်ခု သတ်မှတ်ပုံနဲ့ သူ့ docstring နဲ့ parameter တွေ ဘယ်လို prompt metadata ဖြစ်သွားလဲ ကို ပြပါမယ်။ Docstring ရေးတဲ့ စာနဲ့ function signature ကို အထဲအထဲ ကြည့်ထားပါနော်။

```python
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
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

ပထမဆုံး "LAB 1 — Prompt Anatomy" ကို လုပ်ရင် prompt တစ်ခုရဲ့ အစိတ်အပိုင်းတွေဖြစ်တဲ့ name, description, arguments, return value တို့ကို သီးသန့် မြင်ရတယ်။ Prompt ဆိုတာ — model ကို လမ်းပြပေးတဲ့ သီချင်းစာရွက်လိုမျိုးပါ။ ဒီမူတွေနားမလည်ရင် နောက်ပိုင်း topic တွေဖြစ်တဲ့ argument injection, multi-turn guidance, host contract တွေကို လိုက်လို့ မရတော့ပါဘူး။ အခြေခံမှတစ်ဆင့် အပေါ်ကို တက်ရတာပါ။

---

## Topic 2 — Tool vs Resource vs Prompt — ဘယ်သူက ရွေးသလဲ

### ဘာကို ဆိုလိုတာလဲ

သုံးမျိုးလုံးကို server က declare လုပ်တာ တူပေမယ့် **ဘယ်သူက ရွေးလဲ** နဲ့ **ဘယ်အချိန်မှာ ရွေးလဲ** က မတူပါဘူး။ Tool ဆိုတာ — model က task လုပ်နေစဉ် ခေါ်သုံးတဲ့ လုပ်ဆောင်ချက်၊ resource ဆိုတာ — application က ဖတ်ယူတဲ့ data၊ prompt ဆိုတာ — task မစခင် user က ရွေးတဲ့ လမ်းညွှန်ပါ။ ရွေးသူက ဒီဇိုင်းရဲ့ အဓိက ဆုံးဖြတ်ချက်ပါ။

### ဘာကြောင့် လဲ

ရွေးမှားရင် အလုပ်လုပ်ပုံ တစ်ခုလုံးကို ပြောင်းသွားတယ်။ ဥပမာ — anti-hallucination clause (မမှန်တာ မပြောဆိုရ ဆိုတဲ့ စည်းကမ်း) ကို tool ရဲ့ description ထဲ ထည့်လိုက်ရင် model က tool ကို ခေါ်တဲ့အခါမှသာ အာရုံစိုက်တယ်။ ဒီကွာခြားချက်ကို တိုက်ရိုက်မြင်ဖို့ `highlight.py` lab file က comparison output ထုတ်ပေးတယ်။ အလုပ်တစ်ခုတည်းကို နည်းလမ်းသုံးမျိုးနဲ့ လုပ်ကြည့်ပြီး ခြားနားချက်ကို တိုင်းတာပေးတာပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ အရင်ဆုံး — လိုချင်တာက action (effect) လား ဆိုတာ မေးပါ။ ဖြစ်ရင် tool ပါ။
၂။ data ဖတ်ရမယ် (read) ဆိုရင် resource ပါ။
၃။ workflow ဦးတည်မှု (steering) ကို task မစခင် ထည့်ချင်ရင် prompt ပါ။
၄။ Server ဘက်မှာ ကိုင်တာက Python object (function, return value) ဖြစ်တယ်။
၅။ Client ဘက်မှာ protocol အရ JSON-like object အဖြစ် ရောက်လာတယ်။

### ဥပမာ

ဒီ snippet မှာ အလုပ်တစ်ခုတည်းကို tool, resource, prompt သုံးမျိုးနဲ့ ရေးပြထားတာကို မြင်ရမယ်။ ရွေးသူက ဘယ်သူဖြစ်လဲ၊ ဘယ်အချိန် ခေါ်လဲ ဆိုတာကို သတိပြုကြည့်ပါ။
```python
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
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

ဒီဇိုင်းကို မှားလိုက်ရင် နောက်ပိုင်းမှာ prompt ထဲမှာ action ထည့်တာ၊ tool ထဲမှာ စာသားရှည် ထည့်တာတွေ ဖြစ်လာပါတယ်။ အဲဒါဆို user ရဲ့ မျှော်လင့်ချက်နဲ့ မကိုက်တော့ပါဘူး။ Module ရဲ့ LAB 5 (RCA Prompt Library) မှာ ဒီဇယားကို သုံးပြီး prompt library တစ်ခု တည်ဆောက်ရမှာ ဖြစ်ပါတယ်။

---

## Topic 3 — Argument Injection — Signature သည် Prompt ရဲ့ Argument များ ဖြစ်လာသည်

### ဘာကို ဆိုလိုတာလဲ

`@mcp.prompt` နဲ့ သတ်မှတ်ထားတဲ့ function ရဲ့ parameter တိုင်းက prompt ရဲ့ argument တစ်ခု ဖြစ်လာပါတယ်။ Argument ဆိုတာ — prompt ထဲ အလိုက်သင့် ထည့်ပေးရမယ့် အချက်အလက်လေးပါ။ Host က `get_prompt` နဲ့ render လုပ်တဲ့အခါ ဒီ argument တွေကို ထည့်ပေးရပါတယ်။ Type hint တစ်မျိုးစီအတွက် JSON Schema တစ်ခု ထွက်လာပါတယ်။ Required ဖြစ်မဖြစ်က default ရှိမရှိပေါ်မူတည်ပါတယ်။

### ဘာကြောင့် လဲ

User က prompt တစ်ခုကို ရွေးလိုက်ရင် host က argument form တစ်ခု ဆွဲပြပေးရပါတယ်။ အဲဒါမျိုး ဖြစ်ဖို့ server က signature ကနေ `prompt.arguments` (name, required, schema) တွေကို ထုတ်ပေးရပါတယ်။ ဒါမှ form က အလိုအလျောက် ဆွဲနိုင်မှာ ဖြစ်ပါတယ်။ Complex type တွေကိုတော့ JSON string အဖြစ်ပဲ ပို့ရပါတယ်။ list ဒါမှမဟုတ် dict ကို argument အဖြစ် တိုက်ရိုက်မပေးရပါဘူး။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Host က required argument ကို မထည့်ရင် render ချို့ယွင်းသွားပါတယ်။

၂။ Default ရှိတဲ့ argument ကို မထည့်ရင် default တန်ဖိုးနဲ့ ဆက်လုပ်ပါတယ်။

၃။ Missing argument ကို `None` အဖြစ် coercion လုပ်ပါတယ်။

၄။ Extra argument ကိုတော့ ဖြတ်တောက်ခံရပါတယ် — ignored ဖြစ်သွားတာပါပဲ။

၅။ ဒီလေးမျိုးကို LAB 2 နဲ့ `extra_argument_tests.py` မှာ အသီးသီး တိုင်းတာကြည့်ရမှာ ဖြစ်ပါတယ်။

၆။ Mutable default (ဥပမာ `def f(items: list = [])`) ကိုတော့ သတိထားပါ — render တိုင်း default object အတူတူ နောက်ကျော်သွားနိုင်လို့ပါ။

Argument ထည့်တဲ့နေရာကို template ထဲမှာ တိုက်ရိုက် ဆုံးဖြတ်ရပါတယ် — ထိပ်မှာလား၊ အလယ်မှာလား ဆိုတာပါ။

### ဥပမာ
```python
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
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Host ဘက်မှ မဖြစ်မနေ ဖြေရှင်းရမယ့် error လေးမျိုး ရှိပါတယ်။ အဲဒီထဲက သုံးမျိုး — missing required, bad coercion, extra argument — က argument injection ကနေ လာတာပါ။ ဒါတွေက prompt ထဲမှာ အစပိုင်းကနေ မှန်မှန် ထည့်ပေးရင် ရှောင်လို့ရတယ်။ မှန်အောင် မထည့်ရင် debug အချိန် ကြာပြီး user တွေလည်း tool ကို မှားယွင်းစွာ သုံးမိတတ်ပါတယ်။

---

## Topic 4 — Multi-Turn Guidance နှင့် Anti-Hallucination Clause

### ဘာကို ဆိုလိုတာလဲ

Multi-turn guidance ဆိုတာ — prompt တစ်ခုက model ကို အလှည့်များစွာ ဖြတ်သန်းပြီး လိုက်နာစေတဲ့ ဦးတည်မှု ဖြစ်ပါတယ်။ သူ့ထဲမှာ ပုံစံ သုံးမျိုး ပါတယ် — numbered procedure (အဆင့် ၁, ၂, ၃… နဲ့ ရေးတာ)၊ forced ordering (အဆင့်တွေကို အစဉ်လိုက် လုပ်ခိုင်းတာ)၊ stop conditions (ဘယ်အချိန် ရပ်မလဲ သတ်မှတ်တာ) ပါ။ Anti-hallucination clause ကတော့ "မသိရင် မဖန်တီးနဲ့၊ အချက်အလက် မရှိရင် မရှိဘူးလို့ ပြော" ဆိုတဲ့ စာသားကို prompt ထဲ ထည့်တာ ဖြစ်ပါတယ်။ လူသူမသိတဲ့အချက်ကို မဖန်တီးပြောတာကို hallucination လို့ ခေါ်ပါတယ်။

### ဘာကြောင့် လဲ

Model က အဖြေတစ်ခု အမြဲပေးချင်တဲ့ သဘာဝ ရှိပါတယ်။ ဒါကြောင့် အချက်အလက် မလုံလောက်ရင်တောင် ခန့်မှန်းဖြေရှင်းမှုတစ်ခု ထုတ်တတ်ပါတယ်။ ဒီ clause ကို tool ရဲ့ docstring ထဲမှာ ထားရင် tool ခေါ်တဲ့အချိန်မှာပဲ အသက်ဝင်ပါတယ်။ Task တစ်ခုလုံးရဲ့ အစမှာ အသက်မဝင်ဘူး ဆိုတာက နောက်ကျသွားတာပါ။ ဒါကြောင့် ဒီ clause အတွက် prompt က အမှန်တကယ် သင့်တဲ့နေရာပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Numbered procedure နဲ့ အဆင့်တွေကို နံပါတ်တပ်ပြီး ရေးပါ။
၂။ Forced ordering နဲ့ "အဆင့်အားလုံး မပြီးခင် နောက်ဆင့်ကို မလုပ်နဲ့" လို့ တားပါ။
၃။ Stop condition နဲ့ "ဒီအချက်ကို အတည်ပြုလို့မရရင် ရပ်ပြီး မသိကြောင်း ပြောပါ" လို့ သတ်မှတ်ပါ။
၄။ Clause မလိုက်နာရင် ဘာလုပ်မလဲကိုပါ အပြည့်အစုံ ရေးပါ — ဥပမာ "အချက်အလက် မတွေ့ရင် ခန့်မှန်းဖြေ မပေးနဲ့၊ မတွေ့ကြောင်းပဲ ပြောပါ"။
၅။ Prompt တစ်ခုကို system prompt အဖြစ် server အဆင့်မှာ သတ်မှတ်ရင် ဘယ် client ချိတ်ဆက်လာလာ တညီတည်း အသက်ဝင်ပါတယ်။
```python
from fastmcp import FastMCP

mcp = FastMCP(
    name="research-assistant",
    instructions=(
        "Follow this numbered procedure for every request:\n"
        "1. Identify what the user is asking for.\n"
        "2. Gather facts using the available tools before answering.\n"
        "3. Only answer using information returned by tools.\n"
        "4. If a tool returns no relevant data, say you do not know.\n\n"
        "Do not skip steps. Do not move to the next step until the "
        "current step is complete.\n\n"
        "ANTI-HALLUCINATION CLAUSE: Never invent facts, numbers, "
        "names, or citations. If the required information is missing, "
        "explicitly state that you could not find it instead of "
        "guessing."
    ),
)

@mcp.tool()
def lookup_paper(title: str) -> dict:
    """Look up a paper record by exact title. Returns an empty
    result if no match is found."""
    # Simulated database lookup
    database = {
        "attention is all you need": {"year": 2017, "authors": 8}
    }
    key = title.strip().lower()
    if key in database:
        return {"found": True, "data": database[key]}
    return {"found": False, "data": None}
```
အထက်ပါ ဥပမာမှာ `instructions` parameter ထဲမှာ အဆင့်လေးဆင့်ပါတဲ့ numbered procedure လေးမျိုးပေါင်းတာတွေ၊ forced ordering (ဆိုတာ — အဆင့်တစ်ခု မပြီးခင် နောက်တစ်ခုကို မလုပ်ရဘူးလို့ တားထားတာ) နဲ့ anti-hallucination clause (ဆိုတာ — model အလိုလို မှားယွင်းခန့်မှန်းတာကို တားထားတဲ့ စာကြောင်း) ကို တစ်ပေါင်းတည်း သတ်မှတ်ထားတာ တွေ့ရပါတယ်။ Tool ဘက်က `lookup_paper` ကလည်း ရှာမတွေ့ရင် `{"found": False, "data": None}` ဆိုပြီး တိကျတဲ့ အဖြေပြန်ပေးပါတယ်။ ဒါကြောင့် model လည်း "မတွေ့ဘူး" လို့ပြောဖို့ လုံလောက်တဲ့ အချက်အလက် ရှိသွားပါတယ်။ ခန့်မှန်းပြီး မှားယွင်းတာ ဖြစ်စရာ အကြောင်းရင်း မရှိတော့ပါဘူး။

### သတိထားစရာများ

Clause ရေးထားပေမယ့် model အားလုံးက ၁၀၀ ရာခိုင်နှုန်း လိုက်နာမှာ မဟုတ်ပါဘူး။ ဒါကြောင့် အရေးကြီးတဲ့ အချက်အလက်တွေအတွက် tool ဘက်ကလည်း ခန့်မှန်းချက် ထုတ်ပေးလို့ မရအောင် ကြိုတင်ပြင်ဆင်ထားသင့်ပါတယ်။ တစ်ဖက်မှာလည်း stop condition (ဆိုတာ — ဘယ်အချိန်မှာ ရပ်ရမလဲ ဆိုတာကို သတ်မှတ်တဲ့ စည်းမျဉ်း) ကို ပိုတင်းကျပ်လွန်းရင် model က "မသိဘူး" လို့ပဲ ပြောတတ်သွားပြီး တကယ်ရှိသင့်တဲ့ အဖြေကိုပါ မပေးတော့ပါဘူး။ ဒီနှစ်ခုကြားထဲ အလယ်အလတ် ချမှတ်နိုင်ဖို့ clause ကို တိုတောင်းပြီး တိကျတဲ့ စာလုံးတွေနဲ့ပဲ ရေးတာ အကောင်းဆုံးပါ။

## အနှစ်ချုပ်

- **System prompt** ကို MCP server တစ်ခုလုံးရဲ့ အမူအကျင့်ကို သတ်မှတ်ပေးတဲ့ အခြေခံကျတဲ့ နေရာပါ။ FastMCP မှာတော့ `instructions` parameter နဲ့ သတ်မှတ်ပါတယ်။
- Prompt ရေးတဲ့အခါ role၊ context၊ constraints နဲ့ output format ဆိုတဲ့ အစိတ်အပိုင်းလေးမျိုး ပါစေရင် model ရဲ့ တုံ့ပြန်မှုကို ပိုထိန်းချုပ်နိုင်ပါတယ်။
- Few-shot examples (ဆိုတာ — နမူနာအဖြေတွေ ပြပြီး အတုခိုးစေတဲ့နည်း) ထည့်ရင် model ကို လိုချင်တဲ့ ပုံစံအတိအကျ အတုခိုးစေပြီး format တူညီမှုလည်း သိသိသာသာ တိုးပါတယ်။
- Multi-turn guidance (numbered procedure, forced ordering, stop conditions) နဲ့ anti-hallucination clause ကို တွဲသုံးရင် မှားယွင်းခန့်မှန်းမှု (hallucination) ကို လျှော့ချနိုင်ပါတယ်။