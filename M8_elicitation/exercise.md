# လေ့ကျင့်ခန်းများ — M8 Interactive Elicitation

## လေ့ကျင့်ခန်း ၁ — Elicitation warm-up

`lab_1_elicit_warmup.py` ကို အခြေခံ၍ tool တစ်ခု ရေးပါ။ ထို tool သည် `ctx.elicit()` ကို ခေါ်ပြီး ရိုးရိုးစာသားမေးခွန်းတစ်ခု တင်ရမည်။ ခေါ်ပြီးနောက် ပြန်လာသော result ကို ထုတ်ပြပါ။

**Hints:** `await ctx.elicit(message="...")` ဟူ၍ ခေါ်ပါ။ `ctx` parameter ကို tool function ၏ parameter တစ်ခုအဖြစ် ထည့်ပေးရမည်။ Elicitation သည် server မှ client ဆီသို့ ဦးစွာ စတင်တောင်းခံသော reverse flow ဖြစ်ကြောင်း မှတ်ပါ။

**Expected behavior:** Tool ကို ခေါ်လိုက်သောအခါ server သည် မေးခွန်းကို ပြန်လည်တောင်းဆိုပြီး result object တစ်ခု ပြန်ရရှိသည်။

## လေ့ကျင့်ခန်း ၂ — Booking tool အပြည့်အစုံ

`lab_2_booking_form.py` နှင့် `booking.py` ကို ရှုပါ။ `book_flight` ဟူသော tool တစ်ခု ရေးပါ။ Pydantic model ဖြင့် မေးခွန်းပုံစံ သတ်မှတ်ပြီး form mode ဖြင့် လူသုံးယူသည့် အချက်အလက်များ (ဥပမာ — ခရီးသွားရန် နေ့၊ မြို့) ကို တောင်းပါ။

**Hints:** Pydantic model တစ်ခုကို `response_type` အဖြစ် ပေးလျှင် host ဘက်တွင် native form အဖြစ် ပေါ်လာသည်။ Model ထဲတွင် `Field` ဖြင့် description များ ရေးပေးပါ။

**Expected behavior:** Tool ခေါ်သောအခါ host သည် form တစ်ခု ပြပြီး၊ အသုံးပြုသူ ဖြည့်ပါက အချက်အလက်များ ပြန်ရရှိသည်။

## လေ့ကျင့်ခန်း ၃ — Outcome သုံးမျိုး ခွဲခြားခြင်း

`lab_3_outcome_router.py` အတိုင်း result ၏ outcome အပေါ် မူတည်၍ လမ်းကြောင်းသုံးခု ကွဲပြေးသည့် code ရေးပါ — accept, decline, cancel။ Outcome တစ်ခုစီအတွက် ကွဲပြားသော စာသား ထုတ်ပေးပါ။

**Hints:** Outcome ကို ခွဲခြားရာတွင် result object ထဲမှ တန်ဖိုးကို စစ်ပါ။ Counter တစ်ခု ထည့်၍ outcome အသီးသီး ရောက်ရှိမှုကို မှတ်တမ်းတင်ပါ။

**Expected behavior:** Outcome တစ်ခုစီ ပြန်လာသည့်အခါ သက်ဆိုင်ရာ စာသားသာ ထွက်ပြီး အခြား outcome များ မှားမထွက်ပါ။

## လေ့ကျင့်ခန်း ၄ — Protected gate တည်ဆောက်ခြင်း

`lab_4_protected_gate.py` နှင့် `booking.py` ရှိ protected-service pattern ကို အသုံးပြု၍ အန္တရာယ်ရှိသော လုပ်ဆောင်ချက်တစ်ခု (ဥပမာ — record တစ်ခု ဖျက်ခြင်း) မတိုင်ခင် အတည်ပြုချက် တောင်းသည့် gate တစ်ခု ရေးပါ။ Audit trail တစ်ခုလည်း ထည့်ပါ။

**Hints:** Gate ကို state ပြောင်းမည့် code မတိုင်မချင် ထည့်ပါ။ Audit trail တွင် ဘယ်သူက ဘာကို ခွင့်ပြုခဲ့သလဲ ဆိုသည်ကို မှတ်တမ်းတင်ပါ။ State ကို confirmation ရပြီးမှသာ ပြောင်းပါ။

**Expected behavior:** accept မရမချင်း လုပ်ဆောင်ချက် မဖြစ်ပေါ်ဘဲ၊ decline/cancel ဖြစ်ပါက လုံးဝ မပြောင်းလဲပါ။ Audit trail တွင် ဖြစ်ရပ်တိုင်း စုံသည်။

## လေ့ကျင့်ခန်း ၅ — Mode matrix တိုင်းတာခြင်း

`lab_5_mode_matrix.py` အတိုင်း `mode` parameter ကို ပြောင်း၍ elicit ခေါ်ဆိုမှုကို စမ်းပါ။ `mode="legacy"` ထည့်ခြင်း၊ မထည့်ခြင်းတို့ကြောင့် ဘယ် error ပေါ်လာသလဲ ဆိုသည်ကို ဇယားဖြင့် မှတ်တမ်းတင်ပါ။

**Hints:** Error ၏ ပုံစံကို တိတိကျကျ ဖမ်းပါ။ `-32042` ဟူသော protocol error code ကို URL mode နှင့် ဆက်စပ်မှု ရှိမရှိ စစ်ပါ။ Era နှစ်ခု (handshake နှင့် sessionless) ကွာခြားချက်ကို မှတ်ပါ။

**Expected behavior:** Mode တစ်ခုစီအတွက် အမှားပေါ်ခြင်း (သို့) အောင်မြင်ခြင်းကို တိတိကျစွာ ကွဲပြားစွာ မြင်နိုင်သည်။

## လေ့ကျင့်ခန်း ၆ — Elicitation flow ကို လူမပါဘဲ test လုပ်ခြင်း

`lab_10_pytest_elicitation.py` နှင့် `tests/test_m8_elicitation.py` ကို အခြေခံ၍ elicitation ပါဝင်သော tool တစ်ခုအတွက် pytest test ငါးခု ရေးပါ။ Outcome တစ်ခုစီအတွက် test တစ်ခုစီ ထည့်ပါ။

**Hints:** Test များအကြား module-level state ကို ရှင်းလင်းရမည်။ Handler ကို test ထဲတွင် တိုက်ရိုက် သတ်မှတ်ပေးခြင်းဖြင့် လူသားမပါဘဲ outcome များကို ထိန်းချုပ်နိုင်သည်။

**Expected behavior:** `pytest tests/test_m8_elicitation.py` ကို run လိုက်သောအခါ test အားလုံး အစည်းအရုံးမလိုဘဲ အောင်မြင်စွာ ဖြတ်သည်။
