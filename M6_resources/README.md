# M6 — Read-Only Data Resources (`@mcp.resource`)

> **ကြာမြင့်ချိန်:** 2.5 နာရီ · **Phase:** Phase 2 — MCP Core Surfaces

## ဤသင်ခန်းစာတွင် ဘာရမည်လဲ

- MCP ၏ primitive နှစ်မျိုးဖြစ်သည့် action (tool) နှင့် thing (resource) ကို ခွဲခြားနားလည်ပါမည်။
- `@mcp.resource` decorator ဖြင့် static resource နှင့် URI template resource ကို ရေးတတ်လာမည်။
- `runbook://`, `config://`, `db://`, `file://` စသည့် URI scheme များ၏ နာမည်ပေးစည်းမျဉ်းများကို လေ့လာမည်။
- `mime_type` သည် client အတွက် ဘာကြောင့် အရေးကြီးသလဲ ဆိုသည်ကို နားလည်မည်။
- `read_resource`, `list_resources`, `list_resource_templates` တို့ဖြင့် server တစ်ခုလုံးကို ဖတ်ခြင်းနှင့် စာရင်းကောက်ခြင်း လုပ်တတ်လာမည်။
- pathlib (`Path`, `glob`, `is_file`, `read_text`) ဖြင့် resource ဖိုင်များကို ဘေးကင်းစွာ ရှာဖွေဖတ်ရှိမည်။
- Resource တွင် error channel မရှိသဖြင့် error ကို ကြောင်းကြောင်း ပေါ်လွင်အောင် ရေးနည်းကို လေ့ကျင့်မည်။
- Path confinement ၏ အခြေခံအလွှာ ၂ ခုကို မိတ်ဆက်ခံမည် (အပြည့်အစုံကို M10 တွင် ပြီးမည်)။

## သင်ခန်းစာများ

1. Resource သည် URI ဖြင့် လိပ်စာပေးထားသော ဖတ်ရုံသက်သက် data ဖြစ်ခြင်း။
2. Resource-or-tool ဆုံးဖြတ်ရန် မေးခွန်း ၄ ခု စစ်ဆေးနည်း။
3. URI scheme များ — အစိတ်အပိုင်း၊ ကိုယ်ပိုင် scheme ၏ တရားဝင်မှု၊ နာမည်ပေးစည်းမျဉ်း ၇ ခု။
4. Static resource — `@mcp.resource("inventory://hosts")` ပုံစံ။
5. URI template — `@mcp.resource("runbook://{service}")` ပုံစံနှင့် variable က function parameter ဖြစ်လာပုံ။
6. `mime_type` — default `text/plain` နှင့် client အသုံးပြုပုံ။
7. Read နှင့် enumerate — contract, item shape, list ၃ မျိုး, error ၃ မျိုး။
8. pathlib အသုံးချ — `Path(__file__).with_name(...)`, `/` operator, `glob`, `stem`။
9. Failing loudly — ရှိနေသည့်အရာကို နာမည်ဖြင့် ဖော်ပြခြင်း။
10. Path confinement မိတ်ဆက် — URI router အလွှာ နှင့် `Path.resolve()` containment အလွှာ။

## လိုအပ်ချက်များ (Prerequisites)

- M5_tools ပြီးဆုံးထားရမည် — `@mcp.tool` နှင့် tool အခြေခံကို နားလည်ထားရမည်။
- Python function, decorator, `try/except` အခြေခံကို တတ်ကျွမ်းထားရမည်။
- JSON ဖိုင်ဖတ်ရှိမှုနှင့် pathlib အခြေခံကို အနည်းငယ် သိထားပါက ပိုကောင်းသည်။

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- Server မှ ပြောင်းလဲမှု (action) မလုပ်ဘဲ data (thing) ကိုသာ ပေးအပ်လိုသည့်အခါ။
- Config, runbook, inventory စသည့် ဖိုင်များကို URI ဖြင့် တစ်သမတ်တည်း လိပ်စာပေး၍ client များ ဖတ်နိုင်စေလိုသည့်အခါ။
- ဖိုင်တွဲများကို `glob` ဖြင့် အလိုအလျောက် စာရင်းကောက်ပြီး resource များ ထုတ်ပေးလိုသည့်အခါ။
- နောက်ပိုင်း module များ (M10 ၏ path confinement) အတွက် အခြေခံ ချထားလိုသည့်အခါ။

## ဖိုင်ဖွဲ့စည်းပုံ

- `explanation.md` — သင်ခန်းစာအပြည့်အစုံ (condensed lesson)
- `exercise.md` — လေ့ကျင့်ခန်း ၆ ခု
- `solution.md` — လေ့ကျင့်ခန်းများ၏ အဖြေများ
- `cheatsheet.md` — အမြန်ရှာဖွေရန် အနှစ်ချုပ်
- `../code/` — lab ဖိုင်များ (`lab_1_static_text.py` မှ `lab_9_failure_shapes.py` အထိ၊ `runbooks.py` အပါအဝင်)

## ကိုးကား

- နောက်ဆုံး module: [../M5_tools/README.md](../M5_tools/README.md)
- နောက် module: [../M7_prompts/README.md](../M7_prompts/README.md)
- ဤ module ၏ test: [../../tests/test_m6_resources.py](../tests/test_m6_resources.py)
