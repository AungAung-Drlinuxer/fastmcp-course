# M3 — asyncio & Decorators : ရှင်းလင်းချက်

ဒီ module မှာ decorator တွေရဲ့ အလုပ်လုပ်ပုံ၊ `functools.wraps` metadata trap၊ `asyncio` event loop၊ blocking ပြဿနာ၊ timeout၊ `gather` vs `TaskGroup` နဲ့ docstring စည်းချက်တွေကို သင်ရမှာ ဖြစ်ပါတယ်။

---

## Topic 1 — Decorator နှင့် Closure

### ဘာကို ဆိုလိုတာလဲ

Decorator ဆိုတာ function တစ်ခုကို လက်ခံပြီး အသစ်တစ်ခုပြန်ပေးတဲ့ function ပါ။ Python မှာ function ဟာ object တစ်ခုဖြစ်လို့ အခြား function ကို argument အဖြစ် ပေးလို့ရပါတယ်။ `@` သင်္က fix တစ်ခုဟာ အပေါ်ကနေ အောက်က function ပေါ် apply လုပ်တဲ့ သင်္က fix သာ ဖြစ်ပါတယ်။

### ဘာကြောင့် လဲ

MCP မှာ `@mcp.tool` ဟာ tool တွေကို စနစ်တကျ မှတ်ပုံတင်ဖို့ decorator အသွင် အသုံးပြုထားတာ ဖြစ်ပါတယ်။ Decorator အလုပ်လုပ်ပုံကို နားလည်မှ `@mcp.tool` က တကယ် ဘာလုပ်နေလဲဆိုတာကို မြင်နိုင်ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

Decorator က function ကို wrapper function တစ်ခုနဲ့ ဖုံးပြီး အဲဒီ wrapper ထဲမှာ closure က မူလ function ကို မှတ်ထားပါတယ်။ Wrapper က `*args` / `**kwargs` တွေကို အားလုံး ဖြတ်ပို့ပေးပါတယ်။ Closure ဆိုတာ အပြင် function ရဲ့ အတွင်းပိုင်းက function တွေက အပြင်က variable တွေကို မှတ်ထားနိုင်တဲ့ စွမ်းရည်ပါ။

### ဥပမာ

``python
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
``

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

`@register_tool` လိုမျိုး ကိုယ်ပိုင် registry decorator တစ်ခုကို ကိုယ်တိုင် ဆောက်ဖို့ ဒီ အခြေခံ နားလည်မှု လိုအပ်ပါတယ်။ LAB 1 နဲ့ LAB 2 မှာ ဒီ mechanics တွေကို လက်တွေ့ လေ့ကျင့်ရမှာ ဖြစ်ပါတယ်။

---

## Topic 2 — `functools.wraps` နှင့် Metadata Trap

### ဘာကို ဆိုလိုတာလဲ

Decorator တစ်ခုက function ကို wrapper နဲ့ ဖုံးတဲ့အခါ မူလ function ရဲ့ `__name__`, `__doc__`, signature တို့ဟာ ပျောက်သွားပြီး wrapper ရဲ့ metadata တွေ အစားဝင်သွားပါတယ်။ `functools.wraps` က အဲဒီ metadata တွေကို မူလ function ကနေ ကူးယူပြန်ပေးပါတယ်။

### ဘာကြောင့် လဲ

MCP မှာ tool ရဲ့ အမည်နဲ့ description ဟာ model ကြည့်ရတဲ့ စာချက်ချာ ဖြစ်ပါတယ်။ `wraps` မထည့်ဘူးဆိုရင် tool အမည်အားလုံးဟာ `'wrapper'` ဖြစ်သွားပြီး model က tool တွေကို ခွဲခြားနိုင်တော့မှာ မဟုတ်ပါဘူး။ ဒါက MCP အတွက် သေဆုံးသည့် အမှား ဖြစ်ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

`functools.wraps(fn)` က wrapper ဆောက်ခါစမှာ မူလ `fn` ရဲ့ metadata တွေကို wrapper ပေါ် copy လုပ်ပေးပါတယ်။ ဒါကို LAB 3 မှာ end-to-end တိုင်းတာကြည့်ရမှာ ဖြစ်ပါတယ်။ ဒုတိယ trap က `from __future__ import annotations` နဲ့ ဆက်စပ်ပြီး တတိယ trap က decorator တွေရဲ့ အစဉ် (ordering) ဖြစ်ပါတယ်။

### ဥပမာ

``python
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
``

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

`@mcp.tool` က function ကို ဖုံးတာ မဟုတ်ဘဲ metadata တွေကို ဖတ်ပြီး registry ထဲ မှတ်ပုံတင်တာ ဖြစ်ပါတယ်။ ဒါပေမယ့် ကိုယ်ပိုင် decorator တွေ ရေးတဲ့အခါ `wraps` ကို မမှန်ကန်ဘဲ ထည့်ရင် tool အမည်တွေ ထပ်တူဖြစ်ကုန်မှာ ဖြစ်ပါတယ်။

---

## Topic 3 — Event Loop နှင့် Blocking Trap

### ဘာကို ဆိုလိုတာလဲ

`async def` က function ခေါ်တဲ့အခါ coroutine object တစ်ခုပဲ ပြန်ပါတယ် — တကယ် run တာ မဟုတ်ပါဘူး။ တကယ် run ဖို့ `await` နဲ့ event loop ထဲမှာ ထည့်ပေးရပါတယ်။ Event loop က task တွေကြားမှာ ပြောင်းလဲ while လုပ်ပေးတဲ့ စက်ပါ။

### ဘာကြောင့် လဲ

Coroutine ထဲမှာ `time.sleep` လို blocking ခေါ်ဆိုမှုတစ်ခု ထည့်လိုက်ရင် event loop တစ်ခုလုံး ရပ်တန့်သွားပြီး အခြား task တွေ အားလုံး မလုပ်နိုင်တော့ပါဘူး။ MCP server တစ်ခုလုံးဟာ တစ်ခုခုရဲ့ blocking ကြောင့် တစ်ကြိမ်တည်းနဲ့ ရပ်နိုင်ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

Blocking မလုပ်ဖို့ `await asyncio.sleep()` ကို သုံးရပါတယ်။ တကယ့် blocking library (sync library တွေ) ကို သုံးရမယ်ဆိုရင် `asyncio.to_thread()` နဲ့ သီးသန့် thread ထဲ ပို့ရပါတယ်။ `asyncio.wait_for()` က timeout ထည့်ပေးပြီး ကြာမြင့်တဲ့ ခေါ်ဆိုမှုတွေကို cancel လုပ်ပေးပါတယ်။

### ဥပမာ

``python
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
``

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

MCP API တိုင်းဟာ async ဖြစ်ပါတယ်။ Tool တစ်ခုကို ရေးတိုင်းမှာ blocking ဖြစ်စေတဲ့ ခေါ်ဆိုမှုတွေကို `to_thread` + `wait_for` pattern နဲ့ ဖြေရှင်းဖို့ လိုအပ်ပါတယ်။ LAB 7 နဲ့ LAB 8 မှာ sequential vs concurrent ကို တိုင်းတာကြည့်ရမှာ ဖြစ်ပါတယ်။

---

## Topic 4 — `gather` vs `TaskGroup`

### ဘာကို ဆိုလိုတာလဲ

`asyncio.gather` နဲ့ `asyncio.TaskGroup` နှစ်ခုလုံးက coroutine တွေကို တစ်ပြိုင်တည်း run ပေးပေမယ့် တစ်ခုကျရှုံးတဲ့အခါ အပြုအမူ မတူပါဘူး။

### ဘာကြောင့် လဲ

Tool တစ်ခုထဲမှာ ခေါ်ဆိုမှု များစွာ လုပ်ရင် တစ်ခုကျရှုံးလို့ ကျန်တာတွေ ဘယ်လိုဖြစ်မလဲဆိုတာကို ရွေးချယ်ရမှာ ဖြစ်ပါတယ်။ Partial success ပြန်မလား၊ အားလုံး cancel လုပ်မလားဆိုတာက tool design ရဲ့ အဓိက ဆုံးဖြတ်ချက်ပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

`gather` မှာ default အားဖြင့် exception တစ်ခုတက်လို့ ကျန် task တွေကို cancel လုပ်ပြီး exception ကို ထုတ်ပြပါတယ်။ `return_exceptions=True` ထည့်ရင် error တွေကို value အဖြစ် ရလဒ် list ထဲ ပြန်ပေးပါတယ်။ `TaskGroup` က exception တစ်ခုတက်တာနဲ့ အုပ်စုထဲက task အားလုံးကို cancel လုပ်ပြီး `ExceptionGroup` တစ်ခုတည်း ထုတ်ပါတယ်။

### ဥပမာ

``python
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
``

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Tool တစ်ခုဟာ ရလဒ်တချို့ ရပြီး တချို့ ကျရှုံးတာကို ပြန်ပြချင်ရင် `gather(return_exceptions=True)` က သင့်တော်ပြီး၊ အားလုံး အောင်မြင်မှ ခေါ်ချင်ရင် `TaskGroup` က သင့်တော်ပါတယ်။ LAB 9 မှာ ဒီနှစ်ခုရဲ့ ခြားနားချက်ကို လက်တွေ့ မြင်ရမှာ ဖြစ်ပါတယ်။

---

## Topic 5 — Docstring သည် Tool ရဲ့ စာချက်ချာ

### ဘာကို ဆိုလိုတာလဲ

Tool တစ်ခုရဲ့ docstring ဟာ model ကြည့်ရတဲ့ description ဖြစ်ပြီး၊ Google-style docstring ထဲက Args section က parameter တွေရဲ့ ဖော်ပြချက်အဖြစ် schema ထဲ ရောက်ပါတယ်။

### ဘာကြောင့် လဲ

Schema ဟာ function signature ကနေ ဆောက်တာ ဖြစ်ပြီး description တွေက docstring ကနေ လာပါတယ်။ Docstring format မှန်မမှန်က model ရဲ့ tool ရွေးချယ်မှု တိုက်ရိုက် အာရုံစိုက်စေပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

Google-style docstring မှာ summary တစ်ကြောင်း၊ Args section မှာ parameter တစ်ခုချင်းစီရဲ့ အမည်၊ type နဲ့ ဖော်ပြချက်၊ Error တွေရှိရင် Raises section တို့ကို စနစ်တကျ ရေးရပါတယ်။ LAB 10 မှာ ဒီ docstring contract ကို test လုပ်ကြည့်ရမှာ ဖြစ်ပါတယ်။

### ဥပမာ

``python
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
``

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

ဒီ docstring format ဟာ M4/M5 အတွက် အခြေခံ ဖြစ်ပြီး `lab_10_docstring_contract.py` ကို အသုံးပြုပြီး format မှန်ကန်မှုကို စစ်ဆေးနိုင်ပါတယ်။ ထို့ပြင် LAB 11 ရဲ့ audit harness က tool တွေရဲ့ metadata နဲ့ async-ness ကို အလိုအလျောက် စစ်ပေးပါတယ်။

---

## အနှစ်ချုပ်

- Decorator ဆိုတာ function ကို လက်ခံပြီး function ပြန်ပေးတဲ့ function ဖြစ်ပြီး `@` က apply လုပ်တဲ့ သင်္က fix သာ ဖြစ်သည်။
- `functools.wraps` က မူလ function ရဲ့ `__name__`, `__doc__` တို့ metadata တွေကို wrapper ပေါ် ကူးယူပေးတယ် — မထည့်ရင် MCP tool အမည်အားလုံး `'wrapper'` ဖြစ်သွားတယ်။
- `async def` က function ကို မခေါ်ဘူး၊ coroutine object တစ်ခု ပြန်တယ် — run ဖို့ `await` လိုတယ်။
- Coroutine ထဲမှာ blocking ခေါ်ဆိုမှု (ဥပမာ `time.sleep`) က event loop တစ်ခုလုံးကို ရပ်တန့်စေတယ် — `asyncio.to_thread` နဲ့ ကာကွယ်ပါ။
- ရွေးချယ်စရာ timeout
