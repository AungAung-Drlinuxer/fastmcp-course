# M11 — Capstone: Enterprise DevOps / Knowledge Assistant (ရှင်းလင်းချက်)

ဒီ module က course တစ်ခုလုံးရဲ့ နောက်ဆုံးအဆင့်ပါ။ အရင် module တွေမှာ သင်ယူထားတဲ့ အရာအားလုံးကို စုပြီး production-ready ဖြစ်တဲ့ MCP server တစ်ခု တည်ဆောက်ရမှာပါ။

## ခေါင်းစဉ် ၁ — Production-ready ဆိုသည်မှာ ဘာလဲ

### ဘာကို ဆိုလိုတာလဲ

Production-ready ဆိုတာ — server ဖိုင်တစ်ခုတည်းရေးပြီးရုံ မဟုတ်ဘူးနော်။ Structure စနစ်ကျတာ၊ honesty rule လိုက်နာတာ၊ bounded output၊ guard၊ self-test စတဲ့ စံနှုန်းတွေ အားလုံးပြည့်စုံတာကို ဆိုလိုတာပါ။ Honesty rule ဆိုတာ — မလုပ်နိုင်တာကို မလုပ်နိုင်တယ်ဆိုပြီး ရိုးသားစွာ ဖော်ပြတဲ့ စည်းကမ်းလေးပါ။ Capstone server ဖြစ်တဲ့ `devops_assistant.py` မှာတော့ tool၊ resource၊ prompt ဆိုတဲ့ primitive သုံးမျိုးလုံး ပါဝင်ပါတယ်။ Primitive ဆိုတာ — MCP မှာ သုံးတဲ့ အခြေခံ ဆောက်လုပ်ဘောင်တွေပေါ့။ ဒါ့အပြင် allowlist roots ဆိုတဲ့ လုံခြုံရေးနယ်စည်းလည်း ခိုင်ခိုင်မာမာ သတ်မှတ်ထားပါတယ်။

### ဘာကြောင့် လဲ

Demo server လေးတွေက အလုပ်လုပ်တာကိုပဲ ပြပါတယ်။ ဒါပေမယ့် production မှာကတော့ သူ့နည်းသူ့ဟုတ် မဟုတ်ဘူးနော်။ ဘာလုပ်ခဲ့ဘူးလဲဆိုတာ တိတိကျကျ ဖော်ပြတာ၊ မလုပ်နိုင်တာကို ရိုးသားစွာ ပြောတာ၊ output ကို ကန့်သတ်တာ — ဒီ "hardening" အချက်တွေကသာ အမှန်တကယ် အရေးကြီးပါတယ်။ Hardening ဆိုတာ — server ကို ပိုမိုခံမာအောင် တာဝန်သိစွာ ပြင်ဆင်ထားတဲ့ လုပ်ငန်းစဉ်ပေါ့။ ဒီ module က အဲဒါတွေအားလုံးကို တစ်နေရာတည်း စုပြပေးပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

Server ဖိုင်ကို အပိုင်းလိုက် ဖွဲ့စည်းထားပါတယ်။

၁။ အပေါ်ဆုံးမှာ module docstring နဲ့ import တွေ ရေးထားပါတယ်။
၂။ Configuration paths ဆိုတဲ့ ဖိုင်လမ်းကြောင်း ဆက်တင်တွေ သတ်မှတ်ပါတယ်။
၃။ `_seed()` ဆိုတဲ့ function နဲ့ estate data အစပြု ရေးသွင်းပါတယ်။
၄။ Allowlist roots — server က ဖတ်ခွင့်ပြုတဲ့ လမ်းကြောင်းစာရင်း — သတ်မှတ်ပါတယ်။
၅။ Helper တွေနဲ့ `@mcp.tool` တွေကို အစီအစဉ်တကျ ဆက်ရေးပါတယ်။

အရေးကြီးတာက — allowlist roots စာရင်းပြင်ပက file တွေကို ဘယ်အခြေအနေမှာမှ မဖတ်ရပါဘူး။

### ဥပမာ

Code snippet မှာ production-ready server တစ်ခုရဲ့ ဖွဲ့စည်းပုံ အပိုင်းလိုက် ပေါ်နေတာ မြင်ရမှာပါ။ Structure တွေက အစီအစဉ်ကျကျ စီထားတဲ့အပြင် allowlist နယ်စည်း တင်းကျပ်မှုကို အထူး ဂရုစိုက်ကြည့်ပါနော်။
```python
# The allowlist roots define the security boundary of the server.
ALLOWED_ROOTS = {
    "hosts": "/etc/devops/hosts",
    "logs": "/var/log/devops",
    "runbooks": "/etc/devops/runbooks",
}

def _resolve(kind: str, name: str) -> Path:
    # Only allow reads inside the allowlist; reject anything else loudly.
    base = Path(ALLOWED_ROOTS[kind]).resolve()
    target = (base / name).resolve()
    if not str(target).startswith(str(base)):
        raise ValueError("path escapes allowlist")
    return target
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

LAB 1 (surface probe) မှာ server တစ်ခုကို ယုံမယ်ဆိုရင် အရင်ဆုံး ၎င်းရဲ့ surface — tool၊ resource၊ prompt စာရင်းနဲ့ နယ်စည်းတွေ — ကို ကြည့်ပြီး သေချာရပါတယ်။ Surface ဆိုတာ — server က ဘာတွေ ခေါ်လို့ရတယ်ဆိုတာ ပြသတဲ့ အပြင်ဘက် မျက်နှာစာလေး ပါ။ နယ်စည်းမဲ့ server ကို ဘယ် host မှာမှ လုံခြုံအောင် ထားလို့ မရပါဘူးနော်။

## ခေါင်းစဉ် ၂ — Honesty rule နှင့် bounded output

### ဘာကို ဆိုလိုတာလဲ

Honesty rule ဆိုတာ — metric tool တစ်ခုက တကယ် တိုင်းလို့မရရင် အတုတန်ဖိုး (fake value) မထုတ်ဘဲ `null` ကို ရိုးရိုးသားသား ပြန်ရတယ်။ Bounded output ဆိုတာ — log tool တွေက တစ်ခေါက်မှာ ကန့်သတ်ထားတဲ့ အရေအတွက်လောက်ပဲ ပြန်ရတယ်။ ဆေးရုံမှာ တိုင်းလို့မရတဲ့ အချက်အလက်ကို လုပ်ကြံမပြောဘဲ "မသိဘူး" လို့ ပြောတာနဲ့ တူတာပေါ့။

### ဘာကြောင့် လဲ

`system_metrics` လို tool က Python standard library ကနေ တကယ့်တန်ဖိုးတွေပဲ တိုင်းရတယ်။ တိုင်းလို့မရတဲ့ event တစ်ခုကို လုပ်ကြံပြောတာထက် `null` ပြန်တာက ပိုယုံရတယ်။ မဟုတ်ရင် client က မမှန်တဲ့ data ကို အခြေခံပြီး ဆုံးဖြတ်ချက်လုပ်သွားမှာ မို့လို့ပါ။ Log ကို အကန့်အသတ်မဲ့ ထုတ်ပေးရင် client ရဲ့ token အားလုံး ကုန်သွားပြီး ဘာမှ ဆက်လုပ်လို့ မရတော့ဘူး။

### ဘယ်လို အလုပ်လုပ်လဲ

`read_log` tool က filter ကို tool boundary အတွင်းမှာ လုပ်တယ်။ ဖိုင်တစ်ခုလုံးကို client ဘက် မပို့ဘဲ server ဘက်မှာပဲ စစ်ပြီး ကန့်သတ်အရေအတွက်ပဲ ပြန်တယ်။ ပြောရရင် —

၁။ client က `read_log` ကို ခေါ်တယ်။
၂။ server က log ဖိုင်ကို ဖွင့်တယ်။
၃။ server ဘက်မှာပဲ filter နဲ့ ကန့်သတ်တယ်။
၄။ ကျန်တဲ့ အရေအတွက်လောက်ပဲ client ကို ပြန်ပို့တယ်။

LAB 3 (log forensics) မှာတော့ "အဆိုးဆုံး event" ကို ရှာတာထက် "ပထမဆုံး anomalous event" ကို ရှာတာကို လေ့ကျင့်ပါတယ်နော်။

### ဥပမာ

ဒီ snippet မှာ metric tool တစ်ခုက တိုင်းလို့မရတဲ့အခါ `null` ပြန်တဲ့ပုံနဲ့ log tool တစ်ခုက ကန့်သတ်ပြန်တဲ့ပုံကို ပြထားပါတယ်။ Tool က fake value ထုတ်သလား၊ output က အကန့်အသတ်ရှိသလား ဆိုတာကို သေချာကြည့်ပါ။
```python
@mcp.tool()
def system_metrics(host: str) -> dict:
    # Read real values only from the standard library; no invention.
    cpu = _read_cpu_percent_if_available(host)
    if cpu is None:
        # Honesty rule: report null rather than a fabricated number.
        return {"host": host, "cpu_percent": None, "note": "not measurable"}
    return {"host": host, "cpu_percent": cpu}
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

LAB 2 (metrics audit) မှာ declared၊ measured နဲ့ honest null သုံးခုကို နှိုင်းယှဉ်ပြီး စစ်ရပါတယ်။ Automation အပေါ် အခြေခံထားတဲ့ DevOps စနစ်မှာ တန်ဖိုးတခု မှားနေရင် ဆုံးဖြတ်ချက်တွေ အမှားလိုက် ထွက်လာတယ်။ ဒါက production မှာ downtime ရှည်တာ၊ အချိန်ကုန်တာကို ဖန်တီးပါတယ်။

## ခေါင်းစဉ် ၃ — Protected-service guard နှင့် elicitation

### ဘာကို ဆိုလိုတာလဲ

`restart_service` tool က guard နှစ်လမ်း ပါတယ် — ဆိုလိုတာက အန္တရာယ်မရှိတဲ့ service ဆိုရင် တိုက်ရိုက် လုပ်ပေးပြီး၊ protected service ဆိုရင် elicitation နဲ့ အတည်ပြုချက် တောင်းပါတယ်။ Elicitation ဆိုတာ — server က အသုံးပြုသူဆီ မေးခွန်းထုတ်ပြီး အတည်ပြုချက် ယူတဲ့ နည်းလေးပါ။ ဒုတိယလမ်းမှာ server က service ကို restart မလုပ်ဘဲ ဘာမှ မလုပ်ခဲ့ဘူးဆိုတာ အဖြေပြန်ပါတယ်။

### ဘာကြောင့် လဲ

Production မှာ ဒိုမိန်း စီမံခန့်ခွဲမှု (governance) အမျိုးအစား service တချို့ကို အလိုအလျောက် restart လုပ်ရင် အန္တရာယ် ရှိပါတယ်။ အဲဒါမို့ လူတယောက်ရဲ့ အတည်ပြုချက် မရှိဘဲ လုပ်ရင် data ပျက်ဆီးနိုင်ပြီး downtime ဖြစ်နိုင်ပါတယ်။ MCP ရဲ့ elicitation capability က ဒီအတည်ပြုချက် တောင်းဖို့ စံနည်းစနစ်တခု ပေးပါတယ်။ LAB 4 မှာ client အပြုအမူလေးမျိုးကို တိုင်းတာ စမ်းသပ်ရပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Client က `restart_service` ကို ခေါ်ပါတယ်။
၂။ Server က service က protected လား စစ်ပါတယ်။
၃။ Protected မဟုတ်ရင် တန်း restart လုပ်ပြီး အဖြေပြန်ပါတယ်။
၄။ Protected ဖြစ်ရင် elicitation နဲ့ အသုံးပြုသူဆီ အတည်ပြုချက် တောင်းပါတယ်။
၅။ Client က `mode="legacy"` နဲ့ တုံ့ပြန်နိုင်ပါတယ်။
၆။ အတည်ပြုချက်ရရင် restart လုပ်ပြီး၊ ငြင်းရင် ဘာမှ မလုပ်ဘဲ ရှင်းရှင်းလင်းလင်း ဖော်ပြပါတယ်။

Guard ရဲ့ body က "ငါ ဘာလုပ်ခဲ့လဲ၊ ဘာမလုပ်ခဲ့လဲ" ဆိုတာကို အတိအကျ ပြောရပါတယ်။

### ဥပမာ

ဒီ snippet မှာ protected service တခုကို restart လုပ်ဖို့ ခေါ်ပြီး elicitation အတည်ပြုချက် တောင်းတဲ့ ပုံစံကို ပြထားပါတယ်။ အတည်ပြုချက် ငြင်းတဲ့အခါ server က ဘာမှ မလုပ်ဘူးဆိုတဲ့ အဖြေကို ဂရုစိုက်ကြည့်ပါ။
```python
@mcp.tool()
def restart_service(host: str, service: str) -> dict:
    # Guard: two paths — harmless services vs protected services.
    if service in PROTECTED_SERVICES:
        result = ctx.elicit(
            f"Restart protected service '{service}' on '{host}'?",
            mode="legacy",
        )
        if not result.get("confirmed"):
            # State clearly what was NOT done — no silent failure.
            return {"restarted": False, "service": service,
                    "reason": "user declined confirmation"}
    _do_restart(host, service)
    return {"restarted": True, "service": service}
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

LAB 7 (estate resource guard) မှာ resource template အသစ်နဲ့ guard အသစ်ကို ကိုယ်တိုင်ရေးရပါတယ်။ M10 (security) ကနေ သင်ယူခဲ့တဲ့ အခြေခံမူတွေကို capstone ထဲ လက်တွေ့ရေးပြီး ပေါင်းစပ်ရတာပါ။ ဒါမှ စာထဲအသိတွေ အလုပ်ထဲ ကူးပြောင်းသွားတယ်။

## ခေါင်းစဉ် ၄ — Resource နှင့် Prompt

### ဘာကို ဆိုလိုတာလဲ

Resource ဆိုတာ — ဖတ်ဖို့ အချက်အလက်တွေပါ။ `config://{host}` နဲ့ `runbook://{name}` လို URI template တွေနဲ့ ချိတ်ဆက်ရတယ်။ Prompt ဆိုတာ — `rca_error_log` နဲ့ `capacity_review` လို လမ်းညွှန်ချက် (guidance) ပါ။ Schema တော့ မဟုတ်ဘူးနော်။

### ဘာကြောင့် လဲ

Tool က လုပ်ဆောင်ချက်၊ resource က ဖတ်ရမယ့် အချက်အလက်၊ prompt က စဉ်းစားပုံ လမ်းညွှန်ပါ။ သုံးမျိုးလုံး ခွဲခြားတတ်ဖို့ လိုတယ်။ Prompt တစ်ခုရေးပြီးရင် မေးရမယ့် မေးခွန်း ၃ ခု ရှိတယ် — လမ်းညွှန်ပေးလို့လား၊ token ကုန်ကျမှု သင့်တင့်လား၊ မသိစိတ်ကူး (hallucination) ကို တားဆီးနိုင်လား။ `rca_error_log` မှာ forced step order နဲ့ anti-hallucination clause ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Resource အတွက် URI template ကို သတ်မှတ်တယ်။
၂။ Prompt ထဲမှာ လမ်းညွှန်ချက်တွေကို ရေးတယ်။
၃။ literal `{host}` ကို argument အဖြစ် သတ်မှတ်ဖို့ မမေ့နဲ့နော် — ဒါက တကယ် ဖြစ်တတ်တဲ့ bug ပါ။
၄။ Prompt design pattern ၇ မျိုးကို LAB 8 (incident review prompt) မှာ သုံးတယ်။
၅။ ကိုယ်ပိုင် prompt တစ်ခု ရေးပြီး စစ်ဆေးတယ်။

### ဥပမာ

နောက်ပိုင်းမှာ ပေါ်လာမယ့် snippet က resource နဲ့ prompt ကို ဘယ်လို ရေးရမလဲ ပြထားပါတယ်။ literal `{host}` ကို argument အဖြစ် သတ်မှတ်ထားပုံကို သေချာကြည့်ပါနော်။
```python
@mcp.prompt()
def rca_error_log(host: str) -> str:
    # A prompt is guidance, not a schema; force the step order.
    return f"""You are doing root-cause analysis for host '{host}'.
Steps (in order, do not skip):
1. Read the config resource for '{host}'.
2. Call the log tool to find the first anomalous event.
3. Propose one fix, citing only evidence you actually read.
If a step cannot be completed, say so — do not guess."""
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Client (ဥပမာ — Cline သို့မဟုတ် LangGraph) သည် prompt ကို လမ်းညွှန်အဖြစ်သာ ယူရမည်။ Token ကုန်ကျမှုနှင့် iteration စဉ်းစားခြင်းသည် ရေရှည်စီမံခန့်ခွဲမှုတွင် အရေးကြီးသော ကျွမ်းကျင်မှုများဖြစ်သည်။

## ခေါင်းစဉ် ၅ — Self-test နှင့် autonomous client

### ဘာကို ဆိုလိုတာလဲ

Self-test ဆိုသည်မှာ `main()` အတွင်းရှိ ညွှန်ကြားချက်တစ်ခုတည်းဖြင့် server တစ်ခုလုံး အလုပ်လုပ်ကြောင်း သက်သေပြနိုင်သော စနစ်ဖြစ်သည်။ `my_self_test.py` နှင့် `health_check.py` တွင် အကောင်အထည်ဖော်ထားသည်။ LAB 5 (autonomous client) တွင် scripted agent နှင့် LangGraph ဟူ၍ နှစ်ပိုင်းပါဝင်သည်။ Scripted agent ဆိုသည်မှာ client က ချဉ်းကပ်မှု အဆင့်ဆင့်ကို ကြိုတင်ရေးထားသော script အတိုင်း လိုက်နာခြင်းဖြစ်ပြီး၊ LangGraph ဆိုသည်မှာ graph ဖြင့် agent ၏ စဉ်းစားမှု အခြေအနေများကို စီမံခန့်ခွဲခြင်းဖြစ်သည်။

### ဘာကြောင့် လဲ

Grader ရှာမည့် အရာ ၈ ခုကို ကျော်လွန်ရန် self-test သည် အသုံးဝင်ဆုံးဖြစ်သည်။ Linux VM ပေါ်တွင်မူ အချို့တန်ဖိုးများ မတူညီစွာ ပြန်နိုင်သည်ကိုလည်း နားလည်ရမည်။ ဥပမာအားဖြင့် Windows ပေါ်တွင် `\\` ဖြင့် စတင်သော path တစ်ခုသည် Linux ပေါ်တွင် အလုပ်မလုပ်နိုင်ပါ။ Self-test သည် health check အဖြစ်လည်း အသုံးပြုနိုင်သည်။ Server ကို deploy ပြုလုပ်ပြီးတိုင်း တစ်ကြိမ် run ကြည့်ခြင်းဖြင့် tool များ၊ resource များနှင့် prompt များ အားလုံး မှန်ကန်စွာ တုံ့ပြန်နေခြင်းရှိမရှိ အလျင်အမြန် စစ်ဆေးနိုင်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

Autonomy ၏ anti-pattern ၆ မျိုး (ဥပမာ — confirmation မဲ့ လုပ်ဆောင်ခြင်း၊ bounded output ကို လျစ်လျူရှုခြင်း) ကို ရှောင်ပြီး၊ client ဘက်မှ server ၏ surface အားလုံးကို တစ်ပြားဝင် မေးဖို့ script ရေးရသည်။ Client ၏ တာဝန်စာရင်းတွင် — confirm တောင်းခြင်း၊ null ကို လက်ခံခြင်း၊ output ကို ကန့်သတ်ခြင်းနှင့် error များကို ကျေညက်စွာ ကိုင်တွယ်ခြင်းတို့ ပါဝင်သည်။ Self-test script တစ်ခု ရေးရာတွင် အောက်ပါ အဆင့်များကို လိုက်နာရမည် —

```python
# my_self_test.py -- one-shot self-test for the capstone server
import asyncio
from my_server import mcp

async def run_checks():
    # List the server surface first: tools, resources, prompts
    tools = await mcp.list_tools()
    resources = await mcp.list_resources()
    prompts = await mcp.list_prompts()
    print(f"tools={len(tools)} resources={len(resources)} prompts={len(prompts)}")

    # Exercise one representative tool and verify a non-null result
    result = await mcp.call_tool("get_flight_status", {"flight_id": "MM-101"})
    assert result is not None, "tool returned None"
    print("get_flight_status OK")

    # Keep output bounded so logs stay readable
    summary = str(result)[:200]
    print(f"result preview: {summary}")

if __name__ == "__main__":
    asyncio.run(run_checks())
    print("SELF-TEST PASSED")
```
Scripted agent ဘက်မှာ client က tool တစ်ခုချင်းစီကို အစီအစဉ်တကျ ခေါ်ပြီး ရလဒ်တစ်ခုချင်းစီ စစ်ရတယ်။ LangGraph ဘက်မှာတော့ node တစ်ခုချင်းစီက "decide → act → verify" ဆိုတဲ့ သုံးအဆင့်ကို လိုက်နာတယ်။ decide node ဆိုတာ — နောက်ထပ် ဘယ် tool ကို ခေါ်မလဲ ရွေးပေးတဲ့ အဆင့်ပါ။ act node က ရွေးထားတဲ့ tool ကို ခေါ်ပေးတယ်။ verify node က ရလဒ်က သတ်မှတ်ထားတဲ့ ကန့်သတ်ဘောင်အတွင်း ပါမပါ စစ်ပေးတယ်။ Confirmation လိုအပ်တဲ့ action တွေအတွက် `elicitation` ယန္တရားကို သုံးပါတယ် — ဆိုလိုတာက လူဆီက အတည်ပြုချက် တောင်းတဲ့ စနစ်လေးပါ။ ရလဒ် ရှည်လွန်းရင်တော့ bounded output စည်းမျဉ်းကို တင်းကျပ်စွာ လိုက်နာရတယ်။ ဒီလိုဆို autonomous client က လုံခြုံပြီး ခန့်မှန်းလို့ရတဲ့ အလုပ်လုပ်နိုင်တယ်နော်။

## အနှစ်ချုပ်

- Self-test ဆိုတာ — `main()` ထဲမှာ ညွှန်ကြားချက် တစ်ခုတည်းနဲ့ server တစ်ခုလုံးကို စစ်လို့ရတဲ့ အမြန်နည်းလမ်းပါ။ health check အဖြစ်လည်း သုံးလို့ရတယ်။
- Linux VM ပေါ်မှာ path နဲ့ တန်ဖိုးတွေ ကွဲနိုင်လို့ platform အလိုက် ခြားနားချက်တွေကို သတိထားပြီး စမ်းရတယ်။
- Autonomy ရဲ့ anti-pattern ဆိုတာ — autonomous client မှာ ရှောင်သင့်တဲ့ မှားယွင်းပုံစံ ၆ မျိုးပါ။ ဒီတွေကို ရှောင်ပြီး confirm တောင်းခြင်း၊ null စစ်ဆေးခြင်း၊ bounded output တွေကို client ရဲ့ တာဝန်အဖြစ် ထည့်ရတယ်။
- LAB 5 ရဲ့ scripted agent နဲ့ LangGraph နှစ်ပိုင်းကို ပေါင်းလိုက်ရင် decide → act → verify နဲ့ ယုံကြည်စိတ်ချရတဲ့ autonomous client တစ်ခု တည်ဆောက်လို့ရတယ်။