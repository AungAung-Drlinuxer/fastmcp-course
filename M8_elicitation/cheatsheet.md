# Cheatsheet — M8 elicitation, on a few pages

## ဒီဖိုင်မှာ ဘာသင်မလဲ

- ဒီ module တစ်ခုလုံး၏ **အချက် ၁၀** (တစ်မျက်နှာ စည်းမျဉ်း)
- API အကျဉ်း: `ctx.elicit(...)`, `ctx.session.elicit_url(...)`, `response_type` ဇယား
- `mode` ဇယား၊ outcome ဇယား၊ handler contract နှင့် template
- Gate / handler / test / URL mode အတွက် စစ်ဆေးစာရင်း လေးခု
- ⛔ "မလုပ်ရ" စာရင်း (အမှားများဆုံး အလေ့အကျင့်)
- CI တွင် ဘယ်လို run မလဲ
- စကားလုံး အဘိဓာန် (English term → Burmese ရှင်းလင်းချက်)

---

## အပိုင်း ၁ — စည်းမျဉ်း ၁၀

``text
1.  Elicitation သည် လူကို မေးသည် — model ကို မဟုတ်။
    → ဖြေချက်သည် protocol အဆင့်တွင် လူဆီက လာသည် (ဖိုင် ၀၁)

2.  Client(mcp, mode="legacy", elicitation_handler=handler)
    → mode="legacy" မပါလျှင် ToolError: ... unavailable on 2026-07-28 connections (ဖိုင် ၀၇)

3.  response_type ကို အမြဲ ပေးပါ။
    → bool (confirmation) | str (typed) | Literal/list (dropdown) | BaseModel (form) (ဖိုင် ၀၃-၀၄)

4.  Handler သည် async def ဖြစ်ရမည်၊ parameter လေးခု။
    → async def handler(message, response_type, params, context) (ဖိုင် ၀၈)

5.  Outcome သည် return value ဖြစ်သည် — exception မဟုတ်၊ None မဟုတ်။
    → dict/model = accept | ElicitResult(action="decline") | ElicitResult(action="cancel") (ဖိုင် ၀၆)

6.  accept ကို အရင်စစ်ပြီးမှ .data ဖတ်ပါ။
    → action = getattr(result, "action", "accept"); if action != "accept": ... (ဖိုင် ၀၆)

7.  decline ရလျှင် ထပ်မမေးပါ။ cancel ရလျှင် သန့်ရှင်းစွာ ရပ်ပြီး partial state မချန်ပါ။
    → policy ဇယားဖြင့် ရေးပါ (retry=False သုံးမျိုးလုံး) (ဖိုင် ၀၆)

8.  State ကို လူက ခွင့်ပြုပြီးမှ ပြောင်းပါ။
    → try/finally ဖြင့် ရှင်းပါ (ဖိုင် ၀၉)

9.  Server ကိုယ်တိုင် ရှာနိုင်သည့်အရာကို လူကို မမေးပါ။
    → "has moved its own work onto the user" (ဖိုင် ၁၀)

10. Secret / OAuth / payment အတွက် form မသုံးပါ — URL mode သုံးပါ။
    → await ctx.session.elicit_url(message=..., url=..., elicitation_id=...) (ဖိုင် ၀၅)
``

---

## အပိုင်း ၂ — API အကျဉ်း

### Form mode

``python
result = await ctx.elicit(
    message="What date and seat would you like for the flight to Yangon?",
    response_type=BookingDetails,          # required
    # response_title="..."                 # optional; scalar only (TypeError on a model)
    # response_description="..."           # optional; scalar only
)

action = getattr(result, "action", "accept")     # "accept" | "decline" | "cancel"
if action != "accept":
    return {"ok": False, "status": action}
data = result.data                              # available only on accept
``

### URL mode

``python
result = await ctx.session.elicit_url(
    message="Calendar access needs your authorisation. Open the link below, approve, come back.",
    url="https://auth.example.com/oauth/authorize?client=assistant&scope=calendar",
    elicitation_id="calendar-consent-001",
    related_request_id=ctx.request_id,
)

if result.action != "accept":
    return {"ok": False, "status": result.action}
# accept = user consented to open the browser — it is NOT proof a credential arrived
``

### Response ရဲ့ အမျိုးအစားများ

| ဘယ်နေရာ | Object | Attribute |
|---|---|---|
| server, form, accept | `AcceptedElicitation[T]` | `.action`, `.data` |
| server, form, decline | `DeclinedElicitation` | `.action` (data မရှိ) |
| server, form, cancel | `CancelledElicitation` | `.action` (data မရှိ) |
| server, URL mode | `mcp_types.ElicitResult` | `.action`, `.content` (များသောအားဖြင့် `None`) |
| client/handler | handler ၏ return value | — |

### `response_type` ဇယား (schema အပါ)

| response_type | Schema (wire) | UI | `.data` |
|---|---|---|---|
| `str` | `{"properties": {"value": {"type": "string"}}, "required": ["value"]}` | text | `str` |
| `bool` | `... {"type": "boolean"} ...` | checkbox | `bool` |
| `int` | `... {"type": "integer"} ...` | number | `int` |
| `float` | `... {"type": "number"} ...` | number | `float` |
| `Literal["a","b"]` | `... {"enum": ["a","b"]} ...` | dropdown | `str` |
| `["a","b"]` | `... {"enum": ["a","b"]} ...` | dropdown | `str` |
| `{"a": {"title": "A"}}` | `oneOf` + `const` + `title` | dropdown + label | `str` |
| `[["a","b"]]` | `{"type": "array", "items": {"enum": [...]}}` | multi-select | `list[str]` |
| `[{"a": {"title": "A"}}]` | `array` + `items.anyOf` | multi-select + label | `list[str]` |
| `BaseModel` | model ၏ properties | form | model instance |

⭐ Scalar (str/bool/int/float) နှင့် `Literal`/`list[str]` များသည် `{"value": ...}` အတွင်း
ထုပ်သည် → handler က `{"value": ...}` ပြန်ပါ (ဖိုင် ၀၃)။

### `mode` ဇယား

| `mode=` | protocol_version | elicitation | မှတ်ချက် |
|---|---|---|---|
| *(default)* / `"auto"` | `2026-07-28` | ⛔ | `server/discover` ကို စမ်း |
| `"legacy"` | `2025-11-25` | ✅ | handshake era; ⭐ ဒါကို သုံးပါ |
| `"2026-07-28"` | `2026-07-28` | ⛔ | တိုက်ရိုက် လက်ခံ |
| `"2025-11-25"` | — | — | `ValueError` (mode မဟုတ်) |
| `"2025-06-18"` | — | — | `ValueError` |

### Outcome ဇယား

| action | လူက ဘာလုပ်ခဲ့သလဲ | payload | လိုသည့် policy |
|---|---|---|---|
| `accept` | form ဖြည့် / ခွင့်ပြု | `.data` (form) / `.content` (URL) | ဆက်လုပ်ပါ |
| `accept` + `proceed=False` | form ဖြည့်ပြီး ငြင်း | `.data.proceed == False` | `refused_by_user`; reason ကို သိမ်းပါ |
| `decline` | တမင်တကာ ငြင်း | မရှိ | ⛔ retry မလုပ်ပါ; report လုပ်ပါ |
| `cancel` | ဖြေခြင်းမရှိဘဲ ထွက် | မရှိ | ⛔ retry မလုပ်ပါ; partial state မချန်ပါ |

---

## အပိုင်း ၃ — Handler contract

``python
async def handler(message: str, response_type: Any, params: Any = None,
                  context: Any = None) -> Any:
    ...
``

| # | Parameter | ရရှိသည့်အရာ | URL mode |
|---|---|---|---|
| 1 | `message` | server ၏ စာသား | ရှိသည် |
| 2 | `response_type` | schema မှ **client ဆောက်သည့်** class | `None` |
| 3 | `params` | `.mode`, `.requested_schema`, `.url`, `.elicitation_id` | `.mode == "url"` |
| 4 | `context` | request context | ရှိသည် |

``text
⭐ မဖြစ်မနေ async def (sync def → object dict can't be used in 'await' expression)
⭐ parameter လေးခု (three → takes 3 positional arguments but 4 were given)
⭐ return ဖြင့် သာ outcome ဖော်ပြသည် (raise → ToolError; None → MCPError)
``

---

## အပိုင်း ၄ — Handler တစ်ခုကောင်း ရေးခြင်း (စစ်ဆေးစာရင်းနှင့် template)

``text
□ async def ဖြစ်သည်
□ parameter လေးခု ရှိသည် (message, response_type, params, context)
□ လမ်းကြောင်းအားလုံးတွင် တန်ဖိုးတစ်ခု return ဖြစ်သည် (None မဟုတ်)
□ outcome ကို ElicitResult ဖြင့် ဖော်ပြသည်
□ raise မလုပ်ပါ (exception ကို ToolError အဖြစ် ပြောင်းသည့်အတွက်)
□ URL mode ကို ခွဲထားသည် (mode == "url")
□ params.requested_schema ကို getattr ဖြင့် ဖတ်သည်
□ required field များ အားလုံး ဖြည့်သည်
□ secret များကို print/log မလုပ်ပါ
□ timeout / dismiss case ကို cancel အဖြစ် ဖော်ပြသည်
``

### ဥပမာ — စစ်ဆေးစာရင်းကို လိုက်နာသည့် handler

``python
from fastmcp.client.elicitation import ElicitResult


def make_realistic_handler(answers_by_field: dict[str, Any]):
    """A small host: it answers what the schema asks for, and nothing else."""

    async def handler(message: str, response_type: Any, params: Any = None,
                      context: Any = None) -> Any:
        if getattr(params, "mode", "form") == "url":
            # The browser performs the sensitive part; the user consented to open it.
            return ElicitResult(action="accept")

        schema = getattr(params, "requested_schema", None) or {}
        properties = schema.get("properties", {})

        # A form with no fields: nothing to answer, but still a decision.
        if not properties:
            return ElicitResult(action="accept")

        payload = {name: answers_by_field[name]
                   for name in properties if name in answers_by_field}

        missing = [name for name in schema.get("required", []) if name not in payload]
        if missing:
            # The host cannot invent a required value; it cancels instead of guessing.
            return ElicitResult(action="cancel")

        return payload

    return handler
``

⭐ နောက်ဆုံး အပိုင်းကို သတိထားပါ: **မဖြစ်မနေ လိုသည့် တန်ဖိုး မရှိလျှင်
`cancel` ပြန်သည် — ခန့်မှန်းသည့် တန်ဖိုး မထည့်ပါ။** ဒါက "လူက မဖြေခဲ့ခြင်း" ကို
"ခန့်မှန်းချက်" အဖြစ် မပြောင်းစေရန် ကာကွယ်သည်။

---

### Debug print တစ်ခုတည်း ရေးထားသည့် handler template

``python
def make_debug_handler(answer: Any):
    """A handler that shows everything the contract gives you."""

    async def handler(message: str, response_type: Any, params: Any = None,
                      context: Any = None) -> Any:
        mode = getattr(params, "mode", "form")
        print(f"    [host] mode={mode!r} response_type={response_type!r}")
        print(f"    [host] message={message!r}")
        if mode == "url":
            print(f"    [host] url={params.url!r} elicitation_id={params.elicitation_id!r}")
            return ElicitResult(action="accept")
        schema = getattr(params, "requested_schema", None)
        print(f"    [host] schema={schema}")
        return answer

    return handler
``

⭐ ဒီ template ကို ဖိုင် ၁၂ (cheatsheet) တွင်လည်း ထည့်ထားသည် — ကူးယူပြီး သုံးလို့ရသည်။

---

## အပိုင်း ၅ — စစ်ဆေးစာရင်း လေးခု

### Gate (risky action) စစ်ဆေးစာရင်း

``text
□ protected စာရင်းသည် code/config ထဲ (prompt ထဲ မဟုတ်)
□ အန္တရာယ်မရှိလျှင် လုံးဝ မမေးပါ
□ message တွင်: ဘယ်အရာ + ဘာဖြစ်မလဲ + မေးခွန်း
□ state ကို accept ပြီးမှ ပြောင်း; try/finally ဖြင့် ရှင်း
□ idempotent (ထပ်ခေါ်လျှင် ထပ်မမေးပါ)
□ outcome လေးမျိုး ခွဲထား
□ audit: gate + status + ticket/reason; append-only
□ server ဘက်စစ်ဆေးချက် (authorization) သီးသန့်
□ test တစ်ခု ရှိ
``

### Handler စစ်ဆေးစာရင်း

``text
□ async def
□ parameter လေးခု
□ လမ်းကြောင်းအားလုံးတွင် တန်ဖိုး return (None မဟုတ်)
□ outcome ကို ElicitResult ဖြင့်
□ raise မလုပ်ပါ
□ URL mode ကို ခွဲထား (mode == "url")
□ requested_schema ကို getattr ဖြင့်
□ required field အားလုံး ဖြည့်
□ secret ကို print/log မလုပ်
□ dismiss/timeout → cancel
``

### Test စစ်ဆေးစာရင်း

``text
□ accept (proceed=True)
□ accept + proceed=False (refused_by_user)
□ decline (state မပြောင်းကြောင်း assert)
□ cancel (decline နှင့် ကွာ)
□ prompt အရေအတွက် == 1 (retry မရှိ)
□ canary: default mode သည် မရကြောင်း
□ canary: sync handler သည် ပျက်ကြောင်း
□ state ကို fixture ဖြင့် ရှင်း
``

### URL mode စစ်ဆေးစာရင်း

``text
□ https
□ URL ထဲ secret မပါ (client_id/scope သာ)
□ elicitation_id ကို server ဘက်မှ ထုတ်
□ token ကို log/tool output ထဲ မထည့်
□ accept ရလျှင် credential ကို ကိုယ်တိုင် စစ်
□ decline ရလျှင် ထပ်မမေး
□ mode="legacy" ရှိသည်
``

---

## အပိုင်း ၆ — ⛔ မလုပ်ရ စာရင်း

``text
⛔ လူက ငြင်းပြီးမှ ထပ်မေးခြင်း            → prompt များကို လူက မဖတ်တော့ပါ
⛔ decline/cancel ကို error အဖြစ် ပြောင်းခြင်း → model က ထပ်ကြိုးစားသည်
⛔ handler ထဲ raise လုပ်ခြင်း                → ငြင်းဆိုချက်သည် ToolError ဖြစ်သွားသည်
⛔ return None                              → MCPError: Invalid request parameters
⛔ sync def handler                         → object dict can't be used in 'await' expression
⛔ accept မစစ်ဘဲ .data ဖတ်ခြင်း              → decline တွင် AttributeError
⛔ server က ရှာနိုင်သည့် data ကို လူကို မေးခြင်း → ကိုယ့်အလုပ် လူဆီ ရွှေ့ခြင်း
⛔ read-only အလုပ်အတွက် confirm မေးခြင်း     → fatigue
⛔ secret ကို form ဖြင့် မေးခြင်း             → host transcript / model context
⛔ token ကို tool return ထဲ ထည့်ခြင်း         → model က မြင်သည်
⛔ action မစစ်ဘဲ state ကို အရင် ပြောင်းခြင်း  → partial state
⛔ mode="legacy" မေ့ခြင်း                    → unavailable on 2026-07-28 connections
⛔ elicit ကို authorization အနေဖြင့် သုံးခြင်း → policy engine ကို သုံးပါ (M10)
⛔ background task ထဲ imperative elicit       → guard pattern သုံးပါ
⛔ "Are you sure?" ကို နှစ်ခါ မေးခြင်း         → typed confirmation က ပိုကောင်းသည်
``

---

## အပိုင်း ၇ — Error → Fix (အကျဉ်း)

| Error (တိုတိုတု) | ဖြေရှင်းနည်း |
|---|---|
| `unavailable on 2026-07-28 connections` | `mode="legacy"` |
| `Elicitation not supported` | `elicitation_handler=` ထည့် |
| `object dict can't be used in 'await' expression` | handler ကို `async def` |
| `takes N positional arguments but 4 were given` | parameter လေးခု |
| `MCPError: Invalid request parameters` | `{"value": ...}` ပြန်; `None` မပြန် |
| `ToolError: ... <your message>` | `raise` ကို `return` ပြောင်း |
| `AttributeError: ... 'data'` | `accept` ကို အရင်စစ် |
| `AttributeError: requested_schema` | `getattr(params, "requested_schema", None)` |
| `ValueError: mode must be 'legacy', 'auto', ...` | `mode="legacy"` |
| `ImportError: cannot import name 'ElicitationResult'` | `ElicitResult` (client) / `AcceptedElicitation` (server) |
| `not supported inside a background task` | guard pattern (`InputRequiredResult`) |

→ အပြည့်အစုံ: `11-testing-and-debugging.md` အပိုင်း ၇

---

## အပိုင်း ၈ — CI

### CI တွင် run ခြင်း

``bash
uv sync
uv run pytest tests/test_m8_elicitation.py -q          # this module's tests
uv run pytest M8_elicitation/code/lab_10_pytest_elicitation.py -q   # the lab's tests
uv run pytest -q                                       # the whole repo
``

⭐ Lab ၏ test များသည် **module folder ထဲ** တွင်ရှိသည့်အတွက် repo တစ်ခုလုံး run
လုပ်သည့်အခါ အလိုအလျောက် ပါလာသည် (pytest သည် `test_*.py` နှင့် `*_test.py` ကို
ရှာသည်; `lab_10_pytest_elicitation.py` ကို **file path ဖြင့်** run ရသည်)။

``text
⚠️ သတိထားပါ: `uv run pytest` သည် default အားဖြင့် `test_*.py` ကို ရှာသည်
   → `lab_10_pytest_elicitation.py` ကို collect မလုပ်ပါ
   → ⭐ path ဖြင့် တိုက်ရိုက် ပေးပါ (အထက်တွင် ပြထားသည့်အတိုင်း)
``

### CI checklist

``text
□ uv sync (lockfile မှ environment)
□ pytest -q (repo တစ်ခုလုံး)
□ lab ၏ pytest file ကို path ဖြင့် run
□ ⭐ canary test တစ်ခု (default mode သည် မရကြောင်း) — ဒါက version upgrade ကို ဖမ်းသည်
□ flakiness မရှိကြောင်း — ဒီ test များသည် deterministic ဖြစ်ရမည် (network မလို)
``

---

## အပိုင်း ၉ — စကားလုံး အဘိဓာန်

| English | Burmese ရှင်းလင်းချက် |
|---|---|
| elicitation | server က tool အလယ်တွင် ရပ်ပြီး လူကို အချက်အလက်/ခွင့်ပြုချက် မေးခြင်း |
| back-channel | server → client လမ်းကြောင်း (request တစ်ခု လွှတ်နိုင်သည့် လမ်း) |
| protocol era | ချိတ်ဆက်မှုတွင် ကျင့်သုံးသည့် protocol version (`2025-11-25` / `2026-07-28`) |
| handshake | `initialize` ဖြင့် session တည်ဆောက်သည့် သမိုင်းဝင် စတင်ခြင်း |
| sessionless | session မရှိသည့် era; request တိုင်း ကိုယ်ပိုင် (back-channel မရှိ) |
| form mode | client က native form ရေးဆွဲပြီး လူက ဖြည့်သည့် mode |
| URL mode | လူကို browser link ပေးပြီး out-of-band လုပ်ဆောင်သည့် mode |
| response_type | မေးခွန်း၏ ပုံစံ (JSON Schema ကို ဆောက်သည့် source) |
| requested_schema | wire ပေါ်တွင် client ရသည့် JSON Schema |
| handler | host ဘက်တွင် elicitation ကို ဖြေသည့် `async def` function |
| outcome | `accept` / `decline` / `cancel` |
| prompt fatigue | မေးခွန်း အလွန်များလို့ လူက prompt များကို မဖတ်တော့ခြင်း |
| gate | အန္တရာယ်ရှိသည့် အလုပ်ကို ရပ်တန့်ပြီး ခွင့်ပြုချက် မေးသည့် code |
| idempotent | ထပ်ခေါ်လျှင် ထပ်မလုပ်ဘဲ တူညီသည့် ရလဒ် ပြန်ခြင်း |
| canary test | "အခြေအနေက မပြောင်းသေးကြောင်း" ကို စစ်သည့် test |
| out-of-band | server ၏ လမ်းကြောင်းကို မဖြတ်ဘဲ (browser ထဲ) လုပ်ဆောင်ခြင်း |

---

## အပိုင်း ၁၀ — ဖိုင်လမ်းကြောင်း မြေပုံ

``text
Concept  →  01-the-reverse-flow.md        (လမ်းကြောင်း ပြောင်းပြန်)
Code     →  02-booking-py-line-by-line.md (booking.py တစ်လိုင်းချင်း)
API      →  03-the-elicit-call.md         (signature + response_type)
Form     →  04-form-mode-and-schemas.md   (native form + schema subset)
URL      →  05-url-mode.md                (browser flows)
Outcome  →  06-three-outcomes.md          (accept/decline/cancel)
Mode     →  07-the-mode-requirement.md    (mode="legacy" တိုင်းတာထားသည်)
Handler  →  08-the-handler-contract.md    (async, 4 args, return value)
Gate     →  09-protected-service-pattern.md
Don't    →  10-when-not-to-elicit.md
Test     →  11-testing-and-debugging.md
Sheet    →  12-cheatsheet.md              (ဤဖိုင်)
Answers  →  13-labs-answers.md           (lab 1-6)
Answers  →  14-labs-answers-advanced.md  (lab 7-11 + self-check)

Labs (M8_elicitation/code/):
   lab_1_elicit_warmup.py     lab_6_url_flow.py
   lab_2_booking_form.py      lab_7_question_shapes.py
   lab_3_outcome_router.py    lab_8_triage_decides.py
   lab_4_protected_gate.py    lab_9_handler_contract.py
   lab_5_mode_matrix.py       lab_10_pytest_elicitation.py
``

---

## နိဒါန်း

- စည်းမျဉ်း ၁၀ သည် ဒီ module တစ်ခုလုံး၏ အနှစ်ချုပ် — မေးခွန်းတိုင်းကို ဒီအပေါ်
  ပြန်စစ်ပါ
- API သည် နှစ်လိုင်းသာ: `ctx.elicit(message, response_type=...)` နှင့်
  `ctx.session.elicit_url(...)`
- `mode="legacy"` သည် form နှင့် URL mode နှစ်မျိုးလုံးအတွက် မဖြစ်မနေ
- Outcome သည် return value; `.data` ကို `accept` ပြီးမှ ဖတ်ပါ
- စစ်ဆေးစာရင်း လေးခု (gate, handler, test, URL) ကို commit မတိုင်မီ ဖြတ်ပါ
- ⛔ မလုပ်ရ စာရင်းတွင် အကြောင်းရင်းများကို တိုတိုတု မှတ်ထားသည်
- Error → Fix ဇယားသည် ရှာရမည့်နေရာကို ဆိုသည် (အပြည့်အစုံ ဖိုင် ၁၁)

## ကိုးကား

- `13-labs-answers.md` — lab 1-6 ၏ အဖြေ
- `14-labs-answers-advanced.md` — lab 7-11 ၏ အဖြေ
- `11-testing-and-debugging.md` — error triage အပြည့်အစုံ
- [`../../VERIFIED.md`](../VERIFIED.md) — တိုင်းတာထားသည့် အချက်အားလုံး
- [`../code/booking.py`](code/booking.py) — ဤ module ၏ ဥပမာ server