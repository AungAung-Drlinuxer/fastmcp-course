# M0 — လေ့ကျင့်ခန်းများ

## လေ့ကျင့်ခန်း ၁ — MCP မရှိခင် ပြဿနာကို ဖော်ပြပါ

MCP မရှိခင် AI model တစ်ခုကို tool ၃ ခုနဲ့ ချိတ်ဆက်ရရင် ဘယ်လို ပြဿနာတွေ ကြုံရမလဲဆိုတာကို ကိုယ်ပိုင်စကားလုံးတွေနဲ့ ၃ ကြောင်း ရေးပါ။

**Hints:** integration တစ်ခုချင်းစီအတွက် ရေးရတဲ့ code၊ ပြောင်းလဲရေးရမှု၊ စျေးကွက်ကြီးမှုတို့ကို စဉ်းစားပါ။

**Expected behavior:** ကွဲပြားတဲ့ ပြဿနာ ၃ ခုကို ဖော်ပြနိုင်ရမည်။

## လေ့ကျင့်ခန်း ၂ — JSON-RPC request တစ်ခု ဖန်တီးပါ

Python dict တစ်ခုကို ဖန်တီးပြီး MCP client က server ဆီ ပို့တဲ့ JSON-RPC request format အတိုင်း JSON string အဖြစ် ပြောင်းပါ။

**Hints:** `jsonrpc`, `id`, `method` key ၃ ခု လိုအပ်သည်။ `json.dumps()` ကို သုံးပါ။

**Expected behavior:** JSON string တစ်ခု ထွက်လာပြီး format မှန်ကန်ရမည်။

## လေ့ကျင့်ခန်း ၃ — Host / Client / Server ကို ခွဲပြပါ

အောက်ပါ အခြေအနေတွေအနက်မှ ဘယ်ဟာက Host၊ ဘယ်ဟာက Client၊ ဘယ်ဟာက Serverလဲဆိုတာ ရေးပါ — (a) user နဲ့ စကားပြောနေတဲ့ chat app (b) chat app ထဲက server တစ်ခုနဲ့ ချိတ်ဆက်ပေးတဲ့ အစိတ်အပိုင်း (c) database query tool ဖော်ထုတ်ပေးတဲ့ process။

**Hints:** Client က Host ထဲမှာ နေထိုင်ပြီး Server တစ်ခုနဲ့ ချိတ်ဆက်သည်ကို မှတ်ပါ။

**Expected behavior:** (a)=Host, (b)=Client, (c)=Server ဟု မှန်ကန်စွာ ခွဲနိုင်ရမည်။

## လေ့ကျင့်ခန်း ၄ — LAB 1 လုပ်ပါ: protocol ကို ကိုယ်တိုင် မြင်ပါ

`../code/lab_1_see_the_protocol.py` ဖိုင်ကို ဖွင့်ပြီး လိုက်လုပ်ပါ။ Client နဲ့ Server ကြားမှာ JSON-RPC message တွေ အစစ်အမှန် ဖြတ်သန်းသွားတာကို လေ့လာပါ။

**Hints:** ဖိုင်ကို `python ../code/lab_1_see_the_protocol.py` နဲ့ run ပြီး ထွက်လာတဲ့ JSON message တွေကို ဂရုစိုက် ကြည့်ပါ။

**Expected behavior:** JSON-RPC request နဲ့ response တွေကို output ထဲမှာ မြင်ရမည်။

## လေ့ကျင့်ခန်း ၅ — LAB 2 လုပ်ပါ: surface ၄ မျိုးကို စစ်ပါ

`../code/lab_2_four_surfaces.py` ဖိုင်ကို run ပြီး server က ဘာတွေကို ဖော်ထုတ်ပြီး ဘာတွေကို မဖော်ထုတ်ဘူးလဲဆိုတာကို လေ့လာပါ။

**Hints:** ဖော်ထုတ်ချက် စာရင်းထဲမှာ ဘာ tool၊ ဘာ resource တွေ ပါဝင်လဲဆိုတာကို ကြည့်ပါ။ မပါဝင်တာတွေလည်း သတိထားပါ။

**Expected behavior:** server ရဲ့ ဖော်ထုတ်ချက် စာရင်းကို output ထဲမှာ မြင်ရပြီး မဖော်ထုတ်ထားတာတွေကို ခွဲခြားသိရမည်။

## လေ့ကျင့်ခန်း ၆ — `@mcp.tool` pattern ကို ရှင်းပါ

`FastMCP` နဲ့ tool တစ်ခု ကြေညာရာမှာ `@mcp.tool()` decorator က ဘယ်လို အလုပ်လုပ်လဲဆိုတာကို ၄ ကြောင်း ရှင်းပြပါ။

**Hints:** function က JSON Schema ဘယ်လို ရလဲ၊ server က ဘယ်လို မှတ်ပုံတင်လဲဆိုတာကို တွဲစဉ်းစားပါ။

**Expected behavior:** decorator ရဲ့ အလုပ်လုပ်ပုံ ၄ ဆင့်ကို ရှင်းပြနိုင်ရမည်။
