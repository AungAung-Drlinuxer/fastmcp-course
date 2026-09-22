# M5 — Action-Oriented Tools (`@mcp.tool`)

> **ကြာမြင့်ချိန်:** 3 နာရီ · **Phase:** Phase 2 — MCP Core Surfaces

## ဤသင်ခန်းစာတွင် ဘာရမည်လဲ

- `@mcp.tool` ဖြင့် စံချိန်မီ MCP tool တစ်ခု ရေးဆွဲနည်း
- Contract ဖိုင်းများ (name, docstring, `Args:`, annotations, return) နှင့် JSON Schema သို့ ကူးပြောင်းပုံ
- Exception မြှင့်တင်ခြင်း (Raise) နှင့် Data ပြန်ပို့ခြင်း (Return) ၏ ကွာခြားချက်
- Pydantic validation နှင့် boundary defense
- `async def` tool များနှင့် `httpx` ဖြင့် external API ခေါ်ဆိုနည်း
- Tool trio (search → enumerate → fetch) နှင့် truncation၊ clamping နည်းပညာများ

## သင်ခန်းစာများ

1. MCP Tool ဆိုတာ ဘာလဲ — one action, one verb, one narrow contract
2. Contract Fields — name, docstring, `Args:`, annotations, return
3. Raise vs Return — `CallToolResult` နှင့် error taxonomy
4. The Hint Field — model ဖတ်ရှုသည့် အစိတ်အပိုင်း
5. Pydantic Validates the Request — validation gate နှင့် domain rules
6. Async Tools — sequential vs concurrent
7. httpx — timeouts, User-Agent, `raise_for_status()`
8. The Tool Trio — `search_articles` → `list_sections` → `get_content`
9. Truncation at the Tool Boundary — `offset`, `limit`, `truncated`, `next_offset`
10. Air-Gapped Fixtures နှင့် Honest Sources
11. The MediaWiki Wikitext Shape Trap — normalisation
12. Clamping Untrusted Limits — CLAMP vs REFUSE policy

## လိုအပ်ချက်များ (Prerequisites)

- M4_fastmcp_basics ကို ပြီးမြောက်ထားရမည် — FastMCP server တစ်ခု စတင်တည်ဆောက်နိုင်ရမည်
- Python type annotations အခြေခံ သိထားရမည်
- Terminal၊ `uv run` နှင့် traceback ဖတ်နည်း (tutorial `00-beginner-bridge.md` တွင် အသေးစိတ်ရှိသည်)

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- LLM အတွက် လုံခြုံသော၊ ရှင်းလင်းသော tool များ ရေးချင်သည့်အခါ
- External API များ (Wikipedia ကဲ့သို့) ကို MCP tool အဖြစ် ချိတ်ဆက်ချင်သည့်အခါ
- Model က error ကို ပြန်လည်ဆင်ခြင်နိုင်ရေး hint များ ဒီဇိုင်းလုပ်ချင်သည့်အခါ

## ဖိုင်ဖွဲ့စည်းပုံ

- `explanation.md` — သင်ခန်းစာအပြည့်အစုံ၊ ဘာကြောင့်/ဘယ်လို အလုပ်လုပ်လဲ ရှင်းပြထားသည်
- `exercise.md` — လက်တွေ့လေ့ကျင့်ခန်း ၆ ခု (lab ဖိုင်များနှင့် တွဲဖက်ထားသည်)
- `solution.md` — လေ့ကျင့်ခန်းအဖြေများ
- `../code/` — lab ကုဒ်ဖိုင်များ (`lab_1_error_taxonomy.py` မှ `lab_11_clamp_untrusted_limits.py` အထိ)

## ကိုးကား

- ရှေ့ပိုင်း: [../M4_fastmcp_basics/README.md](../M4_fastmcp_basics/README.md)
- နောက်ပိုင်း: [../M6_resources/README.md](../M6_resources/README.md)
- စမ်းသပ်မှု: [../tests/test_m5_tools.py](../tests/test_m5_tools.py)
