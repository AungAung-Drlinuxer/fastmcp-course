# Cheatsheet — M3: asyncio, Decorators and Docstrings

## ဒီဖိုင်မှာ ဘာသင်မလဲ

- ဒီ module တစ်ခုလုံး၏ အချက်အလက်များကို **တစ်နေရာတည်း** ပြန်စုခြင်း
- Decorator, async, docstring — သုံးပိုင်း၏ **တစ်ချက်ကြည့် ဇယား**
- ⭐ အမှားတိုင်း၏ **လက္ခဏာ → အကြောင်းရင်း → ဖြေရှင်းနည်း**
- ဆုံးဖြတ်ချက် ဇယားများ (gather vs TaskGroup၊ sync vs async၊ decorator vs partial)
- Command များနှင့် ဖိုင်စာရင်း

---

## အပိုင်း ၁ — Decorator ၏ အခြေခံ

```python
# decorator = a function that takes a function and returns a function
def logged(fn):
    @functools.wraps(fn)                     # ⭐ mandatory
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


@logged                                       # = probe = logged(probe)
def probe(x: int) -> int:
    """Probe a service."""
    return x
```

```text
⭐ @decorator  သည် f = decorator(f) သာဖြစ်သည်
⭐ @decorator(arg) သည် f = decorator(arg)(f) — အလွှာ တစ်ခု ပို
⭐ @a / @b ထပ်လျှင် `b` အရင် run သည် (fn နှင့် အနီးဆုံး)
```

| လိုအပ်ချက် | ရေးရမည် |
|---|---|
| Call ကို ဖမ်းချင် | `def wrapper(*args, **kwargs)` + `@functools.wraps(fn)` |
| Argument ယူချင် | `def deco(arg): def decorator(fn): ...; return decorator` |
| Registration သာ | `def deco(fn): registry[fn.__name__] = ...; return fn` (wraps မလို) |
| Async tool ဖုံးချင် | `async def wrapper(...)`: + `await fn(...)` |
| Function အချို့ ကြိုဖြည့် | `functools.partial` (decorator မဟုတ်) |

---

## အပိုင်း ၂ — ⭐ Metadata အချက် ၄ ခု

```text
__name__          → tool ၏ နာမည် (model က ခေါ်သည်)
__doc__           → tool ၏ description
__annotations__   → parameters ၏ type (JSON Schema)
__wrapped__       → functools.wraps က ချိတ်ပေးသည် (signature() က လိုက်ကြည့်သည်)
```

### `functools.wraps` မပါလျှင် (တိုင်းတာထားသည်)

| | မပါ | ပါ |
|---|---|---|
| `__name__` | `'wrapper'` | `'provision'` |
| `__doc__` | `None` | `'Provision a VM.'` |
| `__annotations__` | `{}` | ကျန်သည် |
| `__wrapped__` | မရှိ | ရှိ |
| schema `properties` | `{}` | parameters ရှိ |
| tool name (list ထဲ) | `'wrapper'` | `'disk_usage'` |

```text
⭐ trap ကို ရှာတွေ့သည့်နည်းလမ်း —
   name='wrapper'  +  description=''  +  properties={}  +  error မတက်
```

### ⚠️ Decorator အစဉ် bug

```python
first = naive_logger(good)     # metadata gets destroyed
second = logged(first)         # ❌ wraps copies the already-broken version
```

```text
⭐⭐ "garbage in, garbage copied" — functools.wraps သည် copy ကိရိယာ၊
   မှော်ဆရာ မဟုတ်
⭐ ဖြေရှင်းနည်း: function အသစ်မှ စ; @mcp.tool ကို အပေါ်ဆုံးတွင်ထား
```

---

## အပိုင်း ၃ — Closure နှင့် `bind_partial`

```python
def deco(fn):
    signature = inspect.signature(fn)      # ⭐ read once at import time

    def wrapper(*args, **kwargs):
        bound = signature.bind_partial(*args, **kwargs)   # only what the caller provides
        if "username" in bound.arguments:
            check(bound.arguments["username"])
        return fn(*args, **kwargs)
    return wrapper
```

| လိုအပ်ချက် | သုံးရမည် |
|---|---|
| Caller မပေးသည့် default ကို မစစ်ချင် | `bind_partial` |
| Argument အားလုံး ပါရမည် | `bind` |
| Signature ကို call တိုင်း မဖတ်ချင် | import အချိန် closure ထဲ သိမ်း |
| Closure ထဲ rebinding | `nonlocal` |
| Closure မလိုဘဲ state | `wrapper.calls = 0` (attribute) |

---

## အပိုင်း ၄ — async ၏ အခြေခံ

```python
async def fetch(name: str) -> str:            # coroutine function
    await asyncio.sleep(0.25)                 # ⭐ yield point
    return f"{name}:ok"


asyncio.run(main())                            # only once at the entry point
```

```text
⭐ async def f(x)  → coroutine object (body မ run)
⭐ await f(x)      → ဒါမှ run သည်
⭐ await          → control ကို loop သို့ ပြန်ပေးသည် (ရပ်ပြီး စောင့်ခြင်း မဟုတ်)
⭐ coroutine object ကို တစ်ခါသာ await လို့ရ
```

### ── I/O-bound အတွက် ⭐

| အခြေအနေ | ရေးရမည် |
|---|---|
| I/O (HTTP/DB/file) | `async def` + `await` |
| Blocking library (sqlite3, boto3) | `await asyncio.to_thread(fn, ...)` |
| CPU-bound Python | `asyncio.to_thread` (GIL) သို့မဟုတ် process pool |
| Timeout | `await asyncio.wait_for(coro, timeout=T)` |
| Coroutine ထဲ အိပ်ချင် | `await asyncio.sleep(s)` — ⚠️ `time.sleep` မသုံး |

### ⭐ တိုင်းတာထားသည့် နံပါတ်

```text
sequential (4 tasks × 0.25s)     1.03s
concurrent (gather)              0.26s        → 3.9x
to_thread (3 blocking calls)     0.25s  (0.75s serial မှ)
heartbeat ticks: async 9  |  time.sleep 0  |  to_thread 10
```

---

## အပိုင်း ၅ — `gather` vs `TaskGroup`

| | `gather` | `TaskGroup` |
|---|---|---|
| အောင်မြင်လျှင် ရလဒ် | return value (list) | `task.result()` |
| ကျရှုံးလျှင် | **ပထမ exception** raise | `ExceptionGroup` |
| ကျန်တာ | ⚠️ **ဆက်လုပ်နေသည်** | ✅ **cancel လုပ်သည်** |
| Syntax | `await asyncio.gather(...)` | `async with asyncio.TaskGroup() as g:` |
| Order | document order | task အလိုက် |
| Version | အားလုံး | 3.11+ |

```python
# for partial success ⭐ best for MCP tools
report = await asyncio.gather(*(safe(n) for n in names))
# try/except inside safe() → gather never sees the exception
```

| လိုအပ်ချက် | သုံးရမည် |
|---|---|
| အားလုံး အောင်မြင်ရမည် | `asyncio.TaskGroup` |
| Partial success ရမည် | `gather(return_exceptions=True)` + dict ပြောင်း |
| ပြီးသည့်အစဉ် | `asyncio.as_completed` |
| အုပ်စုလိုက် deadline | `wait_for(gather(...), t)` |

---

## အပိုင်း ၆ — Timeout နှင့် Error

```python
try:
    data = await asyncio.wait_for(fetch(url), timeout=10)
except asyncio.TimeoutError:
    return {"ok": False, "error": "timeout", "url": url}     # ⭐ data, not a crash
```

```text
⭐ အပြင်သို့ ခေါ်သည့် ခေါ်ချက်တိုင်းတွင် timeout
⭐ timeout က client ၏ timeout ၏ ၅၀–၇၀% ထား
⭐ wait_for သည် task ကို cancel လုပ်သည် (leak မရှိ)
⭐ 3.11+: asyncio.TimeoutError IS builtins.TimeoutError
```

### Return vs Raise (VERIFIED.md)

| လုပ်ဆောင်ချက် | Client ရရှိသည့်အရာ |
|---|---|
| `return {"ok": False, "error": "..."}` | `CallToolResult(..., is_error=False)` — **data** |
| `raise ZeroDivisionError` | `ToolError` — plan မပါသော error string |

```text
⭐ မျှော်လင့်နိုင်သည့် ကျရှုံးမှု → data အဖြစ် return
⭐ မမျှော်လင့်နိုင်သည့် bug   → raise
❌ `except Exception: pass` — agent အတွက် အဆိုးဆုံး
```

### Retry

```python
async def retry(coro_factory, attempts=3, base_delay=0.05):
    for attempt in range(1, attempts + 1):
        try:
            return await coro_factory(attempt)     # ⭐ function, not coroutine object
        except (asyncio.TimeoutError, RuntimeError):
            await asyncio.sleep(base_delay * (2 ** (attempt - 1)))
    raise RuntimeError(f"all {attempts} attempts failed")
```

```text
✅ Retry: timeout, 503, 429, deadlock
❌ Retry မ လုပ်: 400 validation, 401/403 auth, 404, idempotent မဟုတ်သည့် write
```

---

## အပိုင်း ၇ — Docstring (Google style)

```python
def disk_usage(path: str, human: bool = True) -> dict:
    """Report disk usage for a filesystem path.          <- imperative summary

    Args:
        path: Absolute or relative path to inspect. Must exist on the server host.
        human: When true, scale the numbers to KB/MB/GB instead of raw bytes.

    Returns:
        A dict with total, used and free.

    Raises:
        FileNotFoundError: when the path does not exist on the server host.
    """
```

```text
⭐ စည်းမျဉ်း ၄ ခု:
   1. One-line summary, imperative
   2. ဗလာလိုင်း + Args: (parameter တိုင်း)
   3. တန်ဖိုး ဘယ်လိုရှိရမည်ကို ပြော ("it is a string" မဟုတ်)
   4. ကျရှုံးမှုကို ရေး (Raises: / "Returns an empty list when ...")
```

### ⚠️ Format သည် contract

| Docstring | ရလဒ် |
|---|---|
| summary + `Args:` | ✅ parameter description ၂/၂ |
| `"Does the thing with the stuff."` | ❌ ၀/၂ — description အားလုံး ဆုံး |
| `:param path:` (Sphinx) | ❌ ၀/၂ — parser က မသိ |

```text
⭐⭐ သုံးခုလုံး **register ဖြစ်သည်**၊ error မတက်၊ တစ်ခုသာ အသုံးဝင်သည်
```

### Schema တွင် ဘာလာသလဲ (VERIFIED.md)

| Source | Appears as |
|---|---|
| parameter name | property key |
| annotation / `Literal` | `type` / `enum` |
| `Field(ge=1, le=16)` | `minimum` / `maximum` |
| `Field(default=2)` | `default` |
| `Field(description=...)` | `description` |
| docstring `Args:` | parameter `description` |

---

## အပိုင်း ၈ — MCP API အချက် (VERIFIED.md)

```text
fastmcp 4.0.5 · pydantic 2.13.5 · python 3.11.x
```

| 2.x says | 4.0.5 has | Error |
|---|---|---|
| `ElicitationResult` | `AcceptedElicitation` / `DeclinedElicitation` / `CancelledElicitation` | `ImportError` |
| `tool.inputSchema` | `tool.parameters` | `AttributeError` |
| `template.uriTemplate` | `template.uri_template` | `AttributeError` |
| `await mcp.get_tools()` | `await mcp.list_tools()` | `AttributeError` |

| ဘယ်နေရာ | Object | Schema ကို ဖတ်ရာ |
|---|---|---|
| server: `await mcp.list_tools()` | `FunctionTool` | `.parameters` |
| client: `await client.list_tools()` | `Tool` | `.input_schema` |

```text
⭐ `@mcp.tool` သည် registration decorator — သင့် fn ကို မဖုံး၊ ဒါကြောင့်
   `disk_usage("/tmp")` ဆက်ခေါ်လို့ရ
⭐ tool.parameters ကို ပုံနှိပ်ကြည့်ပါ — model မြင်သည့်အရာ အတိအကျ
```

---

## အပိုင်း ၉ — ⭐ အမှား → ဖြေရှင်းနည်း (အဓိကပိုင်း)

| လက္ခဏာ | အကြောင်းရင်း | ဖြေရှင်းနည်း |
|---|---|---|
| `__name__ == 'wrapper'` | `functools.wraps` မပါ | `@functools.wraps(fn)` |
| schema `properties = {}` | wrapper ၏ signature `(*args, **kwargs)` | wraps ထည့်ပါ / `return fn` |
| description `''` | docstring မရှိ | docstring ရေးပါ |
| `"type": "unknown"` | `from __future__ import annotations` | `typing.get_type_hints(fn)` |
| Parameter description မရ | `Args:` format မှား / Sphinx style | Google `Args:` ပြောင်း |
| Tool နှစ်ခု၊ တစ်ခုသာ ပေါ် | နာမည် collision (`'wrapper'`) | wraps ထည့်ပါ |
| `wrapped=True` ဖြစ်လျက် metadata ပျက် | ပျက်ပြီးသား fn ကို wraps | function အသစ်မှ စ |
| `took 0.000s` | sync wrapper အပေါ် async fn | `async def wrapper` + `await` |
| Tool return က JSON မဖြစ် | coroutine object ပြန်သည် | wrapper ကို async လုပ်ပါ |
| `RuntimeWarning: coroutine was never awaited` | `await` မေ့ | await / `asyncio.run` |
| `RuntimeError: cannot reuse already awaited coroutine` | coroutine object ကို နှစ်ခါ await | function ကို ပြန်ခေါ် |
| `asyncio.run() cannot be called from a running event loop` | nested run | async fn ထဲမှ `await` |
| heartbeat ticks = 0 | coroutine ထဲ `time.sleep` | `asyncio.sleep` / `to_thread` |
| Server တစ်ခုလုံး "ရပ်" | blocking call | `await asyncio.to_thread(...)` |
| `TypeError: object str can't be used in 'await' expression` | sync fn ကို await | await ဖျက် / `to_thread` |
| Tool ထာဝရ စောင့်နေသည် | timeout မရှိ | `wait_for(..., timeout=T)` |
| Timeout အလုပ်မလုပ် | `except CancelledError: pass` | ပြန်မြှောက်ပါ (`raise`) |
| `object of type ValueError is not JSON serializable` | `return_exceptions=True` ရလဒ် တိုက်ရိုက်ပြန် | dict အဖြစ် ပြောင်း |
| `SyntaxError: cannot have both 'except' and 'except*'` | `try` တစ်ခုတွင် ရော | `except*` သာ |
| `AttributeError: module 'asyncio' has no attribute 'TaskGroup'` | Python ≤ 3.10 | 3.11+ တင် |
| `AttributeError: 'FunctionTool' object has no attribute 'inputSchema'` | 2.x code | `.parameters` |
| `AttributeError: 'Tool' object has no attribute 'parameters'` | client-side object | `.input_schema` |
| `UnboundLocalError: count` | `nonlocal` မေ့ | `nonlocal count` |
| `TypeError: 'NoneType' object is not callable` | decorator က `return fn` မေ့ | `return fn` |
| `Task was destroyed but it is pending!` | `create_task` reference မသိမ်း | task ကို ကိုင်ထား |

---

## အပိုင်း ၁၀ — ⭐ လက္ခဏာ ၃ ခု

```text
⭐⭐ ဒီ module ၏ အခက်ဆုံး အမှား ၄ ခုတွင် တူညီသည့် လက္ခဏာ ၃ ခု:

၁. error မတက်ပါ
၂. အလုပ်တစ်ဝက် လုပ်ပေးသည် (tool list ထဲ ပါသည် / timing ပြသည်)
၃. "ဘာမှ မပျက်ဘူး" ဟု ထင်ရသည်

→ ⭐ ဒီလက္ခဏာကို မြင်လျှင် error message ကို မရှာပါနဲ့ —
   metadata နှင့် async-ness ကို တိုက်ရိုက် စစ်ပါ
```

---

## အပိုင်း ၁၁ — Audit Harness

```python
PLACEHOLDER_NAMES = {"wrapper", "decorator", "inner", "wrapped", "func", "<lambda>"}

def audit_tool(fn) -> dict:
    problems: list[str] = []
    if getattr(fn, "__name__", "") in PLACEHOLDER_NAMES:
        problems.append("name is a placeholder")
    if not inspect.getdoc(fn):
        problems.append("no docstring")
    if not (getattr(fn, "__annotations__", {}) or {}):
        problems.append("no annotations")
    body = [p for p in inspect.signature(fn).parameters.values()
            if p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)]
    if not body:
        problems.append("signature is only *args/**kwargs")
    return {"verdict": "OK" if not problems else "BROKEN", "problems": problems}
```

```python
# ⭐ error that metadata audit cannot catch
assert inspect.iscoroutinefunction(fn), "tools that do I/O must be async"
```

```text
⭐ နှစ်ခုလုံး လိုသည်: audit_tool(fn)["verdict"] == "OK"  +  iscoroutinefunction(fn)
⭐ verdict ကို OK / BROKEN (သို့ WARN) — M1 ၏ `env_check.py` နှင့် တူညီ
```

---

## အပိုင်း ၁၂ — Command နှင့် ဖိုင်

```bash
cd D:\fastmcp-course

# module codes
uv run python -m M3_asyncio_decorators.code.decorators
uv run python -m M3_asyncio_decorators.code.async_io
uv run python -m M3_asyncio_decorators.code.docstrings

# labs
uv run python -m M3_asyncio_decorators.code.lab_1_decorator_mechanics
uv run python -m M3_asyncio_decorators.code.lab_2_closures
uv run python -m M3_asyncio_decorators.code.lab_3_wraps_trap
uv run python -m M3_asyncio_decorators.code.lab_4_register_tool
uv run python -m M3_asyncio_decorators.code.lab_4b_list_tools
uv run python -m M3_asyncio_decorators.code.lab_5_validated_tool
uv run python -m M3_asyncio_decorators.code.lab_5b_async_decorator
uv run python -m M3_asyncio_decorators.code.lab_6_event_loop
uv run python -m M3_asyncio_decorators.code.lab_7_sequential_vs_gather
uv run python -m M3_asyncio_decorators.code.lab_8_to_thread_timeout
uv run python -m M3_asyncio_decorators.code.lab_9_taskgroup_exceptions
uv run python -m M3_asyncio_decorators.code.lab_10_docstring_contract
uv run python -m M3_asyncio_decorators.code.lab_11_audit_tool
uv run python -m M3_asyncio_decorators.code.lab_11b_audit_async

# ⭐ treat the warning as an error (to catch 'coroutine was never awaited')
uv run python -W error::RuntimeWarning -m M3_asyncio_decorators.code.lab_6_event_loop
```

### တစ်လိုင်း စစ်ဆေးမှုများ

```bash
# check metadata
uv run python -c "
import inspect
from M3_asyncio_decorators.code.decorators import disk_usage
print(disk_usage.__name__, repr(inspect.getdoc(disk_usage)), disk_usage.__annotations__)"

# check signature (effectiveness of wraps)
uv run python -c "
import inspect
from M3_asyncio_decorators.code.lab_5_validated_tool import create_user
print(inspect.signature(create_user))"

# check async-ness
uv run python -c "
import inspect; from fastmcp import FastMCP
mcp = FastMCP('x')
@mcp.tool
async def t(a: str) -> dict:
    '''Do a thing.

    Args:
        a: The a.
    '''
    return {}
print(inspect.iscoroutinefunction(t))"
```

---

## အပိုင်း ၁၃ — နောက်ဆုံး စည်းမျဉ်း ၁၀ ခု

```text
၁.  Wrapper တိုင်းတွင် @functools.wraps — style မဟုတ်၊ tool ကို ဖော်ပြနိုင်စေသည့်အချက်
၂.  Registration decorator များသည် `return fn` — wrapper မဆောက်ပါ
၃.  @mcp.tool ကို အပေါ်ဆုံးတွင်ထား၊ သင့်ကိုယ်ပိုင် decorator များကို အောက်တွင်
၄.  Async tool ကို ဖုံးသည့် wrapper သည် `async def` + `await fn(...)`
၅.  I/O ရှိသည့်အရာအားလုံး `async def` — `time.sleep` ကို coroutine ထဲ မသုံးပါ
၆.  ဖျောက်လို့မရသည့် blocking library → `await asyncio.to_thread(...)`
၇.  အပြင်သို့ ခေါ်သည့် ခေါ်ချက်တိုင်းတွင် `asyncio.wait_for` timeout
၈.  မျှော်လင့်နိုင်သည့် ကျရှုံးမှုကို data အဖြစ် return — `except: pass` မလုပ်ပါ
၉.  Docstring သည် tool description — imperative summary + Args: + ကျရှုံးမှု
၁၀. Error မတက်သည့် bug ကို ကိုယ်တိုင် audit လုပ်ပါ — metadata + async-ness
```

---

## နိဒါန်း

- Decorator = function ယူပြီး function ပြန်ပေး; `@` သည် `f = deco(f)` သာ
- ⭐ `functools.wraps` မပါလျှင် `'wrapper'` / `None` / `{}` — tool သည် ခေါ်လို့မရ၊ error မတက်
- Closure နှင့် `bind_partial` သည် validation decorator များ၏ အခြေခံ
- Argument ယူသည့် decorator တွင် function အလွှာ တစ်ခု ပို; wraps ကို အတွင်းလွှာတွင်သာ
- ⭐ `async def` သည် coroutine object ဆောက်သည်; `await` သည် yield point
- ⭐ gather သည် 4 tasks တွင် ~4x; `time.sleep` သည် heartbeat ticks = 0 (server ရပ်)
- `to_thread` သည် loop ကို လွတ်စေသည် — အလုပ်ကို မမြန်စေပါ
- ⭐ timeout မရှိလျှင် agent သည် client လွတ်သည်အထိ ရပ်နေသည်
- gather vs TaskGroup: orphan task vs cancel; partial success အတွက် `safe()` + gather
- ⭐ Docstring format သည် contract — `Args:` မမှန်လျှင် description အားလုံး ဆုံး၊ error မတက်
- Audit harness: metadata ၄ ခု + `iscoroutinefunction` — CI တွင် run ပါ

## ကိုးကား

- `01-what-is-a-decorator.md` မှ `12-debugging-and-audit.md` — ဖိုင်တိုင်း၏ အကျဉ်းချုပ်
- `14-labs-answers.md` · `15-labs-answers-part2.md` — LAB တိုင်း၏ အဖြေ
- [`../code/`](code/) — module code နှင့် lab ဖိုင်များ
- [`../../VERIFIED.md`](../VERIFIED.md) — စမ်းသပ်ပြီး အတည်ပြုထားသော API အချက်များ