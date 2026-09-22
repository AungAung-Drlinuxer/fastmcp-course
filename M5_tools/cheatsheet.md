# M5 Cheatsheet — Action-Oriented Tools (@mcp.tool)

## ဒီဖိုင်မှာ ဘာသင်မလဲ

- ⭐ ပထမဆုံး ဖတ်ရမည့်အရာ: `./00-beginner-bridge.md` —
  programming အခြေခံ မရှိသေးလျှင် ထိုဖိုင်ကို အရင်ဖတ်ပါ
- ဤ module တစ်ခုလုံး၏ အကျဉ်းချုပ် — ပြန်ကြည့်ရန် ရည်ရွယ်သည့် ဖိုင်
- Tool anatomy → JSON Schema ဇယား
- **Raise vs Return** ဆုံးဖြတ်ရန် ဇယား (M5 ၏ နှလုံးသား)
- Error code များ၊ hint ရေးသည့် ပုံစံ၊ validation error code များ
- async/httpx/truncation/fixture/clamp/normalise — တစ်ကြောင်းချင်း စည်းမျဉ်းများ
- စမ်းသပ်ရန် command များ + မှားလေ့ရှိသည့် အမှားများ၏ ဇယား
- ⚠️ FastMCP 4.0.5 ၏ အမည်များ (2.x tutorial များနှင့် ကွဲပြားသည်)

---

## ၁ — Tool anatomy → wire contract

```text
source ထဲ                         client မြင်သည့်အရာ
────────────────────────────────────────────────────────────────
def divide(a: float, b: float)    →  properties: {a: {...}, b: {...}}
   ↑ parameter အမည်                →  required: [a, b]
a: float                          →  "type": "number"
a: int                            →  "type": "integer"
a: str                            →  "type": "string"
a: list[str]                      →  {"type": "array", "items": {"type": "string"}}
a: Literal["fast", "safe"]        →  "enum": ["fast", "safe"]
a: Annotated[int, Field(ge=0, le=100)]  →  "minimum": 0, "maximum": 100
a: Annotated[str, Field(min_length=3)]  →  "minLength": 3
a: int = 5                        →  "default": 5  (required ထဲ မပါ)
a: Annotated[str, Field(description="...")] → "description": "..."
"""Summary line."""               →  tool.description
Args: a: The numerator.           →  "description": "The numerator."
-> dict                           →  structured content (outputSchema)
(FastMCP အလိုအလျောက်)             →  "additionalProperties": false
```

| ကိစ္စ | ရလဒ် |
|---|---|
| docstring မရှိ | `tool.description` = `None` |
| `Args:` block ထဲ မပါသည့် parameter | `description` **မရ** |
| parser မသိသည့် ခေါင်းစီး (`Inputs:`) | parameter description များ တိတ်ဆိတ်စွာ ပျောက် |
| `@mcp.tool(name="x")` | wire အမည် `x` (function အမည် မဟုတ်) |
| `@mcp.tool(description="...")` | summary ကို override; `Args:` က ဆက်အလုပ်လုပ် |
| `-> float` ပြန် | `.data` = float; `structured_content` = `{"result": ...}` |
| `-> dict` ပြန် | `.data` = သင့် dict ( **ဤဟာ M5 တွင် လိုသည်** ) |

**Docstring ခေါင်းစီး (တိုင်းတာထားသည်):** `Args:` ✅ · `Arguments:` ✅ ·
`Parameters:` ✅ · `Params:` ✅ · `Inputs:` ❌ · `Keyword Args:` ❌ · `Yields:` ❌

```python
# ✅ M5's tool style
@mcp.tool
def divide(a: float, b: float) -> dict:
    """Divide a by b, reporting a zero denominator as data instead of raising.

    Args:
        a: The numerator.
        b: The denominator. Must not be zero.
    """
    if b == 0:
        return _fail("division_by_zero", "The denominator must be non-zero; try a different b.")
    return _ok(result=a / b)
```

---

## ၂ ⭐ — Raise vs Return (ဆုံးဖြတ်ရန် ဇယား)

```text
"ငါ့ bug/environment လား" → raise (သို့) ဖမ်းမထားဘဲ လွှတ်
"caller ၏ ခေါ်မှု လား"     → structured error ပြန် (ok: false, error, hint)
"type/range/enum မှား လား"  → Pydantic ကို လွှတ် (raise လုပ်ပြီးသား)
```

| အခြေအနေ | လုပ်ရမည့်အရာ | ဘယ်သူ ဖမ်းသလဲ | model ရသည့်အရာ |
|---|---|---|---|
| `a="one"` (type မှား) | ဘာမှ မလုပ် | Pydantic | `ToolError: 1 validation error ... [type=float_parsing]` |
| `b` မပါ | ဘာမှ မလုပ် | Pydantic | `[type=missing_argument]` |
| `mode="turbo"` | ဘာမှ မလုပ် | Pydantic | `[type=literal_error]` |
| `extra=1` | ဘာမှ မလုပ် | Pydantic | `[type=unexpected_keyword_argument]` |
| `b=0` | `return _fail(...)` | — | `{"ok": false, "error": "division_by_zero", "hint": "..."}` |
| `x=-4` (√) | `return _fail(...)` | — | `{"ok": false, "error": "negative_input", "hint": "..."}` |
| article မရှိ | `return {"ok": False, ...}` | — | `{"ok": false, "error": "missing_title", "hint": "Run search_articles first"}` |
| upstream 503/timeout | `return {"ok": False, ...}` | — | `{"ok": false, "error": "upstream_unreachable", "hint": "Retry ..."}` |
| `limit=500` (ဖတ်ရန် tool) | clamp + `clamped: true` | — | `{"ok": true, "clamped": true, "limit": 20, ...}` |
| သင့် code ၏ bug | ဖမ်းမထားဘဲ လွှတ် | (log) | — |

**တိုင်းတာထားသည့် ကွာခြားချက်:**

```text
structured error: CallToolResult(is_error=False, structured_content={...}, data={...})
raise လုပ်:       ToolError: Error calling tool 'safe_divide': float division by zero
                 (raise_on_error=False ဖြင့်) is_error=True, structured_content=None, data=None
request error:    is_error=True, structured_content=None, content="1 validation error for call[...]"
```

⭐ **`structured_content: None`** ဆိုသည့် လိုင်းသည် raise လုပ်ခြင်း၏ အကျိုးဆက် —
သင့် error code လုံးဝ ပျောက်သည်။

---

## ၃ — ကုဒ် နှစ်ခု: `_ok` / `_fail`

```python
def _ok(**payload: Any) -> dict:
    return {"ok": True, **payload}


def _fail(code: str, hint: str) -> dict:
    """Every failure carries a machine-readable code AND a human/agent-readable hint.

    The code lets a client branch; the hint is what the model actually reads. Omitting the
    hint produces an agent that retries the same wrong call.
    """
    return {"ok": False, "error": code, "hint": hint}
```

⭐ `_fail(code, hint)` — `hint` သည် **required**; မေ့လို့ မရ။

**Error code စည်းမျဉ်း:** English · snake_case · stable · condition ကို ဖော်ပြ
(`division_by_zero`, `negative_input`, `unknown_sensor`, `missing_title`,
`upstream_unreachable`, `limit_out_of_range`, `offset_out_of_range`, `unknown_section`).

---

## ၄ — အမှား၏ အစိတ်အပိုင်း ၄ ခု (wire ပေါ်တွင်)

```json
{"ok": false,
 "error": "unknown_sensor",
 "hint": "'boiler1' is not a sensor. Available: boiler-01, boiler-02, pump-07. Did you mean 'boiler-01'?",
 "available": ["boiler-01", "boiler-02", "pump-07"],
 "did_you_mean": "boiler-01"}
```

| field | ဘယ်သူ ဖတ်သလဲ | ဘာအတွက် |
|---|---|---|
| `ok` | program + model | အောင်မြင်/မအောင်မြင် (branch လုပ်ရန်) |
| `error` | **program** | machine-readable code (stable) |
| `hint` | ⭐ **model** | ဘာမှားခဲ့ + ဘာရနိုင်သည် + **ဘာလုပ်ရမည်** |
| `available` | program/model | ဖြစ်နိုင်သည့် တန်ဖိုးများ |
| `did_you_mean` | ⭐ program (model) | actionable suggestion |
| `legal` | program | `{"min": 1, "max": 20}` — auto-correct အတွက် |
| `source` | model | `"live"` / `"fixture"` / `"none"` |
| `stale` | program/model | `true` လျှင် fixture သည် အဟောင်းဖြစ်နိုင် |
| `note` | model | ဘာကြောင့် fallback ဖြစ်ခဲ့ |
| `truncated` | ⭐ model | `true` လျှင် နောက်ထပ် ရှိသေး |
| `next_offset` | model | နောက် window ကို ခေါ်ရန် ဂဏန်း |
| `count` / `total` | model | ရလဒ် အရေအတွက် (ရေတွက်ရန် မလိုပါ) |

**Hint ရေးသည့် ပုံစံ ၅ ချက်:** imperative · ဂဏန်းများကို ပြော (`got 500`, `1-20`) ·
နောက် tool/parameter ၏ အမည် · တစ်ကြောင်း–နှစ်ကြောင်း · English။

**Hint မပါလျှင်:** scripted agent သည် **တူညီသည့် ခေါ်မှုကို ထပ်**သည် —
တိုင်းတာထားသည်: hint ရှိ → turn 2 တွင် အောင်မြင်; hint မရှိ → turn 3၊ `succeeded: False`။

---

## ၅ — Validation error codes (တိုင်းတာထားသည်)

| ပို့သည့်အရာ | code |
|---|---|
| `"one"` ကို `float` သို့ | `float_parsing` |
| `None` ကို `float` သို့ | `float_type` |
| `40.5` ကို `int` သို့ | `int_from_float` |
| `"half"` ကို `int` သို့ | `int_parsing` |
| `3.0` ကို `int` သို့ | ✅ လက်ခံသည် (coercion) |
| `140` (`le=100`) | `less_than_equal` |
| `-1` (`ge=0`) | `greater_than_equal` |
| `"a1"` (`min_length=3`) | `string_too_short` |
| `"turbo"` (`Literal`) | `literal_error` |
| parameter မပါ | `missing_argument` |
| မရှိသည့် key | `unexpected_keyword_argument` |
| `5` ကို `str` သို့ (list ထဲ) | `string_type` |

```text
စာသား ပုံစံ:
1 validation error for call[set_fan_speed]
percent
  Input should be less than or equal to 100 [type=less_than_equal, input_value=140, input_type=int]
    For further information visit https://errors.pydantic.dev/2.13/v/less_than_equal
```

⭐ **Function body ထဲ `isinstance`/range check မထည့်ပါနှင့်** — request error များသည်
body မစတင်မီ ဖြစ်သည် (သင့် code ကို မရောက်ပါ)။ Domain rule များသာ code ထဲ ထား။

---

## ၆ — async စည်းမျဉ်း

```text
I/O (HTTP, DB, LLM, file) → async def + await
CPU-only, လျင်မြန်       → def
```

| စည်းမျဉ်း | အကြောင်းရင်း |
|---|---|
| `async def` ထဲ `await` ရှိရမည် | `time.sleep()` က event loop ကို ပိတ်သည် |
| `asyncio.run()` ကို coroutine ထဲ မခေါ်ပါနှင့် | `RuntimeError: cannot be called from a running event loop` |
| Server method များကို `await` လုပ်ပါ | `await mcp.list_tools()` |
| `asyncio.run(main())` ကို entry point တစ်နေရာတည်း | `if __name__ == "__main__":` |
| parallel ခေါ်ရန် `asyncio.gather(...)` | ၃ × 0.3s → sequential `0.98s`၊ concurrent `0.31s` |
| await မလုပ်သည့် coroutine ကို `.close()` | `RuntimeWarning` မထွက်စေရန် |

```python
async def _registry() -> None:
    """List what the server publishes, without a client — useful while developing.

    Async on purpose: calling asyncio.run() here would raise "cannot be called from a running
    event loop", because main() is already inside one. A server method that is async must be
    awaited, not re-entered.
    """
    print("Registered tools:", [t.name for t in await mcp.list_tools()])
```

---

## ၇ — httpx checklist

```python
async with httpx.AsyncClient(timeout=10.0) as client:                  # ⭐ timeout is a must
    response = await client.get(API, params=params,                     # ⭐ params= (not an f-string)
                                headers={"User-Agent": "my-agent/0.1"}) # ⭐ UA is a must
    response.raise_for_status()                                        # ⭐ 4xx/5xx → exception
    payload = response.json()
    if "error" in payload:                                             # ⭐ HTTP 200 error
        return {"ok": False, "error": "upstream_error",
                "hint": f"Upstream rejected the request ({payload['error'].get('code')})."}
    hits = payload.get("query", {}).get("search", [])                   # ⭐ .get() chain
```

| တိုင်းတာထားသည့် အချက် | ရလဒ် |
|---|---|
| UA မပေး (httpx default) | **403** `python-httpx/0.28.1` |
| UA ပေး (`fastmcp-course/0.1`) | 200 `application/json; charset=utf-8` |
| `timeout=0.001` | `httpx.ConnectTimeout` |
| `/slow` + `timeout=0.2` | `httpx.ReadTimeout` |
| `/slow` + `timeout=5.0` | 200 |
| 403 + `raise_for_status()` | `httpx.HTTPStatusError: Client error '403 Forbidden' for url ...` |
| `action=nonsenseaction` | **status 200** + `{"error": {"code": "badvalue"}}` |
| connection မရ | `httpx.ConnectError: All connection attempts failed` |
| httpx default timeout | `Timeout(timeout=5.0)` |

⭐ **စစ်ဆေးမှု ၃ ဆင့်:** transport (`raise_for_status`) → application (`"error" in payload`)
→ shape (`.get(...)` ကွင်းဆက်)။

---

## ၈ — Tool trio (search → enumerate → fetch)

```text
search_articles(query, limit)  → {"ok", "source", "note", "count", "results":[{"title"}]}
list_sections(article)         → {"ok", "source", "article", "count", "sections":[{"index","title","level"}]}
get_content(article)           → {"ok", "source", "title", "length", "truncated", "content"}
read_section(article, heading) → {"ok", "source", "article", "heading", "chars", "text"}
```

| စည်းမျဉ်း | အကြောင်းရင်း |
|---|---|
| `title` သာ ပြန် (`snippet` မပါ) | hit တစ်ခု 400 → 25 chars (တိုင်းတာထားသည်) |
| `count` ကို ပြန်ပါ | model က ရေတွက်ရန် မလို |
| `article`/`title` ကို ပြန်ပါ | ဘာအကြောင်း ဖြေနေသည်ကို model စစ်နိုင်သည် |
| `total` ကို ပြန်ပါ | pagination ဆုံးဖြတ်နိုင်သည် |
| "ရလဒ် ၀" ≠ error | `ok: true, count: 0` (မှန်ကန်သည်) |
| upstream error → `ok: false` | HTTP 200 ဖြင့် လာသည့် `{"error": ...}` |
| Logic ကို plain helper ထဲ (`_content()`) | tool function ကို တိုက်ရိုက် ခေါ်လို့ မရ |
| အလုပ်ကို tool ထဲ ရွှေ့ (`read_section`) | model ကို string ရှာခိုင်းခြင်း = token ကုန် |

---

## ၉ — Truncation

```python
    limit = 4000
    return {
        "ok": True,
        "length": len(text),                 # ⭐ resource size
        "returned": len(window),             # ⭐ window size
        "offset": offset,                    # ⭐ where to start
        "truncated": end < len(DOCUMENT),    # ⭐ any more left?
        "next_offset": end if end < len(DOCUMENT) else None,   # ⭐ Next window
        "content": window,
    }
```

| တိုင်းတာထားသည့် အချက် | တန်ဖိုး |
|---|---|
| စာရွက် (138,000 chars) | ≈ 34,500 tokens |
| window (2000 chars) | ≈ 500 tokens |
| windows needed | 69 |
| `limit=10000000` → clamp | 4000 chars |
| `limit=1` → clamp | 200 chars |
| `offset=-500` → clamp | 0 |
| MCP article (live wikitext) | 17,280 chars → `truncated=True` |
| Python article (live wikitext) | 143,366 chars |

⭐ `CHARS_PER_TOKEN = 4` သည် **ခန့်မှန်းချက်** (တိကျသည့်ဂဏန်း မဟုတ်)။
⭐ **ဖြတ်လျှင် ပြောပါ** — silent truncation သည် model ကို "အားလုံး ဒါပဲ" ဟု ထင်စေသည်။

---

## ၁၀ — Fixture & honest source

```python
try:
    result = await _probe(service)
except Exception as exc:  # noqa: BLE001 — offline is an expected condition here
    return {"ok": True, "source": "fixture",
            "note": f"live probe failed ({type(exc).__name__}); fixture is from "
                    f"{FIXTURES[service]['captured']} and may be stale",
            "stale": True, "service": service, "data": FIXTURES[service]}
return {"ok": True, "source": "live", "note": None, "stale": False, ...}
```

| `source` | အဓိပ္ပါယ် | `ok` |
|---|---|---|
| `"live"` | upstream မှ တကယ် ရ | `true` |
| `"fixture"` | သိမ်းထားသည် data (note + stale ပါ) | `true` |
| `"none"` | data မရခဲ့ (refuse) | `false` |

⭐ **ဘယ်တော့မှ** fixture ကို `"live"` ဟု မပြန်ပါနှင့် (lab တွင် anti-pattern အဖြစ် ပြထားသည်)။
⭐ `--live` flag ဖြင့် fallback ကို ပိတ်လျှင်: `ToolError: Error calling tool
'search_articles': All connection attempts failed` (တိုင်းတာထားသည်)။

---

## ၁၁ — Clamp

```python
def clamp(value: int, low: int, high: int) -> tuple[int, bool]:
    """Return (clamped_value, was_changed) — the flag is what makes the clamp reportable."""
    fixed = max(low, min(high, value))
    return fixed, fixed != value
```

| Policy | ဘယ်အခါ | ကုဒ် |
|---|---|---|
| **CLAMP** | ဖတ်ရန်/စာရင်း tool | `limit = max(1, min(20, limit))` + `clamped: true` |
| **REFUSE** | ပြောင်းလဲ/ကုန်ကျ tool | `if not 1 <= limit <= 20: return {"ok": False, "error": "limit_out_of_range", "hint": ..., "legal": {...}}` |

**တိုင်းတာထားသည်:** `limit=500 → 20 (clamped=True)`, `limit=0 → 1`,
`limit=-3 → 1`, `offset=9999 → 29 (clamped=True)`, `offset=25 → count=5 (clamped=False)`။
Naive tool: `limit=500` → ၃၀ ခု၊ **error မရှိ၊ ဘာမှ မပြော** ← အန္တရာယ်။

⚠️ `Field(le=20)` နှင့် clamp ကို **တစ်ချိန်တည်း မထားပါနှင့်** — clamp ကို မရောက်တော့ပါ။

---

## ၁၂ — Wikitext shape normalisation

```python
def wikitext_of(parse: dict) -> str:
    """Normalise both upstream shapes to a string. The whole fix is this one line."""
    raw = parse.get("wikitext", "")
    return raw.get("*", "") if isinstance(raw, dict) else (raw or "")
```

| shape | ဖြစ်နိုင်သည့် error |
|---|---|
| `str` | `AttributeError: 'str' object has no attribute 'get'` |
| `{"*": "..."}` | `TypeError: unhashable type: 'slice'` |
| `None` | `TypeError: object of type 'NoneType' has no len()` |

⭐ Tool ထဲတွင် `"shape": type(raw).__name__` ကို ပြန်ပြောပါ။
⭐ Test ကို **shape နှစ်မျိုးလုံး** ဖြင့် ရေးပါ (`get_text_naive` က small တွင် အောင်မြင်)။

---

## ၁၃ — စမ်းသပ်ရန် command များ

```bash
# Reading the registry without a client
uv run python -c "import asyncio; from M5_tools.code.calculator import mcp; print([t.name for t in asyncio.run(mcp.list_tools())])"
# → ['divide', 'sqrt_of', 'safe_divide']

# Reading the schema (server-side: .parameters)
uv run python -c "import asyncio, json; from M5_tools.code.calculator import mcp; ts=asyncio.run(mcp.list_tools()); print(json.dumps(ts[0].parameters, indent=2))"

# Descriptions
uv run python -c "import asyncio; from M5_tools.code.calculator import mcp; print([(t.name, t.description.splitlines()[0]) for t in asyncio.run(mcp.list_tools())])"

# Run the modules
uv run python -m M5_tools.code.calculator
uv run python -m M5_tools.code.wikipedia                 # With fixture fallback
uv run python -m M5_tools.code.wikipedia --live           # Live only (ToolError if offline)
uv run python -m M5_tools.code.lab_5_tool_trio --offline

# labs
uv run python -m M5_tools.code.lab_1_error_taxonomy
uv run python -m M5_tools.code.lab_2_hint_contract
uv run python -m M5_tools.code.lab_3_validate_the_boundary
uv run python -m M5_tools.code.lab_4_async_and_loop
uv run python -m M5_tools.code.lab_6_offline_fixture_server
uv run python -m M5_tools.code.lab_7_wikitext_normalise
uv run python -m M5_tools.code.lab_8_docstring_contract
uv run python -m M5_tools.code.lab_9_http_client_hygiene
uv run python -m M5_tools.code.lab_10_truncation_budget
uv run python -m M5_tools.code.lab_11_clamp_untrusted_limits

# Suppressing stderr (FastMCP's rich log)
uv run python -m M5_tools.code.lab_1_error_taxonomy 2>/dev/null

# Check imports (syntax)
uv run python -c "import M5_tools.code.calculator, M5_tools.code.wikipedia"
```

---

## ၁၄ — ⚠️ API အမည်များ (FastMCP 4.0.5)

| 2.x tutorial များက ဆိုသည် | 4.0.5 တွင် တကယ် ရှိသည် | မှားလျှင် မြင်ရမည့်အရာ |
|---|---|---|
| `tool.inputSchema` | `tool.parameters` (server) / `.input_schema` (client) | `AttributeError` / deprecation warning |
| `await mcp.get_tools()` | `await mcp.list_tools()` | `AttributeError: 'FastMCP' object has no attribute 'get_tools'` |
| `template.uriTemplate` | `template.uri_template` | `AttributeError` |
| `ElicitationResult` | `AcceptedElicitation` / ... (M8) | `ImportError` |
| `Client(str(path))` | `Client(Path(...))` (deprecated) | `FastMCPDeprecationWarning` |

| နေရာ | object | schema ကို ဖတ်သည့်အမည် |
|---|---|---|
| server: `await mcp.list_tools()` | `FastMCP` | `.parameters` |
| client: `await client.list_tools()` | `Tool` | `.input_schema` |

⭐ `Client(mcp)` (in-process, default `mode="auto"`) → `protocol_version == "2026-07-28"`
(တိုင်းတာထားသည်)။ M8 ၏ elicitation အတွက် `mode="legacy"` လိုသည် (`protocol_version ==
"2025-11-25"`)။

---

## ၁၅ — မှားလေ့ရှိသည့် အမှား ၁၅ ခု → လက္ခဏာ → ဖြေရှင်းနည်း

| လက္ခဏာ | အကြောင်းရင်း | ဖြေရှင်းနည်း |
|---|---|---|
| `ToolError: Error calling tool 'x': float division by zero` | tool က raise လုပ်သည် | structured error ပြန်ပါ (`_fail`) |
| model က တူညီသည့် ခေါ်မှုကို ထပ်သည် | `hint` မပါ | `hint` + `did_you_mean` ထည့်ပါ |
| `structured_content: None` | raise (သို့) validation error | domain failure ကို dict ပြန်ပါ |
| `unexpected_keyword_argument` | `additionalProperties: false` | schema ထဲက parameter များသာ ပို့ပါ |
| `ToolError: 1 validation error ...` | type/range/enum မှား | argument ပြင်ပါ (သို့) `Literal` သုံးပါ |
| `isinstance` check က တစ်ခါမှ run မဖြစ် | Pydantic က စစ်ပြီးသား | annotation ကို ပြောင်းပါ |
| `RuntimeError: cannot be called from a running event loop` | coroutine ထဲ `asyncio.run()` | `await` လုပ်ပါ |
| `RuntimeWarning: coroutine ... was never awaited` | `await` မေ့ | `await` (သို့) `.close()` |
| `verdict concurrent is faster: False` | `time.sleep` in async tool | `await asyncio.sleep` |
| `AttributeError: 'str' object has no attribute 'get'` | string ကို dict ဟု ထင်နေသည် | `isinstance(raw, dict)` |
| `TypeError: unhashable type: 'slice'` | dict ကို slice လုပ်နေသည် | normaliser သုံးပါ |
| `403 Forbidden` | User-Agent မရှိ | `headers={"User-Agent": ...}` |
| `ConnectTimeout` / `ReadTimeout` | timeout လွန်သည် | `TimeoutException` ဖမ်းပြီး transient hint |
| `KeyError: 'search'` (upstream) | error payload | `"error" in payload` + `.get()` ကွင်းဆက် |
| output ကြီးလွန်သည် / context ပြည့် | truncation မရှိ | `truncated` + `next_offset` + `limit` |

---

## နိဒါန်း

- Tool တစ်ခုသည် **contract** တစ်ခု — အမည်၊ docstring၊ `Args:`၊ annotations၊ return
- **Bad request → Pydantic**; **bad situation → structured error**; **သင့် bug → raise**
- ⭐ Structured error သည် `is_error=False` + `structured_content` ဖြင့် ရောက်သည်; raise သည်
  ထို နှစ်ခုလုံးကို **ဖျက်သည်**
- ⭐ `hint` သည် model ဖတ်သည့် တစ်ခုတည်းသော အစိတ်အပိုင်း — hint မရှိလျှင် agent က
  တူညီသည့် ခေါ်မှုကို ထပ်
- async (I/O), httpx (timeout + UA + `raise_for_status`), trio (search/enumerate/fetch),
  truncation (`truncated`+`next_offset`), fixture (`source`), clamp (`clamped`+`legal`),
  normalise (shape) — ဒါ M5 ရဲ့ ကိရိယာသေတ္တာ
- ⭐ **Registry ကို အမြဲ ဖတ်ပါ**: `[t.name for t in await mcp.list_tools()]`

## ကိုးကား

- [`../code/calculator.py`](code/calculator.py) · [`../code/wikipedia.py`](code/wikipedia.py)
- `./14-labs-answers.md` — LAB ၁၂ ခု၏ အဖြေများ
- [`../../VERIFIED.md`](../VERIFIED.md) — စမ်းသပ်ပြီး အတည်ပြုထားသည့် API အချက်များ
- `M5 — file 1` · `M5 — file 3 (raise vs return)` ·
  `M5 — file 4 (hint)`