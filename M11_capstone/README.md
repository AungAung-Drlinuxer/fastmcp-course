# M11 — Capstone: Enterprise DevOps / Knowledge Assistant

> **ကြာမြင့်ချိန်:** 6 နာရီ · **Phase:** Phase 4 — Hardening & Capstone

## ဤသင်ခန်းစာတွင် ဘာရမည်လဲ

- MCP server တစ်ခုကို အစဉ်လိုက်ဖတ်ပြီး **production-ready** ဆိုသည့် အဓိပ္ပာယ်ကို လက်တွေ့နားလည်ရမည်
- Tool, Resource, Prompt, Elicitation ဟူသော **primitive လေးမျိုးလုံး** ကို တစ်နေရာတည်း၌ တွဲဖက်အသုံးချရမည်
- Host metrics တွင် **honesty rule** (တိုင်းလို့မရလျှင် null ဟု ရိုးသားစွာ ဖော်ပြခြင်း) ကို လိုက်နာရမည်
- Log tool များတွင် **bounded output** နှင့် protected service အတွက် **confirm guard** ကို တည်ဆောက်ရမည်
- **Self-test** တစ်ခုတည်းဖြင့် server တစ်ခုလုံး အလုပ်လုပ်ကြောင်း သက်သေပြနိုင်ရမည်
- LangGraph နှင့် Cline ဖြင့် **autonomous client** တစ်ခုကို ချိတ်ဆက်ရမည်

## သင်ခန်းစာများ

1. Capstone မိတ်ဆက် — production-ready ဆိုတာ ဘာလဲ
2. Server ဖွဲ့စည်းပုံ — configuration paths, allowlist roots, seed estate
3. Shared helper နှစ်ခု — `_resolve` နှင့် `_fail`
4. Host metrics — standard library မှ တကယ့်တန်ဖိုးများနှင့် honesty rule
5. Log tools — listing, filtered reading, bounded output
6. Protected-service guard — elicitation နှင့် `mode="legacy"`
7. Resources — URI templates (`config://{host}`, `runbook://{name}`) နှင့် loud failures
8. Prompts — guided RCA, forced step order, anti-hallucination clause
9. Prompt ရေးခြင်းနှင့် စစ်ခြင်း — literal `{host}` bug နှင့် pattern ၇ မျိုး
10. Self-test — တစ် command ဖြင့် တစ်ခုလုံးကို သက်သေပြခြင်း
11. Client-side autonomy — scripted agent နှင့် anti-pattern ၆ မျိုး
12. LangGraph / Cline integration နှင့် production checklist

## လိုအပ်ချက်များ (Prerequisites)

- **M10_security** အား အပြီးသတ်ဖြတ်ပြီးဖြစ်ရမည် — elicitation, guard, allowlist သဘောတရားများ ဆက်စပ်နေသောကြောင့်
- FastMCP ဖြင့် tool, resource, prompt သုံးမျိုး ရေးနိုင်စွမ်း ရှိရမည်
- Python standard library (`pathlib`, metrics နှင့်ဆိုင်သော module များ) အခြေခံ သိရှိရမည်

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- MCP server တစ်ခုကို sandbox မှ အမှန်တကယ် အသုံးပြုနိုင်သည့် အဆင့်သို့ တိုးမြှင့်လိုသည့်အခါ
- DevOps / incident-response ကဲ့သို့သော အသိုင်းအဝိုင်း server တစ်ခု တည်ဆောက်လိုသည့်အခါ
- Course တစ်ခုလုံးရဲ့ အသိပညာကို အစပျိုသည့် နောက်ဆုံး project တစ်ခု လိုအပ်သည့်အခါ

## ဖိုင်ဖွဲ့စည်းပုံ

| ဖိုင် | အသုံးပြုပုံ |
|---|---|
| `explanation.md` | သင်ခန်းစာအကျဉ်းချုပ် (condensed lesson) |
| `exercise.md` | လေ့ကျင့်ခန်း ၆ ခု |
| `solution.md` | လေ့ကျင့်ခန်းအဖြေများ |
| `cheatsheet.md` | အမြန်ကြည့်စာရင်း (quick reference) |
| `../code/` | Lab ကုဒ်ဖိုင်များ (`devops_assistant.py`, `health_check.py`, lab ၁ မှ ၈ အထိ) |

## ကိုးကား

- အရင် module — [../M10_security/README.md](../M10_security/README.md)
- နောက် module — ဤ module သည် course ၏ နောက်ဆုံး module ဖြစ်သည်
- စစ်ဆေးမှုဖိုင်များ — [../../tests/test_m11_capstone.py](../tests/test_m11_capstone.py), [../../tests/test_m11_lab6_extension.py](../tests/test_m11_lab6_extension.py)
- Lab ကုဒ် — [../code/devops_assistant.py](code/devops_assistant.py), [../code/my_self_test.py](code/my_self_test.py)
