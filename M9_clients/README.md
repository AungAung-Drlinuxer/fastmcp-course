# M9 — Host & Client Orchestration

> **ကြာမြင့်ချိန်:** 3.5 နာရီ · **Phase:** Phase 3 — Advanced Interaction

ဒီ module မှာ MCP client ဆိုတာ အတိအကျ ဘာလဲ၊ host နဲ့ ဘယ်လိုချိတ်ဆက်မလဲ၊ LangGraph နဲ့ orchestration ကို ဘယ်လို တည်ဆောက်မလဲ ဆိုတာကို လက်တွေ့စမ်းကြည့်ပြီး သင်ရမှာပါ။

## ဤသင်ခန်းစာတွင် ဘာရမည်လဲ

- MCP client loop ကို model မပါဘဲ Python program တစ်ခုအနေနဲ့ ကိုယ်တိုင်ရေးခြင်း
- tools, resources, templates, prompts — surface လေးမျိုးကို client method လေးခုနဲ့ ရှာဖွေခြင်း
- Model ထုတ်တဲ့ tool call emission ကနေ schema အပေါ်မူတည်ပြီး dispatch လုပ်ခြင်း
- Host (Cline) ရဲ့ `cline_mcp_settings.json` ကို ဖတ်ခြင်း၊ audit လုပ်ခြင်း
- MCP → LangChain adapter ကို လက်ဖြင့်ရေးခြင်း
- LangGraph state, `add_messages` reducer, nodes, edges, cycle ရဲ့ stop condition
- Checkpointer နဲ့ `thread_id` — ဒုတိယအကြိမ် စကားပြောတဲ့အခါ ဘာမှတ်ထားလဲ
- Chooser နှစ်မျိုး — `scripted_chooser` နဲ့ `model_chooser`
- Server တစ်ခုကို host များစွာ၊ server များစွာကို host တစ်ခု — orchestration

## သင်ခန်းစာများ

1. Client loop ဆိုတာ သာမန် programming — MCP without a model
2. Surface လေးမျိုးကို ရှာဖွေခြင်း — tools, resources, templates, prompts
3. Schema ကနေ dispatch လုပ်ခြင်း — model က တကယ်ဘာထုတ်လဲ
4. Host နဲ့ စာရင်းသွင်းခြင်း — Cline settings file နဲ့ stdio transport
5. MCP → LangChain adapter ကို လက်ဖြင့်ရေးခြင်း
6. LangGraph state နဲ့ `add_messages` reducer
7. Graph — nodes, edges, routing နဲ့ stop condition လိုတဲ့ cycle
8. Checkpointing နဲ့ threads — ဒုတိယအကြိမ်မှာ ဘာမှတ်လဲ
9. Scripted chooser နဲ့ model chooser — graph တစ်ခု၊ ဦးနှစ်လုံး
10. Orchestration — server တစ်ခု၊ host များစွာ / server များစွာ၊ host တစ်ခု

## လိုအပ်ချက်များ (Prerequisites)

- M8_elicitation အပြီးသတ်ဖို့ — MCP အခြေခံ၊ tool သဘောတရားတွေ နားလည်ထားဖို့
- Python — function, dict, class နဲ့ exception handling အခြေခံ
- JSON ဖိုင်ဖတ်တတ်ဖို့၊ JSON Schema အကြမ်းသိဖို့
- LAB 9 (model chooser) အတွက် — LLM API key (မရှိရင်လည်း `scripted_chooser` နဲ့ ဆက်လက်လုပ်နိုင်ပါတယ်)

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- MCP server တစ်ခုကို ကိုယ်ပိုင် Python program ထဲကနေ ခေါ်သုံးချင်တဲ့အခါ
- Server တစ်ခုကို Cline လိုမျိုး host တစ်ခုထဲ စာရင်းသွင်းချင်တဲ့အခါ
- LLM ပါတဲ့ agent loop တစ်ခုကို LangGraph နဲ့ တည်ဆောက်ပြီး MCP tools ချိတ်ချင်တဲ့အခါ
- Agent loop တွေ infinite cycle မဖြစ်စေဖို့ step budget စနစ်တကျထားချင်တဲ့အခါ
- Server အများအပြားကို host တစ်ခုထဲ တစ်ပြိုင်တည်း စီမံခန့်ခွဲချင်တဲ့အခါ

## ဖိုင်ဖွဲ့စည်းပုံ

- `explanation.md` — သင်ခန်းစာအကြဉ်းချုပ် (concept အားလုံးရှင်းပြထားသည်)
- `exercise.md` — လေ့ကျင့်ခန်း ၆ ခု (LAB 1 မှ LAB 10 အထိ စုစည်းထားသည်)
- `solution.md` — အဖြေများ (အသေးစိတ်ရှင်းပြချက်နှင့်တကွ)
- `cheatsheet.md` — အမြန်ရှာဖွေရန် ကိုးကားစာရင်း
- `../code/` — lab ကုဒ်ဖိုင်များ (`tool_loop.py`, `langgraph_client.py` အပါအဝင်)

## ကိုးကား

- အရင် module — [../M8_elicitation/README.md](../M8_elicitation/README.md)
- နောက် module — [../M10_security/README.md](../M10_security/README.md)
- ဒီ module ရဲ့ စမ်းသပ်ချက် — [../../tests/test_m9_client_loop.py](../tests/test_m9_client_loop.py)
