# M1 — Modern Python Environment (uv)

> **ကြာမြင့်ချိန်:** 2 နာရီ · **Phase:** Phase 1 — Foundations

## ဤသင်ခန်းစာတွင် ဘာရမည်လဲ

- Python environment ပြဿနာများကို `uv` ဖြင့် ဖြေရှင်းနည်း
- `.venv` ဆိုတာ ဘာလဲ၊ ဘာကြောင့် လိုအပ်လဲ
- `pyproject.toml` ဖိုင်ဖြင့် project ကို သတ်မှတ်ခြင်း
- Python version ကို lock လုပ်ခြင်းက ဘာကြောင့် အရေးကြီးလဲ
- `env_check.py` စစ်ဆေးပရိုဂရမ်ကို ဖတ်နိုင်စွမ်း ရရှိလာမည်

## သင်ခန်းစာများ

1. ပြဿနာကို အရင်နားလည်ပါ — Python environment ရဲ့ အခက်အခဲများ
2. `*.venv*` ဆိုတာ ဘာလဲ
3. `uv` က ဘာကွာသလဲ
4. `pyproject.toml` ဖိုင်ရဲ့ တာဝန်
5. Interpreter ပြဿနာကို ရှာခြင်း
6. `env_check.py` ကို တစ်လိုင်းချင်း ဖတ်ခြင်း

## လိုအပ်ချက်များ (Prerequisites)

- M0_orientation module ကို ပြီးမြောက်ထားရမည်
- ကွန်ပျူတာတွင် `uv` ကို install လုပ်ထားရမည်
- Terminal/command line အခြေခံ အသုံးပြုနိုင်ရမည်

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- MCP project အသစ်တစ်ခု စတင်တည်ဆောက်ချင်တဲ့အခါ
- "ကျွန်တော့်စက်မှာ အလုပ်လုပ်တယ်" ဆိုတဲ့ environment ပြဿနာများ တွေ့ရင်
- အဖွဲ့လိုက် project တစ်ခုမှာ Python version တူညီစေချင်တဲ့အခါ

## ဖိုင်ဖွဲ့စည်းပုံ

- `explanation.md` — သင်ခန်းစာအပြည့်အစဉ် ရှင်းလင်းချက်
- `exercise.md` — လေ့ကျင့်ခန်း ၆ ခု
- `solution.md` — လေ့ကျင့်ခန်းအဖြေများ
- `cheatsheet.md` — အမြန်ကြည့်စာရင်း
- `../code/env_check.py` — လက်တွေ့စစ်ဆေးမည့် lab ကုဒ်ဖိုင်

## ကိုးကား

- အရင် module — [M0_orientation](../M0_orientation/README.md)
- နောက် module — [M2_types_pydantic](../M2_types_pydantic/README.md)
- စစ်ဆေးရန် test များ — [test_m10_security.py](../tests/test_m10_security.py), [test_m11_capstone.py](../tests/test_m11_capstone.py), [test_m11_lab6_extension.py](../tests/test_m11_lab6_extension.py)
