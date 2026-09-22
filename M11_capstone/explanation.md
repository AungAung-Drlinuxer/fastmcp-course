# M11 — Capstone: Enterprise DevOps / Knowledge Assistant (ရှင်းလင်းချက်)

ဒီ module သည် course တစ်ခုလုံး၏ နောက်ဆုံးအဆင့်ဖြစ်ပြီး၊ ယခင် module များမှ သင်ယူထားသည့် အရာအားလုံးကို စုစည်းပြီး production-ready ဖြစ်သော MCP server တစ်ခုအဖြစ် တည်ဆောက်ရမည်ဖြစ်သည်။

## ခေါင်းစဉ် ၁ — Production-ready ဆိုသည်မှာ ဘာလဲ

### ဘာကို ဆိုလိုတာလဲ

ဒီ course တွင် "production-ready" ဆိုသည်မှာ server ဖိုင်တစ်ခုသာမက — structure စနစ်ကျခြင်း၊ honesty rule လိုက်နာခြင်း၊ bounded output၊ guard၊ self-test စသည့် စံနှုန်းများအားလုံး ပြည့်စုံခြင်းကို ဆိုလိုသည်။ Capstone server ဖြစ်သော `devops_assistant.py` တွင် tool၊ resource၊ prompt ဟူသော primitive သုံးမျိုးလုံးပါဝင်ပြီး၊ လုံခြုံရေးနယ်စည်း (allowlist roots) ကို ခိုင်ခိုင်မာမာ သတ်မှတ်ထားသည်။

### ဘာကြောင့် လဲ

အလွယ်တကူ ရေးထားသော demo server များသည် အလုပ်လုပ်သည်ကိုသာ ပြသည်။ Production တွင်မူ — ဘာလုပ်ခဲ့ဘူးကို တိတိကျကျဖော်ပြခြင်း၊ မလုပ်နိုင်သည်ကို ရိုးသားစွာ ပြောခြင်း၊ output ကို ကန့်သတ်ခြင်း — စသည့် "hardening" အချက်များသာ အမှန်တကယ် အရေးကြီးသည်။ ဒီ module က ၎င်းတို့အားလုံးကို တစ်နေရာတည်းတွင် စုစည်းပြသည်။

### ဘယ်လို အလုပ်လုပ်လဲ

Server ဖိုင်ကို အပိုင်းလိုက် ဖွဲ့စည်းထားသည် — module docstring၊ import များ၊ configuration paths၊ `_seed()` ဟူသော estate စတင်ရေးသားမှု၊ allowlist roots၊ helper များ၊ ထို့နောက် `@mcp.tool` များ။ Allowlist roots ဆိုသည်မှာ server က ဖတ်ခွင့်ပြုသည့် လမ်းကြောင်းများစာရင်းသာ ဖြစ်ပြီး၊ အဲဒီစာရင်းပြင်ပရှိ file များကို ဘယ်အခြေအနေမှာမှ မဖတ်ရပါ။

### ဥပမာ

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

LAB 1 (surface probe) တွင် server တစ်ခုကို ယုံကြည်မည်ဆိုပါက အရင်ဆုံး ၎င်း၏ surface — tool၊ resource၊ prompt စာရင်းနှင့် နယ်စည်းများ — ကို စာရင်းကြည့်ရမည်။ နယ်စည်းမဲ့ server သည် ဘယ် host မှာမှ လုံခြုံမည် မဟုတ်ပါ။

## ခေါင်းစဉ် ၂ — Honesty rule နှင့် bounded output

### ဘာကို ဆိုလိုတာလဲ

Honesty rule ဆိုသည်မှာ — metric tool တစ်ခုက တိုင်းတာနိုင်ခြင်းမရှိပါက အတု တန်ဖိုး (fake value) မထုတ်ပေးဘဲ `null` ကို ရိုးသားစွာ ပြန်ရမည်။ Bounded output ဆိုသည်မှာ log tool များက တစ်ကြိမ်လျှင် ကန့်သတ်ထားသော အကြောင်းအရာ အရေအတွက်သာ ပြန်ရမည်။

### ဘာကြောင့် လဲ

`system_metrics` ကဲ့သို့သော tool သည် Python standard library မှ တကယ့်တန်ဖိုးများကိုသာ တိုင်းတာရသည်။ တိုင်းလို့မရပါက ဖြစ်နိုင်ခြေရှိသည့် event တစ်ခုကို လုပ်ကြံပြောခြင်းထက် `null` ပြန်ခြင်းက ပို၍ ယုံကြည်စိတ်ချရသည်။ Log ကို အကန့်အသတ်မဲ့ ထုတ်ပေးပါက client နှင့် token အားလုံး နစ်နာသွားမည်ဖြစ်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

`read_log` tool သည် filter ကို tool boundary အတွင်းတွင် အလုပ်လုပ်သည် — ဖိုင်တစ်ခုလုံးကို client ဘက်သို့ မပို့ဘဲ၊ server ဘက်မှာ itself filter လုပ်ပြီး ကန့်သတ်အရေအတွက်သာ ပြန်သည်။ LAB 3 (log forensics) တွင် "အဆိုးဆုံး event" ကို မည်သည့်အခါမှ ရှာခြင်းထက် "ပထမဆုံး anomalous event" ကို ရှာခြင်းကို လေ့ကျင့်သည်။

### ဥပမာ

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

LAB 2 (metrics audit) တွင် declared ၊ measured နှင့် honest null တို့ကို နှိုင်းယှဉ်စစ်ဆေးရသည်။ Automation ပေါ်တွင် အခြေခံထားသော DevOps စနစ်တွင် မှားနေသောတန်ဖိုးတစ်ခုသည် အမှားဆုံး ဆုံးဖြတ်ချက်များစွာကို ဖန်တီးနိုင်သည်။

## ခေါင်းစဉ် ၃ — Protected-service guard နှင့် elicitation

### ဘာကို ဆိုလိုတာလဲ

`restart_service` tool သည် နှစ်လမ်းရှိသော guard ဖြစ်သည် — အန္တရာယ်မရှိသော service များအတွက် တိုက်ရိုက်လုပ်ဆောင်ခြင်း၊ protected service များအတွက် elicitation ဖြင့် အတည်ပြုချက်တောင်းခြင်း။ ဒုတိယလမ်းတွင် server က service ကို မ restart ဘဲ ဘာမှမလုပ်ခဲ့ကြောင်း ဖော်ပြသော အဖြေပြန်သည်။

### ဘာကြောင့် လဲ

Production တွင် service တချို့ (ဥပမာ — ဒိုင်းစီမံခန့်ခွဲမှုဆိုင်ရာ) ကို အလိုအလျောက် restart လုပ်ခြင်းသည် အန္တရာယ်ရှိသည်။ MCP ၏ elicitation capability က အသုံးပြုသူထံမှ အတည်ပြုချက်တောင်းခြင်းအတွက် စံနည်းစနစ်ကို ပေးသည်။ LAB 4 တွင် client အပြုအမူလေးမျိုးကို တိုင်းတာစမ်းသပ်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

Client သည် elicitation ကို `mode="legacy"` ဖြင့် တုံ့ပြန်နိုင်သည်။ Handler contract အရ — အတည်ပြုချက်ရပါက service ကို restart လုပ်ပြီး၊ ငြင်းပယ်ပါက ဘာမှမလုပ်ဘဲ ၎င်းကို ရှင်းလင်းစွာ ဖော်ပြရမည်။ Guard ရဲ့ body သည် "ငါ ဘာလုပ်ခဲ့လဲ၊ ဘာမလုပ်ခဲ့လဲ" ကို အတိအကျ ဖော်ပြရသည်။

### ဥပမာ

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

LAB 7 (estate resource guard) တွင် resource template အသစ်နှင့် guard အသစ်ကို ကိုယ်တိုင်ရေးရမည်။ M10 (security) မှ သင်ယူခဲ့သော အခြေခံမူများကို capstone အတွင်း လက်တွေ့ရေးနှင့် ပေါင်းစပ်ရခြင်းဖြစ်သည်။

## ခေါင်းစဉ် ၄ — Resource နှင့် Prompt

### ဘာကို ဆိုလိုတာလဲ

Resource ဆိုသည်မှာ ဖတ်ရန်အချက်အလက် — `config://{host}` နှင့် `runbook://{name}` ကဲ့သို့ URI template များဖြင့် ချိတ်ဆက်သည်။ Prompt ဆိုသည်မှာ `rca_error_log` နှင့် `capacity_review` ကဲ့သို့ လမ်းညွှန်ချက် (guidance) ဖြစ်ပြီး schema မဟုတ်ပါ။

### ဘာကြောင့် လဲ

Tool သည် လုပ်ဆောင်ချက်၊ resource သည် ဖတ်ရှိရန်အချက်အလက်၊ prompt သည် စဉ်းစားပုံလမ်းညွှန် — သုံးမျိုးလုံးကို ခွဲခြားတတ်ရမည်။ Prompt တစ်ခုရေးပြီးလျှင် မေးရမည့် မေးခွန်း ၃ ခုရှိသည် — လမ်းညွှန်သလား၊ token ကုန်ကျမှု တရားသင့်လား၊ မသိစိတ်ကူး (hallucination) ကို တားဆီးလား။ `rca_error_log` တွင် forced step order နှင့် anti-hallucination clause ပါဝင်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

Prompt ရေးသားရာတွင် literal `{host}` ကို argument အဖြစ် သတ်မှတ်ဖို့ မမေ့ပါနှင့် — ဒါက တကယ့် တွေ့ရလေ့ရှိသော bug ဖြစ်သည်။ Prompt design pattern ၇ မျိုးကို LAB 8 (incident review prompt) တွင် အသုံးပြုပြီး ကိုယ်ပိုင် prompt တစ်ခုကို ရေးပြီး စစ်ဆေးရမည်။

### ဥပမာ

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

Autonomy ၏ anti-pattern ၆ မျိုး (ဥပမာ — confirmation မဲ့ လုပ်ဆောင်ခြင်း၊ bounded output ကို လျစ်လျူရှုခြင်း) ကို ရှောင်ပြီး၊ client ဘက်မှ server ၏ surface အားလုံးကို တစ်ပြားဝင် မေးဖို့ script ရေးရသည်။ Client ၏ တာဝန်စာရင်းတွင် — confirm တောင်းခြင်း၊ null ကို လက်ခံခြင်း၊ output ကို ကန့်သတ်ခြင်းနှင့် error များကို ကျေညီစွာ ကိုင်တွယ်ခြင်းတို့ ပါဝင်သည်။ Self-test script တစ်ခု ရေးရာတွင် အောက်ပါ အဆင့်များကို လိုက်နာရမည် —

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

Scripted agent ဘက်တွင် client သည် tool တစ်ခုချင်းစီကို အစီအစဉ်တကျ ခေါ်ဆိုပြီး ရလဒ်တစ်ခုချင်းစီကို စစ်ဆေးရသည်။ LangGraph ဘက်တွင်မူ node တစ်ခုချင်းစီသည် "decide → act → verify" ဟူ၍ သုံးအဆင့်ကို လိုက်နာသည် — decide node က နောက်ထပ် ခေါ်ရမည့် tool ကို ရွေးချယ်သည်၊ act node က ၎င်း tool ကို ခေါ်ဆိုသည်၊ verify node က ရလဒ်ကို သတ်မှတ်ထားသော ကန့်သတ်ဘောင်အတွင်း ရှိမရှိ စစ်ဆေးသည်။ Confirmation လိုအပ်သော action များအတွက် လူသုံးထောက်ပံ့ပေးသော `elicitation` ယန္တရားကို အသုံးပြုပြီး၊ ရလဒ်အကြောင်းအရာ ရှည်လွန်းသည့်အခါ bounded output စည်းမျဉ်းကို တင်းကျပ်စွာ လိုက်နာရမည်။ ဤသို့ဖြင့် autonomous client သည် လုံခြုံစွာ၊ ခန့်မှန်းနိုင်စွာ အလုပ်လုပ်နိုင်မည် ဖြစ်သည်။

## အနှစ်ချုပ်

- Self-test သည် `main()` အတွင်း ညွှန်ကြားချက်တစ်ခုတည်းဖြင့် server တစ်ခုလုံးကို စစ်ဆေးနိုင်သော အမြန်နည်းလမ်းဖြစ်ပြီး health check အဖြစ်လည်း အသုံးပြုနိုင်သည်။
- Linux VM ပေါ်တွင် path နှင့် အခြားတန်ဖိုးများ ကွဲပြားနိုင်သဖြင့် platform အလိုက် ခြားနားမှုများကို သတိထား၍ စမ်းသပ်ရမည်။
- Autonomy ၏ anti-pattern ၆ မျိုးကို ရှောင်ကြဉ်ပြီး confirm တောင်းခြင်း၊ null စစ်ဆေးခြင်း၊ bounded output တို့ကို client တာဝန်အဖြစ် ထည့်သွင်းရမည်။
- LAB 5 ၏ scripted agent နှင့် LangGraph နှစ်ပိုင်းကို ပေါင်းစပ်ခြင်းအားဖြင့် decide → act → verify ဟူ၍ ယုံကြည်စိတ်ချရသော autonomous client တစ်ခု တည်ဆောက်နိုင်သည်။
