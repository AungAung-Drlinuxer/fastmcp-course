# M5 — Action-Oriented Tools (`@mcp.tool`) — ရှင်းလင်းချက်

## အပိုင်း ၁ — စံချိန်မီ Tool တစ်ခု၏ သဘောသဘာဝ

### ဘာကို ဆိုလိုတာလဲ

MCP tool ဆိုတာ — model က ခေါ်လို့ရတဲ့ Python function တစ်ခုပါပဲ။ `@mcp.tool` decorator ဆိုတာ — function ရှေ့မှာ တစ်ကြောင်းတပ်ရုံနဲ့ အဲဒီ function ကို tool အဖြစ် အလိုအလျောက် မှတ်ပေးတဲ့ စာကြောင်းလေးပါ။ သူ့ကို စားပွဲပေါ်က ခလုတ်လေးနဲ့ နှိပ်တာလိုပဲ — ဘယ် function မှာ တပ်လဲ အဲဒီဟာ tool ဖြစ်သွားတယ်။

စံချိန်မီ tool တစ်ခုမှာ စည်းမျဉ်း ၅ ချက် ရှိပါတယ်။ (၁) လုပ်ငန်း တစ်ခုတည်း၊ (၂) နာမည်ကို verb နဲ့ စတယ်၊ (၃) contract က ကျဉ်းတယ်၊ (၄) docstring က ရှင်းတယ်၊ (၅) type annotation ပြည့်စုံတယ်။

### ဘာကြောင့် လဲ

Model က ကျွန်တော်တို့ရေးတဲ့ code ကို မမြင်ဘူး။ JSON Schema ချည်းပဲ မြင်တယ်။

Contract ကျယ်လွန်းရင် ဘာဖြစ်လဲဆိုတော့ — ဥပမာ `**kwargs` ထည့်လိုက်ရင် — model က မှားခေါ်လို့ရတဲ့ နည်းလမ်းတွေ များသွားတယ်။ အခုခေါ်တာ မှားရင် error ပြန်လာပြီး error နှုန်း တက်သွားတယ်။

One Action Principle အရ — tool တစ်ခုက အလုပ်တစ်ခုတည်းကိုပဲ လုပ်ရမယ်။ ဒါမှ model ခေါ်တဲ့အခါ ဘာဖြစ်မလဲ အတိအကျ ခန့်မှန်းလို့ရတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

Function ရဲ့ အစိတ်အပိုင်း ၅ ခုက FastMCP ကနေ JSON Schema အဖြစ် ပြောင်းပေးတယ်။ အဆင့်တွေက —

၁။ Function name က tool ရဲ့ နာမည်ဖြစ်သွားတယ်။
၂။ Docstring က tool ရဲ့ ရှင်းလင်းချက်ဖြစ်သွားတယ်။
၃။ `Args:` section က parameter တစ်ခုချင်းစီရဲ့ ရှင်းချက်ဖြစ်တယ်။
၄။ Parameter annotation တွေက type စစ်တဲ့ သတင်းပေးတယ်။
၅။ Return annotation က ရလဒ်ရဲ့ ပုံစံပြတယ်။

Annotation တွေမှာ `Annotated`, `Field`, `Literal` နဲ့ constraint ထည့်လို့ရတယ်။ wire ပေါ်က နာမည်နဲ့ description ကိုလည်း override လုပ်လို့ရတယ်။

### ဥပမာ

ဒီ snippet မှာ `@mcp.tool` တပ်ထားတဲ့ function တစ်ခုက schema အဖြစ် ဘယ်လိုပြောင်းသွားလဲ ကြည့်ရမယ်။ Docstring ထဲက စာ တစ်လုံးချင်း ဘယ်နေရာရောက်လဲ ဆိုတာကို အထူး သတိထားကြည့်ပါ။
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

ဒီအပိုင်းက ကုဒ်ရေးသူအတွက်လည်း အရေးကြီးပေမယ့် — တကယ့် အဓိကက သင့် tool ကို ခေါ်မယ့် model အတွက်ပါ။
Schema ရှင်းလင်းလေ၊ model မှားတတ်လေ နည်းပါတယ်။
Schema မရှင်းရင် model က မှားတဲ့ tool ကို ခေါ်မိပြီး debug လုပ်ရတဲ့ အချိန် ကြာသွားတယ်။

## အပိုင်း ၂ — Raise vs Return

### ဘာကို ဆိုလိုတာလဲ

ဒီနေရာမှာ သုံးတဲ့ စကားလုံးနှစ်ခုရှိပါတယ်။ "Raise" ဆိုတာ — function ထဲမှာ error ဖြစ်နေတယ်ဆိုပြီး exception ကို ပစ်တင်တဲ့ နည်းပါ။ "Return" ဆိုတာ — error ဖြစ်ခဲ့ပြီးလည်း ပုံစံစနစ်ကျတဲ့ data အနေနဲ့ ပြန်ပို့တဲ့ နည်းပါ။
Client က `CallToolResult` လက်ခံရတဲ့အခါ ဒီနှစ်ခုက မတူတဲ့ ရလဒ် ပေးပါတယ်။
ဥပမာ — ဆိုင်က "မရှိဘူး" လို့ ပြန်ပြောတာ (return) နဲ့ ဆိုင်ရှေ့မှာ အော်လိုက်တာ (raise) လိုမျိုး ကွဲပြားတယ်။
Raise လုပ်လိုက်ရင် `isError=True` နဲ့ အမှားအဖြစ် မှတ်ယူခံရတယ်။

### ဘာကြောင့် လဲ

ရွှေရောင် စည်းမျဉ်း (golden rule) တစ်ခုရှိပါတယ်။
**Bad REQUEST** — ဥပမာ parameter မှားတာ — ကို သီးသန့် error တစ်ခုအနေနဲ့ raise လုပ်သင့်တယ်။
**Bad SITUATION** — ဥပမာ ကိန်းစားလို့ရပေမယ့် တန်ဖိုးမရှိတာ — ကိုတော့ data အဖြစ် return ပြန်သင့်တယ်။
ဘာကြောင့်လဲ ဆိုတော့ ဒီလို အခြေအနေတွေက ပုံမှန် လုပ်ဆောင်ချက်ရဲ့ ရလဒ်တစ်မျိုးသာ ဖြစ်လို့ပါ။
Error အားလုံးကို raise လုပ်လိုက်ရင် model က "ဒါ ပုံမှန်ရလဒ်လား၊ အမှားလား" မခွဲနိုင်တော့ပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ `_ok()` နဲ့ `_fail()` helper တွေနဲ့ response ပုံစံကို တစ်ညီတည်း သတ်မှတ်ပါ။
၂။ Tool ထဲမှာ ဖြစ်နိုင်တဲ့ exception တွေကို ကိုယ်တိုင် ဖမ်းဆုပ်ပါ (catch)။
၃။ ဖမ်းတဲ့အခါ စံချိန်မီတဲ့ error code ထည့်ပြီး ပြန်ပို့ပါ။
၄။ ဒါမှ လုံခြုံရေး အချက်အလက်တွေ မယိုစိမ့်ပါ။
၅။ စမ်းသပ်တဲ့အခါ client ဘက်ကနေ `raise_on_error=False` သုံးပါ။
၆။ ဒါဆို error response ကို exception မဖြစ်စေဘဲ စစ်ဆေးနိုင်တယ်။

### ဥပမာ

ဒီ snippet မှာ raise လုပ်တဲ့ tool နဲ့ return ပြန်တဲ့ tool ရဲ့ ကွာခြားချက်ကို ပြထားပါတယ်။
`isError` field နဲ့ client ဘက်က ရလဒ်ကို သတိထားကြည့်ပါ။
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

Model က error စာထဲမှာ ဘာရေးထားလဲ အပေါ်မူတည်ပြီး နောက်တစ်ဆင့် ဘာလုပ်မလဲ ဆုံးဖြတ်ပါတယ်။ Code နဲ့ message မရှင်းရင် model က မှားတဲ့လမ်းကိုပဲ ဆက်သွားတတ်ပါတယ်။ ဒီအခါမျိုးမှာ debug ချိန် ကြာပြီး tool တစ်ခုကို အလွဲခေါ်မိတာတွေ ဖြစ်လာနိုင်ပါတယ်။

## အပိုင်း ၃ — The Hint Field

### ဘာကို ဆိုလိုတာလဲ

Hint ဆိုတာ — error ပြန်တဲ့အခါ model အတွက် ထည့်ပေးထားတဲ့ အကြံပေးစာလေးပါ။ လူနှစ်ယောက်စကားပြောရင် "ဒီလိုပြင်စမ်း" လို့ ခေါ်ပြောတာနဲ့ တူတယ်နော်။ Schema constraint ကတော့ မခေါ်ခင် အဝင်မှာ တားပေးတာပါ။ Runtime hint ကတော့ ခေါ်ပြီးတဲ့နောက် လမ်းညွှန်ပေးတာပါ။

### ဘာကြောင့် လဲ

Hint မပါတဲ့ error မှာ model က ဘာမှန်းမသိဘဲ အဲဒီ tool ကိုပဲ ထပ်ခေါ်တတ်ပါတယ်။ ဒါဆို loop ထဲက မထွက်နိုင်တော့ပါဘူး။ `_closest()` ဆိုတဲ့ helper လေးနဲ့ "အနီးစပ်ဆုံး အမည်မှန်" ကို hint ထဲထည့်ပေးရင် model က ချက်ချင်း ပြင်ပြီး အလုပ်အသင့်ဖြစ်သွားပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ ဘာမှားလဲ ဆိုတာကို ရေးပါ။
၂။ ဘာလို့မှားလဲ ဆိုတာကို ရှင်းပြပါ။
၃။ ဘယ်လိုပြင်ရမလဲ ဆိုတာကို ပြောပါ။
၄။ မှန်တဲ့ ဥပမာတစ်ခု ထည့်ပေးပါ။
၅။ Retry လုပ်ရမလား ဆိုတာ ဖော်ပြပါ။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Host orchestrator (အလုပ်ချိတ်ဆက်ပေးတဲ့ စနစ်)တွေဖြစ်တဲ့ LangGraph / Claude က hint ကို ဖတ်ပြီး နောက်တစ်ဆင့်ကို ရွေးပါတယ်။ Hint ကောင်းရင် ထပ်ခေါ်နေရတဲ့ loop နဲ့ token ကုန်ကျစရိတ် လျော့ပါတယ်။ Hint ဆိုးရင်တော့ token အများကြီး ဖြုန်းပြီး အလုပ်လည်း မအောင်မြင်ပါဘူး။

## အပိုင်း ၄ — Validation နှင့် Async

### ဘာကို ဆိုလိုတာလဲ

Pydantic ဆိုတာ — request က tool function ထဲ မရောက်ခင် စစ်ပေးတဲ့ အကာအလွှာလေးပါ။ Type မကိုက်ရင် FastMCP က ကိုယ်စား error ပြန်ပေးလို့ သင့် function ထဲမှာ type check ထပ်ရေးစရာ မလိုပါဘူး။ တံခါးဝတွင်း အဝင်အထွက်ကို စစ်ပေးတာနဲ့ တူတယ်နော်။

### ဘာကြောင့် လဲ

Type rules (အမျိုးအစား စည်းမျဉ်း) ကိုတော့ Pydantic က စစ်ပေးပြီးသားပါ။ Domain rules (စနစ်ရဲ့ စည်းမျဉ်း — ဥပမာ ကိန်းလား၊ ဘယ်လောက်အထိ ခွင့်ပြုမလဲ) ကိုပဲ ကိုယ်တိုင် စစ်ရန် ကျန်နေတုန်းပါ။ နယ်နိမိတ်မှာပဲ တားဆီးတဲ့ boundary defense ကြောင့် ကုဒ် ပိုတိုသွားပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Tool တိုင်းကို `async def` နဲ့ ရေးရင် ဒီ module ရဲ့ default အတိုင်း ဖြစ်ပါတယ်။
၂။ Network ခေါ်တဲ့ I/O-bound tool တွေကို `async def` နဲ့ ရေးပါ — တစ်ချိန်တည်းမှာ အလုပ်တွေ တပြိုင်တည်း လုပ်ပါတယ်။
၃။ Sync tool ရေးမိရင် event loop (အလုပ်ခွဲဝေတဲ့ စနစ်) ကို ပိတ်ဆို့တတ်ပါတယ်။
၄။ Coroutine (`async def` ထဲက အလုပ်) အတွင်းမှာ `asyncio.run()` ကို ထပ်ခေါ်ရင် မရပါဘူး။

### ဥပမာ

ဒီ snippet မှာ Pydantic က type မှားတာကို ဘယ်လို အလိုက်သင့် error ပြန်လဲ ဆိုတာ ပြထားပါတယ်။ Error message ထဲမှာ ဘယ် field မှားလဲ၊ ဘယ်လိုပြင်ရမလဲ ဆိုတာ ရှင်းရှင်းပါနေမလား ဆိုတာကို စောင့်ကြည့်ပါ။
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

တိုင်းတာကြည့်ရင် sequential နဲ့ ၃ ခါခေါ်ရင် ၃ စက္ကန့်ကြာတယ်ပါ။ ဒါပေမယ့် concurrent နဲ့ ခေါ်ရင် ၁ စက္ကန့်ပဲ ကြာတယ်။ External API tool တွေမှာ ဒီ ကွာခြားချက်က အရမ်းကြီးပါတယ်။ Server တစ်ခုလုံး ရပ်နေရင် user တွေ အားလုံး စောင့်နေရတယ်။

## အပိုင်း ၅ — httpx၊ Trio၊ Truncation၊ Clamping

### ဘာကို ဆိုလိုတာလဲ

External API ခေါ်ရင် `httpx` ကို သုံးရမယ် — timeout သတ်မှတ်တာ၊ User-Agent ထည့်တာ၊ `raise_for_status()` ခေါ်တာ ဆိုတဲ့ စည်းမျဉ်း ၃ ခုကို မဖြစ်မနေ လိုက်ရမယ်။ Timeout ဆိုတာ — ဖုန်းဆက်ပြီး ဘယ်လောက် စောင့်မလဲ ဆိုတဲ့ အချိန်ကန့်သတ်ချက်လေးပါ။ ဒါမှ "HTTP 200 မဟုတ်တဲ့ အောင်မြင်မှု" ဆိုတဲ့ အရာကို မြင်နိုင်မယ်။

### ဘာကြောင့် လဲ

Timeout မထည့်ရင် tool တစ်ခုက server တစ်ခုလုံးကို ဆိုင်းငံ့သွားစေနိုင်တယ်။ တစ်ခြား tool တွေပါ တွဲပြီး ပျက်တယ်။ `raise_for_status()` မခေါ်ရင် error message ပါတဲ့ body ကို "အောင်မြင်တယ်" လို့ မှားယွင်းပြီး လက်ခံမိတယ်။ LLM ကလည်း error ကို အစစ်အမှန် data လို့ ယူဆပြီး အလုပ်ဆက်လုပ်မိတယ်။ ဒါကြောင့် ဒီ စည်းမျဉ်း ၃ ခုက ကာကွယ်ပေးတာပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

Tool trio pattern ဆိုတာ — မေးခွန်းကြီးတစ်ခုကို tool သုံးခုနဲ့ အဆင့်ဆင့် ဖြေတဲ့ နည်းပါ။

၁။ `search_articles` နဲ့ စာလုံး ရှာဖွေတယ်။
၂။ `list_sections` နဲ့ အပိုင်းအစ ဘာတွေရှိလဲ ဖော်ပြတယ်။
၃။ `get_content` နဲ့ အန္တရာယ်ကြီးတဲ့ content အပိုင်းကို ယူတယ်။

Content ကြီးတွေကိုတော့ window tool နဲ့ ဖြတ်တောက်ပြန်ပို့တယ် — `offset`, `limit`, `truncated`, `next_offset` တွေ ပါတယ်။ ဥပမာ — ၁၃၈,၀၀၀ စာလုံးရှိတဲ့ document ကို ၁၇,၂၈၀ chars လောက်အထိ လျှော့ပေးနိုင်တယ်။

Untrusted input — အပြင်က user ရေးတဲ့ data — ကိုတော့ CLAMP (ကန့်သတ်ချက်ထဲ ကပ်တာ) ဒါမှမဟုတ် REFUSE (ငြင်းပယ်တာ) နဲ့ ကိုင်ရတယ်။ Naive tool က untrusted `limit` ကို အတိုင်းအတာမရှိ လက်ခံလိုက်ရင် server resource ဆုံးရှုံးတယ်။

Wikipedia wikitext မှာ shape နှစ်မျိုးရှိတယ်။ တစ်မျိုးပဲ ကိုင်ရင် crash ထွက်တယ်။ normalisation တစ်လိုင်းထည့်ရုံနဲ့ ကာကွယ်လို့ရတယ်။ Offline lab မှာ fixture — သိမ်းထားတဲ့ စမ်းသပ် data လေး — နဲ့ အင်တာနက်မလိုပဲ စမ်းသပ်နိုင်တယ်။ `--live` flag နဲ့တော့ fallback ကို ပိတ်ပြီး အစစ်အမှန် API ကို ချိတ်လို့ရတယ်နော်။

### ဥပမာ

နောက်ပိုင်း code မှာ `httpx` နဲ့ External API ခေါ်တဲ့ tool နဲ့ truncation window နဲ့ ပြန်ပို့တဲ့ tool ကို မြင်ရမယ်။ Timeout သုံးချက်လိုက်နာထားမှုနဲ့ `truncated` flag ဘယ်လိုပြန်လဲဆိုတာကို သတိထားကြည့်ပါ။
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

Context window က ကန့်သတ်ချက်ရှိတယ် — ဆိုလိုတာက model တစ်ကြိမ်မှာ ဖတ်နိုင်တဲ့ စာလုံးရေ အနည်းငယ်ပဲ ရှိတာပါ။ ဒါကြောင့် data ကြီးရင် တစ်ခဏတမ်း အပိုင်းလိုက် ပြပါတယ်။ အဲဒီအခါ `truncated=true` ဆိုတာ ပေါ်လာတယ်။ ဒါက "အပိုင်းကျန်တယ်" လို့ အချက်ပေးတဲ့ အထောက်အထားပါ။ Model က `next_offset` ကို သုံးပြီး ကျန်အပိုင်းကို ဆက်တောင်းနိုင်တယ်။ ဒါကပဲ model နဲ့ data ကြီးကြီးကြားမှာ တံတားသဖွယ် ဖြစ်ပါတယ်။ ဒါမှ breaks မခံရဘဲ production မှာ အလုပ်လုပ်တာပါ။

## အနှစ်ချုပ်

- Tool တစ်ခုက action တစ်ခုပါ — နာမည်ကို verb နဲ့ စရေးပါ၊ contract ကို ကျဉ်းကျဉ်းချုပ်ပါ
- Contract အစိတ်အပိုင်း ၅ ခုက JSON Schema ဖြစ်လာတယ်
- REQUEST မှားရင် → raise/error ပါ၊ SITUATION ဆိုးရင် → data နဲ့ ပြန်ပါ
- Hint က model အတွက် အချက်ပြတစ်ခုပါ — retry လုပ်လို့ ရတာလား၊ မရတာလား ရေးပေးပါ
- Pydantic က type rules ကို စစ်ပေးတယ် — ကိုယ်က domain rules ကိုပဲ ဆက်စစ်ရတယ်
- `async def` + `httpx` သန့်သန့်ရှင်းရှင်း သုံးပါ (timeout, User-Agent, `raise_for_status()`)
- Trio pattern + truncation window နဲ့ context window ကို ကာကွယ်ပါ
- Untrusted limits ကို CLAMP လို့လည်း ကိုင်ရမယ်၊ REFUSE လို့လည်း ကိုင်ရမယ်ပါ