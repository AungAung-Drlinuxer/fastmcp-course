# M1 — Modern Python Environment (uv): ရှင်းလင်းချက်

## အပိုင်း ၁ — ပြဿနာကို အရင်နားလည်ပါ

### ဘာကို ဆိုလိုတာလဲ

Python project တစ်ခုစီမှာ package များ၊ version များနဲ့ interpreter တွေ ကွဲပြားနိုင်သည်။ ဒီအချက်တွေက project တစ်ခုရဲ့ အောင်မြင်မှု သို့မဟုတ် ကျရှုံးမှုကို သီးသန့် ဆုံးဖြတ်ပေးလို့ရသလောက် အရေးကြီးသည်။

### ဘာကြောင့် လဲ

Package တွေ တစ်နေရာထဲ ပူးပေါင်းထားရင် version တိုက်ဆုန်းမှုများ ဖြစ်ပေါ်သည်။ Project တစ်ခုက ရွေ့လို့ မရတော့တဲ့ အခြေအနေ ရောက်လာနိုင်သည်။ အခြားသူတွေ ကိုယ့် project ကို တည်ဆောက်ရင်လည်း တူညီတဲ့ error တွေ နှစ်ဆိုင်ခံရသည်။

### ဘယ်လို အလုပ်လုပ်လဲ

Project တစ်ခုချင်းစီကို သူ့နေရာမှာ သီးသန့် ထားပါသည်။ ဒါကို isolation လို့ ခေါ်သည်။ Python မှာ ဒီအတွက် `.venv` နဲ့ `pyproject.toml` တို့ကို အသုံးပြုသည်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

MCP server တည်ဆောက်တဲ့အခါ dependency တွေ မှန်ကန်စွာ install မဖြစ်ရင် လုံးဝ မအလုပ်လုပ်နိုင်ပါ။ ဒီ module က နောက် module အားလုံးရဲ့ အခြေခံ ဖြစ်သည်။

## အပိုင်း ၂ — `.venv` ဆိုတာ ဘာလဲ

### ဘာကို ဆိုလိုတာလဲ

`.venv` ဆိုတာ "virtual environment" ဆိုတဲ့ ဖိုင်တွဲ တစ်ခုဖြစ်သည်။ သူ့ထဲမှာ Python interpreter တစ်ခု အတုနဲ့ project အတွက်သာ install ထားတဲ့ package တွေ ပါဝင်သည်။

### ဘာကြောင့် လဲ

System-wide Python ကို တိုက်ရိုက် အသုံးပြုရင် အားလုံးရဲ့ project တွေက တစ်နေရာတည်းကို မှီခိုလို့ ပြဿနာ ဖြစ်သည်။ `.venv` က project တစ်ခုချင်းစီကို ကိုယ်ပိုင် package စပေ့ တစ်ခု ပေးလိုက်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

Project folder တစ်ခုထဲ `.venv` ဖိုင်တွဲ တစ်ခု ဖန်တီးသည်။ Activate လုပ်တဲ့အခါ shell က `.venv` ထဲက Python ကိုပဲ ရှာသည်။ Package တွေ ထဲ install ရင် system Python ကို မထိခိုက်ပါ။

### ဥပမာ

``python
# This is shell, shown as a block for clarity:
# uv init creates pyproject.toml, uv add installs into .venv
# .venv/bin/python (macOS/Linux) or .venv\Scripts\python (Windows)
# Expected output: a .venv/ directory inside your project folder
``

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

`mcp` package က version တစ်ခုကို လိုအပ်သလို `pydantic` က နောက်တစ်ခု လိုချင်နိုင်သည်။ `.venv` မှာ ဒီတိုက်ဆုန်းမှုက အခြား project တွေဆီ မရောက်စေပါ။

## အပိုင်း ၃ — `uv` က ဘာကွာသလဲ

### ဘာကို ဆိုလိုတာလဲ

`uv` ဆိုတာ Rust နဲ့ ရေးထားတဲ့ Python package/project manager တစ်ခုဖြစ်သည်။ `pip`၊ `venv`၊ `pip-tools` တို့ရဲ့ လုပ်ငန်းတာဝန် အားလုံးကို တစ်ခုတည်းနဲ့ လုပ်ပေးသည်။

### ဘာကြောင့် လဲ

ရိုးရိုး `pip` + `venv` နဲ့ ဆင်းရင် လုပ်ထုံးလုပ်နည်း အဆင့်တွေ များသည် — environment ဖန်တီး၊ activate လုပ်၊ install လုပ်၊ lock file ရေး။ `uv` က ဒါအားလုံးကို မြန်စွာ တစ်ပြိုင်တည်း လုပ်ပေးသည်။

### ဘယ်လို အလုပ်လုပ်လဲ

- `uv init` — project အသစ်နဲ့ `pyproject.toml` ဖန်တီး
- `uv add <package>` — dependency ထည့်ပြီး `.venv` ထဲ install
- `uv run <script>` — `.venv` ထဲက Python နဲ့ အလုပ်လုပ်
- `uv python install <version>` — Python version တစ်ခု download

### ဥပမာ

``python
# Shell commands for starting a project with uv:
#   uv init my-mcp-project
#   cd my-mcp-project
#   uv add mcp
#   uv run python env_check.py
# Expected output: pyproject.toml, uv.lock and .venv/ created,
# and env_check.py runs with the project's own interpreter.
``

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

MCP development မှာ dependency အသစ်တွေ ထည့်ဖို့ မကြာခဏ လိုအပ်သည်။ `uv` က ဒီလုပ်ငန်းကို စက္ကန့်ပိုင်းမှာ ပြီးစေလို့ အချိန်ရှင်းပေးသည်။

## အပိုင်း ၄ — `pyproject.toml`

### ဘာကို ဆိုလိုတာလဲ

`pyproject.toml` ဆိုတာ project ရဲ့ metadata နဲ့ dependency စာရင်း ပါဝင်တဲ့ ဖိုင်ဖြစ်သည်။ Project နာမည်၊ Python version လိုအပ်ချက်နဲ့ package တွေကို ဖော်ပြသည်။

### ဘာကြောင့် လဲ

README ထဲ dependency တွေ စာရင်းရေးထားတာထက် `pyproject.toml` က စက်ဖြင့် ဖတ်နိုင်သည်။ `uv` က ဒီဖိုင်ကို ဖတ်ပြီး environment တစ်ခုလုံးကို ပြန်တည်ဆောက်ပေးနိုင်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

TOML format နဲ့ `[project]` section ထဲ `name`၊ `requires-python`၊ `dependencies` တို့ကို သတ်မှတ်သည်။ `uv add` လုပ်တိုင်း ဒီဖိုင်က အလိုအလျောက် ပြင်သည်။

### ဥပမာ

``toml
# pyproject.toml example
[project]
name = "my-mcp-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "mcp>=1.0.0",
]
``

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

အဖွဲ့ဝင်တစ်ယောက် `git clone` လုပ်ပြီး `uv sync` လုပ်ရင် environment တစ်ခုလုံး ပြန်ရသည်။ "ကျွန်တော့်စက်မှာ ဘာကြောင့် မအလုပ်လုပ်ဘူးလဲ" လို့ မေးစရာ မလိုတော့ပါ။

## အပိုင်း ၅ — Interpreter ပြဿနာကို ရှာခြင်း

### ဘာကို ဆိုလိုတာလဲ

Shell ထဲ `python` ရိုက်တဲ့အခါ ဘယ် Python က အလုပ်လုပ်သလဲ ဆိုတာ မသိရင် မှားယွင်းမှုများ ဖြစ်သည်။ `import mcp` error တွေက များသောအားဖြင့် လမ်းကြောင်း မှားနေလို့ ဖြစ်သည်။

### ဘာကြောင့် လဲ

System Python တစ်ခု၊ `.venv` Python တစ်ခု၊ တစ်ခါတစ်ရံ PATH ထဲ အခြား Python တွေ အထိ ရှိနိုင်သည်။ မှားတဲ့ interpreter နဲ့ package တွေ install လုပ်မိရင် `.venv` ထဲ ဘာမှ မရောက်ပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

`uv run` ကို အသုံးပြုပါ — သူက `.venv` ကို အလိုအလျောက် ရွေးပေးသည်။ `env_check.py` ကို လည်း လက်တွေ့ စစ်ဆေးဖို့ အတွက် ရေးထားသည်။

### ဥပမာ

``python
# env_check.py prints which interpreter and packages you are using.
# Run it from the project root:
#   uv run python env_check.py
# Expected output lines:
#   Python executable: /path/to/project/.venv/bin/python
#   Python version: 3.11.x
#   Package versions found in this environment only.
``

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Course အဆင့်မှာ test များ ကျွမ်းကျော်တဲ့အခါ ပထမဆုံး စစ်သင့်တာက "ဘယ် Python နဲ့ လုပ်နေတာလဲ" ဆိုတာပါပဲ။ `env_check.py` က ဒါကို အလိုအလျောက် ဖြေပေးသည်။

## အပိုင်း ၆ — `env_check.py` ကို တစ်လိုင်းချင်း ဖတ်ခြင်း

### ဘာကို ဆိုလိုတာလဲ

`../code/env_check.py` ဆိုတာ environment ကို စစ်ဆေးတဲ့ Python script တစ်ခုဖြစ်သည် — ဘယ် interpreter၊ ဘယ် version၊ ဘယ် package တွေ ရှိလဲ ဆိုတာကို ထုတ်ပြသည်။

### ဘာကြောင့် လဲ

Error တစ်ခု တွေ့တဲ့အခါ ကုဒ် ဘယ်နေရာမှာ မှားလဲ ဆိုတာထက် environment ဘယ်နေရာမှာ မှားလဲ ဆိုတာက ပိုမကြာခဏ ဖြစ်သည်။ ဒီ script က ဒီကိစ္စကို ဖြေရှင်းပေးသည်။

### ဘယ်လို အလုပ်လုပ်လဲ

`sys.executable` နဲ့ `sys.version` တို့က interpreter လမ်းကြောင်းနဲ့ version ကို ပြသည်။ ပြီးရင် `importlib.metadata` ကို အသုံးပြုပြီး package version တွေကို ရှာပြသည်။

### ဥပမာ

``python
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
``

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

M1 ကနေ M11 အထိ လမ်းကြောင်းပြဿနာ တွေ့တိုင်း ဒီ script ကို အသုံးပြုရမည်။ ဖတ်တတ်ရင် ဘယ် error မှ ကြောက်စရာ မရှိတော့ပါ။

## အနှစ်ချုပ်

- Environment ပြဿနာတွေက project ရဲ့ အောင်မြင်မှုကို ဆုံးဖြတ်သလို အရေးကြီးသည်
- `.venv` က project တစ်ခုချင်းစီကို သီးသန့် package စပေ့ ပေးသည်
- `uv` က ရိုးရိုး tools တွေထက် မြန်ပြီး လုပ်ထုံးကို ရိုးရှင်းစေသည်
- `pyproject.toml` က project ကို စက်ဖြင့်ဖတ်နိုင်တဲ့ ပုံစံနဲ့ သတ်မှတ်ပေးသည်
- `env_check.py` က interpreter နဲ့ package တွေကို စစ်ဆေးပေးသည်
