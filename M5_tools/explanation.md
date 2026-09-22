# M5 — Action-Oriented Tools (`@mcp.tool`) — ရှင်းလင်းချက်

## အပိုင်း ၁ — စံချိန်မီ Tool တစ်ခု၏ သဘောသဘာဝ

### ဘာကို ဆိုလိုတာလဲ

MCP tool ဆိုတာ model က ခေါ်ဆိုနိုင်သည့် function တစ်ခုဖြစ်သည်။ `@mcp.tool` decorator တစ်ခုတည်းနှင့် ပုံမှန် Python function ကို tool အဖြစ် အလိုအလျောက် မှတ်ပုံတင်ပေးသည်။ စံချိန်မီ tool တစ်ခုသည် — (၁) လုပ်ဆောင်ချက် တစ်ခုတည်း၊ (၂) verb-first အမည်၊ (၃) narrow contract၊ (၄) ရှင်းလင်းသော docstring၊ (၅) type annotation ပြည့်စုံခြင်း — ဤစည်းမျဉ်း ၅ ချက်ကို လိုက်နာရမည်။

### ဘာကြောင့် လဲ

Model သည် JSON Schema ကိုသာ မြင်ရသည်။ Contract ကျယ်လွန်းလျှင် (ဥပမာ `**kwargs`) model သည် မှားယွင်းစွာ ခေါ်ဆိုနိုင်သည့် နည်းလမ်းများ များလာပြီး error နှုန်း တက်လာသည်။ One Action Principle အရ tool တစ်ခုသည် လုပ်ဆောင်ချက် တစ်ခုတည်းကိုသာ လုပ်ရမည်။

### ဘယ်လို အလုပ်လုပ်လဲ

Function ၏ အစိတ်အပိုင်း ၅ ခု (name, docstring, `Args:`, annotations, return annotation) သည် FastMCP မှတဆင့် JSON Schema အဖြစ် ကူးပြောင်းသည်။ Annotation များကို `Annotated`, `Field`, `Literal` ဖြင့် constraint ထည့်နိုင်ပြီး wire name နှင့် description ကိုလည်း override လုပ်နိုင်သည်။

### ဥပမာ

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("calculator")

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers.

    Args:
        a: The first number.
        b: The second number.
    """
    return a + b
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

ကုဒ်ရေးသူများအတွက် မဟုတ် — သင့် tool ကို ခေါ်ဆိုမည့် model အတွက် ဖြစ်သည်။ Schema ရှင်းလင်းလေ၊ model မှားလေ နည်းသည်။

## အပိုင်း ၂ — Raise vs Return

### ဘာကို ဆိုလိုတာလဲ

Exception မြှင့်တင်ခြင်း (raise) နှင့် structured data ပြန်ပို့ခြင်း (return) သည် client ရရှိသည့် `CallToolResult` ပေါ်တွင် ကွဲပြားသည်။ Raise လုပ်လျှင် `isError=True` ဖြင့် အမှားအဖြစ် အသိအမှတ်ပြုခြင်းခံရသည်။

### ဘာကြောင့် လဲ

ရွှေရောင်စည်းမျဉ်းမှာ — **Bad REQUEST** (ဥပမာ parameter မှား) သည် သီးသန့် error တစ်ခုဖြစ်ပြီး **Bad SITUATION** (ဥပမာ ကိန်းစားနိုင်သော်လည်း တန်ဖိုးမရှိ) သည် data အဖြစ် ပြန်ပို့သင့်သည်။ အကြောင်းမှာ နောက်ဆုံးအခြေအနေများသည် ပုံမှန် လုပ်ဆောင်ချက်၏ ရလဒ်တစ်မျိုးဖြစ်သောကြောင့်ဖြစ်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

`_ok()` နှင့် `_fail()` helper များဖြင့် response ပုံစံကို တညီတည်းထားသည်။ Unhandled exception များသည် လုံခြုံရေး အချက်အလက် ယိုစိမ့်နိုင်သောကြောင့် ကိုယ်တိုင် ဖမ်းဆုပ်ကာ စံချိန်မီ error code ထည့်သင့်သည်။ စမ်းသပ်မှုတွင် `raise_on_error=False` သုံး၍ client ဘက်မှ error response ကို စစ်ဆေးနိုင်သည်။

### ဥပမာ

```python
def _ok(data, hint=None):
    # Standard success envelope with an optional hint.
    result = {"ok": True, "data": data}
    if hint:
        result["hint"] = hint
    return result

def _fail(code, message, hint=None):
    # Standard failure envelope the model can act on.
    return {"ok": False, "error": code, "message": message, "hint": hint}
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Model သည် error text တွင် ပါရှိသည့် အချက်အလက်အပေါ် မူတည်၍ နောက်တစ်ဆင့်ကို ဆုံးဖြတ်သည်။ ရှင်းလင်းသော code နှင့် message မရှိလျှင် model က အလွဲအသုံးပြုတတ်သည်။

## အပိုင်း ၃ — The Hint Field

### ဘာကို ဆိုလိုတာလဲ

Hint ဆိုတာ model အတွက် ရေးထားသော အကြံပြုချက်စာသားဖြစ်ပြီး error response ထဲတွင် ပါဝင်သည်။ Schema constraint သည် ခေါ်ဆိုမှု မဖြစ်မီ တားဆီးပြီး၊ runtime hint သည် ခေါ်ဆိုပြီးသည့်နောက် လမ်းညွှန်သည်။

### ဘာကြောင့် လဲ

တိုင်းတာမှုများအရ hint မပါဝင်သည့် error response တွင် model က တစ်ဖန်ပြန်၍ ထပ်မမေးဘဲ ထပ်ခေါ်တတ်သည်။ `_closest()` heuristic ကဲ့သို့ helper ဖြင့် "အနီးစပ်ဆုံး မှန်သော အမည်" ကို hint ထဲထည့်ပေးလျှင် model က ချက်ချင်း ပြင်ဆင်နိုင်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

Hint တစ်ကြောင်းတွင် — (၁) ဘာမှားသည်၊ (၂) ဘာလို့မှားသည်၊ (၃) ဘယ်လိုပြင်ရမည်၊ (၄) ဥပမာ၊ (၅) retry ရမည်လား — ပါဝင်သင့်သည်။ Error များကို retry-able (ယာယီ) နှင့် permanent (အပြီးသတ်) ဟု ခွဲခြား၍ hint တွင် ဖော်ပြသည်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Host orchestrator များ (LangGraph / Claude) သည် hint ကို ဖြတ်သန်း၍ နောက်တစ်ဆင့်ကို ရွေးချယ်ကြသည်။ Hint ကောင်းလျှင် loop နှင့် token ကုန်ကျစရိတ် လျှော့နိုင်သည်။

## အပိုင်း ၄ — Validation နှင့် Async

### ဘာကို ဆိုလိုတာလဲ

Pydantic သည် request ကို tool function ထဲ မရောက်မီ စစ်ဆေးပေးသည် (validation gate)။ Type မကိုက်လျှင် FastMCP က ကိုယ်စားလှယ် error ပြန်ပေးသောကြောင့် သင့် function အတွင်းတွင် type check ထပ်ရေးစရာ မလိုပါ။

### ဘာကြောင့် လဲ

Type rules (အမျိုးအစားစည်းမျဉ်း) ကိ Pydantic က စစ်ပေးပြီး၊ Domain rules (စနစ်စည်းမျဉ်း — ဥပမာ စားလို့ရသောကိန်းလား) ကိုသာ ကိုယ်တိုင် စစ်ရန် ကျန်သည်။ Boundary defense ဖြင့် ကုဒ် ပိုတိုသည်။

### ဘယ်လို အလုပ်လုပ်လဲ

`async def` သည် ဤ module ၏ default ဖြစ်သည်။ I/O-bound tool များ (network ခေါ်ဆိုမှု) ကို `async def` ဖြင့် ရေးလျှင် concurrent အလုပ်လုပ်ပြီး၊ sync tool များသည် event loop ကို ပိတ်ဆို့တတ်သည်။ Coroutine အတွင်းမှ `asyncio.run()` ကို ထပ်ခေါ်၍ မရပါ။

### ဥပမာ

```python
import asyncio

async def fetch_one(client, name: str) -> dict:
    # I/O-bound work: await instead of blocking the event loop.
    await asyncio.sleep(1)
    return {"name": name}

async def main():
    # Concurrent calls finish in about 1 second, not 3.
    results = await asyncio.gather(
        fetch_one(None, "a"),
        fetch_one(None, "b"),
        fetch_one(None, "c"),
    )
    print(results)

asyncio.run(main())
# Expected output: [{'name': 'a'}, {'name': 'b'}, {'name': 'c'}]
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

တိုင်းတာမှုများအရ sequential ၃ ခေါ်ဆိုမှုသည် စုစုပေါင်း ၃ စက္ကန့် ကြာလျှင်၊ concurrent သည် ၁ စက္ကန့်သာ ကြာသည်။ External API tool များတွင် အရေးကြီးသည်။

## အပိုင်း ၅ — httpx၊ Trio၊ Truncation၊ Clamping

### ဘာကို ဆိုလိုတာလဲ

External API ခေါ်ဆိုရာတွင် `httpx` သုံးရမည် — timeout သတ်မှတ်ခြင်း၊ User-Agent ထည့်ခြင်း၊ `raise_for_status()` ခေါ်ခြင်း ဤသုံးချက်ကိ တညီတည်း လိုက်နာရမည်။ "HTTP 200 မဟုတ်သော အောင်မြင်မှု" များရှိသည်။

### ဘာကြောင့် လဲ

Timeout မရှိလျှင် tool တစ်ခုက server တစ်ခုလုံးကို ဆိုင်းငံ့စေနိုင်သည်။ `raise_for_status()` မခေါ်လျှင် error body ကို အောင်မြင်မှုအဖြစ် မှားယွင်းစွာ လက်ခံတတ်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

Tool trio pattern သည် မေးခွန်းတစ်ခုကို tool သုံးခုဖြင့် ဖြေရသည် — `search_articles` (စာလုံးရှာဖွေ)၊ `list_sections` (အပိုင်းအစများ ဖော်ပြ)၊ `get_content` (အန္တရာယ်ကြီး tool၊ ကျည်ကာ)။ Content ကြီးများကို `offset`, `limit`, `truncated`, `next_offset` ပါဝင်သော window tool ဖြင့် ဖြတ်တောက်၍ ပြန်ပို့သည်။ ၁၃၈,၀၀၀ စာလုံး document သည် ၁၇,၂၈၀ chars တစ်ဝက်ခန့်သို့ လျှော့နိုင်သည်။

Untrusted input များကို CLAMP (ကန့်သတ်ချက်ထဲသို့ ကပ်ရန်) သို့မဟုတ် REFUSE (ငြင်းပယ်ရန်) policy တစ်ခုဖြင့် ကိုင်တွယ်ရမည်။ Naive tool များသည် untrusted `limit` ကို အလိုအလျောက် လက်ခံ၍ resource ဆုံးရှုံးစေတတ်သည်။

Wikipedia wikitext သည် shape နှစ်မျိုးရှိပြီး တစ်မျိုးသာ ကိုင်လျှင် crash ဖြစ်တတ်သည် — normalisation တစ်လိုင်းဖြင့် ကာကွယ်နိုင်သည်။ Offline lab များတွင် fixture ဖြင့် အင်တာနက် မလိုပဲ စမ်းသပ်နိုင်ပြီး `--live` flag ဖြင့် fallback ကို ပိတ်၍ စစ်မှန်သော API သို့ ချိတ်ဆက်နိုင်သည်။

### ဥပမာ

```python
def get_content(title: str, offset: int = 0, limit: int = 4000) -> dict:
    # Window over a large document; never dump the whole thing.
    doc = load_document(title)
    chunk = doc[offset:offset + limit]
    truncated = offset + limit < len(doc)
    return {
        "content": chunk,
        "offset": offset,
        "truncated": truncated,
        "next_offset": offset + limit if truncated else None,
    }

print(get_content("long_page", 0, 10))
# Expected output: {'content': 'The first t', 'offset': 0, 'truncated': True, 'next_offset': 10}
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Context window သည် ကန့်သတ်ချက်ရှိသည်။ `truncated=true` ရလျှင် model သည် `next_offset` ကို အသုံးပြု၍ ကျန်အပိုင်းကို ဆက်ဖတ်နိုင်သည် — ဒါကပဲ model နှင့် ကြီးမားသော data ကြားမှာ တံတားဖြစ်သည်။

## အနှစ်ချုပ်

- Tool တစ်ခု = action တစ်ခု၊ verb-first အမည်၊ narrow contract
- Contract အစိတ်အပိုင်း ၅ ခုက JSON Schema ဖြစ်လာသည်
- Bad REQUEST → raise/error၊ Bad SITUATION → data return
- Hint သည် model အတွက် signal တစ်ခု ဖြစ်သည် — retry-able လား permanent လား ဖော်ပြပါ
- Pydantic က type rules ကို စစ်ပေးသည်၊ ကိုယ်က domain rules ကိုသာ စစ်ရမည်
- `async def` + `httpx` hygiene (timeout, User-Agent, `raise_for_status()`)
- Trio pattern + truncation window ဖြင့် context window ကို ကာကွယ်ပါ
- Untrusted limits ကို CLAMP သို့ REFUSE ဖြင့် ကိုင်တွယ်ပါ
