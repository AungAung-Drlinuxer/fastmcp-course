# M1 — Modern Python Environment (uv): ရှင်းလင်းချက်

## အပိုင်း ၁ — ပြဿနာကို အရင်နားလည်ပါ

### ဘာကို ဆိုလိုတာလဲ

Python project တစ်ခုချင်းစီမှာ package တွေ၊ version တွေ၊ interpreter တွေ ကွဲပြားနိုင်တယ်။ Interpreter ဆိုတာ — Python code ကို လည်ပတ်ပေးတဲ့ program လေးပါ။ ဒီအချက်တွေက project အောင်မြင်မှု ရော ကျရှုံးမှု ရော ဆုံးဖြတ်ပေးတဲ့ အရေးကြီးတဲ့ အပိုင်းတွေပါ။

### ဘာကြောင့် လဲ

Package တွေ တစ်နေရာတည်းထဲ ပူးပေါင်းထားရင် version တိုက်ဆိုင်မှုတွေ ဖြစ်လာတယ်။ ဥပမာ — project တစ်ခုက package version ၁ လိုချင်ပြီး နောက်တစ်ခုက version ၂ လိုချင်ရင် တစ်ခု အလုပ်မလုပ်တော့ပါဘူး။ အခြားသူတွေ ကိုယ့် project ကို ပြန်ဆောက်ရင်လည်း တူညီတဲ့ error တွေ ထပ်ကြုံရတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Project တစ်ခုချင်းစီကို သူ့နေရာမှာ သီးသန့်ခွဲထားတယ်။
၂။ ဒီလို ခွဲထားတဲ့ နည်းကို isolation လို့ ခေါ်တယ်။
၃။ Python မှာ ဒီအတွက် `.venv` နဲ့ `pyproject.toml` ကို အသုံးပြုတယ်။
၄။ ဒါဆို project တစ်ခုရဲ့ package တွေက တခြား project တွေကို မထိတော့ပါဘူး။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

MCP server ဆောက်တဲ့အခါ dependency တွေ မှန်ကန်စွာ install မဖြစ်ရင် လုံးဝ အလုပ်မလုပ်ပါဘူး။ Dependency ဆိုတာ — ကိုယ့် project အလုပ်လုပ်ဖို့ လိုအပ်တဲ့ တခြား package တွေပါ။ ဒီ module က နောက် module အားလုံးရဲ့ အခြေခံဖြစ်လို့ ဒီအပိုင်း မှားရင် အောက်ဆင်းရော ရှုပ်ရော ဖြစ်နိုင်တယ်။

## အပိုင်း ၂ — `.venv` ဆိုတာ ဘာလဲ

### ဘာကို ဆိုလိုတာလဲ

`.venv` ဆိုတာ "virtual environment" ဆိုတဲ့ ဖိုင်တွဲ တစ်ခုပါ။ သူ့ထဲမှာ project အတွက် သီးသန့် Python interpreter တစ်ခု နဲ့ install ထားတဲ့ package တွေ ပါဝင်တယ်။ ဥပမာ ပြောရရင် — အိမ်တစ်အိမ်စီမှာ ကိုယ်ပိုင် မီးဖိုချောင် တစ်ခုစီ ရှိသလိုမျိုးပါ။

### ဘာကြောင့် လဲ

System-wide Python ကို တိုက်ရိုက် သုံးရင် project အားလုံးက တစ်နေရာတည်းကို မှီခိုကုန်တယ်။ တစ်ခုမှာ package အသစ် install ရင် တခြား project တွေ ပျက်သွားနိုင်တယ်။ `.venv` က project တစ်ခုချင်းစီကို ကိုယ်ပိုင် package နေရာ တစ်ခုစီ ပေးလိုက်တယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Project folder တစ်ခုထဲ `.venv` ဖိုင်တွဲ တစ်ခု ဖန်တီးတယ်။
၂။ Activate လုပ်တဲ့အခါ shell က `.venv` ထဲက Python ကိုပဲ ရှာသုံးတယ်။
၃။ Package တွေကို ဒီ `.venv` ထဲမှာပဲ install ရတယ်။
၄။ ဒါဆို system Python ကို မထိခိုက်တော့ပါဘူး။

### ဥပမာ

ဒီ snippet မှာ `.venv` ဖန်တီးပြီး activate လုပ်ပုံကို ပြထားတယ်။ ဖိုင်တွဲ နာမည် ရော command ရော အတိအကျ ချရေးထားတဲ့အပိုင်းကို သတိထားကြည့်ပါ။
```python
# This is shell, shown as a block for clarity:
# uv init creates pyproject.toml, uv add installs into .venv
# .venv/bin/python (macOS/Linux) or .venv\Scripts\python (Windows)
# Expected output: a .venv/ directory inside your project folder
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

`mcp` package က version တစ်ခု လိုချင်ပြီး `pydantic` က နောက်တစ်ခု လိုချင်တာ ဖြစ်နိုင်ပါတယ်။ `.venv` ကို သုံးရင် ဒီတိုက်ဆိုင်မှုက အခြား project တွေဆီ မရောက်ပါဘူး။ တစ် project တစ်ခါ ရှုပ်ပွပြီး ပြန်ရှာရတာ ခံစားရတယ်။

## အပိုင်း ၃ — `uv` က ဘာကွာသလဲ

### ဘာကို ဆိုလိုတာလဲ

`uv` ဆိုတာ — Rust နဲ့ ရေးထားတဲ့ Python package/project manager တစ်ခုပါ။ `pip`၊ `venv`၊ `pip-tools` တွေရဲ့ အလုပ်အားလုံးကို tool တစ်ခုတည်းနဲ့ လုပ်ပေးတယ်။ ဓားတစ်လက်နဲ့ အားလုံး လုပ်လို့ရသလိုမျိုးပေါ့။

### ဘာကြောင့် လဲ

ရိုးရိုး `pip` + `venv` နဲ့ ဆင်းရင် အဆင့်တွေ များပါတယ် — environment ဖန်တီး၊ activate လုပ်၊ install လုပ်၊ lock file ရေး။ အဆင့်များလို့ ချန်ထားမိရင် နောက်မှာ ဘာဖြစ်နေလဲ မသိတော့ပါဘူး။ `uv` က ဒါအားလုံးကို မြန်မြန် တစ်ပြိုင်တည်း လုပ်ပေးတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

- `uv init` — project အသစ်နဲ့ `pyproject.toml` ဖန်တီးပေးတယ်
- `uv add <package>` — dependency ထည့်ပြီး `.venv` ထဲ install လုပ်ပေးတယ်
- `uv run <script>` — `.venv` ထဲက Python နဲ့ script အလုပ်လုပ်ပေးတယ်
- `uv python install <version>` — Python version တစ်ခု download လုပ်ပေးတယ်

### ဥပမာ

အောက်မှာ နမူနာ code ကို မြင်ရမယ်။ `uv` command တွေ ဘယ်လို သုံးလဲ ဆိုတာကို ကြည့်ပါနော်။ command တစ်ခုစီက ဘာလုပ်ပေးလဲ ဆိုတာကို သတိထားကြည့်ပါ။
```python
# Shell commands for starting a project with uv:
#   uv init my-mcp-project
#   cd my-mcp-project
#   uv add mcp
#   uv run python env_check.py
# Expected output: pyproject.toml, uv.lock and .venv/ created,
# and env_check.py runs with the project's own interpreter.
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

MCP development လုပ်ရင် dependency အသစ်တွေ ထည့်ဖို့ မကြာခဏ လိုလာတယ်။ Dependency ဆိုတာ — project အလုပ်လုပ်ဖို့ လိုတဲ့ အပို package တွေပါ။ `uv` က ဒီအလုပ်ကို စက္ကန့်ပိုင်းမှာ ပြီးစေပါတယ်။ ဒါကြောင့် setup အတွက် အချိန် အများကြီး ရှင်းပေးပါတယ်။

## အပိုင်း ၄ — `pyproject.toml`

### ဘာကို ဆိုလိုတာလဲ

`pyproject.toml` ဆိုတာ project ရဲ့ အချက်အလက်တွေနဲ့ dependency စာရင်း ပါတဲ့ ဖိုင်ပါ။ မှတ်ရလွယ်အောင် ပြောရရင် — ဆေးသေတ္တာလိုမျိုးပေါ့။ ထဲမှာ ဘာစားဆေးတွေ ရှိလဲ ဆိုတာ စာရင်းပါနေတယ်။ Project နာမည်၊ Python version နဲ့ package တွေကို ဒီဖိုင်ထဲ ဖော်ပြထားတယ်။

### ဘာကြောင့် လဲ

README ထဲ dependency တွေ လက်ဖြင့် ရေးထားရင် — တစ်ယောက်ယောက် မှားရေးမိရင် အခြားသူက install လုပ်လို့ မရဘဲ error တက်တယ်။ `pyproject.toml` ကတော့ စက်ဖြင့် ဖတ်နိုင်တဲ့ format ပါ။ `uv` က ဒီဖိုင်ကို ဖတ်ပြီး environment တစ်ခုလုံးကို အလိုအလျောက် ပြန်တည်ဆောက်ပေးတယ်။ ဒါကြောင့် လူမှားနိုင်တဲ့ အပိုင်း ရှင်းသွားတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ TOML format နဲ့ ဖိုင်ကို ရေးပါတယ်။
၂။ `[project]` section ထဲ `name` ကို သတ်မှတ်ပါတယ်။
၃။ `requires-python` နဲ့ Python version လိုအပ်ချက်ကို ဖော်ပြပါတယ်။
၄။ `dependencies` ထဲ လိုတဲ့ package တွေကို စာရင်းတင်ပါတယ်။
၅။ `uv add` လုပ်တိုင်း ဒီဖိုင်က အလိုအလျောက် ပြင်သွားပါတယ်။

### ဥပမာ

အောက်မှာ `pyproject.toml` ရဲ့ အလုပ်လုပ်ပုံ နမူနာ ကြည့်ရမှာပါ။ `dependencies` စာရင်းနဲ့ Python version ကို သတိထားကြည့်ပါနော်။
```toml
# pyproject.toml example
[project]
name = "my-mcp-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "mcp>=1.0.0",
]
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

အဖွဲ့ဝင်တစ်ယောက် `git clone` လုပ်ပြီး `uv sync` လုပ်ရင် environment တစ်ခုလုံး ပြန်ရပါတယ်။ ဒါကြောင့် "ကျွန်တော့်စက်မှာ ဘာကြောင့် မအလုပ်လုပ်ဘူးလဲ" လို့ မေးစရာ မလိုတော့ပါဘူး။ အချိန်လည်း ချွေတာပြီး debugging လည်း လျှော့သွားပါတယ်။

## အပိုင်း ၅ — Interpreter ပြဿနာကို ရှာခြင်း

### ဘာကို ဆိုလိုတာလဲ

Interpreter ဆိုတာ — `python` ရိုက်လိုက်တဲ့အခါ အလုပ်လုပ်ပေးတဲ့ Python program အစစ်လေးပါ။ Shell ထဲ `python` ရိုက်တဲ့အခါ ဘယ် Python က အလုပ်လုပ်သလဲ ဆိုတာ မသိရင် မှားယွင်းမှုတွေ ဖြစ်လာပါတယ်။ `import mcp` error တွေက များသောအားဖြင့် လမ်းကြောင်း မှားနေလို့ ဖြစ်တာပါ။

### ဘာကြောင့် လဲ

System Python တစ်ခု၊ `.venv` Python တစ်ခု ဆိုပြီး ရှိနိုင်ပါတယ်။ တစ်ခါတစ်ရံ PATH ထဲ အခြား Python တွေပါ ပါဝင်နေတတ်ပါတယ်။ PATH ဆိုတာ — Shell က program တွေကို ဘယ်နေရာမှာ ရှာမလဲ ဆိုတဲ့ စာရင်းလေးပါ။ မှားတဲ့ interpreter နဲ့ package တွေ install လုပ်မိရင် `.venv` ထဲ ဘာမှ မရောက်ပါဘူး။ ဒါဆို server အလုပ်လုပ်မှာ မဟုတ်ပါဘူး။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ `uv run` ကို သုံးပါ — သူက `.venv` ကို အလိုအလျောက် ရွေးပေးပါတယ်။
၂။ `env_check.py` ကို run ကြည့်ပါ — ဘယ် Python နဲ့ ဘယ် package တွေ ရှိနေလဲ ဆိုတာ ပြပါတယ်။
၃။ error ပေါ်ရင် ဘယ် interpreter က ခေါ်နေလဲ ဆိုတာ အရင်စစ်ပါ။
၄။ လမ်းကြောင်းမှန်ရင် `import mcp` က အဆင်ပြေသွားပါတယ်။

### ဥပမာ

ဒီ snippet မှာ `uv run` နဲ့ `env_check.py` သုံးပြီး interpreter ကို စစ်တာ ပြထားပါတယ်။ ဘယ် Python path နဲ့ `mcp` package ရှိမရှိကို အထူး ကြည့်ပါနော်။
```python
# env_check.py prints which interpreter and packages you are using.
# Run it from the project root:
#   uv run python env_check.py
# Expected output lines:
#   Python executable: /path/to/project/.venv/bin/python
#   Python version: 3.11.x
#   Package versions found in this environment only.
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Course အတွင်းမှာ test တစ်ခု fail သွားရင် အရင်ဆုံး စစ်ရမှာက "ဘယ် Python နဲ့ လုပ်နေတာလဲ" ပါပဲ။ `env_check.py` က ဒါကို အလိုအလျောက် ဖြေပေးပါတယ်။ ဒါမျိုး မစစ်ရရင် error ကို နာရီပိုင်း ရှာနေရတယ်။ တကယ်တော့ အချိန်ကုန်တာက ကုဒ် မဟုတ်ဘဲ environment ဖြစ်နေတတ်တာပါ။

## အပိုင်း ၆ — `env_check.py` ကို တစ်လိုင်းချင်း ဖတ်ခြင်း

### ဘာကို ဆိုလိုတာလဲ

`../code/env_check.py` ဆိုတာ environment ကို စစ်ပေးတဲ့ Python script ပါ။ Environment ဆိုတာ — ကိုယ် run နေတဲ့ Python interpreter၊ version နဲ့ install လုပ်ထားတဲ့ package တွေ ဆိုတဲ့ အနေအထားကို ပြောတာပါ။

### ဘာကြောင့် လဲ

Error တွေ့ရင် ကိုယ်ထင်တာက ကုဒ် မှားနေတယ် ဆိုပြီး ကုဒ်ကိုပဲ ရှာတတ်တယ်။ ဒါပေမယ့် တကယ်တော့ environment မှားနေတာက ပိုများပါတယ်။ Python version မတူလို့၊ package မရှိလို့ fail တာတွေ ဖြစ်တတ်တာပါ။ ဒီ script က အဲဒါကို တန်းပြပေးတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ `sys.executable` က အခု run နေတဲ့ Python interpreter ရဲ့ လမ်းကြောင်း ပြပါတယ်။
၂။ `sys.version` က Python version ပြပါတယ်။
၃။ `importlib.metadata` ကို သုံးပြီး install လုပ်ထားတဲ့ package တွေကို ရှာပါတယ်။
၄။ ပြီးရင် အဲဒီ package version တွေကို ထုတ်ပြပါတယ်။

### ဥပမာ

ဒီ snippet မှာ `env_check.py` ရဲ့ အထဲပိုင်းကို အလိုင်းချင်း မြင်ရမှာပါ။ ဘယ် command က ဘာထွက်လဲ ဆိုတာကို သတိထားကြည့်ပါနော်။
```python
import sys
import importlib.metadata as metadata

# Show which interpreter is running this script
print("Python executable:", sys.executable)

# Show the Python version in use
print("Python version:", sys.version.split()[0])

# Check a package version inside this environment only
try:
    print("mcp version:", metadata.version("mcp"))
except metadata.PackageNotFoundError:
    print("mcp is NOT installed in this environment")

# Expected output:
# Python executable: .../.venv/bin/python
# Python version: 3.11.9
# mcp version: 1.x.x (or the NOT installed message)
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

M1 ကနေ M11 အထိ လမ်းကြောင်းမှာ ပြဿနာ တွေ့တိုင်း ဒီ script ကို အရင်ပြေးကြည့်ပါ။ ဒါဆို error တက်တာဟာ code ကြောင့်လား၊ environment ကြောင့်လား ဆိုတာ ချက်ချင်းခွဲသိရပါတယ်။ ဒါမျိုး မခွဲနိုင်ရင် debug လုပ်ချိန် နာရီပေါင်းများစွာ ကုန်သွားတတ်ပါတယ်။ ဖတ်တတ်သွားရင်တော့ ဘယ် error မှ ကြောက်စရာ မရှိတော့ပါဘူး။

## အနှစ်ချုပ်

- Environment ပြဿနာတွေက code ရေးတာထက်တောင် project အောင်မြင်မှုကို အများကြီး သက်ဆိုင်ပါတယ်
- `.venv` က project တစ်ခုချင်းစီအတွက် package သီးသန့်နေရာ ပေးတာပါ
- `uv` က အခြား tools တွေထက် မြန်ပြီး အလုပ်လုပ်ပုံလည်း ရိုးရှင်းပါတယ်
- `pyproject.toml` က project အချက်အလက်တွေကို စက်ဖြင့်ဖတ်နိုင်တဲ့ ဖိုင်တစ်ခုထဲ စုပေးထားပါတယ်
- `env_check.py` က interpreter နဲ့ package တွေ မှန်မမှန် စစ်ပေးတဲ့ script ပါ