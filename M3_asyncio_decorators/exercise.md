# လေ့ကျင့်ခန်းများ — M3: asyncio & Decorators

အောက်ပါ လေ့ကျင့်ခန်း ၆ ခုကို အစဉ်အတိုင်း ဖြေဆိုပါ။ `../code/` ဖိုင်တွဲထဲက lab ဖိုင်များနှင့် တူညီသော ပုံစံကို လိုက်နိုင်ပါသည်။

## လေ့ကျင့်ခန်း ၁ — Decorator ကို လက်ဖြင့် တည်ဆောက်ခြင်း

Function တစ်ခုကို လက်ခံပြီး အခြား function ပြန်ပေးသော decorator တစ်ခုကို လက်ဖြင့် ရေးပါ။ Decorator မရေးမီ အရင်ဆိုရင် function ကို variable တစ်ခုအဖြစ် သိမ်းပြီး အခြား အမည်သို့ ပေးပြောင်း၍ ခေါ်ကြည့်ပါ။ ထို့နောက် wrapper ထဲမှာ မူလ function ခေါ်ခြင်းအပြင် print တစ်ကြောင်း ထည့်သည့် decorator ရေးပြီး `@` သင်္ကေတဖြင့် အသုံးပြုကြည့်ပါ။ `lab_1_decorator_mechanics.py` ကို အခြေခံပါ။

**Hints:** Function သည် object တစ်ခုဖြစ်သောကြောင့် အမည်ပေးပြောင်းလို့ရသည်။ `@` သင်္ကေတသည် အပေါ်မှ အောက်သို့ အလုပ်လုပ်သည် — `@dec` သည် `fn = dec(fn)` နှင့် တူညီသည်။

**Expected behavior:** Decorator တပ်ထားသော function ကို ခေါ်ရုံမှာ wrapper ထဲမှာ ရေးထားသော print ပေါ်ပြီး မူလ function ၏ ရလဒ်လည်း ပုံမှန်ရသည်။

## လေ့ကျင့်ခန်း ၂ — Closure နှင့် `*args` / `**kwargs`

Wrapper function တစ်ခုက ပြင်ပက variable တစ်ခုကို မှတ်သားသည့် (closure) decorator တစ်ခု ရေးပါ။ Wrapper ကို `*args, **kwargs` ဖြင့် ဖြေဆိုပြီး မူလ function ဆီ အားလုံးကို ဖြတ်ပို့ပေးပါ။ Counter တစ်ခုကို closure အဖြစ် သိမ်းပြီး function ကို ခေါ်တိုင်း တစ်တက်တိုးစေပါ။ `lab_2_closures.py` နှင့် `decorators.py` ကို ကိုးကားပါ။

**Hints:** Closure ဆိုသည်မှာ wrapper ထဲကနေ ပြင်ပ scope ၏ variable ကို ဖမ်းယူထားခြင်းဖြစ်သည်။ `*args` / `**kwargs` ကို အသုံးပြုမှသာ argument အားလုံး လွတ်လွတ်လပ်လပ် ရောက်မည် — သို့သော် JSON Schema ဖန်တီးရာတွင် ဤပုံစံမှာ ပြဿနာရှိသည်ကို မှတ်သားပါ။

**Expected behavior:** Function ကို ၃ ခေါ်လျင် counter သည် ၃ ဖြစ်ပြီး မည်သည့် argument ပုံစံဖြင့် ခေါ်ခေါ် မှန်ကန်စွာ အလုပ်လုပ်သည်။

## လေ့ကျင့်ခန်း ၃ — Metadata Trap နှင့် `functools.wraps`

`functools.wraps` မထည့်ထားသော decorator တစ်ခုနှင့် ထည့်ထားသော decorator တစ်ခု — နှစ်ခုလုံးကို ရေးပြီး ခြားနားချက်ကို `__name__`, `__doc__` ဖြင့် တိုက်စစ်ပါ။ Registry decorator တစ်ခုက `__name__` ကို ဖတ်၍ tool အမည် ပေးသည်ဟု ယူဆပြီး မထည့်လျင် tool အမည် `'wrapper'` ဖြစ်သွားမည့်အချက်ကို လက်တွေ့ပြပါ။ `lab_3_wraps_trap.py` ကို အခြေခံပါ။

**Hints:** `@mcp.tool` က function ၏ metadata ကို ဖတ်၍ tool အမည်နှင့် ဖော်ပြချက် တည်ဆောက်သောကြောင့် metadata ပျောက်နေခြင်းသည် MCP အတွက် သေဆုံးသည့် အမှားဖြစ်သည်။ Decorator အများကို တွဲသုံးသောအခါ အစဉ် (ordering) လည်း အရေးကြီးသည်။

**Expected behavior:** `wraps` မပါသော decorator ၏ `__name__` သည် `wrapper` ဖြစ်ပြီး၊ ပါသော decorator ၏ `__name__` သည် မူလ function အမည်ဖြစ်သည်။

## လေ့ကျင့်ခန်း ၄ — Registry Decorator နှင့် Tool List

`@register_tool` ပုံစံ registry decorator တစ်ခုကို ကိုယ်ပိုင် ရေးပါ — `inspect.signature` (သို့မဟုတ် `__doc__` ဖြင့် docstring) မှ parameters သတင်းအချက်များ ထုတ်ယူပြီး dictionary တစ်ခုထဲ မှတ်ပါ။ ထို့နောက် မှတ်ထားသော tool များကို စာရင်းပြန်ခြင်း (list) function တစ်ခု ရေးပါ။ `lab_4_register_tool.py` နှင့် `lab_4b_list_tools.py` ကို ကိုးကားပါ။

**Hints:** Registry ဆိုသည်မှာ decorator အလုပ်လုပ်ချိန်တွင် function ကို dictionary ထဲ သိမ်းဆည်းခြင်းသာဖြစ်သည် — ခေါ်ချိန်တွင် မဟုတ်။ `inspect.getdoc(fn)` သည် `fn.__doc__` ထက် ပိုမှန်ကန်သော ရလဒ်ပေးသည်။

**Expected behavior:** Decorator တပ်ထားသော function များသည် registry ထဲ အမည်၊ docstring နှင့် parameters နှင့်အတူ ပေါ်ပြီး မတပ်ထားသော function များ မပါဝင်ပါ။

## လေ့ကျင့်ခန်း ၅ — Event Loop၊ Blocking Trap နှင့် `gather`

`async def` function နှစ်ခု ရေးပါ — တစ်ခုတွင် `time.sleep` (blocking) ထည့်ပြီး တစ်ခုတွင် `asyncio.sleep` ထည့်ပါ။ Sequential ခေါ်ခြင်းနှင့် `asyncio.gather` ဖြင့် ခေါ်ခြင်း — နှစ်မျိုးလုံးကို `time.perf_counter` ဖြင့် အချိန်တိုင်းပြီး နှိုင်းယှဉ်ပါ။ `lab_6_event_loop.py` နှင့် `lab_7_sequential_vs_gather.py` ကို အခြေခံပါ။

**Hints:** `async def` ကို သီးသန့်ခေါ်လျင် coroutine object တစ်ခုသာ ရပြီး `await` နှင့်သာ တကယ် run သည်။ Coroutine တစ်ခုကို တစ်ခါသာ await လုပ်လို့ရသည်။ Blocking call တစ်ခုက event loop တစ်ခုလုံးကို အချိန်ဆွဲထားသည်။

**Expected behavior:** `time.sleep` ကို အသုံးပြုသော version သည် `gather` နှင့်ပင် sequential ကဲ့သို့ အချိန်ကြာပြီး `asyncio.sleep` version သည် concurrent အဖြစ် အချိန်သက်သာသည်။

## လေ့ကျင့်ခန်း ၆ — Timeout၊ TaskGroup နှင့် Audit Harness

Blocking အလုပ်တစ်ခုကို `asyncio.to_thread` ဖြင့် လွှတ်ပြီး `asyncio.wait_for` ဖြင့် timeout တပ်ပါ။ ထို့နောက် `asyncio.TaskGroup` ထဲမှာ task ၃ ခု ထည့်ပြီး တစ်ခုက exception ပေးစေကား ကျန် task များ ဘယ်လိုဖြစ်သည်ကို ကြည့်ပါ။ နောက်ဆုံး `asyncio.iscoroutinefunction` ဖြင့် tool တစ်ခုသည် async ဖြစ်/မဖြစ် စစ်သော `audit_tool` ပုံစံ harness တစ်ခု ရေးပါ။ `lab_8_to_thread_timeout.py`, `lab_9_taskgroup_exceptions.py` နှင့် `lab_11_audit_tool.py` ကို ကိုးကားပါ။

**Hints:** Timeout ကို မလွဲမရှောင်သာရမှုဖြစ်သည်မှာ ပြင်ပဆက်သွယ်မှုတိုင်း ရပ်တန့်နိုင်သောကြောင့်ဖြစ်သည်။ `TaskGroup` တွင် task တစ်ခု ကျရှုံးလျင် `ExceptionGroup` ရရှိပြီး ကျန် task များ cancel ခံရသည် — `gather` ၏ ကျရှုံးမှု အပြုအမူနှင့် မတူပါ။ Metadata တွေက်တောင် async ဖြစ်ခြင်းကို မမြင်နိုင်သောကြောင့် `iscoroutinefunction` ကို audit ထဲ ထည့်ရမည်။

**Expected behavior:** Timeout ကျော်လျင် `TimeoutError` ရပြီး TaskGroup တွင် `ExceptionGroup` ရရှိသည်။ Audit harness သည် sync နှင့် async tool နှစ်မျိုးကို တိုက်စစ်နိုင်ပြီး verdict ထုတ်ပြသည်။
