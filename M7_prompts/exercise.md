# လေ့ကျင့်ခန်းများ — M7 Workflow Steering Prompts (`@mcp.prompt`)

ဒီလေ့ကျင့်ခန်းများကို လုပ်ဆောင်ရန် `../code/` ဖိုလ်ဒါထဲက lab ဖိုင်များကို အခြေခံပါ။ တစ်ခုစီအတွက် ဖန်တီးရမည့်ဖိုင် နှင့် စစ်ဆေးရမည့်အချက်များကို အောက်တွင် ဖော်ပြထားသည်။

## လေ့ကျင့်ခန်း ၁ — Prompt အခြေခံဖွဲ့စည်းပုံ (LAB 1)

`lab_1_prompt_anatomy.py` ကို ဖန်တီးပါ — `@mcp.prompt` decorator ကို သုံး၍ prompt တစ်ခုကို ကြေညာပါ။ Prompt တစ်ခု၏ အစိတ်အပိုင်းများ (အမည်၊ description၊ argument များ၊ စာသား) ကို ခွဲခြားပြပါ။ Server ဘက်မှ prompt registry ထဲတွင် ဘာတွေ ပါဝင်သည်ကို စစ်ဆေးပါ။

**Hints:** `@mcp.prompt` ကို bare ပုံစံဖြင့် သုံးပါ။ Function ရဲ့ docstring သည် description ဖြစ်လာသည်ကို သတိပြုပါ။ `highlight.py` ထဲက နမူနာကို ကြည့်ပါ။

**Expected behavior:** Prompt သည် server ရဲ့ prompt list ထဲမှာ အမည်၊ description နှင့် တွဲဖက်ပေါ်လာသည်။ Render လုပ်သောအခါ စာသားပြည့်စုံစွာ ထွက်လာသည်။

## လေ့ကျင့်ခန်း ၂ — Argument များ (LAB 2)

`lab_2_prompt_arguments.py` ကို ဖန်တီးပါ — argument လိုအပ်သည့် prompt တစ်ခုကို ရေးပါ။ Required argument၊ default ရှိသော argument၊ type coercion ဖြစ်ပုံ၊ argument လို့နေသောအခါ၊ နှင့် အပို argument ပေးလိုက်သောအခါ ဖြစ်ပုံများကို တစ်ခုစီ စမ်းသပ်ပြပါ။

**Hints:** Function signature ကို JSON Schema အဖြစ် ပြောင်းပေးသည်ကို သတိပြုပါ။ Complex type များကို host က JSON string အဖြစ် ပို့သည်။ Mutable default ရဲ့ အန္တရာယ်ကိုလည်း စမ်းကြည့်ပါ။

**Expected behavior:** Required argument မပေးလျှင် error ရသည်။ Default ရှိသော argument မပေးလျှင် default တန်ဖိုး အသုံးပြုသည်။ Extra argument များက prompt ကို မပျက်စေဘဲ လျစ်လျူရှုခံရသည် သို့မဟုတ် သတိပေးချက်ရသည်။

## လေ့ကျင့်ခန်း ၃ — Multi-turn Prompt (LAB 3)

`lab_3_highlight_sections_prompt.py` ကို ဖန်တီးပါ — numbered procedure ပါဝင်ပြီး stop condition ရှိသော `highlight_sections_prompt` တစ်ခုကို ရေးပါ။ Forced ordering နှင့် output shape သတ်မှတ်ချက်များကို prompt စာသားထဲမှာ ထည့်သွင်းပါ။

**Hints:** Numbered procedure ဆိုသည်မှာ ၁။ ၂။ ၃။ စသည့် အဆင့်များဖြင့် ရေးသည့်ပုံစံဖြစ်သည်။ Stop condition က model ကို ဘယ်အချိန်မှာ ရပ်ရမည်ကို ညွှန်ကြားသည်။ `extra_multiturn_prompt.py` ကို ညွှန်းကိုးအဖြစ် ကြည့်ပါ။

**Expected behavior:** Render ရလဒ်တွင် အဆင့်များ ရှင်းလင်းစွာ နံပါတ်တပ်ထားပြီး stop condition စာသား ပါဝင်သည်။ Argument များကို မှန်ကန်သော နေရာများတွင် ထည့်သွင်းထားသည်။

## လေ့ကျင့်ခန်း ၄ — Custom-Type Trap (LAB 4)

`lab_4_custom_type_trap.py` ကို ဖန်တီးပါ — custom return type တစ်ခုကို ပြန်ပေးသော prompt တစ်ခုကို ရေးပြီး အဲဒီ prompt သည် registry ထဲမှာ ပေါ်လာသော်လည်း render လုပ်သောအခါ ပျက်သွားပုံကို မှတ်တမ်းတင်ပါ။ Error စာသားကို ခွဲခြမ်းပြီး ဖြေရှင်းနည်း သုံးမျိုးထဲက တစ်မျိုးကို အသုံးပြု၍ ပြင်ပါ။

**Hints:** Custom return type သည် register ဖြစ်သော်လည်း render မအောင်မြင် — ဒါက "fail late" ပြဿနာဖြစ်သည်။ ဖြေရှင်းနည်းများထဲမှာ return type ကို `str` ဖြစ်စေခြင်း၊ `Message` type များ သုံးခြင်း သို့မဟုတ် structure ပြန်ပြင်ခြင်း ပါဝင်သည်။ `mini_exercise_trap.py` နှင့် `extra_render_selftest.py` ကို ကြည့်ပါ။

**Expected behavior:** ပထမတွင် render error ဖမ်းဆုပ်ရမိသည်။ ပြင်ပြီးနောက် prompt သည် အပြည့်အစုံ render ဖြစ်သည်။ Render self-test ကို တွဲဖက် ထည့်သွင်းပါက အနာဂတ်မှာ ဒီပြဿနာကို အစောကြည့်တွေ့နိုင်သည်။

## လေ့ကျင့်ခန်း ၅ — RCA Prompt Library (LAB 5)

`lab_5_rca_prompt_library.py` ကို ဖန်တီးပါ — root cause analysis (RCA) အဆင့်ငါးဆင့်ပါဝင်သော prompt library တစ်ခုကို ရေးပါ။ Prompt တစ်ခုစီတွင် anti-hallucination clause ထည့်ပါ — ဆိုလိုသည်မှာ အချက်အလက်မရှိပါက ဖန်တီးမထုတ်ရန် ညွှန်ကြားချက် ပါဝင်စေပါ။ Consistency ကို တိုင်းတာရန် `extra_consistency_check.py` ပုံစံကို အသုံးပြုပါ။

**Hints:** Anti-hallucination clause သည် tool ထဲမှာ မဟုတ်ဘဲ prompt ထဲမှာ ထားရသည့် အကြောင်းရင်းကို စဉ်းစားပါ — prompt က model ရဲ့ အမူအကျင့်ကို လမ်းညွှန်သည်၊ tool ကမူ လုပ်ဆောင်ချက်ကို သတ်မှတ်သည်။ Clause သုံးမျိုးရှိပြီး ဘယ်အခါ ဘယ်ဟာသုံးရမည်ကို ရွေးချယ်ပါ။

**Expected behavior:** Library ထဲက prompt တိုင်းက တူညီသော format၊ တူညီသော အဆင့်တက်ပုံ နှင့် တူညီသော stop condition များ ထုတ်ပေးသည်။ Consistency check က prompt များအကြား ကွဲလွဲမှုကို ရှာတွေ့ပါက အချက်ပြသည်။

## လေ့ကျင့်ခန်း ၆ — Host Contract (LAB 6)

`lab_6_host_contract.py` ကို ဖန်တီးပါ — host ဘက်ကနေ server ရဲ့ prompt list ကို ဖတ်ပြီး `prompt.arguments` များကို ပြသပါ။ ရွေးချယ်ထားသော prompt တစ်ခုကို argument များဖြင့် render လုပ်ပြပါ။ Host မဖြစ်မနေ ကိုင်တွယ်ရမည့် error လေးမျိုး (argument လို့နေခြင်း၊ render မအောင်မြင်ခြင်း၊ prompt မတွေ့ခြင်း၊ type မကိုက်ညီခြင်း) ကို တစ်ခုစီ ဖမ်းဆုပ်ပြပါ။

**Hints:** Host ရဲ့ API နှစ်ခုမှာ — prompt list ရယူခြင်း နှင့် prompt render လုပ်ခြင်း — ဖြစ်သည်။ Server-side object နှင့် client-side object တို့ ကွာခြားချက်ကို သတိပြုပါ။ Multi-prompt flow တစ်ခုကို host က ဘယ်လို ဆက်သွယ်ဆက်ဆံမလဲ ဆိုသည်ကို စဉ်းစားပြီး menu ကို ဒီဇိုင်းဆွဲပါ။ `extra_argument_tests.py` ကို အကူအညီအဖြစ် ကြည့်ပါ။

**Expected behavior:** Host က prompt list ကို အမည်၊ description၊ argument schema တို့ဖြင့် ပြသည်။ Render ရလဒ်က စာသားပြည့်စုံ ထွက်လာသည်။ Error လေးမျိုးစလုံးကို သင့်လျော်သော အချက်ပြချက်များဖြင့် ဖမ်းဆုပ်နိုင်သည် — server ပျက်မသွားဘဲ error ကို ကိုင်တွယ်နိုင်သည်။
