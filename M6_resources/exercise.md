## လေ့ကျင့်ခန်း ၁ — Static text resource ရေးခြင်း

`lab_1_static_text.py` ကို ကိုယ်တိုင် ရေးပါ။ `@mcp.resource("status://summary")` ပုံစံဖြင့် static text resource တစ်ခု ဖန်တီးပြီး server status စာသားကို ပြန်ပေးပါ။ Return type အနေဖြင့် `str` သုံးပြီး `mime_type` ကို မသတ်မှတ်ပါက default ဖြစ်သည့် `text/plain` ရရှိကြောင်း စစ်ဆေးပါ။

**Hints:** decorator ထဲမှာ URI string တစ်ခုတည်း ရေးလျှင် static resource ဖြစ်သည်။ function parameter မလိုအပ်ပါ။

**Expected behavior:** `list_resources()` တွင် URI တစ်ခု ပေါ်ပြီး `read_resource("status://summary")` ကို ခေါ်လျှင် စာသား ပြန်ရသည်။

## လေ့ကျင့်ခန်း ၂ — Static JSON resource နှင့် mime_type

`lab_2_static_json.py` အတိုင်း host inventory JSON resource တစ်ခု ရေးပါ။ `dict` ကို return လုပ်ပြီး `mime_type="application/json"` သတ်မှတ်ပါ။ default `text/plain` နှင့် ကွဲပြားကြောင်း client ဘက်မှ ကြည့်ပါ။

**Hints:** `mime_type` သည် ကြေညာချက်သာဖြစ်ပြီး content ကို ပြောင်းလဲမပေးပါ။ JSON string ကို ကိုယ်တိုင် serialize လုပ်ရန် လိုနိုင်သည်။

**Expected behavior:** Read လုပ်လျှင် `mime_type="application/json"` ပါလာပြီး JSON မှန်ကန်စွာ parse လုပ်နိုင်သည်။

## လေ့ကျင့်ခန်း ၃ — URI template ရေးခြင်း

`lab_3_runbook_template.py` ကို ကိုင်တွယ်ပါ။ `@mcp.resource("runbook://{service}")` template တစ်ခု ရေးပြီး service အမည်အလိုက် runbook ဖိုင်ကို ဖတ်ပေးပါ။ မရှိသော service အတွက် မေးလျှင် ဘယ် service များ ရရှိနိုင်ကြောင်း ပါဝင်သော error တက်စေပါ။

**Hints:** template variable သည် function parameter အဖြစ် အလိုအလျောက် ဖြစ်လာသည်။ ဖိုင်ရှာရန် `Path` နှင့် `glob` သုံးပါ။

**Expected behavior:** `read_resource("runbook://deploy")` ကိုခေါ်လျှင် runbook အကြောင်းအရာ ရသည်။ မသိသော အမည်ကို ဖော်ပြလျှင် error တက်ပြီး ရနိုင်သော အမည်များ ပါသည်။

## လေ့ကျင့်ခန်း ၄ — Enumeration ထောင်ချောက် လေ့လာခြင်း

`lab_4_enumeration_trap.py` အတိုင်း ထောင်ချောက်ကို တိုင်းတာပါ။ Static resource များသာ `list_resources()` တွင် ပေါ်ပြီး template resource များက `list_resource_templates()` တွင်သာ ပေါ်ကြောင်း သက်သေပြပါ။

**Hints:** Template ကို `read_resource` ဖြင့် တိုက်ရိုက် ဖော်ပြ၍ ရသည် — enumeration နှင့် read သည် သီးသန့်ဖြစ်သည်။

**Expected behavior:** Client တစ်ခုသည် list နှစ်မျိုးလုံး မေးမှသာ server ရဲ့ resource အားလုံးကို မြင်နိုင်သည်။

## လေ့ကျင့်ခန်း ၅ — Generic reader loop ရေးခြင်း

`lab_5_reader_loop.py` အတိုင်း server တစ်ခုလုံးကို enumerate လုပ်သည့် client ရေးပါ။ Static list နှင့် template list နှစ်ခုစလုံး ရယူပြီး URI တစ်ခုချင်းကို `read_resource` ဖြင့် ဖတ်ပါ။ Read တွင် error ၃ မျိုး ထွက်နိုင်ခြင်းကို သတိထားပါ။

**Hints:** Read contract အရ URI တစ်ခုသည် list ထဲပါလျှင်ပါ၍ read အတွင်း error တက်နိုင်သည် — ဥပမာ ဖိုင် ပျက်နေလျှင်။

**Expected behavior:** Loop တစ်ခုတည်းဖြင့် server ရဲ့ resource အားလုံးကို ဖတ်နိုင်ပြီး error တက်လျှင် ချက်ချင်း မရပ်ဘဲ ဆက်သွားနိုင်သည်။

## လေ့ကျင့်ခန်း ၆ — Path confinement စမ်းသပ်ခြင်း

`lab_6_confinement.py` အတိုင်း အလွှာ ၂ ခု ကိုင်တွယ်ပါ — URI router နှင့် `Path.resolve()` ဖြင့် containment စစ်ခြင်း။ `runbook://../secrets` ကဲ့သို့ မလိုလားအပ်သော URI များကို လမ်းကြောင်းပြင်ပသို့ ထွက်မသွားစေရန် တားဆီးပါ။

**Hints:** URI ထဲက `..` ကို router က ဖမ်းရပြီး ကျန်တာကို `resolve()` ဖြင့် အတွင်း path မှ ထွက်သွားမှု စစ်ရသည်။ Symlink များကို M10 တွင်မှ အတိအကျ ကိုင်တွယ်မည်။

**Expected behavior:** မှားသော URI များကို error ဖြင့် ငြင်းပြီး တရားဝင် service အမည်များ ကား ပုံမှန်အတိုင်း အလုပ်လုပ်သည်။
