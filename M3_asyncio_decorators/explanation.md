# M3 — asyncio & Decorators : ရှင်းလင်းချက်

ဒီ module မှာ decorator အလုပ်လုပ်ပုံ၊ `functools.wraps` metadata trap၊ `asyncio` event loop၊ blocking ပြဿနာ၊ timeout၊ `gather` vs `TaskGroup` နဲ့ docstring စည်းချက်တွေ သင်ရမှာ ဖြစ်ပါတယ်။

---

## Topic 1 — Decorator နှင့် Closure

### ဘာကို ဆိုလိုတာလဲ

Decorator ဆိုတာ — function တစ်ခုကို လက်ခံပြီး function အသစ်တစ်ခု ပြန်ပေးတဲ့ function ပါ။ Python မှာ function ဟာ object တစ်ခု ဖြစ်လို့ အခြား function ကို argument အဖြစ် ပေးလို့ရတယ်။ `@` ကတော့ အပေါ်က လိုင်းလေးကို အောက်က function ပေါ် တပ်တဲ့ အမှတ်အသားပါ။ လက်ဆေးရည် ထည့်ပြီး လက်အိတ် ဖုံးသလိုမျိုး — function အပေါ် အလွှာတစ်ခု ထပ်တပ်ပေးတာပါ။

### ဘာကြောင့် လဲ

MCP မှာ `@mcp.tool` ဟာ tool တွေကို စနစ်တကျ မှတ်ပုံတင်ဖို့ decorator အသွင် သုံးထားတာပါ။ Decorator အလုပ်လုပ်ပုံ မသိရင် `@mcp.tool` က တကယ် ဘာလုပ်နေလဲ ဆိုတာကို မမြင်ရဘဲ ဖြစ်တယ်။ အဲဒါဆို tool မှာ ချက်ချင်းပျက်တဲ့အခါ ဘာကြောင့် ပျက်လဲ ရှာလို့ မရတော့ပါဘူး။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Decorator က မူလ function ကို လက်ခံတယ်။
၂။ Wrapper function — မူလ function အပေါ် အလွှာထပ်တပ်ထားတဲ့ function — တစ်ခု ဆောက်တယ်။
၃။ Closure — အထဲက function က အပြင်က variable တွေကို မှတ်ထားနိုင်တဲ့ စွမ်းရည် — က မူလ function ကို မှတ်ထားတယ်။
၄။ Wrapper က `*args` / `**kwargs` အားလုံးကို မူလ function ဆီ ဖြတ်ပို့ပေးတယ်။
၅။ နောက်ဆုံးမှာ wrapper ကို ပြန်ပေးတယ်။

### ဥပမာ

ဒီ snippet မှာ decorator တစ်ခု ကိုယ်တိုင်ရေးပြီး closure က မူလ function ကို ဘယ်လို မှတ်ထားသလဲ ဆိုတာ ပြထားပါတယ်။ အထဲက function က အပြင်က name ကို ဘယ်လို အသုံးချသလဲ ဆိုတာကို သတိထားကြည့်ပါ။
```python
import functools

def log_calls(fn):
    # This decorator wraps fn and prints every call
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        print(f"calling {fn.__name__} with {args}, {kwargs}")
        return fn(*args, **kwargs)
    return wrapper

@log_calls
def add(a, b):
    return a + b

result = add(3, b=4)
print(result)
# Expected output:
# calling add with (3,), {'b': 4}
# 7
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

`@register_tool` လိုမျိုး ကိုယ်ပိုင် registry decorator တစ်ခု ကိုယ်တိုင် ဆောက်ချင်ရင် ဒီ အခြေခံ နားလည်ဖို့ လိုပါတယ်။ Registry ဆိုတာ — tool တွေကို အမည်နဲ့ စာရင်းမှတ်ထားတဲ့ စာရင်းစာအုပ်လေးပါ။ LAB 1 နဲ့ LAB 2 မှာ ဒီ mechanics တွေကို လက်တွေ့ လေ့ကျင့်ရမှာ ပါတယ်။

---

## Topic 2 — `functools.wraps` နှင့် Metadata Trap

### ဘာကို ဆိုလိုတာလဲ

Decorator ဆိုတာ — function ရှေ့မှာ ထိုးပြီး အရာထပ်ဆောက်ပေးတဲ့ အလွှာလေးပါ။ Wrapper ဆိုတာ — မူလ function ကို အပြင်ကနေ ဖုံးပေးတဲ့ function အသစ်ပါ။ Metadata ဆိုတာ — function ရဲ့ အမည်၊ docstring၊ signature လို အချက်အလက်တွေပါ။

Decorator တစ်ခုက function ကို wrapper နဲ့ ဖုံးလိုက်ရင် မူလ function ရဲ့ `__name__`, `__doc__`, signature တွေ ပျောက်သွားတယ်။ အစားမှာ wrapper ရဲ့ metadata တွေပဲ ပေါ်လာတယ်။ `functools.wraps` က အဲဒီ metadata တွေကို မူလ function ကနေ ကူးပြန်ပေးတယ်။ လူတစ်ယောက်ပေးလိုက်တဲ့ စာတစ်စောင်ကို မှတ်မိအောင် ကူးရေးပေးတာနဲ့ တူတယ်။

### ဘာကြောင့် လဲ

MCP မှာ tool ရဲ့ အမည်နဲ့ description က model က ကြည့်တဲ့ စာချုပ် ဖြစ်ပါတယ်။ `wraps` မထည့်ဘူးဆိုရင် tool အားလုံးရဲ့ အမည်ဟာ `'wrapper'` ဖြစ်သွားတယ်။ ဒါဆို model က tool တွေကို ခွဲမခွာနိုင်တော့ဘူး။ Model က မှားတဲ့ tool ကို ခေါ်မိပြီး အလုပ်တွေ ပျက်သွားတယ်။ ဒါက MCP အတွက် သေဆုံးတဲ့ အမှားပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

`functools.wraps(fn)` က wrapper ဆောက်ခါစမှာ မူလ `fn` ရဲ့ metadata တွေကို wrapper ပေါ် copy လုပ်ပေးတယ်။ အလုပ်လုပ်ပုံ အဆင့်တွေကို ကြည့်ကြရအောင် —

၁။ `@wraps(fn)` ကို wrapper function ရှေ့မှာ တပ်တယ်။
၂။ `wraps(fn)` က `fn` ရဲ့ metadata တွေကို ယူသည်။
၃။ အဲဒီ metadata တွေကို wrapper ပေါ် ကူးထည့်ပေးတယ်။
၄။ ခေါ်သူက wrapper ကို ကြည့်ရင်လည်း မူလ function အမည် ပေါ်နေတယ်။

ဒါကို LAB 3 မှာ end-to-end တိုင်းတာကြည့်ရမှာ ပါတယ်။ ဒုတိယ trap က `from __future__ import annotations` နဲ့ ဆက်စပ်ပါတယ်။ တတိယ trap က decorator တွေရဲ့ အစဉ် (ordering) ပါ။

### ဥပမာ

ဒီ snippet မှာ `wraps` ထည့်တာနဲ့ မထည့်တာရဲ့ ကွာခြားချက်ကို ပြထားပါတယ်။ `__name__` ရဲ့ တန်ဖိုး ဘယ်ဟာ ပြောင်းသွားလဲဆိုတာကို သတိထားကြည့်ပါ။
```python
import functools

# Without wraps: metadata is lost
def bad(fn):
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper

# With wraps: metadata survives
def good(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper

@bad
def tool_one():
    """Original docstring."""
    pass

@good
def tool_two():
    """Original docstring."""
    pass

print(tool_one.__name__, tool_two.__name__)
print(tool_two.__doc__)
# Expected output:
# wrapper tool_two
# Original docstring.
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

`@mcp.tool` က function ကို ဖုံးတာ မဟုတ်ဘဲ metadata တွေကို ဖတ်ပြီး registry ထဲ မှတ်ပုံတင်တာ ဖြစ်ပါတယ်။ ဒါပေမယ့် ကိုယ်ပိုင် decorator တွေ ရေးတဲ့အခါ `wraps` ကို မမှန်ကန်ဘဲ ထည့်ရင် tool အမည်တွေ ထပ်တူဖြစ်ကုန်မှာ ဖြစ်ပါတယ်။

---

## Topic 3 — Event Loop နှင့် Blocking Trap

### ဘာကို ဆိုလိုတာလဲ

`async def` က function ခေါ်တဲ့အခါ coroutine object တစ်ခုပဲ ပြန်ပါတယ် — တကယ် run တာ မဟုတ်ပါဘူး။ တကယ် run ဖို့ `await` နဲ့ event loop ထဲမှာ ထည့်ပေးရပါတယ်။ Event loop က task တွေကြားမှာ ပြောင်းလဲပေးတဲ့ စက်ပါ။

### ဘာကြောင့် လဲ

Coroutine ထဲမှာ `time.sleep` လို blocking ခေါ်ဆိုမှုတစ်ခု ထည့်လိုက်ရင် event loop တစ်ခုလုံး ရပ်တန့်သွားပြီး အခြား task တွေ အားလုံး မလုပ်နိုင်တော့ပါဘူး။ MCP server တစ်ခုလုံးဟာ တစ်ခုခုရဲ့ blocking ကြောင့် တစ်ကြိမ်တည်းနဲ့ ရပ်နိုင်ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

Blocking မလုပ်ဖို့ `await asyncio.sleep()` ကို သုံးရပါတယ်။ တကယ့် blocking library (sync library တွေ) ကို သုံးရမယ်ဆိုရင် `asyncio.to_thread()` နဲ့ သီးသန့် thread ထဲ ပို့ရပါတယ်။ `asyncio.wait_for()` က timeout ထည့်ပေးပြီး ကြာမြင့်တဲ့ ခေါ်ဆိုမှုတွေကို cancel လုပ်ပေးပါတယ်။

### ဥပမာ

```python
import asyncio
import time

async def blocking_coroutine():
    # time.sleep blocks the entire event loop
    time.sleep(1)
    return "done"

async def nonblocking_coroutine():
    # asyncio.sleep lets other tasks run
    await asyncio.sleep(1)
    return "done"

async def main():
    start = time.perf_counter()
    # Two non-blocking sleeps overlap: about 1 second total
    results = await asyncio.gather(
        nonblocking_coroutine(),
        nonblocking_coroutine(),
    )
    elapsed = time.perf_counter() - start
    print(results, f"{elapsed:.2f}s")

asyncio.run(main())
# Expected output:
# ['done', 'done'] 1.00s
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

MCP API တိုင်းက async နဲ့ ရေးထားပါတယ်။ Tool တစ်ခုရေးတိုင်း blocking ဖြစ်စေတဲ့ ခေါ်ဆိုမှုတွေကို `to_thread` + `wait_for` pattern နဲ့ ဖြေရှင်းဖို့ လိုပါတယ်။ မဖြေရှင်းရင် server တစ်ခုလုံး ရပ်တန့်သွားပြီး အခြား tool တွေလည်း မလုပ်နိုင်တော့ပါဘူး။ LAB 7 နဲ့ LAB 8 မှာ sequential vs concurrent ကို တိုင်းတာကြည့်ရမှာ ဖြစ်ပါတယ်။

---

## Topic 4 — `gather` vs `TaskGroup`

### ဘာကို ဆိုလိုတာလဲ

`asyncio.gather` နဲ့ `asyncio.TaskGroup` နှစ်ခုလုံးက coroutine တွေကို တစ်ပြိုင်တည်း run ပေးပါတယ်။ coroutine ဆိုတာ — async function တစ်ခုကို ခေါ်လိုက်တဲ့အခါ ရလာတဲ့ အလုပ်လုပ်ဆောင်မှုလေးပါ။ ဒါပေမယ့် တစ်ခုကျရှုံးရင် နှစ်ခုက အပြုအမူ မတူပါဘူး။ လမ်းတစ်လမ်းမှာ ကားတွေအားလုံး ရပ်သွားသလိုမျိုးနဲ့ ကွဲပြားပါတယ်။

### ဘာကြောင့် လဲ

Tool တစ်ခုထဲမှာ ခေါ်ဆိုမှု များစွာ လုပ်ရင် တစ်ခုကျရှုံးလို့ ကျန်တာတွေ ဘယ်လိုဖြစ်မလဲ ကို ရွေးချယ်ရပါတယ်။ မရွေးရင် တစ်ခုမှာ error တက်လို့ ကျန်ရလဒ်တွေ အားလုံး ဆုံးရှုံးသွားနိုင်ပါတယ်။ Partial success ပြန်မလား၊ အားလုံး cancel လုပ်မလားဆိုတာက tool design ရဲ့ အဓိက ဆုံးဖြတ်ချက်ပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ `gather` မှာ default အားဖြင့် exception တစ်ခုတက်လို့ ကျန် task တွေကို cancel လုပ်ပါတယ်။
၂။ ပြီးရင် exception ကို ထုတ်ပြပါတယ်။
၃။ `return_exceptions=True` ထည့်ရင် error တွေကို value အဖြစ် ရလဒ် list ထဲ ပြန်ပေးပါတယ်။
၄။ `TaskGroup` က exception တစ်ခုတက်တာနဲ့ အုပ်စုထဲက task အားလုံးကို cancel လုပ်ပါတယ်။
၅။ ပြီးမှ `ExceptionGroup` တစ်ခုတည်း ထုတ်ပါတယ်။

### ဥပမာ

အောက်မှာ ရှိတဲ့ snippet က `gather` နဲ့ `TaskGroup` ရဲ့ ကွာခြားချက်ကို ပြထားပါတယ်။ တစ်ခု error တက်တဲ့အခါ ကျန် task တွေ ဘယ်လိုဆက်လုပ်မလဲဆိုတာကို သတိထားကြည့်ပါနော်။
```python
import asyncio

async def ok(index):
    await asyncio.sleep(0.1)
    return f"result-{index}"

async def boom():
    await asyncio.sleep(0.05)
    raise ValueError("boom")

async def main():
    # gather with return_exceptions: errors come back as values
    results = await asyncio.gather(
        ok(1), boom(), ok(2),
        return_exceptions=True,
    )
    for r in results:
        # Exceptions appear in the result list itself
        print(type(r).__name__ if isinstance(r, Exception) else r)

asyncio.run(main())
# Expected output:
# result-1
# ValueError
# result-2
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Tool တစ်ခုကို ခေါ်တဲ့အခါ တချို့ အလုပ်ဖြစ်ပြီး တချို့ ကျရှုံးနိုင်ပါတယ်။ ကျရှုံးတဲ့ tool တွေကိုပါ ရလဒ်အဖြစ် ပြန်ယူချင်ရင် `gather(return_exceptions=True)` ကို သုံးပါတယ်။ အားလုံး အောင်မြင်မှ ဆက်ချင်ရင်တော့ `TaskGroup` က ပိုသင့်တော်ပါတယ်။ မှားသတ်မှတ်ထားတဲ့ နည်းလမ်းနဲ့ ရေးမိရင် tool တစ်ခု ပျက်လို့ တခြား tool တွေပါ အလုပ်မလုပ်တော့ပါဘူး။ LAB 9 မှာ ဒီနှစ်ခုရဲ့ ခြားနားချက်ကို လက်တွေ့ မြင်ရမှာပါ။

---

## Topic 5 — Docstring သည် Tool ရဲ့ စာချုပ်

### ဘာကို ဆိုလိုတာလဲ

Docstring ဆိုတာ — function ရဲ့ အောက်မှာ triple quote နဲ့ ရေးတဲ့ ရှင်းလင်းချက်စာပါ။ Tool တစ်ခုရဲ့ docstring ဟာ model ကြည့်တဲ့ description လို့ သတ်မှတ်ပါတယ်။ ဒါက လူခေါ်တဲ့ စာချုပ်လိုမျိုး — ဘာလုပ်တယ်၊ ဘယ် parameter တွေ ယူတယ်ဆိုတာကို ပြောပြပါတယ်။

### ဘာကြောင့် လဲ

Docstring မရေးထားရင် model က tool ရဲ့ ရည်ရွယ်ချက်ကို မသိပါဘူး။ မသိရင် မှားတဲ့ tool ကို ခေါ်တာရော၊ မှားတဲ့ parameter နဲ့ ခေါ်တာရော ဖြစ်လာပါတယ်။ Google-style docstring ထဲက Args section က parameter တွေရဲ့ ဖော်ပြချက်အဖြစ် schema ထဲ ရောက်သွားပါတယ်။ ဒါကြောင့် docstring က model အတွက် လမ်းပြပုံစံလို အလုပ်လုပ်ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Schema က function signature ကနေ အလိုအလျောက် ဆောက်ပါတယ်။
၂။ Description တွေက docstring ထဲကနေ ယူပါတယ်။
၃။ Google-style docstring မှာ summary တစ်ကြောင်း အရင်ရေးပါတယ်။
၄။ Args section မှာ parameter တစ်ခုချင်းစီရဲ့ အမည်၊ type နဲ့ ဖော်ပြချက် ရေးပါတယ်။
၅။ Error တွေရှိရင် Raises section ထဲ ရေးပါတယ်။
၆။ LAB 10 မှာ ဒီ docstring contract ကို test လုပ်ကြည့်ရမှာပါ။

### ဥပမာ

ဒီ snippet မှာ Google-style docstring နဲ့ tool တစ်ခု ရေးထားပုံကို ပြပါတယ်။ Summary ကြောင်း၊ Args section မှာ parameter ဖော်ပြချက် ရေးထားပုံကို သတိထားကြည့်ပါနော်။
```python
def get_weather(city: str, units: str = "celsius") -> dict:
    """Get the current weather for a city.

    Args:
        city: City name, e.g. "Yangon".
        units: Temperature unit, "celsius" or "fahrenheit".

    Returns:
        dict with keys "city", "temp", "units".
    """
    return {"city": city, "temp": 30, "units": units}

print(get_weather.__doc__.splitlines()[0])
# Expected output:
# Get the current weather for a city.
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

ဒီ docstring format ကို M4/M5 အတွက် အခြေခံအဖြစ် သုံးရပါတယ်။ `lab_10_docstring_contract.py` နဲ့ format မှန်လား စစ်လို့ရပါတယ်။ LAB 11 ရဲ့ audit harness ကလည်း tool metadata နဲ့ async ဖြစ်မဖြစ်ကို အလိုအလျောက် စစ်ပေးပါတယ်။ ဒီ format မမှန်ရင် နောက်ဆက်တွဲ lab တွေအားလုံး ပျက်ပါတယ်နော်။

---

## အနှစ်ချုပ်

- Decorator ဆိုတာ — function တစ်ခုကို လက်ခံပြီး function တစ်ခု ပြန်ပေးတဲ့ function လေးပါ။ `@` ကတော့ အဲဒါကို apply လုပ်တဲ့ syntax အမှတ်အသားပဲ ဖြစ်ပါတယ်။
- `functools.wraps` က မူလ function ရဲ့ `__name__`, `__doc__` စတဲ့ metadata တွေကို wrapper ဆီ ကူးပေးပါတယ်။ မထည့်ရင် MCP tool နာမည်အားလုံး `'wrapper'` ဖြစ်သွားပြီး tool မှားခေါ်မိပါတယ်။
- `async def` က function ကို မ run ဘူး၊ coroutine object တစ်ခု ပြန်ပါတယ်။ run ချင်ရင် `await` လိုပါတယ်။
- Coroutine ထဲမှာ `time.sleep` လို blocking ခေါ်ဆိုမှု ရေးမိရင် event loop တစ်ခုလုံး ရပ်သွားပါတယ်။ `asyncio.to_thread` နဲ့ ကာကွယ်ပါ။
- Timeout မထည့်ထားရင် MCP call တစ်ခုကို အဆုံးမသတ်ဘဲ ဆွဲထားနိုင်ပါတယ်။ `asyncio.wait_for` နဲ့ အချိန်ကန့်သတ်ပါ။