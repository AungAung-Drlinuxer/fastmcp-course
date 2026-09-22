# M8 — Interactive Elicitation (`await ctx.elicit()`) — ရှင်းလင်းချက်

## ၁ — Reverse Flow ဆိုတာ ဘာကို ဆိုလိုတာလဲ

### ဘာကို ဆိုလိုတာလဲ
သာမန် MCP မှာဆိုရင် `client -> server` ဆိုပြီး client က အရင်တောင်းပြီး server က အဖြေပေးတယ်။ Reverse flow ဆိုတာ — ပြောင်းပြန်လေ။ Server က tool အလယ်မှာ ရပ်ပြီး လူကို တိုက်ရိုက် မေးလို့ရတယ်။ Server က ဘာမှ မဖြစ်မီ အရင် စကားပြောလို့ရတဲ့ တစ်ခုတည်းရှိတဲ့ စွမ်းရည်ပါ။

### ဘာကြောင့် လဲ
Tool တစ်ခုက လိုအပ်တဲ့ အချက်အလက်အားလုံးကို အစကတည်းက မသိနိုင်ဘူး။ "စတုတ္ထ parameter တစ်ခု ထပ်ထည့်ပေးပါ" လို့ အတင်း တောင်းခိုင်းတဲ့ ဒီဇိုင်းက ခေတ်ဟောင်း protocol era ပုံစံပဲ။ Elicitation က back-channel — ခေါ် လှည့်ပြန်လမ်း — တစ်ခုနဲ့ လူကို တိုက်ရိုက် မေးခွင့်ပေးလိုက်တာပါ။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ Tool ထဲမှာ `await ctx.elicit()` ကို ခေါ်တယ်။
၂။ Server က session တစ်ခုလုံးကို ခေတ္တ ရပ်ထားတယ်။
၃။ မေးခွန်းကို host application ဆီ ပို့လိုက်တယ်။
၄။ လူက ဖြေပြီးသားမှ အဖြေ ပြန်ရောက်လာတယ်။
၅။ Tool က အဖြေနဲ့ ဆက် အလုပ်လုပ်တယ်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
မေးရမှ ရတဲ့ အချက်အလက် — ဥပမာ ခရီးသွားသူရဲ့ နာမည်၊ စိတ်ကျန်းမာရေး အခြေအနေ — ကို ကြိုပြီး parameter အဖြစ် တောင်းနေစရာ မလိုတော့ပါဘူး။ Tool စာရင်းက တိုသွားပြီး အသုံးပြုသူနဲ့ ပိုနီးစပ်သွားတယ်။ မရှိရင်တော့ အသုံးပြုသူက ဘာမှန်ဘာမမှန် ခန့်မှန်းဖြည့်ရပြီး မှားတဲ့ အချက်အလက်နဲ့ tool ပြေးတတ်တယ်။

## ၂ — `await ctx.elicit()` ခေါ်ဆိုမှု

### ဘာကို ဆိုလိုတာလဲ
`ctx.elicit(message, response_type=...)` ဆိုတာ — context ထဲက လူကို မေးခွန်းထုတ်တဲ့ နည်းလမ်းလေ။ `message` ကို လူဖတ်ရတဲ့ စာအဖြစ် ရေးရပြီး၊ `response_type` က ပုံစံ ငါးမျိုးထဲက ရွေးရတယ်။

### ဘာကြောင့် လဲ
Scalar အဖြေတွေကို `{"value": ...}` ဆိုတဲ့ wrapper ထဲ ထုပ်ရတယ်။ ဘာကြောင့်လဲဆိုတော့ JSON မှာ `str`၊ `int` လို primitive တွေကို object တစ်ခုတည်းအဖြစ် တန်းပို့လို့ မရလို့ပါ။ ပြီးရင် master model နဲ့ `response_title` က မေးခွန်းရဲ့ ခေါင်းစဉ်ကို ထိန်းပေးတယ်။ ဒါမှ UI မှာ မေးခွန်းက နားလည်လွယ်တယ်။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ မေးခွန်းပုံစံအတွက် Pydantic model တစ်ခု သတ်မှတ်တယ်။
၂။ အဲဒီ model ကို `response_type` မှာ ထည့်တယ်။
၃။ `ctx.elicit(...)` ကို tool ထဲက ခေါ်တယ်။
၄။ အဖြေက result object တစ်ခုအဖြစ် ပြန်ရောက်တယ်။
၅။ အဲဒီ object ထဲက field တွေကို ယူပြီး ဆက်လုပ်တယ်။

### ဥပမာ
အောက်က snippet မှာ Pydantic model တစ်ခု သတ်မှတ်ပြီး `ctx.elicit()` နဲ့ မေးပုံ ပြထားတယ်။ အဖြေက result object ထဲ ဘယ်လို ရောက်လာလဲဆိုတာကို အဓိက ကြည့်ပါ။
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
မေးခွန်းပုံစံ ငါးမျိုး (scalar, enum, multi-select, form, URL) ကို အချိန်မှန် ရွေးတတ်ရင် လူသုံးသူက ဖြေရတာ သိသိသာသာ အလွယ်ကျတယ်။
မေးခွန်းပုံစံမှားရင် လူက ဖြေရခက်ပြီး အဖြေလည်း မှားလွယ်တယ်။
ဒါကြောင့် အဲဒါပွဲစားဆိုင်သီချင်းထက် စာရင်းတွက်စက်လို ခေါ်ဆိုမှု အမှားတွေ နည်းသွားစေပါတယ်။

## ၃ — Form Mode နှင့် JSON Schema

### ဘာကို ဆိုလိုတာလဲ
Form mode ဆိုတာ — Pydantic schema တစ်ခုကို host ဘက်မှာ form ပုံစံနဲ့ ပြတဲ့ mode ပါ။
Google Form လို ဖြည့်ရတဲ့ ကွက်လေးတွေနဲ့တူတယ်။
`required` နဲ့ `default` က လူကို ဘယ်နှစ်ကွက် ဖြည့်ခိုင်းမလဲ ဆုံးဖြတ်ပါတယ်။ `enum` က dropdown ဖြစ်ပြီး `array` က multi-select ဖြစ်တယ်။

### ဘာကြောင့် လဲ
Host က JSON Schema တစ်ဝက်လောက်ပဲ render လုပ်နိုင်ပါတယ်။
ဒါကြောင့် schema က ရိုးရိုးရှင်းရှင်း ရှိရတယ်။
သတိထားရန် — form က လုံခြုံရေး အာမခံချက် မဟုတ်ဘူးနော်။
ဆိုလိုတာက server ဘက်မှာ ဖြေမှုကို ပြန်စစ်ရသေးတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ
Pydantic model ထဲ ဖြည့်ကွက်တွေကို သတ်မှတ်ပြီး `response_type` မှာ ပေးလွှတ်ရတယ်။

### ဥပမာ
ဒီ snippet မှာ Pydantic schema တစ်ခုကို form mode နဲ့ ဘယ်လို ပေးလွှတ်လဲ ပြထားပါတယ်။ `enum` နဲ့ `required` ဘယ်လို ပေါ်လဲ ဆိုတာ ဂရုစိုက်ကြည့်ပါ။
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
လူက စကားလုံး ရိုက်စရာ မလိုပါဘူး။ ကွက်ဖြည့်ရုံပဲ လိုတယ်။ မေးခွန်းအားလုံး တစ်ကွက်တည်းမှာ ပြီးသွားတယ်။ ဒါက အလုပ်တွေ မြန်အောင် ကူပါတယ်။

## ၄ — URL Mode

### ဘာကို ဆိုလိုတာလဲ
Form နဲ့ မမေးသင့်တဲ့ အချက်အလက်တွေ ရှိတယ် — ဥပမာ password တို့ OAuth နဲ့ login လုပ်ရတဲ့ အရာတွေ။ OAuth ဆိုတာ — တခြား site က account နဲ့ ဝင်ခွင့် ယူတဲ့ စနစ်လေးပါ။ URL mode က လူကို browser ဆီ လွှတ်ပြီး ဖြေရစေတယ်။ ဥပမာဆို ဘဏ် app က သင့်ကို ဘဏ် website ကို ပို့ပြီး login ခိုင်းတာနဲ့ တူတယ်။

### ဘာကြောင့် လဲ
Form တစ်ခုထဲ စကားဝှက် ရိုက်ခိုင်းတာက လုံခြုံရေးအရ မှားနေတယ်။ စကားဝှက်က chat history ထဲ ကျန်ခဲ့ရင် data leak ဖြစ်သွားတယ်။ URL mode က အဲဒီ ပြဿနာကို ရှောင်ပေးတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ Host က URL တစ်ခုကို ပို့လွှတ်တယ်။
၂။ Host က `requested_schema` ထဲ URL မြင်ရင် form မဟုတ်ဘူးလို့ သိတယ်။
၃။ Browser ဖွင့်ပြီး လူက အဲဒီမှာ ဖြေတယ်။
၄။ Outcome သုံးမျိုးကတော့ အရင်လိုပဲ အတူတူပါပဲ။
၅။ Protocol အဆင့် တစ်ခု ထပ်ရှိတယ် — error code `-32042`။
၆။ URL က https ဖြစ်ရမယ်၊ localhost ခွင့်ပြုချက် စတာတွေကိုလည်း စစ်ဆေးရတယ်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
Login မလုပ်ရသေးတဲ့ user ကို tool တစ်ခုတည်းနဲ့ ပြီးအောင် လုပ်ပေးနိုင်တယ်။ ဒါမှ debug အချိန် သက်သာပြီး အလုပ် ရပ်တန့်တာ (downtime) လည်း လျှော့ပါတယ်။

## ၅ — Outcome သုံးမျိုး — accept, decline, cancel

### ဘာကို ဆိုလိုတာလဲ
Elicitation တစ်ခုရဲ့ ဖြေမှုက outcome သုံးမျိုးထဲက တစ်မျိုးပါ — `accept` (လက်ခံတယ်)，`decline` (ငြင်းပယ်တယ်)，`cancel` (ပယ်ဖျက်တယ်)။ ဒါပုံစံမျိုး စာပို့ပုံးလေး မှတ်ပါ — လက်ခံ၊ ငြင်း၊ ပြန်ထုတ်။ အပြင်မှာ `accept` + `proceed=False` ဆိုတဲ့ စတုတ္ထ အခြေအနေလည်း ရှိတယ်။

### ဘာကြောင့် လဲ
သုံးမျိုးကို ရောလိုက်ရင် မတူတဲ့ အခြေအနေတွေကို တူတယ်လို့ မှားယွင်း သတ်မှတ်မိတယ်။ တစ်မျိုးစီအတွက် ကွဲပြားတဲ့ policy လိုအပ်တယ်။ အရေးကြီးတာက — `decline` က လူရဲ့ ဆုံးဖြတ်ချက်၊ `cancel` က host ရဲ့ ဆုံးဖြတ်ချက်ပါ။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ Outcome တိုင်းအတွက် branch တစ်ခုစီ code ထဲ ရေးတယ်။
၂။ `hint` နဲ့ လူ့ဘာသာနဲ့ ရှင်းပြပေးတယ်။

### ဥပမာ
ဒီ snippet မှာ outcome သုံးမျိုးစလုံးကို ဘယ်လို ခွဲခြမ်းစိတ်ဖြာလဲ ပြထားတယ်။ `decline` နဲ့ `cancel` ကို တူညီတဲ့ code နဲ့ မကိုင်ထားဘူးလို့ စစ်ကြည့်ပါ။
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
Sessionless transport တွေမှာ elicitation က အလုပ်မလုပ်နိုင်။ Default ကို မပြောင်းဘဲ error ကို လက်ခံရသည်မှာ တိတ်တဆိတ် ပျက်ခြင်း မဟုတ်ဘဲ ထင်ရှားစွာ error ပြရန် ရည်ရွယ်သည်။ ခြွင်းချက် တစ်ခုတည်းက `legacy_only` transport ဖြစ်သည်။

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
Handler ကို မတတ်ရင် host နဲ့ server က ဆက်ပြောလို့ မရတော့ပါဘူး။ Elicitation မှာ host ဘက်ရဲ့ တစ်ဝက်အပိုင်း ဖြစ်တယ်။ ဒါကို မှားရင် user ဆီက အချက်အလက် တောင်းခြင်းတွေ အလုပ်မလုပ်တော့ပါဘူး။

## ၈ — Protected-Service Pattern နှင့် ဘယ်အခါ မမေးရ

### ဘာကို ဆိုလိုတာလဲ
Protected-service pattern ဆိုတာ — အန္တရာယ်ရှိတဲ့ အလုပ်မှာ confirmation gate ထားတာ ဖြစ်တယ်။ Confirmation gate ဆိုတာ — အလုပ်လုပ်ခင် user ဆီက "ရှင်းပါ၊ လုပ်ချော်လား?" လို့ တစ်ခေါက် အတည်ပြုတဲ့ တံခါးလေးပါ။ ဥပမာ — ငွေဖြတ်တာ၊ data ပယ်တာတွေမှာ ပေါ့။ တစ်ဘက်မှာတော့ မေးစရာမလိုတဲ့ အချက်အလက်ကို မေးတာက anti-pattern ဖြစ်တယ်။

### ဘာကြောင့် လဲ
User တွေကို တခါပြီးတခါ confirm နှိပ်ခိုင်းရင် confirmation fatigue ဖြစ်လာတယ်။ ဒါဆို user က မဖတ်ဘဲ အလိုအလျောက် "confirm" နှိပ်တတ်သွားပြီး တောင်းတဲ့ အချက်အလက် မှားတောင် သတိမထားမိပါဘူး။ Confirmation gate ရဲ့ ရည်ရွယ်ချက် ကုန်သွားတယ်။ ဒါကြောင့် elicitation ကို အန္တရာယ်ရှိတဲ့ နေရာတွေမှာပဲ သုံးသင့်ပါတယ်။

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

- **Idempotent ဖတ်ခြင်းအလုပ်များ** — Idempotent ဆိုတာ — ဘာမှ မပြောင်းစေဘဲ ဘေးကင်းစွာ ထပ်လုပ်လို့ရတဲ့ အလုပ်။ read-only query၊ search၊ report ထုတ်တာတွေမှာ ဘာမှ မပြောင်းလဲသွားတာပါ။ ဒါတွေမှာ confirmation မေးစရာ မလိုပါဘူး။
- **Data ထဲမှာ ရှိပြီးသား အချက်အလက်** — database ထဲ customer ရဲ့ email က ရှိပြီးသား။ အဲဒါကို user ကို ပြန်မေးတာက အလွန် ကုန်ကျစရိတ်ကြီးပါတယ်။ context ထဲက ရနိုင်ရင် အဲဒါကိုပဲ သုံးပါ။
- **ဆက်တိုက် နှိပ်နေရမည့် workflow** — တစ်ခေါက်ချင်း အတည်ပြုခိုင်းရင် workflow တစ်ခုလုံး ရပ်သွားတယ်။ user ကလည်း စိတ်ညစ်သွားတယ်။ အဲလို workflow မှာ မမေးပါနဲ့။

### သတိထားရန် စည်းမျဉ်းတစ်ခု
မေးခင် ကိုယ့်ကိုယ်ကိုယ် ဒီလို မေးကြည့်ပါ — "ဒီ tool က မှားသွားရင် ပြန်ပြင်လို့ ရမလား၊ ငွေကြေး ဒါမှမဟုတ် data ဆုံးရှုံးမှု ရှိမလား?" ပြန်ပြင်လို့ရရင် မမေးပါနဲ့။ ပြန်ပြင်လို့ မရဘူးဆိုရင် confirmation တောင်းပါ။

## အနှစ်ချုပ်

- **Elicitation** ဆိုတာ — server က client ဆီကနေ အချက်အလက် တောင်းနိုင်တဲ့ MCP စံနှုန်းထဲက နည်းလမ်းတစ်ခု။ FastMCP မှာ `Context.elicit()` နဲ့ သုံးတယ်။
- **ခေါ်ဆိုမှု ပုံစံ**ကို JSON Schema နဲ့ သတ်မှတ်တယ်။ အဖြေတွေကိုလည်း `SendResult`၊ `AcceptResult`၊ `DeclineResult` ဆိုပြီး ခွဲနိုင်တယ်။
- **Protected-service pattern** ဆိုတာ — အန္တရာယ်ရှိတဲ့ လုပ်ဆောင်ချက်တွေမှာ confirmation gate ချထားတဲ့ ပုံစံ။ user က `Decline` လုပ်ရင် လုပ်ဆောင်ချက်ကို အပြီးအပိုင် ရပ်ရတယ်။
- **မမေးသင့်တဲ့ အချက်များ** — idempotent ဖတ်တဲ့ အလုပ်တွေ၊ context ထဲ ရှိပြီးသား data၊ အဲဒါပဲ။ မကြာခဏ အတည်ပြုခိုင်းရတဲ့ workflow တွေမှာ elicitation ကို ရှောင်ပါ။ ဒါမှ confirmation fatigue — user က confirmation တွေ များလွန်းလို့ ပင်ပန်းသွားတဲ့ အခြေအနေ — မဖြစ်ပါဘူး။