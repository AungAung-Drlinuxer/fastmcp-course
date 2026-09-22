# M8 — Interactive Elicitation (`await ctx.elicit()`) — ရှင်းလင်းချက်

## ၁ — Reverse Flow ဆိုတာ ဘာကို ဆိုလိုတာလဲ

### ဘာကို ဆိုလိုတာလဲ
သာမန် MCP လမ်းကြောင်းမှာ `client -> server` ဟု client က ဦးစွာ တောင်းဆိုပြီး server က အဖြေပေးသည်။ Reverse flow ကတော့ ပြောင်းပြန် — server က tool အလယ်မှာ ရပ်တန့်ပြီး လူသုံးသူဆီ မေးခွန်းထုတ်လို့ ရသည်။ ဒါက server က ဦးစွာ စကားပြောသည့် တစ်ခုတည်းသော စွမ်းရည်ဖြစ်သည်။

### ဘာကြောင့် လဲ
Tool တစ်ခုက အားလုံး လိုအပ်သည့် အချက်အလက်ကို အစကတည်းက မသိနိုင်။ "စတုတ္ထ parameter တစ်ခု ထပ်ထည့်ပါ" ဆိုသည့် ဒီဇိုင်းက ခေတ်ဟောင်း protocol era က ဖြစ်ပြီး၊ elicitation က back-channel တစ်ခုအနေနဲ့ လူကို တိုက်ရိုက် မေးခွင့်ပေးသည်။

### ဘယ်လို အလုပ်လုပ်လဲ
`await ctx.elicit()` ကို tool အတွင်းမှာ ခေါ်သည်နှင့် server က session တစ်ခုလုံးကို ခေတ္တရပ်ထားပြီး host application ဆီ မေးခွန်းကို ပို့လွှတ်သည်။ လူက ဖြေပြီးမှ tool က ဆက်လက် အလုပ်လုပ်သည်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
မေးရမှ ရှိသည့် အချက်အလက် (ဥပမာ — ခရီးသွားသူရဲ့ နာမည်၊ စိတ်ကျန်းမာရေး အခြေအနေ) ကို ကြိုပြီး parameter အဖြစ် တောင်းနေစရာ မလိုတော့ပါ။ Tool ရဲ့ စာရင်းက တိုသွားပြီး အသုံးပြုသူနဲ့ ပိုနီးစပ်သည်။

## ၂ — `await ctx.elicit()` ခေါ်ဆိုမှု

### ဘာကို ဆိုလိုတာလဲ
`ctx.elicit(message, response_type=...)` ဆိုတာ context ထဲက မေးခွန်းထုတ်တဲ့ နည်းလမ်းဖြစ်သည်။ `message` က လူတစ်ယောက်အတွက် ရေးရသည်၊ `response_type` က ပုံစံ ငါးမျိုးနဲ့ ရွေးရသည်။

### ဘာကြောင့် လဲ
Scalar အဖြေများကို `{"value": ...}` ဟု wrapper ထဲ ထုပ်ရသည်မှာ JSON မှာ `str`၊ `int` စသည့် primitive များကို တစ်ခုတည်း object အဖြစ် မပို့နိုင်သောကြောင့်ဖြစ်သည်။ Master model နဲ့ `response_title` က မေးခွန်းရဲ့ ခေါင်းစဉ်ကို ထိန်းပေးသည်။

### ဘယ်လို အလုပ်လုပ်လဲ
မေးခွန်းပုံစံတစ်ခုစီအတွက် Pydantic model သတ်မှတ်ပြီး `response_type` မှာ ထည့်သွင်းသည်။ ဖြေမှုက result object တစ်ခုအဖြစ် ပြန်ရောက်သည်။

### ဥပမာ
```python
from pydantic import BaseModel

class Confirm(BaseModel):
    ok: bool

@mcp.tool
async def delete_file(path: str, ctx: Context) -> str:
    # Ask the human a yes/no question mid-tool
    result = await ctx.elicit(
        "Delete this file?",
        response_type=Confirm,
    )
    return f"action={result.action}"
# Expected output:
# action=accept
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
မေးခွန်းပုံစံ ငါးမျိုး (scalar၊ enum၊ multi-select၊ form၊ URL) ကို မှန်ကန်စွာ ရွေးတတ်ရင် လူသုံးသူရဲ့ ဖြေရလွယ်မှု သိသိသာသာ တိုးသည်။

## ၃ — Form Mode နှင့် JSON Schema

### ဘာကို ဆိုလိုတာလဲ
Form mode က Pydantic schema တစ်ခုကို host ဘက်မှာ native form တစ်ခုအဖြစ် ပြသည့် mode ဖြစ်သည်။ `required` နဲ့ `default` က လူကို ဘယ်နှစ်ကွက် ဖြည့်ခိုင်းမလဲ ဆုံးဖြတ်ပြီး၊ `enum` က dropdown, `array` က multi-select ဖြစ်သည်။

### ဘာကြောင့် လဲ
Host က JSON Schema ရဲ့ restricted subset တစ်ဝက်ပဲ render လုပ်နိုင်သည်။ ဒါကြောင့် schema က ရိုးရိုးရှင်းရှင်းဖြစ်ရသည်။ သတိပြုရန် — form သည် လုံခြုံရေး အာမခံချက် မဟုတ်ပါ၊ ဆိုလိုတာက server ဘက်မှာ ဖြေမှုကို ပြန်စစ်ရသေးသည်။

### ဘယ်လို အလုပ်လုပ်လဲ
Pydantic model ထဲ ဖိုင်ကွက်များကို သတ်မှတ်ပြီး `response_type` မှာ ပေးလွှတ်သည်။

### ဥပမာ
```python
from pydantic import BaseModel, Field

class BookingForm(BaseModel):
    passenger: str = Field(description="Full name")
    seat: str = Field(default="window", description="window / aisle")
    meal: str | None = Field(default=None)

@mcp.tool
async def book_flight(flight_no: str, ctx: Context) -> str:
    # The host renders this schema as a native form
    result = await ctx.elicit(
        "Please confirm your booking details.",
        response_type=BookingForm,
    )
    return f"booked for {result.data.passenger}"
# Expected output:
# booked for Daw Aye
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
လူက စကားလုံးရိုက်စရာ မလိုဘဲ ကွက်ဖြည့်ရုံပဲ လိုသည်။ မေးခွန်းအားလုံး တစ်ကွက်တည်းမှာ ပြီးသွားသည်။

## ၄ — URL Mode

### ဘာကို ဆိုလိုတာလဲ
Form နဲ့ မမေးသင့်သည့် အချက်အလက်များရှိသည် — ဥပမာ password သို့ OAuth ဖြင့် login လုပ်ရသည့် အရာများ။ URL mode က လူကို browser ဆီ လွှတ်ပြီး ဖြေရစေသည်။

### ဘာကြောင့် လဲ
Form တစ်ခုထဲ စကားဝှက် ရိုက်ခိုင်းခြင်းက လုံခြုံရေးအရ မှားနေသည်။ URL mode က အဲဒီ class ရဲ့ ပြဿနာကို ရှောင်ပေးသည်။

### ဘယ်လို အလုပ်လုပ်လဲ
URL တစ်ခုကို ပို့လွှတ်သည်။ Host က `requested_schema` ထဲ URL မြင်လျှင် form မဟုတ်ကြောင်း သိပြီး browser ဖွင့်ပေးသည်။ Outcome သုံးမျိုး အတူတူ ရှိသည်၊ protocol အဆင့်တစ်ခု ထပ်ရှိသည် — error code `-32042`။ URL က https ဖြစ်ရမည်၊ localhost ခွင့်ပြုချက် စသည်တို့ကို စစ်ဆေးရသည်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
Login မလုပ်ရသေးသည့် အသုံးပြုသူကို tool တစ်ခုတည်းနဲ့ ပြီးအောင် လုပ်ပေးနိုင်သည်။

## ၅ — Outcome သုံးမျိုး — accept, decline, cancel

### ဘာကို ဆိုလိုတာလဲ
Elicitation တစ်ခုရဲ့ ဖြေမှုက outcome သုံးမျိုးထဲက တစ်မျိုးဖြစ်သည် — `accept` (လက်ခံ)，`decline` (ငြင်းပယ်)，`cancel` (ပယ်ဖျက်)။ `accept` + `proceed=False` ဟူသည့် စတုတ္ထ အခြေအနေလည်း ရှိသည်။

### ဘာကြောင့် လဲ
သုံးမျိုးကို ရောလိုက်လျှင် မတူသည့် အခြေအနေတွေကို တူသည်ဟု မှားယွင်း သတ်မှတ်သည်။ တစ်မျိုးစီအတွက် ကွဲပြားသည့် policy လိုအပ်သည် — `decline` က လူရဲ့ ဆုံးဖြတ်ချက်ဖြစ်ပြီး `cancel` က host ရဲ့ ဆုံးဖြတ်ချက်ဖြစ်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ
Outcome တိုင်းအတွက် branch တစ်ခုစီ code ထဲ ရေးသည်၊ `hint` ဖြင့် လူ့ဘာသာနဲ့ ရှင်းပြသည်။

### ဥပမာ
```python
@mcp.tool
async def charge_card(amount: int, ctx: Context) -> str:
    result = await ctx.elicit(
        f"Charge {amount} USD to your saved card?",
        response_type=Confirm,
    )
    if result.action == "accept":
        return "charged"
    elif result.action == "decline":
        # The human said no — stop and explain
        return f"stopped: {result.data.reason}"
    else:
        # cancel came from the host, not the human
        return "cancelled by host"
# Expected output:
# stopped: too expensive
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
Model (LLM) က outcome များကို ခွဲခြားမြင်သည်။ `hint` ကောင်းတစ်ခုက နောက်ထပ် မေးစရာ မလိုအောင် လျှော့ပေးသည်။

## ၆ — `mode="legacy"` လိုအပ်ချက်

### ဘာကို ဆိုလိုတာလဲ
Elicitation က back-channel ဖြစ်၍ era နှစ်ခုရှိသည် — handshake ခေတ်နှင့် sessionless ခေတ်။ `mode` parameter က ဘယ်ခေတ်မျိုးနဲ့ အလုပ်လုပ်မလဲ ကို သတ်မှတ်သည်။

### ဘာကြောင့် လဲ
Sessionless transport တွေမှာ elicitation က အလုပ်မလုပ်နိုင်။ Default ကို မပြောင်းဘဲ error ကို လက်ခံရသည်မှာ တိတ်တဆိတ် ပျက်နည်း မဟုတ်ဘဲ ထင်ရှားစွာ error ပြရန် ရည်ရွယ်သည်။ ခြွင်းချက် တစ်ခုတည်းက `legacy_only` transport ဖြစ်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ
`mode="legacy"` ထည့်လိုက်ရုံဖြင့် handshake ခေတ်နဲ့ ကိုက်ညီစေသည်။ Error ရှိပါက mode matrix (lab 5 ရဲ့ တကယ့် output) နဲ့ တိုင်းတာပြီး ရှာသည်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
Transport တစ်ခုစီအတွက် အလုပ်လုပ်မလုပ်ကို ကြိုမသိနိုင်လျှင် production မှာ ပျက်နိုင်သည်။ ဇယားအရ ခွဲခြားပြီးမှ ရွေးရသည်။

## ၇ — Handler Contract

### ဘာကို ဆိုလိုတာလဲ
Host application က elicitation request လာသည့်အခါ ခေါ်ရမည့် function ကို handler ဟုခေါ်သည်။ Contract က — async ဖြစ်ရမည်၊ parameter လေးခု မဖြစ်မနေ ရှိရမည်၊ outcome ကို return value အဖြစ် ပြန်ရမည်။

### ဘာကြောင့် လဲ
Parameter လေးခုက protocol ရဲ့ ဖွဲ့စည်းမှုပင်ဖြစ်သည် — context, message, schema, params စသည်။ တစ်ခုချွတ်လျှင် host က ခေါ်မရပါ။ Handler လုံးဝ မထည့်လျှင် fallback လိုအပ်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ
`make_handler` ပုံစံနဲ့ ရေးပြီး `params` ကို ဖတ်ကာ လူ့အဖြေကို ဆက်သွင်းသည်။ Contract ကို တမင် ချိုးပြီး (lab 8) ပြန်ပြင်ခြင်းဖြင့် သင်ယူသည်။

### ဥပမာ
```python
async def make_handler():
    # Minimal host-application handler shape (from booking.py)
    async def handler(ctx, message, schema, params):
        # Read params and answer on behalf of the human
        answer = schema(**params)
        return ("accept", answer, None)
    return handler
# Expected output:
# handler registered
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
Handler ကိုမတတ်ရင် host နဲ့ server က ဆက်လက် မပြောနိုင်ပါ။ ဒါက elicitation ရဲ့ host ဘက်တစ်ဝက်ဖြစ်သည်။

## ၈ — Protected-Service Pattern နှင့် ဘယ်အခါ မမေးရ

### ဘာကို ဆိုလိုတာလဲ
အန္တရာယ်ရှိသည့် အလုပ် (ငွေဖြတ်ခြင်း၊ data ပယ်ဖျက်ခြင်း) မတိုင်ခင် confirmation gate တစ်ခု ထားခြင်းကို protected-service pattern ဟုခေါ်သည်။ အခြားတစ်ဘက်မှာ — မေးစရာ မလိုသည့် အချက်အလက်ကို မေးခြင်းက anti-pattern ဖြစ်သည်။

### ဘာကြောင့် လဲ
Confirmation fatigue က လူသား user တွေကို လိုက်နာရခက်စေသည်။ ရိုးရိုးသားသား ဖတ်စရာ မလိုသည့် အလုပ်တစ်ခုချင်းစီအတွက် အတည်ပြုချက် မေးနေရင် user က အလိုအလျောက် "confirm" ကို နှိပ်လိုက်ဖို့ လေ့ကျင့်သွားပြီး confirmation gate ရဲ့ အဓိကရည်ရွယ်ချက် ပျက်ပြယ်သွားသည်။ ဒါကြောင့် elicitation ကို စစ်မှန်စွာ အန္တရာယ်ရှိတဲ့ နေရာတွေမှာပဲ သုံးသင့်သည်။

### Protected service တစ်ခု ဥပမာ

```python
from fastmcp import FastMCP, Context

mcp = FastMCP("Payments")

@mcp.tool
async def transfer_money(
    amount: float,
    to_account: str,
    ctx: Context,
) -> str:
    """Transfer money to another account (requires confirmation)."""
    # Ask the user to confirm the risky action before proceeding
    confirmation = await ctx.elicit({
        "message": f"Transfer {amount} USD to account {to_account}? "
                   "This cannot be undone.",
        "requestedSchema": {
            "type": "object",
            "properties": {
                "confirmed": {
                    "type": "boolean",
                    "description": "True to proceed with the transfer",
                }
            },
            "required": ["confirmed"],
        },
    })

    # If the user declined (or dismissed the dialog), do nothing
    if not (confirmation.data and confirmation.data.confirmed):
        return "Transfer cancelled — no money was moved."

    return f"Transferred {amount} USD to {to_account}."
```

### ဘယ်အခါ မမေးရ

- **Idempotent ဖတ်ခြင်းအလုပ်များ** — read-only query၊ search၊ report ထုတ်ခြင်းတို့မှာ ဘာမှ ပြောင်းလဲမသွားသဖြင့် မေးရန် မလိုပါ။
- **Data ထဲမှာ ရှိပြီးသား အချက်အလက်** — database ထဲ ရှိတဲ့ customer ရဲ့ email ကို user ကို ပြန်မေးခြင်းက noise သာ ဖြစ်သည်။ contextထဲက ရနိုင်ရင် အဲဒါကိုပဲ သုံးပါ။
- **ဆက်တိုက် နှိပ်နေရမည့် workflow** — တစ်ခေါက်ချင်း အတည်ပြုရင် ရှိသမျှ workflow တစ်ခုလုံး ရပ်တန့်သွားပြီး user experience ကို ပျက်စေသည်။

### သတိထားရန် စည်းမျဉ်းတစ်ခု
မေးခင် ကိုယ်ကိုယ်တိုင် မေးပါ — "ဒီ tool က မှားရင် ပြန်ပြင်လို့ ရမလား၊ ငွေကြေး သို့မဟုတ် data ဆုံးရှုံးမှု ရှိမလား?" ဆိုတာကို။ ပြန်ပြင်လို့ရလျှင် မမေးပါနဲ့။ ပြန်ပြင်လို့ မရလျှင် confirmation တောင်းပါ။

## အနှစ်ချုပ်

- **Elicitation** ဆိုသည်မှာ server ကနေ client ဆီသို့ အချက်အလက် တောင်းခံနိုင်သည့် MCP စံနှုန်းတွင် ပါဝင်သော နည်းလမ်းတစ်ခုဖြစ်ပြီး FastMCP ရှိ `Context.elicit()` ဖြင့် အသုံးပြုသည်။
- **ခေါ်ဆိုမှု ပုံစံ**ကို JSON Schema ဖြင့် သတ်မှတ်ပြီး အဖြေများကို `SendResult`၊ `AcceptResult`၊ `DeclineResult` အဖြစ် ခွဲခြားနိုင်သည်။
- **Protected-service pattern** သည် အန္တရာယ်ရှိသော လုပ်ဆောင်ချက်များအတွက် confirmation gate ထားခြင်းဖြစ်ပြီး user က `Decline` လုပ်လျှင် လုပ်ဆောင်ချက်ကို အပြီးအပိုင် ရပ်ဆိုင်းရမည်။
- **မမေးသင့်သည့် အချက်များ** — idempotent ဖတ်ခြင်းအလုပ်များ၊ context ထဲ ရှိပြီးသား data၊ နှင့် မကြာခဏ အတည်ပြုရမည့် workflow များတွင် elicitation ကို ရှောင်ကြဉ်၍ confirmation fatigue ကို ကာကွယ်ပါ။
