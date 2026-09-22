# M2 — Type Hints, Introspection & Pydantic

> **ကြာမြင့်ချိန်:** 3 နာရီ · **Phase:** Phase 1 — Foundations

## ဤသင်ခန်းစာတွင် ဘာရမည်လဲ

MCP server တစ်ခုရှိ `@mcp.tool` တစ်ခုစီသည် Python function တစ်ခုပေါ်တွင် အခြေခံသည်။ function ၏ type hint များနှင့် docstring ကို ဖတ်ပြီး **JSON Schema** ကို အလိုအလျောက် ထုတ်ပေးရသည်။ ဤ module တွင် —

- Type hints ဆိုတာ documentation မဟုတ်ဘဲ **runtime တွင် ဖတ်နိုင်သော data** ဖြစ်သည့်အချက်
- `list[dict[str, int]]` ကဲ့သို့ nested hint များကို `get_origin()` / `get_args()` ဖြင့် ဖြည့်ခွဲဖတ်နည်း
- `Literal[...]` က `str` ထက် tool parameter အတွက် ဘာကြောင့် ပိုသင့်တော်သည်
- `inspect.signature()` ဖြင့် function ၏ parameter များကို object ကဲ့သို့ ဖတ်နည်း
- Hand-rolled JSON Schema ဆောက်နည်းနှင့် ၎င်းက မမြင်နိုင်သည့်အရာများ (PEP 563 trap, description)
- Pydantic `BaseModel` နှင့် `Field()` — declaration တစ်ခုတည်းမှ **validation + schema** နှစ်ခုစလုံး ရရှိနည်း
- `ValidationError` ကို `loc`, `type`, `input` တို့ဖြင့် debugger ကဲ့သို့ ဖတ်နည်း
- Schema **drift** (ကိုးကားရင်းမြစ်နှစ်ခု မကိုက်ညီတော့ခြင်း) ကို test ဖြင့် ဖမ်းနည်း

## သင်ခန်းစာများ

1. Type Hints Are Data, Not Documentation — `__annotations__` နှင့် `from __future__ import annotations`
2. Every Hint Form and the Schema Shape It Produces — scalar, container, `X | None`, `Literal`, nested model
3. `get_origin`, `get_args` and How a Union Is Detected — recursive reader
4. Why `Literal` Beats `str` for a Tool Parameter — MCP အခြေအနေ
5. The `inspect` Module — `signature()`, `Parameter.empty`, `param.kind`, docstring
6. Building the JSON Schema by Hand — `annotation_to_schema()`, `function_to_schema()`
7. Pydantic `BaseModel` and `Field` — One Declaration, Two Outputs
8. Reading a `ValidationError` — `errors()`, `loc`, `type`, `str(exc)`
9. `VMProvisionSchema` — the Worked Example, Line by Line
10. One Declaration, No Drift — FastMCP ရင်းမြစ်နှစ်ခု ပေါင်းနည်း

## လိုအပ်ချက်များ (Prerequisites)

- **M1_python_env** ပြီးဆုံးထားရမည် — Python environment, FastMCP installation နှင့် ပထမဆုံး MCP server ကို ရေးပြီးဖြစ်ရမည်
- Python function, dictionary, class အခြေခံကို သိထားရမည်

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- မိမိ၏ `@mcp.tool` function တစ်ခုအတွက် client ဘက်မှ ဘာပါမလဲ၊ ဘယ် type ဖြစ်ရမလဲကို တိတ်ကျ သတ်မှတ်လိုသောအခါ
- Tool တစ်ခုသို့ မှားယွင်းသော input ရောက်လာသည့်အခါ error ကို မြန်မြန် ဖတ်ရှု ဖြေရှင်းလိုသောအခါ
- Schema နှင့် implementation ကွဲပြားမသွားစေရန် (no drift) test ဖြင့် အာမခံလိုသောအခါ
- နောက် module **M3_asyncio_decorators** ရှိ decorator နှင့် async သင်ခန်းစာများအတွက် အခြေခံအဖြစ်လည်း အသုံးဝင်သည်

## ဖိုင်ဖွဲ့စည်းပုံ

- `explanation.md` — သင်ခန်းစာ (condensed lesson)
- `exercise.md` — လေ့ကျင့်ခန်း ၆ ခု (LAB 1 – LAB 7 မှ ရွေးထုတ်ထားသည်)
- `solution.md` — လေ့ကျင့်ခန်းအဖြေများ
- `cheatsheet.md` — အမြန်ဖတ်စရာ (quick reference)
- `../code/` — lab code files (`type_hints.py`, `introspect.py`, `schema_demo.py`, `lab_1` မှ `lab_7` အထိ)

## ကိုးကား

- ရှေ့ module — [M1_python_env](../M1_python_env/README.md)
- နောက် module — [M3_asyncio_decorators](../M3_asyncio_decorators/README.md)
- ဤ module ၏ test — [test_m2_schema.py](../tests/test_m2_schema.py)
