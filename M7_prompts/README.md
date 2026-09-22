# M7 — Workflow Steering Prompts (`@mcp.prompt`)

> **ကြာမြင့်ချိန်:** 2 နာရီ · **Phase:** Phase 2 — MCP Core Surfaces

## ဤသင်ခန်းစာတွင် ဘာရမည်လဲ

MCP server တစ်ခုရဲ့ ပစ္စည်း သုံးမျိုးအနက်မှ prompt ဆိုသည့် ပစ္စည်းကို ဤ module တွင် သင်ကြားရမည်။ Prompt ဆိုသည်မှာ server က declare လုပ်ပြီး host က အသုံးပြုသူထံ မီနူးအဖြစ် တင်ပြသည့် template ဖြစ်သည် — task စတင်မီ အသုံးပြုသူ ကိုယ်တိုင် ရွေးချယ်ရသော workflow steering ကိရိယာဖြစ်သည်။

- `@mcp.prompt` decorator နှစ်မျိုး (bare နှင့် named) ဖြင့် prompt ကြေညာခြင်း
- Function signature သည် prompt arguments အဖြစ် ပြောင်းလဲပုံ (argument injection)
- Tool vs Resource vs Prompt — ဘယ်အချိန်မှာ ဘယ်ဟာကို သုံးသင့်သလဲ ဆိုသည့် ဆုံးဖြတ်ချက်
- Consistency သည် prompt ရဲ့ တန်ဖိုးအခြေခံဖြစ်ခြင်း
- Multi-turn guidance format များ — numbered procedure, forced ordering, stop conditions
- Anti-hallucination clause ကို prompt ထဲ ထည့်သင့်သည့် အကြောင်း
- Custom return type ကို မှားယွင်းစွာ သုံးမိလျှင် ဖြစ်ပွားသည့် trap — registered ဖြစわောင်း render မဖြစ်သည့် ပြဿနာ
- Host ဘက်မှ prompt များကို listing လုပ်ခြင်းနှင့် rendering လုပ်ခြင်း contract

## သင်ခန်းစာများ

1. Prompt ဆိုတာ ဘာလဲ — template ဖြစ်ပုံနှင့် ဘယ်သူက ရွေးသလဲ
2. `@mcp.prompt` decorator နှစ်မျိုးဖြင့် ကြေညာခြင်း
3. Argument injection — type hint တစ်မျိုးစီအတွက် schema
4. Consistency သည် အခြေခံတန်ဖိုးဖြစ်ခြင်း
5. Multi-turn guidance format များ
6. Anti-hallucination clause
7. Custom return type trap — fail late ဖြစ်ပုံနှင့် ဖြေရှင်းနည်း
8. Host contract — list နှင့် render
9. Error catalogue နှင့် troubleshooting

## လိုအပ်ချက်များ (Prerequisites)

- [M6_resources](../M6_resources/README.md) အပြီးသတ်ထားရမည် — resource များကို နားလည်ပြီးဖြစ်ရမည်
- Python type hint အခြေခံ သင်ယူပြီးဖြစ်ရမည်
- FastMCP server တစ်ခု run နိုင်သည့် ပတ်ဝန်းကျင် ပြင်ဆင်ပြီးဖြစ်ရမည်

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- အသုံးပြုသူများအား တူညီသော workflow အဆင့်များဖြင့် အစီအစဉ်တကျ ဆက်လက်လုပ်ဆောင်စေလိုသောအခါ
- Model အဖြေများ တညီတည်း မထွက်စေရန် consistency လိုအပ်သော ကဏ္ဍများ (ဥပမာ — RCA prompt library) တွင်
- Tool ထဲ မထည့်သင့်သော လမ်းညွှန်ချက်များ (ဥပမာ — anti-hallucination clause) ကို သီးသန့်နေရာတွင် သိမ်းဆည်းလိုသောအခါ
- Host application တစ်ခုအတွက် prompt မီနူးကို ဒီဇိုင်းဆွဲနေသောအခါ

## ဖိုင်ဖွဲ့စည်းပုံ

| ဖိုင် | အသုံးဝင်မှု |
|---|---|
| `explanation.md` | အခြေခံသင်ခန်းစာအပြည့်အစုံ |
| `exercise.md` | လေ့ကျင့်ခန်း ခြောက်ခု |
| `solution.md` | လေ့ကျင့်ခန်းအဖြေများ |
| `cheatsheet.md` | အမြန်ရှာဖွေရန် အညွှန်း |

## ကိုးကား

- အရင် module — [M6_resources](../M6_resources/README.md)
- နောက် module — [M8_elicitation](../M8_elicitation/README.md)
- ဤ module ရဲ့ test ဖိုင် — [test_m7_prompts.py](../tests/test_m7_prompts.py)
- Lab code ဖိုင်များ — [code/](code/) ဖိုင်တွဲ (lab 1 မှ lab 6၊ extras နှင့် mini-exercise အပြည့်အစုံ ပါဝင်သည်)
