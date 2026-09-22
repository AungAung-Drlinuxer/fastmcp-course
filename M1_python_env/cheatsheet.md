# M1 — Cheatsheet


- `uv` သည် venv + install + lock + sync လေးဆင့်ကို တစ်ချက်တည်း ပေါင်းသည်
- `pyproject.toml` က project ရဲ့ single source of truth ဖြစ်သည်
- `.venv` က project တစ်ခုစီကို သီးသန့် ခွဲသည် — dependency hell ကို ဖြေသည်
- ⭐ `uv run` သည် `activate` ထက် လုံခြုံသည် — မှားသည့် interpreter ကို ဖြေသည်
- Version ကို ချုပ်ခြင်း (`>=4.0.5,<5`) သည် အလှဆင် မဟုတ် — FastMCP ၏ API ရွေ့ခဲ့သည်
- Interpreter ပြဿနာကို `sys.executable` ဖြင့် ရှာသည် — `env_check.py` က ဒါကို စောစီးစွာ ဖြေသည်


- [`../code/env_check.py`](code/env_check.py) — ဤဖိုင်၏ နောက်ဆုံး အပိုင်းတွင် တစ်လိုင်းချင်း ဖတ်ထားသည်
- [`../README.md`](../README.md) — module အကျဉ်း
- [`../../VERIFIED.md`](../VERIFIED.md) — စမ်းသပ်ပြီး အတည်ပြုထားသော API အချက်များ
