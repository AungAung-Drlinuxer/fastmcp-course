# M3 — asyncio & Decorators : လေ့ကျင့်ခန်း အဖြေများ (solution.md)

## လေ့ကျင့်ခန်း ၁ — Decorator ကို လက်ဖြင့် ဆောက်ခြင်း

```python
def trace(fn):
    # decorator: take a function, return a new function
    def wrapper():
        print("before")
        result = fn()
        print("after")
        return result
    return wrapper

@trace
def hello():
    print("hello")

hello()          # prints before / hello / after
print(hello.__name__)  # 'wrapper' -- metadata was lost on purpose
```

**အဓိကအယူအဆ** — Decorator ဆိုတာ function တစ်ခုကို လက်ခံပြီး အလုပ်လုပ်စေမယ့် function အသစ်တစ်ခုကို ပြန်ပေးတဲ့ function သာ ဖြစ်သည်။

## လေ့ကျင့်ခန်း ၂ — Wrapper ထဲက Closure များ

```python
def count_calls(fn):
    count = 0  # closure state, one memory per decorated function
    def wrapper(*args, **kwargs):
        nonlocal count
        count += 1
        print(f"call #{count}")
        return fn(*args, **kwargs)  # forward everything
    return wrapper

@count_calls
def add(a, b=0):
    return a + b

add(1, b=2)
add(3)
```

**အဓိကအယူအဆ** — Wrapper ထဲမှာ `*args` / `**kwargs` နဲ့ closure state ကို သုံးပြီး မူလ function ရဲ့ အပြုအမူအားလုံးကို မှန်ကန်စွာ ဖြတ်ပို့ပေးရမည်။

## လေ့ကျင့်ခန်း ၃ — Metadata Trap ကို ဖြေရှင်းခြင်း

```python
import functools

def keep_name(fn):
    @functools.wraps(fn)  # copies __name__, __doc__, __module__, __qualname__
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper

@keep_name
def my_tool():
    """Docstring is part of the tool contract."""

print(my_tool.__name__)  # 'my_tool', not 'wrapper'
print(my_tool.__doc__)
```

**အဓိကအယူအဆ** — `functools.wraps` မထည့်ဘဲ decorator ရေးရင် tool နာမည် `wrapper` ဖြစ်သွားပြီး MCP registry မှာ docstring နဲ့ schema အတွက် စာချုပ်တစ်ခုလုံး ပျက်သွားမည်။

## လေ့ကျင့်ခန်း ၄ — `@register_tool` ကို ကိုယ်တိုင် ရေးခြင်း

```python
import functools, inspect

TOOLS = {}

def register_tool(fn):
    # store name, docstring and parameters in a registry dict
    TOOLS[fn.__name__] = {
        "description": inspect.getdoc(fn),
        "parameters": list(inspect.signature(fn).parameters),
        "fn": fn,
    }
    return fn  # registry decorator returns the function unchanged

@register_tool
def greet(name: str) -> str:
    """Say hello to a person."""
    return f"Hello, {name}!"

print(TOOLS["greet"]["description"])
```

**အဓိကအယူအဆ** — Registry decorator က function ကို မဖုံးဘဲ ၎င်းရဲ့ metadata ကို ဖတ်ပြီး စာရင်းထဲ သိမ်းထားတဲ့ pattern က `@mcp.tool` ရဲ့ အခြေခံ အယူအဆ ဖြစ်သည်။

## လေ့ကျင့်ခန်း ၄B — `@mcp.tool` ဖြည့်ထားတဲ့ registry ကို ဖတ်ခြင်း

```python
import asyncio
from mcp.client.session import ClientSession
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(command="python", args=["server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()  # MCP API is async
            for t in tools.tools:
                print(t.name, "--", t.description)

asyncio.run(main())
```

**အဓိကအယူအဆ** — MCP API တိုင်း async ဖြစ်ပြီး `await session.list_tools()` နဲ့ `@mcp.tool` က ဖြည့်သွားတဲ့ registry ကို တကယ့် client ဘက်ကနေ ဖတ်လို့ရသည်။

## လေ့ကျင့်ခန်း ၅ — စစ်ဆေးတဲ့ tool decorator

```python
import functools

def validated(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if not kwargs.get("text"):
            raise ValueError("text must not be empty")
        return fn(*args, **kwargs)
    return wrapper

@validated
def shout(text: str) -> str:
    """Return text in upper case."""
    return text.upper()

print(shout(text="hi"))
```

**အဓိကအယူအဆ** — Decorator validation က call ခဏမှာ စစ်တာ ဖြစ်ပြီး pydantic validation က schema အဆင့်မှာ စစ်တာ ဖြစ်သဖြင့် နှစ်ခုစလုံး လိုအပ်သည်။

## လေ့ကျင့်ခန်း ၅B — Sync နဲ့ async နှစ်ခုလုံး အလုပ်လုပ်တဲ့ decorator

```python
import asyncio, functools, inspect

def audit(fn):
    if inspect.iscoroutinefunction(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            print("async: before")
            return await fn(*args, **kwargs)
    else:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            print("sync: before")
            return fn(*args, **kwargs)
    return wrapper

@audit
async def slow():
    await asyncio.sleep(0.1)

asyncio.run(slow())
```

**အဓိကအယူအဆ** — `inspect.iscoroutinefunction` နဲ့ ခွဲခြားပြီး sync/async နှစ်မျိုးလုံးကို လက်ခံနိုင်တဲ့ decorator တစ်ခုတည်း ရေးသင့်သည်။

## လေ့ကျင့်ခန်း ၆ — Event loop ကို အပြင်ကနေ မြင်ခြင်း

```python
import asyncio, time

async def job(n):
    await asyncio.sleep(0.2)  # await is what actually runs the body
    return n * 2

async def main():
    coro = job(1)  # calling async def does NOT run it
    print(type(coro))       # coroutine, not started
    result = await coro    # a coroutine can only be awaited once
    print(result)

start = time.perf_counter()
asyncio.run(main())
print(f"{(time.perf_counter() - start):.2f}s")
```

**အဓိကအယူအဆ** — `async def` ကို ခေါ်တာက coroutine object တည်ဆောက်တာသာ ဖြစ်ပြီး `await` မလုပ်မချင်း event loop ပေါ်မှာ တကယ် run မည် မဟုတ်ပါ။

## လေ့ကျင့်ခန်း ၇ — Sequential နဲ့ gather ကို တိုင်းတာခြင်း

```python
import asyncio, time

async def io_task(n):
    await asyncio.sleep(0.3)  # non-blocking wait, loop stays free
    return n

async def main():
    t0 = time.perf_counter()
    a = await io_task(1); b = await io_task(2)  # sequential
    t1 = time.perf_counter()
    print(f"sequential: {t1 - t0:.2f}s")

    t0 = time.perf_counter()
    await asyncio.gather(io_task(1), io_task(2))  # concurrent
    t1 = time.perf_counter()
    print(f"gather: {t1 - t0:.2f}s")

asyncio.run(main())
```

**အဓိကအယူအဆ** — `asyncio.sleep` လို non-blocking wait တွေကို `gather` နဲ့ ပေါင်းလိုက်ရင် အချိန်က ပေါင်းလိုက်တာ မဟုတ်ဘဲ အရှည်ဆုံး task တစ်ခုလောက်သာ ကြာမည်။

## လေ့ကျင့်ခန်း ၈ — `to_thread` နဲ့ `wait_for`

```python
import asyncio, time

def blocking_read():
    time.sleep(0.3)  # blocking library, runs in a thread instead
    return "data"

async def main():
    result = await asyncio.wait_for(
        asyncio.to_thread(blocking_read), timeout=0.5
    )
    print(result)

asyncio.run(main())
```

**အဓိကအယူအဆ** — Blocking library ကို coroutine ထဲမှာ တိုက်ရိုက် မခေါ်ဘဲ `asyncio.to_thread` ထဲ ထည့်ပြီး `asyncio.wait_for` နဲ့ timeout သတ်မှတ်တာက tool တိုင်းအတွက် နောက်ဆုံး pattern ဖြစ်သည်။

## လေ့ကျင့်ခန်း ၉ — `gather` vs `TaskGroup`

```python
import asyncio

async def ok(n):
    await asyncio.sleep(0.1)
    return n

async def boom():
    await asyncio.sleep(0.05)
    raise ValueError("one task failed")

async def main():
    results = await asyncio.gather(ok(1), boom(), ok(2),
                                   return_exceptions=True)
    for r in results:
        print(repr(r))  # exception comes back as a value

asyncio.run(main())
```

**အဓိကအယူအဆ** — `gather(return_exceptions=True)` က ကျရှုံးမှုကို value အဖြစ် ပြန်ပေးလို့ partial success ဖန်တီးလို့ရပြီး `TaskGroup` က အမှားတစ်ခုကို ExceptionGroup အဖြစ် တစ်ပြိုင်တည်း ထုတ်ပြမည်။

## လေ့ကျင့်ခန်း ၁၀ — Docstring စာချုပ်

```python
def convert(celsius: float) -> float:
    """Convert a temperature from Celsius to Fahrenheit.

    Args:
        celsius (float): Temperature in degrees Celsius.

    Returns:
        float: Temperature in degrees Fahrenheit.
    """
    return celsius * 9 / 5 + 32

print(convert.__doc__)
```

**အဓိကအယူအဆ** — Docstring က လူအတွက်သာ မဟုတ်ဘဲ model မြင်တဲ့ tool description နဲ့ argument ဖော်ပြချက် ဖြစ်ပြီး Google-style format ကို တသမတ်တည်း လိုက်နာရမည်။

## လေ့ကျင့်ခန်း ၁၁ — Audit harness ဆောက်ခြင်း

```python
import functools, inspect

def audit_tool(fn):
    # verify the metadata a tool registry needs
    problems = []
    if fn.__name__ == "wrapper":
        problems.append("missing functools.wraps")
    if not inspect.getdoc(fn):
        problems.append("missing docstring")
    if problems:
        raise SystemExit(f"{fn.__name__}: {problems}")
    return fn

@audit_tool
def my_tool():
    """A verified tool."""
    return 1

print(my_tool())
```

**အဓိကအယူအဆ** — Audit harness က tool တိုင်းရဲ့ metadata လေးမျိုး (name, doc, module, signature) ကို test တွေနဲ့ အလိုအလျောက် စစ်ပြီး bug ဖြစ်လာခင်း ဖမ်းပေးမည်။

## လေ့ကျင့်ခန်း ၁၁B — Async-ness ကို audit လုပ်ခြင်း

```python
import functools, inspect

def must_be_async(fn):
    # metadata alone cannot prove async-ness, check the type
    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        if not inspect.iscoroutinefunction(fn):
            raise TypeError(f"{fn.__name__} must be async def")
        return await fn(*args, **kwargs)
    return wrapper

@must_be_async
async def tool_a():
    return "ok"

import asyncio
print(asyncio.run(tool_a()))
```

**အဓိကအယူအဆ** — Metadata မြင်လို့ မရတဲ့ async ဖြစ်မဖြစ်ကို `inspect.iscoroutinefunction` နဲ့ runtime မှာ တိုက်ရိုက် စစ်ဆေးရမည်။
