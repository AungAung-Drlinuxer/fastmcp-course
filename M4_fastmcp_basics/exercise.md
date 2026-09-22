## လေ့ကျင့်ခန်း ၁ — ပထမဆုံး server ကို ကိုယ်တိုင်ရေးခြင်း

`../code/hello_server.py` ကို ကြည့်ပြီး တူညီသည့် ပုံစံဖြင့် မိမိကိုယ်ပိုင် server ဖိုင်တစ်ခု ရေးပါ။ လိုအပ်ချက်များ —
- `from fastmcp import FastMCP` ဖြင့် import လုပ်ခြင်း
- `mcp = FastMCP("my-first-server")` ဖြင့် server object ဖန်တီးခြင်း
- `@mcp.tool` ဖြင့် tool တစ်ခု မှတ်ပုံတင်ခြင်း (လွယ်ကူသည့် လုပ်ငန်းတစ်ခု၊ ဥပမာ — စာသားကို အကြီးအသေး ပြောင်းခြင်း)
- `main()` တွင် `mcp.run()` ကို ခေါ်ခြင်း

**Hints:** `hello_server.py` ရဲ့ module docstring ဟာ server ကို ဘယ်လို run မလဲ ဖိုင်ကိုယ်တိုင် ပြောပြပါတယ်။ ဒီပုံစံကို လိုက်မှီပါ။ `if __name__ == "__main__":` block ကို မမေ့ပါနှင့်။

**Expected behavior:** ဖိုင်ကို run ရုံနှင့် server စောင့်နေပြီး ဘာမှ crash မဖြစ်ပါ။

## လေ့ကျင့်ခန်း ၂ — Server object ကို code ဖြင့် စစ်ဆေးခြင်း

`lab_2_client_demo.py` ကို မူတည်ပြီး server object အပေါ် အောက်ပါအချက်များကို Python script တစ်ခုဖြင့် စစ်ပါ —
- server ၏ နာမည် (ဆောက်လုပ်စဉ် ပေးခဲ့သည့် နာမည်) ကို ဖတ်ခြင်း
- register ဖြစ်ထားသည့် tool များ၏ အရေအတွက ကို ရေတွက်ခြင်း
- tool တစ်ခုချင်းစီ၏ နာမည်ကို ထုတ်ပြခြင်း

**Hints:** `FastMCP("course-hello")` ထဲ ပေးလိုက်တဲ့ နာမည်ဟာ client ဘက်မှာ မြင်ရတဲ့ server နာမည် ဖြစ်ပါတယ်။ Tool များကို server object ပေါ်မှ တိုက်ရိုက် ရယူနိုင်သည့် API ကို FastMCP မှ ပေးထားပါတယ်။

**Expected behavior:** Script run လိုက်ရင် server နာမည်၊ tool အရေအတွက နှင့် tool နာမည်များ ထွက်လာပြီး ဘယ် tool မှ ပျောက်နေတာ မရှိပါ။

## လေ့ကျင့်ခန်း ၃ — stdio ထောင်ချောက်ကို ကိုယ်တိုင် မြင်ခြင်း

`lab_1_echo_server.py` နှင့် `lab_2_stdout_trap.py` ကို အသုံးပြုပါ။ ပထမ — echo tool တစ်ခုပါသည့် server ကို client မှ `Client(Path)` ဖြင့် ခေါ်ပြီး အလုပ်လုပ်ကြောင်း အတည်ပြုပါ။ ထို့နောက် server ထဲ အလွဲအလက် `print()` တစ်ကြောင်း ထည့်ပြီး ဘာဖြစ်သည်ကို လေ့လာပါ။

**Hints:** stdio transport မှာ server ၏ `stdout` ဟာ protocol လိုင်း အဓိက ဖြစ်ပါတယ်။ ၎င်းထဲ အခြားအရာ ရောမိုလျှင် client က JSON အဖြစ် ဖတ်ဖို့ ကြိုးစားပြီး ပျက်သွားစေနိုင်ပါတယ်။ `stderr` ကတော့ protocol မဟုတ်တဲ့ အရာတွေ ထုတ်ဖို့ လိုအပ်ပါတယ်။

**Expected behavior:** `print()` မပါခင် — round trip အောင်မြင်ပါတယ်။ ပါပြီးရင် — client ဘက်မှာ parse error သို့မဟုတ် ချိတ်ဆက်မှု ပျက်စီးမှု မြင်ရပါမယ်။

## လေ့ကျင့်ခန်း ၄ — တူညီသည့် server ကို HTTP ဖြင့် ခေါ်ခြင်း

`lab_3_http_client.py` ကို ကြည့်ပါ။ လေ့ကျင့်ခန်း ၁ ၏ server ကို HTTP transport ဖြင့် run ပြီး client တစ်ခုမှ `list_tools` နှင့် `call_tool` ဖြင့် ခေါ်ပါ။ ပြီးလျှင် မေးခွန်း သုံးခုကို ဖြေပါ —
- HTTP မှာ server က စောင့်ပြီး client က dial လုပ်တာ မှန်/မမှန်
- HTTP မှာ `print()` ရေးလို့ ရ/မရ (stdio နှင့် နှိုင်းယှဉ်၍)
- `host` အနေဖြင့် `127.0.0.1` နှင့် `0.0.0.0` ကွာခြားချက်

**Hints:** `main()` ဟာ transport ကို ရွေးသည့် နေရာ ဖြစ်ပါတယ်။ HTTP မှာ protocol လိုင်းက `stdout` မဟုတ်ဘဲ HTTP ဖြစ်လို့ `print()` က အန္တရာယ် မရှိပါ။ ဒါပေမယ့် HTTP server ဟာ ကွန်ရက်ပေါ် ရောက်နိုင်တာကြောင့် တကယ့် အန္တရာယ် ရှိပါတယ် — auth နှင့် သက်ဆိုင်ပါတယ်။

**Expected behavior:** HTTP client က server ၏ tool စာရင်း ရယူပြီး ခေါ်ဆိုမှု အောင်မြင်ပါတယ်။

## လေ့ကျင့်ခန်း ၅ — Client discovery နှင့် registration audit

`lab_4_discover_tools.py` ကို မူတည်ပါ။ client တစ်ခု ရေးပြီး —
- `list_tools()` ဖြင့် tool စာရင်း ရယူခြင်း
- tool တစ်ခုချင်းစီ၏ `name` နှင့် `input_schema` ကို ထုတ်ပြခြင်း
- `call_tool()` ဖြင့် tool တစ်ခုကို မှားယွင်းသည့် argument ဖြင့် ခေါ်ကြည့်ပြီး `is_error` ကို စစ်ခြင်း

**Hints:** Tool တစ်ခုကို မှားသည့် နည်းနှစ်မျိုး ရှိပါတယ် — လုံးဝ မရှိတဲ့ နာမည်နှင့် ခေါ်တာ (`is_error=True` ရပါတယ်) နှင့် ရှိပေမယ့် argument မှားတာ (schema validation အရ ကျရှုံးနိုင်ပါတယ်) တို့ ဖြစ်ပါတယ်။ `is_error=False` ဖြစ်လျက်ပင် tool အတွင်း ကျရှုံးမှု ရှိနိုင်တာကို သတိပြုပါ။

**Expected behavior:** မှားယွင်းသည့် ခေါ်ဆိုမှုများကို program ချက်ချင်း crash မဖြစ်ဘဲ result object ထဲက `is_error` ဖြင့် ခွဲခြား မြင်ရပါတယ်။

## လေ့ကျင့်ခန်း ၆ — Calculator + Currency lab အပြည့်အစုံ

`lab_5_currency_server.py` နှင့် `lab_5_drive_both.py` ကို run ပါ။ ပြီးလျှင် —
- Server ထဲ ပါသည့် tool တစ်ခုကို `Literal` type ဖြင့် parameter တစ်ခု ထည့်ပြီး client ဘက်မှ `input_schema` ထဲ `enum` ဖြစ်လာသည်ကို ကြည့်ပါ
- `required` field စာရင်းကို ဖတ်ပြီး ဘယ် parameter များ မဖြစ်မနေ ပေးရမလဲ ဆိုတာ စစ်ပါ
- `lab_5_drive_both.py` က transport နှစ်မျိုးလုံးကို ဘယ်လို စမ်းသပ်သလဲ ဆိုတာ ရှင်းပြပါ

**Hints:** Server-side မှာ schema ကို `.parameters` ဟု ခေါ်ပြီး client-side မှာ `.input_schema` ဟု ခေါ်ပါတယ် — နာမည် မတူတာက အမှားအများဆုံး နေရာ ဖြစ်ပါတယ်။ Lab အမှားများ (error → အကြောင်းရင်း → ဖြေရှင်းနည်း) ကို tutorial 12 က ဇယားဖြင့် ပြထားပါတယ်။

**Expected behavior:** Server တစ်ခုတည်းကို stdio နှင့် HTTP transport နှစ်မျိုးလုံးဖြင့် အောင်မြင်စွာ ခေါ်ဆိုနိုင်ပြီး ဘယ်လိုးသားကိုမဆို ဘယ် transport က သင့်တော်သလဲ ဆုံးဖြတ်နိုင်သည့် အသိ ရရှိပါတယ်။
