# M1 — လေ့ကျင့်ခန်းများ

## လေ့ကျင့်ခန်း ၁ — uv နဲ့ project အသစ် တည်ဆောက်ခြင်း

LAB 1 အတိုင်း — `uv init` ဖြင့် project အသစ်တစ်ခု ဖန်တီးပြီး `pyproject.toml` နဲ့ `.venv` ဖိုင်တွေ ရှိမရှိ စစ်ပါ။ ရလဒ်ကို `env_check.py` (folder `../code/`) ဖြင့် အတည်ပြုပါ။

**Hints:** `uv init`၊ `uv add mcp`၊ `uv run python env_check.py` တို့ကို အစဉ်လိုက် သုံးပါ။
**Expected behavior:** project folder ထဲ `pyproject.toml` နဲ့ `.venv` ဖိုင်တွဲ ပေါ်လာပြီး `env_check.py` က `.venv` interpreter ကို ပြသည်။

## လေ့ကျင့်ခန်း ၂ — Version ချုပ်ခြင်းကို စမ်းသပ်ခြင်း

LAB 2 အတိုင်း — `requires-python` ကို `pyproject.toml` ထဲ သတ်မှတ်ပြီး မတည်းတဲ့ Python version နဲ့ run ကြည့်ပါ။ `uv` က ဘာဖြေပြလဲ ဆိုတာကို မှတ်တမ်းတင်ပါ။

**Hints:** `requires-python = ">=3.11"` ကို ပြင်ပြီး `uv run` ကို ပြန်သုံးကြည့်ပါ။
**Expected behavior:** Python version မပြည့်စုံရင် `uv` က error ထုတ်ပြီး ရှင်းပြသည်၊ ပြည့်စုံရင် ဆက်လက် အလုပ်လုပ်သည်။

## လေ့ကျင့်ခန်း ၃ — pyproject.toml ကို ဖတ်ခြင်း

LAB 3 အတိုင်း — `uv add` လုပ်ပြီးနောက် `pyproject.toml` ထဲ dependencies စာရင်း ဘယ်လို ပြောင်းသွားလဲ ဆိုတာကို `git diff` (သို့) ဖိုင်ကို တိုက်ရိုက်ဖတ်၍ လေ့လာပါ။

**Hints:** `name`၊ `requires-python`၊ `dependencies` key သုံးခုကို ခွဲခြား သတ်မှတ်ပါ။
**Expected behavior:** ထည့်လိုက်တဲ့ package တစ်ခုစီက `dependencies` list ထဲ တစ်လိုင်း တိုးသည်။

## လေ့ကျင့်ခန်း ၄ — Interpreter လမ်းကြောင်း စစ်ခြင်း

`sys.executable` ပြသည့် ကိုယ်ပိုင် script တစ်ခု ရေးပြီး system Python နဲ့ `.venv` Python တို့ရဲ့ ကွာခြားချက်ကို ပြပါ။

**Hints:** ရိုးရိုး `python` နဲ့ run တဲ့အခါ၊ `uv run python` နဲ့ run တဲ့အခါ output နှစ်မျိုးကို နှိုင်းယှဉ်ပါ။
**Expected behavior:** `uv run` က `.venv` interpreter path ကို ပြပြီး ရိုးရိုး `python` က system interpreter ကို ပြသည် (သို့) လမ်းကြောင်း ကွဲပြားသည်။

## လေ့ကျင့်ခန်း ၅ — env_check.py ကို တစ်လိုင်းချင်း ဖတ်ခြင်း

`../code/env_check.py` ကို လိုင်းအလိုက် ဖတ်ပြီး သူ့ရဲ့ ချုပ်ကိုင်မှု structure (import → print → version check) ကို မိတ်ဆက်စာ တစ်စောင် ရေးပါ။

**Hints:** `sys` နဲ့ `importlib.metadata` import တွေက ဘာအလုပ်လုပ်လဲ ကို စဉ်းစားပါ။
**Expected behavior:** import တွေ၊ executable ထုတ်ပြမှု၊ version ထုတ်ပြမှု ဆိုတဲ့ အစီအစဉ်ကို ခွဲခြားနိုင်သည်။

## လေ့ကျင့်ခန်း ၆ — Environment ပြဿနာ ရှာဖွေခြင်း

သိမ်းဆည်းရန် `uv.lock` ဖိုင် တစ်ခု ဖန်တီးပြီး အဖွဲ့ဝင်တစ်ယောက် project ကို `git clone` လုပ်ပြီးနောက် `uv sync` နဲ့ environment ကို ပြန်တည်ဆောက်တဲ့ အခြေအနေကို ခန့်မှန်းပြီး ရှင်းပါ။

**Hints:** lock file က ဘာကို သေချာစေလဲ — exact versions — ဆိုတာကို အာရုံစိုက်ပါ။
**Expected behavior:** `uv sync` လုပ်တဲ့အခါ dependency တွေရဲ့ version တွေ အတိအကျ တူညီစွာ ပြန်ရသည်။
