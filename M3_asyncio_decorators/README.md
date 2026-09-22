# M3 — asyncio & Decorators

> **ကြာမြင့်ချိန်:** 2.5 နာရီ · **Phase:** Phase 1 — Foundations

## ဤသင်ခန်းစာတွင် ဘာရမည်လဲ

- Python function သည် object တစ်ခုဖြစ်ပုံနှင့် decorator ၏ အနှစ်သာရကို နားလည်ရမည်
- Closure, `*args` / `**kwargs` ဖြင့် wrapper က argument အားလုံးကို ဖြတ်ပို့ပုံကို လက်တွေ့သုံးရမည်
- `functools.wraps` မသုံးပါက metadata (အမည်၊ docstring၊ signature) ပျောက်ဆုံးသည့် trap ကို တိုင်းတာ၍ မြင်ရမည်
- `@register_tool` decorator ကို ကိုယ်တိုင်ဆောက်ပြီး `@mcp.tool` အတွင်း ဘာဖြစ်နေသလဲ မြင်ရမည်
- Docstring သည် tool ၏ ဖော်ပြချက်ဖြစ်ပုံ — Google-style docstring မှ JSON Schema ထိ — ကို စာချုပ်အဖြစ် မြင်ရမည်
- `async def`, `await`, event loop နှင့် coroutine တို့၏ အလုပ်လုပ်ပုံကို တိုင်းတာမှုဖြင့် အထောက်အထားမြင်ရမည်
- Blocking trap, `asyncio.to_thread`, `wait_for` timeout နှင့် retry အစုံကို ကိုင်တွယ်နိုင်ရမည်
- `asyncio.gather` နှင့် `asyncio.TaskGroup` ၏ ကျရှုံးမှု ကွဲပြားပုံကို တွေ့ရမည်
- Decorator နှင့် async tool ၏ အမှားများကို ရှာဖွေနိုင်သည့် audit harness တစ်ခု ဆောက်ရမည်

## သင်ခန်းစာများ

1. Decorator ဆိုတာ ဘာလဲ — function ယူ၍ function ပြန်သည့် ဖွဲ့စည်းပုံ
2. Closure နှင့် `*args` / `**kwargs` — wrapper က အားလုံးကို ရှေ့ဆက်ပေးပုံ
3. `functools.wraps` နှင့် Metadata Trap — MCP tool အတွက် အန္တရာယ်
4. `@register_tool` — `@mcp.tool` ၏အောက်ခံ decorator
5. `@mcp.tool` ၏ အတွင်းစနစ် — schema ဘယ်ကလာ၍ ဘယ်လိုဖော်ပြသလဲ
6. Argument ပါသည့် Decorator — factory → decorator → wrapper အလွှာသုံးလွှာ
7. Event Loop နှင့် Coroutine — `async def` ခေါ်ဆိုမှုက မ run သေးပုံ
8. Blocking Trap — coroutine အတွင်းရှိ `time.sleep` ၏ ဆိုးရွားမှု
9. `asyncio.to_thread` နှင့် Timeout — ထွက်ပြေးခေါ်ဆိုမှုတိုင်းတွင် ကာရံချက်
10. `gather` vs `TaskGroup` — တစ်ခုကျရှုံးလျှင် တစ်ဖက်က ဘာလုပ်သလဲ
11. Docstring ကို စာချုပ်အဖြစ် သတ်မှတ်ခြင်း
12. Debugging နှင့် Audit — အမှားအားလုံး၏ တူညီသည့် လက္ခဏာများ

## လိုအပ်ချက်များ (Prerequisites)

- [M2 — Types & Pydantic](../M2_types_pydantic/README.md) ကို ပြီးမြောက်ထားရမည် — pydantic validation အသိအမှတ်ပြုခြင်းနှင့် JSON Schema အခြေခံ လိုအပ်သည်
- Python 3.10+ (TaskGroup အတွက် 3.11+ ဖြစ်လျှင် ပိုကောင်းသည်)
- Python function, `def`, exception handling အခြေခံ

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- Tool တစ်ခုကို `@mcp.tool` ဖြင့် စာရင်းသွင်းလိုသည့်အခါ — decorator က metadata ဘယ်လိုဖတ်သလဲ သိရှိနေရသည်
- Tool အမည် `'wrapper'` ဖြစ်နေခြင်း၊ docstring မရောက်လာခြင်းကဲ့သို့ ပြဿနာများကို ဖြေရှင်းရာတွင်
- I/O ခေါ်ဆိုမှုပါသည့် tool များကို timeout နှင့် error handling နှင့်အတူ ရေးရာတွင်
- Docstring မှ model ဆီရောက်သည့် schema ကို စစ်ဆေးလိုသည့်အခါ

## ဖိုင်ဖွဲ့စည်းပုံ

- `explanation.md` — သင်ခန်းစာအားလုံး၏ ချုံးထားသည့် ရှင်းလင်းချက်
- `exercise.md` — လေ့ကျင့်ခန်း ၆ ခု (lab ဖိုင်များနှင့် တွဲ)
- `solution.md` — လေ့ကျင့်ခန်းတိုင်း၏ အဖြေများ
- `cheatsheet.md` — လျင်မြန်စွာ ရှာဖွေရန် အမှတ်အသားများ
- `../code/` — lab နှင့် အထောက်အကူ Python ဖိုင်များ

## ကိုးကား

- ယခင် module: [M2 — Types & Pydantic](../M2_types_pydantic/README.md)
- နောက် module: [M4 — FastMCP Basics](../M4_fastmcp_basics/README.md)
- ဤ module ၏ test: [test_m3_decorators.py](../tests/test_m3_decorators.py)
