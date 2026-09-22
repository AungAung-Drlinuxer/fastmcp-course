# M8 — Interactive Elicitation (`await ctx.elicit()`)

> **ကြာမြင့်ချိန်:** 3 နာရီ · **Phase:** Phase 3 — Advanced Interaction

## ဤသင်ခန်းစာတွင် ဘာရမည်လဲ

ဤ module တွင် MCP server မှ client ဘက်သို့ ဦးစွာ စကားပြောသည့် တစ်ခုတည်းသော စွမ်းရည် — elicitation — ကို သင်ရမည်။ ပြီးလျှင်：

- Reverse flow ဆိုသည်မှာ ဘာလဲ၊ ၎င်းကို protocol က ဘယ်လို ခွင့်ပြုသလဲ
- `await ctx.elicit(message, response_type=...)` ခေါ်ဆိုမှုရဲ့ signature နှင့် အသုံးပြုပုံ
- `response_type` ပုံစံ ငါးမျိုးနှင့် တစ်ခုစီနောက်က JSON Schema
- Form mode (Pydantic schema ဖြင့် native form ဖန်တီးခြင်း) နှင့် URL mode
- Outcome သုံးမျိုး — `accept`၊ `decline`၊ `cancel` — တစ်ခုစီအတွက် policy
- `mode="legacy"` လိုအပ်ချက်နှင့် era ကွာခြားချက်
- Handler contract: parameter လေးခု၊ async၊ return value
- အန္တရာယ်ရှိသည့် လုပ်ဆောင်မှုများမတိုင်မီ confirmation gate ထည့်ခြင်း
- Elicit လုပ်သင့်/မလုပ်သင့် ဆုံးဖြတ်နည်းနှင့် လူလိုမတောင်းဘဲ test လုပ်နည်း

## သင်ခန်းစာများ

1. Reverse flow — `server -> client` လမ်းကြောင်း
2. `booking.py` — module ၏ တကယ့် code
3. `ctx.elicit()` ခေါ်ဆိုမှုနှင့် question shape များ
4. Form mode နှင့် Pydantic schema များ
5. URL mode နှင့် outcome သုံးမျိုး
6. `mode` လိုအပ်ချက်၊ handler contract၊ protected gate၊ decision rule၊ testing

## လိုအပ်ချက်များ (Prerequisites)

- M7_prompts module ပြီးဆုံးထားရမည်
- `@mcp.tool`၊ context (`ctx`) နှင့် async Python အခြေခံ နားလည်ထားရမည်
- Pydantic model ရေးနည်း သိထားရမည်

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

Tool တစ်ခုက ဆက်လက် လုပ်ဆောင်ရန် လူသုံးထောင်ထက် မရှိမဖြစ် အချက်အလက် လိုအပ်သည့်အခါ၊ သို့မဟုတ် ပျက်စီးစေနိုင်သည့် လုပ်ဆောင်မှုမတိုင်မီ အတည်ပြုချက် ယူရန် လိုအပ်သည့်အခါ — ဥပမာ flight booking၊ payment confirmation၊ တစ်စုံတစ်ခုကို ဖျက်ရန် တောင်းဆိုခြင်း။ Model က မဖြေနိုင်သော မေးခွန်းကို server က တိုက်ရိုက် လူကို မေးရန် အသုံးဝင်သည်။

## ဖိုင်ဖွဲ့စည်းပုံ

| ဖိုင် | အဓိပ္ပာယ် |
|---|---|
| `explanation.md` | သင်ခန်းစာအပြည့်အစုံ (lesson) |
| `exercise.md` | လက်တွေ့ စာရင်း ၆ ခု |
| `solution.md` | စာရင်းတစ်ခုချင်းစီ၏ အဖြေများ |
| `cheatsheet.md` | အမြန် ကြည့်ရန် စည်းမျဉ်းများ |
| `../code/` | Lab code များ (`booking.py` အပါအဝင်) |

## ကိုးကား

- အရင် module — [M7_prompts](../M7_prompts/README.md)
- နောက် module — [M9_clients](../M9_clients/README.md)
- ဤ module ၏ test များ — [`../../tests/test_m8_elicitation.py`](../tests/test_m8_elicitation.py)
