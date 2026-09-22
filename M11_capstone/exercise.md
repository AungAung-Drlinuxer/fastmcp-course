# လေ့ကျင့်ခန်း M11 — Capstone: Enterprise DevOps / Knowledge Assistant

## လေ့ကျင့်ခန်း ၁ — Surface probe (LAB 1)

`lab_1_surface_probe.py` ကို ဖွင့်ပြီး `list_tools`၊ `list_resources`၊ `list_prompts` သုံးမျိုးလုံးကို တစ်ပတ် run ပါ။ ၎င်းတို့ ပေးလိုက်သည့် surface အားလုံးကို ဇယားတစ်ခု ရေးထုတ်ပြီး — နာမည်၊ အမျိုးအစား (tool / resource / prompt)၊ ဆက်သွယ်နိုင်သည့် parameter များ — မိမိကိုယ်တိုင် ယုံကြည်စေရန် စာရင်းကောက်ပါ။ ထို့နောက် ဇယားထဲက တစ်ခုခုကို ရွေးပြီး တကယ် run ကြည့်ပါ။

**Hints:** `devops_assistant.py` ကို အရင် run ထားရမည်။ probe ဖိုင်က server နဲ့ ဆက်သွယ်သည့် client အဖြစ် အလုပ်လုပ်သည်။ surface ကို မသင့်တော်မီ ယုံမှားတတ်သည်ကို သတိပြုပါ။

**Expected behavior:** နာမည်နှင့် parameter များပါဝင်သော surface ဇယားတစ်ခု ရရှိပြီး၊ ရွေးချယ်ထားသည့် primitive တစ်ခု၏ တကယ့် output ကို မြင်ရမည်။

## လေ့ကျင့်ခန်း ၂ — Metrics audit (LAB 2)

`lab_2_metrics_audit.py` ဖြင့် `system_metrics` tool ၏ တကယ့် output ကို ဖန်တီးပါ။ CPU၊ memory စသည့် တန်ဖိုးများကို ကြည့်ပြီး — တိုင်းတာထားသော တန်ဖိုးများ၊ null ဖြစ်နေသော အချက်များ (ဥပမာ VM တွင် မရနိုင်သော metric) — ကို မှတ်တမ်းတင်ပါ။ Honesty rule အရ ဘာကြောင့် null ကို ပိုင်နိုင်ပြီး မှားယွင်းသော ဂဏန်းတစ်ခုကို မပိုင်သင့်သည်ကို မိမိဘာသာ ရှင်းပြပါ။

**Hints:** Metric တိုင်း၏ အချို့သည် Linux VM ပေါ်တွင် ရရှိမှု မတူနိုင်ပါ။ `health_check.py` ကိုလည်း တွဲဖက်ကြည့်နိုင်သည်။

**Expected behavior:** Declared vs measured ကွာခြားချက်များနှင့် honest null အား ဖော်ပြထားသော audit မှတ်တမ်းတစ်ခု ရရှိမည်။

## လေ့ကျင့်ခန်း ၃ — Log forensics (LAB 3)

`lab_3_log_forensics.py` ဖြင့် `list_logs` နှင့် `read_log` ကို အသုံးပြုပြီး အီစတေးအတွင်းရှိ ပထမဆုံး anomalous event (ထူးခြားသော ဖြစ်ရပ်) ကို ရှာပါ။ Filter ကို tool boundary တွင် သုံးပြီး bounded output ကို လက်ခံရရှိမှုကို စစ်ဆေးပါ။ အော်သံအကြီးဆုံး (loudest) error မဟုတ်ဘဲ အမှား၏ အကြောင်းရင်းဖြစ်သော ပထမ event ကို ဖော်ပြပါ။

**Hints:** Read လုပ်သည့် output သည် ကန့်သတ်ထားသောအရေအတွက်ဖြင့် ပြန်လာသည်။ Filter option တစ်ခုခု ရှိ၊ ရှိသည့် option များကို `list_tools` မှ schema ထဲတွင် ဖတ်နိုင်သည်။

**Expected behavior:** ပထမ anomalous event ၏ အချိန်၊ ဖိုင်နှင့် အကြောင်းအရာတို့ကို ဖော်ပြထားသော forensic အစီရင်ခံစာ ရရှိမည်။

## လေ့ကျင့်ခန်း ၄ — Confirm guard (LAB 4)

`lab_4_confirm_guard.py` ဖြင့် `restart_service` tool ကို ခုနှစ်လမ်းလောက် အန္တရာယ်မရှိသော service (unprotected path) နှင့် protected service (elicitation path) — ဟု သီးသန့် run ကြည့်ပါ။ Client ဘက်မှ confirmation ပေးမူ လေးမျိုး (accept, decline, error, no handler) ကို အသီးသီးစမ်းပြီး ရလဒ်အသီးသီးကို ကွဲပြားစွာ မှတ်တမ်းတင်ပါ။

**Hints:** `mode="legacy"` သည် elicitation မကိုင်တွယ်နိုင်သော client များအတွက် ဖြစ်သည်။ Guard ရဲ့ အဖြေသည် မိမိ မလုပ်ခဲ့သောအရာကို ရှင်းပြရမည်။

**Expected behavior:** လမ်းနှစ်လမ်းစလုံးတွင် client အပြုအမူ လေးမျိုး၏ ရလဒ်ဇယား ရရှိပြီး၊ protected service ကို confirmation မရှိဘဲ restart မလုပ်မိစေရ (restart လုပ်ပြီးကြောင်း) စေရမည်။

## လေ့ကျင့်ခန်း ၅ — Autonomous client (LAB 5)

`lab_5_autonomous_client.py` ကို အသုံးပြုပြီး script အလိုက် tool ခေါ်ဆိုမှုများ ပြုလုပ်ပါ။ Part A (scripted agent) အဖြစ် surface probe → metrics → log forensics ဟူ၍ အစီအစဉ်တစ်ခုကို အလိုအလျောက် run စေပါ။ ရရှိလာသော output များကို ပြန်ချုပ်ပြီး `system_metrics` မှ ရှိရှိသမျှ အချက်အလက်များနှင့် တိုက်ဆိုင်စစ်ဆေးပါ။ နိုင်ငံသာ anti-pattern (ခန့်မှန်းချက်ကို အချက်အလက်လို့ ယူဆခြင်း) များ မကျူးကျော်စေရန် သတိပြုပါ။

**Hints:** ဤသင်ခန်းစာမှ "autonomous" ဆိုသည်မှာ လူစွက်မစွက်ဘဲ script အလိုက် လည်ပတ်ခြင်းသာ ဖြစ်သည်။ LangGraph နှင့် Cline အပိုင်းများသည် ရွေးချယ်စရာ extension ဖြစ်သည်။

**Expected behavior:** လူစွက်မစွက်ဘဲ အီစတေးအား စစ်ဆေးသော client run တစ်ခု ပြီးမြောက်ပြီး၊ ခန့်မှန်းချက်မပါဝင်သော အနှစ်ချုပ် ရရှိမည်။

## လေ့ကျင့်ခန်း ၆ — ကိုယ်ပိုင် extension (LAB 6 / LAB 7 / LAB 8)

`lab_6_estate_memory_tool.py`၊ `lab_7_estate_resource_guard.py` နှင့် `lab_8_incident_review_prompt.py` ဖိုင်များကို အခြေခံ၍ ကိုယ်ပိုင် extension တစ်ခု ရေးပါ — tool အသစ်၊ resource template အသစ် + guard အသစ် သို့မဟုတ် incident review prompt အသစ်။ ချဲ့ထွင်မှုတိုင်းအတွက် စစ်ဆေးမှု ၅ ချက် (schema မှန်၊ allowlist boundary မှန်၊ honest null မှန်၊ self-test မှန်၊ `test_m11_capstone.py` နှင့် `test_m11_lab6_extension.py` pass) အားလုံး ဖြေဆိုနိုင်ရမည်။ နောက်ဆုံး `my_self_test.py` ကို run ပြီး တစ်ကြိမ်တည်း အားလုံးအလုပ်လုပ်ကြောင်း သက်သေပြပါ။

**Hints:** လေ့ကျင့်ခန်း ၆ မှ honesty rule နှင့် LAB 4 မှ guard design ကို လိုက်နာပါ။ Prompt ရေးသည့်အခါ `{host}` ကဲ့သို့ စာလုံးစစ်စစ် အမှားကို သတိပြုပြီး prompt testing မေးခွန်း ၃ ခု ကို ဖြေပါ။ Production checklist ရဲ့ စည်းမျဉ်းများကို အခြေခံရမည်။

**Expected behavior:** Extension အသစ်တစ်ခုကို server တွင် ထည့်သွင်းပြီး၊ `mcp dev` (သို့) `my_self_test.py` ဖြင့် အားလုံးအလုပ်လုပ်ပြီး tests အားလုံး pass ရမည်။
