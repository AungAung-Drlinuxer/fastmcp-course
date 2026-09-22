# M5 — လေ့ကျင့်ခန်းများ

## လေ့ကျင့်ခန်း ၁ — Calculator Server ထဲသို့ Tool အသစ် ထည့်သွင်းခြင်း

`../code/lab_0_hello_tool.py` နှင့် `../code/calculator.py` ကို အခြေခံပြီး စံချိန်မီ tool တစ်ခု (ဥပမာ `divide`) ကို ထည့်သွင်းပါ။ Verb-first အမည်၊ summary + `Args:` ပါဝင်သော docstring၊ type annotations နှင့် return annotation အပြည့်အစုံ ထည့်ပါ။

**Hints:** `@mcp.tool()` decorator ကို မမေ့ပါနှင့်။ `Args:` section တွင် parameter တိုင်းကို ရှင်းပါ။
**Expected behavior:** `mcp` object တွင် tool အသစ် ပေါ်လာပြီး schema ထဲတွင် description များ ပါဝင်သည်။

## လေ့ကျင့်ခန်း ၂ — Docstring ပုံစံ ၃ မျိုးကို တိုင်းတာခြင်း

`../code/lab_8_docstring_contract.py` ကို အသုံးပြု၍ function တစ်ခုကို docstring ပုံစံ ၃ မျိုးဖြင့် (မရှိသည်၊ summary သာ၊ summary + `Args:`) ရေးကာ JSON Schema က ဘယ်လိုကွာခြားသည်ကို နှိုင်းယှဉ်ပါ။

**Hints:** FastMCP သည် docstring မှ description ကို ဆွဲထုတ်သည်။ `Args:` section သည် parameter description ဖြစ်လာသည်။
**Expected behavior:** `Args:` ပါဝင်သည့် version ၌ schema တွင် parameter description များ ပါဝင်ပြီး အခြား version များတွင် မပါဝင်။

## လေ့ကျင့်ခန်း ၃ — Error Taxonomy ကို တိုင်းတာခြင်း

`../code/lab_1_error_taxonomy.py` ဖြင့် Bad REQUEST (parameter မှား) နှင့် Bad SITUATION (ဥပမာ သုညဖြင့်စားခြင်း) ကို ကွဲပြားစွာ ကိုင်တွယ်ပါ။ `_ok()` / `_fail()` helper များနှင့် စံချိန်မီ error code များ သုံးပါ။

**Hints:** `raise_on_error=False` ဖြင့် client ဘက်မှ error response ကို စစ်နိုင်သည်။ Unhandled exception များကို ရှောင်ပါ။
**Expected behavior:** Bad REQUEST သည် `isError=True` response ဖြစ်ပြီး Bad SITUATION သည် structured data အဖြစ် ပြန်သည်။

## လေ့ကျင့်ခန်း ၄ — Hint မပါဝင်မှု၏ ကုန်ကျစရိတ်

`../code/lab_2_hint_contract.py` ကို အသုံးပြု၍ hint ပါဝင်သော error နှင့် မပါဝင်သော error ကို နှိုင်းယှဉ်ပါ။ Hint ထဲတွင် "ဘာမှား၊ ဘာလို့၊ ဘယ်လိုပြင်၊ ဥပမာ၊ retry ရမလား" ပါဝင်စေပါ။

**Hints:** `_closest()` heuristic ကဲ့သို့ helper ဖြင့် အနီးစပ်ဆုံး မှန်သော အမည်ကို hint ထဲထည့်ပါ။ Retry-able နှင့် permanent ကို ခွဲပါ။
**Expected behavior:** Hint ပါသော error ကို ရလျှင် နောက်ထပ် မေးခွန်း ထပ်ဖြေရန် မလိုတော့ပဲ တန်ဖိုးကို ဆက်လက် တွက်နိုင်သည်။

## လေ့ကျင့်ခန်း ၅ — Validation Gate ကို ထိုးဖောက်စမ်းသပ်ခြင်း

`../code/lab_3_validate_the_boundary.py` ဖြင့် request ၁၂ မျိုး (type မှား၊ integer လွန်၊ string တို၊ integer သုည စသည်) ကို ပို့ကာ Pydantic က ဘယ် error code ပြန်သည်ကို မှတ်တမ်းတင်ပါ။ Type rules ကိ Pydantic က စစ်ပြီး domain rules (ဥပမာ သုညထက်ကြီးရမည်) ကို ကိုယ်တိုင် စစ်ရမည်ကို အတည်ပြုပါ။

**Hints:** Validation error သည် tool function အတွင်း မရောက်ပါ။ Function အတွင်း ရောက်လာပြီးသားဆိုလျှင် ၄-၄-၄ domain rule ကိစ္စဖြစ်သည်။
**Expected behavior:** Request ၁၂ မျိုးအနက် type မဆီလျော်သည်များကို Pydantic က ဖမ်းဆုပ်ပြီး domain violation များကို ကိုယ်ပိုင် code ဖြင့် ပြန်သည်။

## လေ့ကျင့်ခန်း ၆ — Sequential vs Concurrent နှင့် Tool Trio

`../code/lab_4_async_and_loop.py` ဖြင့် `async def` tool သုံးခုကို sync version နှင့် နှိုင်းယှဉ်တိုင်းတာပါ။ ထို့နောက် `../code/lab_5_tool_trio.py` တွင် `search_articles` → `list_sections` → `get_content` ခေါ်ဆိုမှုကိ တစ်လျှောက်လုပ်ကြည့်ပါ။

**Hints:** `asyncio.gather()` ဖြင့် concurrent ခေါ်ဆိုပါ။ Coroutine အတွင်းမှ `asyncio.run()` ထပ်ခေါ်၍ မရပါ။ Trio ၏ `get_content` တွင် `offset`/`limit` window ထည့်ပါ။
**Expected behavior:** Concurrent version သည် sequential version ထက် သိသိသာသာ မြန်ပြီး trio က ကြီးမားသော document ကို ခြုံငုံမှုအနည်းငယ်ဖြင့် ရယူနိုင်သည်။
