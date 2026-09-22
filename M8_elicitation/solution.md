# M8 — Interactive Elicitation: အဖြေများ (solution.md)

## Lab 1 — Elicitation warm-up

```python
# Minimal elicitation: the server asks the client a question mid-tool.
from mcp.server.fastmcp import Context


@mcp.tool()
async def warmup(ctx: Context) -> str:
    # Ask one simple question and report the raw result.
    result = await ctx.elicit(
        message="Ready to begin? Reply yes or no.",
        response_type="boolean",
    )
    return f"action={result.action} data={result.data}"
```

**အဓိကအယူအဆ** — `await ctx.elicit()` က tool အလယ်မှာ server က client ဆီ တိုက်ရိုက်မေးလို့ရတဲ့ ပထမဆုံး capability ဖြစ်ပါတယ်။

## Lab 2 — The Flight Booking tool, in full

```python
# The booking flow: collect the missing piece before booking.
from pydantic import BaseModel


class FlightChoice(BaseModel):
    # Form mode: the Pydantic model becomes a native form on the host.
    origin: str
    destination: str
    date: str


@mcp.tool()
async def book_flight(origin: str, destination: str, ctx: Context) -> str:
    # Ask for the date only if the caller did not supply one.
    if origin == destination:
        return "origin and destination must differ"
    result = await ctx.elicit(
        message="Please confirm your flight details.",
        response_type=FlightChoice,
    )
    if result.action != "accept":
        return f"booking not confirmed: {result.action}"
    choice = result.data
    return f"booked {choice.origin} -> {choice.destination} on {choice.date}"
```

**အဓိကအယူအဆ** — Elicitation က အားလုံးကို အစကတည်းကမတောင်းဘဲ လိုအပ်တဲ့အချိန်မှာသာ တောင်တဲ့ design ဖြစ်ပါတယ်။

## Lab 3 — Every question shape, and the schema behind it

```python
# Scalar answers arrive wrapped: {"value": ...} inside result.data.
from typing import Literal


class MaintenanceChoice(BaseModel):
    window: Literal["morning", "afternoon", "evening"]


@mcp.tool()
async def ask_everything(ctx: Context) -> str:
    text = await ctx.elicit(message="Your name?", response_type="string")
    flag = await ctx.elicit(message="Subscribe?", response_type="boolean")
    num = await ctx.elicit(message="How many seats?", response_type="number")
    form = await ctx.elicit(
        message="Pick a maintenance window.",
        response_type=MaintenanceChoice,
    )
    return f"{text.data['value']} / {flag.data['value']} / {num.data['value']} / {form.data}"
```

**အဓိကအယူအဆ** — Scalar ပုံစံတွေက `{"value": ...}` နဲ့ ထုပ်ပြီး form mode က Pydantic model တစ်ခုလုံးကို ပြန်ပေးပါတယ်။

## Lab 4 — Design a form the host can render

```python
# Keep the schema inside the restricted subset the host can render.
from pydantic import BaseModel, Field


class BookingForm(BaseModel):
    # required fields force the human to fill every box.
    origin: str
    destination: str
    # default lets the human skip the field.
    seats: int = Field(default=1, ge=1, le=9)
    # enum renders as a dropdown.
    cabin: Literal["economy", "business"] = "economy"
    # optional array renders as multi-select.
    meals: list[str] | None = None
```

**အဓိကအယူအဆ** — Form mode က native form တစ်ခုဖြစ်ပေမယ့် အဆင့်မြင့် Pydantic feature အားလုံးကို မထောက်ပံ့ဘဲ restricted subset တစ်ခုပဲ ထောက်ပံ့ပါတယ်။

## Lab 5 — URL mode: sending the user to a browser

```python
# URL mode: the answer must be typed outside the host, in a browser.
@mcp.tool()
async def login_via_browser(ctx: Context) -> str:
    result = await ctx.elicit(
        message="Continue in your browser: https://example.com/login",
        response_type="url",
    )
    if result.action == "accept":
        return f"user finished the browser flow: {result.data}"
    if result.action == "decline":
        return "user declined the browser flow"
    return "user cancelled before opening the browser"
```

**အဓိကအယူအဆ** — Password သို့မဟုတ် OAuth လို မျိုး type လုပ်သင့်တဲ့အရာတွေကို form နဲ့ မေးမထားပဲ URL mode နဲ့ browser ကို လွှဲပို့ရမယ်။

## Lab 6 — The three outcomes, and the policy each one demands

```python
# Each outcome demands its own policy, written in code.
@mcp.tool()
async def outcome_router(ctx: Context) -> str:
    result = await ctx.elicit(message="Proceed?", response_type="boolean")
    if result.action == "accept":
        if result.data.get("value") is False:
            # Fourth state: accepted the form but answered "no".
            return "acknowledged, will not proceed"
        return "proceeding"
    if result.action == "decline":
        return "user declined; stop and report honestly"
    return "user cancelled; leave state untouched"
```

**အဓိကအယူအဆ** — accept / decline / cancel သုံးမျိုးကို ရောလိုက်ရင် audit trail မှာ ဘယ်သူ့ကိုမှ ယုံမကြောက်တဲ့ log ဖြစ်သွားစေတယ်။

## Lab 7 — Measure the mode matrix yourself

```python
# sessionless transports need mode="legacy" for elicitation.
@mcp.tool()
async def needs_mode(ctx: Context) -> str:
    # Without mode="legacy" on a sessionless transport this raises -32602.
    result = await ctx.elicit(
        message="Confirm?",
        response_type="boolean",
        mode="legacy",
    )
    return f"action={result.action}"
```

**အဓိကအယူအဆ** — Handshake-era transport များမှာ elicitation က ပုံမှန်လုပ်ငန်းလုပ်ပေမယ့် sessionless era မှာ `mode="legacy"` ထည့်ဖို့ လိုအပ်ပါတယ်။

## Lab 8 — Break the handler contract on purpose, then fix it

```python
# The handler contract: async, exactly four params, returns the outcome.


async def confirm_handler(
    ctx,          # context
    params,       # the request payload
    message,      # human-readable question
    schema,       # JSON Schema for the answer
):
    # Break it first: remove a parameter or forget async, watch the error,
    # then restore the four-parameter async signature.
    return "accept", {"value": True}
```

**အဓိကအယူအဆ** — Handler တစ်ခုက async ဖြစ်ရပြီး parameter လေးခု အတိအကျ ရှိရမယ်၊ outcome က return value ဖြစ်ရတယ်။

## Lab 9 — Build a protected gate and read its audit trail

```python
# The protected-service pattern: confirm before anything risky.
audit_log = []


@mcp.tool()
async def maintenance_window(ctx: Context) -> str:
    result = await ctx.elicit(
        message="This restarts the service. Confirm?",
        response_type="boolean",
    )
    if result.action == "accept" and result.data.get("value") is True:
        audit_log.append({"who": ctx.request_id, "what": "restart", "verdict": "accept"})
        return "restart executed"
    audit_log.append({"who": ctx.request_id, "what": "restart", "verdict": result.action})
    return "nothing changed"
```

**အဓိကအယူအဆ** — အန္တရာယ်ရှိတဲ့ အလုပ်တိုင်းရဲ့ ရှေ့မှာ confirmation gate တစ်ခု ထားပြီး ဘယ်သူက ဘာကို ခွင့်ပြုခဲ့လဲဆိုတာ audit trail မှာ ကျန်ရှိရမယ်။

## Lab 10 — Decide whether to elicit at all

```python
# The single test: is the model able to answer without the human?
NEEDS_HUMAN = {"confirm_purchase", "reset_password", "sign_document"}
MODEL_CAN_ANSWER = {"search_flights", "get_weather", "format_text"}


@mcp.tool()
async def dispatch(task: str, ctx: Context) -> str:
    if task in MODEL_CAN_ANSWER:
        return "serve directly; no elicitation needed"
    if task in NEEDS_HUMAN:
        result = await ctx.elicit(message=f"Confirm {task}?", response_type="boolean")
        return f"gate returned {result.action}"
    return "unknown task"
```

**အဓိကအယူအဆ** — မေးခြင်းက တကယ့်ကုန်ကျစရိတ်ရှိလို့ server က ကိုယ်တိုင် ရှာဖွေနိုင်တဲ့အရာအတွက် ဘယ်တော့မှ elicit မလုပ်သင့်ပါ။

## Lab 11 — Testing an elicitation flow without a human

```python
# Elicitation is testable: inject a fake handler, no human needed.
from booking import set_elicit_handler, book_flight


def fake_accept(ctx, params, message, schema):
    # Always answer accept; keeps tests deterministic.
    return "accept", {"origin": "RGN", "destination": "MDL", "date": "2025-01-01"}


set_elicit_handler(fake_accept)


async def test_book_flight_accepts():
    result = await book_flight("RGN", "MDL", None)
    assert "booked" in result
```

**အဓိကအယူအဆ** — Fake handler တစ်ခု ထိုးသွင်းပြီး outcome သုံးမျိုးစလုံးကို လူတစ်ယောက်မပါပဲ CI အတွင်းမှာ test လုပ်နိုင်ပါတယ်။
