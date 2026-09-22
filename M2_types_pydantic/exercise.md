## လေ့ကျင့်ခန်း ၁ — Annotation Report (lab_1_annotation_report.py)

Type hint များကို runtime တွင် data အဖြစ် ဖတ်ယူသည့် function တစ်ခု ရေးပါ။ ပေးထားသည့် function တစ်ခု၏ signature မှ annotation တစ်ခုချင်းစီကို ထုတ်ယူပြီး အောက်ပါအချက်များကို အစီရင်ခံကွာတစ်ခု ထုတ်ပေးပါ — type အမည်၊ `get_origin()`/`get_args()` ရလဒ်၊ ရိုးရိုး scalar လား container လား၊ `None` ပါဝင်သည့် Union လား။ `list[dict[str, int]]` ကဲ့သို့ recursive ဖြစ်သည့် hint ကိုပါ မှန်ကန်စွာ ဖော်ပြနိုင်ရမည်။

**Hints:** `typing.get_type_hints()` ဖြင့် string annotation များကို တကယ့် type အဖြစ် ပြောင်းပါ။ `from __future__ import annotations` ထည့်ထားသည့် file များတွင် annotation များသည် string ဖြစ်နေတတ်သည်ကို သတိပြုပါ။

**Expected behavior:** Function တစ်ခုကို ထည့်ပေးလျှင် annotation တစ်ခုချင်းစီအတွက် အချက်အလက် ပြည့်စုံသည့် report ထွက်ပါသည်။

## လေ့ကျင့်ခန်း ၂ — `str` နှင့် `Literal` ကို တိုက်စစ်ခြင်း (lab_2_literal_contract.py)

Tool parameter တစ်ခုအတွက် `str` type သုံးသည့်အခါနှင့် `Literal["small", "medium", "large"]` သုံးသည့်အခါ ရလဒ် JSON Schema များ ဘယ်လို ကွဲပြားသည်ကို နှိုင်းယှဉ်ပါ။ လက်ခံမည့် တန်ဖိုးအပြင် တန်ဖိုးတစ်ခု ထည့်စမ်းပြီး အမှားကို ဘယ်အဆင့်တွင် ဖမ်းမိသည် — schema အဆင့်တွင်လား၊ validation အဆင့်တွင်လား — ကို မှတ်တမ်းတင်ပါ။

**Hints:** `Literal` သည် JSON Schema တွင် `enum` အဖြစ် ပေါ်လာသည်။ `describe_hint` ကဲ့သို့ helper ဖြင့် annotation ကို စစ်ကြည့်ပါ။

**Expected behavior:** `Literal` သုံးသည့် version တွင် မမှန်သည့် တန်ဖိုးကို အစောဆုံး အဆင့်တွင် ဖမ်းမိပြီး schema ထဲတွင် ခွင့်ပြုတန်ဖိုးများ မြင်ရသည်။

## လေ့ကျင့်ခန်း ၃ — Signature မှ Schema ကို ကိုယ်တိုင် ဆောက်ခြင်း (lab_3_signature_schema.py)

`inspect.signature()` ဖြင့် function တစ်ခု၏ parameter များကို ဖတ်ပြီး JSON Schema တစ်ခု ကိုယ်တိုင် ဆောက်ပါ။ Parameter တစ်ခုချင်းစီအတွက် — annotation ရှိမရှိ (`Parameter.empty` စစ်ပါ)၊ `param.kind`၊ default ရှိမရှိ (required သတ်မှတ်ရန်)၊ docstring မှ description တို့ကို ထည့်သွင်းပါ။ ရလဒ် schema တွင် `properties` နှင့် `required` စာရင်း မှန်ရမည်။

**Hints:** `Parameter.empty` ကို `None` အစား သုံးရသည့် အကြောင်းရင်း — default မရှိခြင်းနှင့် default က `None` ဖြစ်ခြင်းကို ခွဲရန် — ကို သတိရပါ။ `inspect.getdoc()` သည် `__doc__` ထက် ပိုသန့်ရှိပါသည်။

**Expected behavior:** မည်သည့် function ကို ထည့်ပေးလျှင် ရာ သင့်တင့်သည့် JSON Schema object တစ်ခု ထွက်ပါသည်။

## လေ့ကျင့်ခန်း ၄ — `ServerProvisionSchema` ရေးခြင်း (lab_4_server_schema.py)

Pydantic `BaseModel` ဖြင့် server provisioning အတွက် schema တစ်ခု ရေးပါ — ဥပမာ name (required string), cpu_count (required int, `ge=` ကန့်သတ်), region (`Literal` ဖြင့် ခွင့်ပြု region များ), tags (optional `dict[str, str]`, default `{}`) စသည့် field များပါဝင်ရမည်။ `Field(description=...)` ဖြင့် field တစ်ခုချင်းစီကို ရှင်းလင်းစွာ ဖော်ပြပြီး `model_dump()` ဖြင့် ထုတ်ကြည့်ပါ။

**Hints:** Required ဆိုသည်မှာ default မရှိခြင်းသာ ဖြစ်သည် — default `None` ထည့်လိုက်သည်နှင့် optional ဖြစ်သွားသည်ကို သတိပြုပါ။ `model_fields` ဖြင့် field များကို program အလိုက် စစ်နိုင်သည်။

**Expected behavior:** မှန်သည့် payload ထည့်လျှင် model instance တည်ဆောက်နိုင်ပြီး မှားသည့် payload ထည့်လျှင် `ValidationError` ရရှိသည်။

## လေ့ကျင့်ခန်း ၅ — Validation Error ကို Debugger လို ဖတ်ခြင်း (lab_5_validation_drill.py)

လေ့ကျင့်ခန်း ၄ ၏ model (သို့မဟုတ် `schema_demo.py` ထဲက `VMProvisionSchema` နှင့် ဆင်တူသည့် model) ထံသို့ တမင်မှားနေသည့် payload လေးခု ထည့်ပါ — type မမှန်ခြင်း၊ ကန့်သတ်ဘောင်ကျော်ခြင်း၊ `Literal` ထဲ မပါသည့် တန်ဖိုး၊ required field လွတ်နေခြင်း။ တစ်ခုချင်းစီအတွက် `errors()` ရလဒ်ကို `loc`, `type`, `input` သုံးချက်ဖြင့် ဇယားပြုပြီး မှတ်တမ်းတင်ပါ။

**Hints:** `loc` သည် nested field များတွင် လမ်းကြောင်းအဖြစ် ရှည်လာသည် — ဥပမာ `("cpu_count",)` ကဲ့သို့ tuple ဖြစ်သည်။ Error များများ တစ်ချိန်တည်း ထွက်နိုင်သည်။ `ValidationError` သည် `ValueError` ၏ subclass ဖြစ်သည်။

**Expected behavior:** payload တစ်ခုချင်းစီအတွက် မှားရာနေရာ၊ မှားရသည့် အကြောင်းပြချက်၊ လက်ခံရရှိသည့် input တို့ကို ထင်ရှားစွာ မြင်ရသည်။

## လေ့ကျင့်ခန်း ၆ — Drift ကို ကိုယ်တိုင် ဖမ်းခြင်း (lab_7_drift_check.py)

Model declaration တစ်ခု (single source of truth) မှ ထုတ်ယူသည့် JSON Schema နှင့် လက်တွေ့ server က ထုတ်ပြနေသည့် schema ကို နှိုင်းယှဉ်ပါ။ Field တစ်ခုကို model ထဲမှာ ပြင်ထားပြီး schema copy ဟောင်းနှင့် တိုက်စစ်လျှင် ကွဲပြားမှုကို ဖမ်းမိရမည်။ Required/Optional ပြောင်းလဲခြင်းကြောင့်လည်း drift ဖြစ်သည်ကို ပြပါ။ Drift ကို ဖမ်းသည့် နည်းလမ်း အနည်းဆုံး တစ်ခု — schema ကို မှတ်တမ်းတင်ခြင်း သို့မဟုတ် test — ကို အသုံးပြုပါ။

**Hints:** `test_m2_schema.py` ကဲ့သို့ test တစ်ခုဖြင့် expected schema ကို hardcode ထားပြီး နှိုင်းယှဉ်နိုင်သည်။ FastMCP သည် Pydantic model schema နှင့် docstring မှ ရင်းမြစ် နှစ်ခုကို ပေါင်းစပ်သည်ကို သတိပြုပါ။

**Expected behavior:** Declaration တစ်ခုတည်း ပြင်လိုက်လျှင် နှိုင်းယှဉ်မှုက ကွဲပြားမှုကို ချက်ချင်း ညွှန်ပြနိုင်သည်။
