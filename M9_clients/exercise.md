# လေ့ကျင့်ခန်းများ — M9 Host & Client Orchestration

## လေ့ကျင့်ခန်း ၁ — မော်ဒယ်မပါဘဲ client loop တစ်ခုကို ကိုယ်တိုင်ရေးခြင်း

`lab_1_client_loop.py` နှင့် `tool_loop.py` ကို အခြေခံပြီး LLM လုံးဝမပါသော MCP client loop တစ်ခုကို ရေးပါ။ `Client` ဖြင့် server တစ်ခုကို ချိတ်ဆက်ပြီး tool list ကို ယူပါ။ "choose" ဆင့်ကို hardcoded စည်းမျဉ်းတစ်ခု (ဥပမာ — ပထမဆုံး tool ကို ရွေးသည်) ဖြင့် အစားထိုးပါ။ ရွေးထားသော tool ကို ခေါ်ပြီး ရလဒ်ကို ရိုက်ထုတ်ပါ။

**Hints:** Client ကို ဖွင့်တဲ့ နည်းနှစ်မျိုးရှိတယ်ဆိုတာကို tutorial 02 မှာ သတိပြုပါ။ Loop ရဲ့ ဒီဇိုင်းက `tool_loop.py` ထဲမှာ ရှိပြီးသားပါ။
**Expected behavior:** ပရိုဂရမ်က LLM တစ်ကြိမ်မှ မခေါ်ဘဲ tool တစ်ခုကို ခေါ်ပြီး ရလဒ်ကို ရိုက်ထုတ်သည်။ `../../tests/test_m9_client_loop.py` ကို run လို့ အောင်မြင်ရမည်။

## လေ့ကျင့်ခန်း ၂ — မျက်နှာရလယ်ခုကို ရှာဖွေခြင်း

`tool_loop.py` ကို တိုးချဲ့ပြီး client method လေးခုဖြင့် server ရဲ့ မျက်နှာရလယ်များ (tools, resources, templates, prompts) အားလုံးကို ဖော်ပြစေပါ။ မတူညီသော server သုံးခုကို တိုက်ရိုက်ချိတ်ဆက်ကြည့်ပါ။

**Hints:** Client method လေးခုကို အတိအကျ tutorial 02 မှာ စာရင်းပြုထားပါတယ်။ `read_resource` ရဲ့ ပုံစံဟာ အမှားများတဲ့နေရာဖြစ်တာကို သတိထားပါ။
**Expected behavior:** Server တစ်ခုချင်းစီအတွက် tools, resources, templates, prompts လေးမျိုးလုံးရဲ့ အရေအတွက်နဲ့ နာမည်တွေကို ရိုက်ထုတ်ပြသည်။

## လေ့ကျင့်ခန်း ၃ — Schema မှ dispatch လုပ်ခြင်း

`lab_7_dispatch_table.py` ရှိ dispatcher ကို ရေးပါ။ Model တစ်ခုက တကယ်ထုတ်ပေးတဲ့ emission (tool နာမည်နှင့် arguments ပါသော JSON) ရှစ်မျိုးကို လက်ခံပြီး မှန်ကန်မှုကို စစ်ပြီးမှ tool ကို ခေါ်ပါ။ Schema နဲ့ မကိုက်ညီရင် ခေါ်ခင်းကို ငြင်းပါ။

**Hints:** Dispatcher တစ်ခုကို တစ်လိုင်းချင်း ခွဲခြားတာက tutorial 03 ရဲ့ အပိုင်း ၂ ပါ။ တစ်လှည့်ထဲမှာ tool နှစ်ခုခေါ်တဲ့ ကိစ္စလည်း ပါဝင်ပါတယ်။
**Expected behavior:** Schema စစ်ဆေးမှု မမှန်တဲ့ emission ကတော့ tool ခေါ်ခင်း တစ်ခါမှ မဖြစ်ဘဲ ငြင်းချက်တစ်ခု ထွက်သည်။

## လေ့ကျင့်ခန်း ၄ — Host settings file ကို စစ်ဆေးခြင်း

`lab_2_cline_settings.py` ကို သုံးပြီး `cline_mcp_settings.json` တစ်ခုကို ဖတ်ကာ အထဲက entry တစ်ခုချင်းစီကို စစ်ဆေးပါ။ Setting တစ်ခုစီကို FastMCP code အဖြစ် ပြန်ဘာသာပြန်ပြီး အဲဒီ entry က server ကို တကယ် စတင်နိုင်တဲ့အထိ သက်သေပြပါ။

**Hints:** Host ဆိုတာ ဘာလဲဆိုတဲ့ အယူအဆကို tutorial 04 ရဲ့ အပိုင်း ၁ ကနေ ရယူပါ။ Settings ကို FastMCP code အဖြစ် ပြန်ဘာသာပြန်တာက အပိုင်း ၃ ပါ။ stdio transport ကို သတိပြုပါ။
**Expected behavior:** Settings file ထဲက entry တိုင်းအတွက် — command, args, env — တွေကို ရိုက်ထုတ်ပြီး entry တစ်ခုက server တစ်ခုကို အောင်မြင်စွာ စတင်တာကို ပြသည်။

## လေ့ကျင့်ခန်း ၅ — LangGraph နှင့် stop condition

`lab_4_graph_offline.py` နှင့် `lab_6_stop_condition.py` ကို အခြေခံပြီး LangGraph graph တစ်ခုကို ဆောက်ပါ။ State ထဲမှာ `add_messages` reducer ပါရမည်ဖြစ်ပြီး (`lab_5_state_reducer.py` ကို ကြည့်ပါ) cycle တစ်ခုပါတဲ့ nodes နှင့် edges တွေကို တွဲဆက်ပါ။ Stop condition မပါတဲ့ အခြေအနေကို အရင် လေ့လာပြီး step budget နဲ့ ပြင်ပါ။

**Hints:** `ToolNode` က တကယ် ဘာလုပ်သလဲ၊ `tools_condition` က ဘယ်လို ဆုံးဖြတ်သလဲ ဆိုတာတွေက tutorial 07 ပါ။ Budget ဆိုတာ ဘာကို ကာကွယ်သလဲဆိုတဲ့ အပိုင်းကို ဖတ်ပါ။ `langgraph_client.py` နဲ့ ချိတ်ဆက်ကြည့်ပါ။
**Expected behavior:** Budget မပါရင် loop က ရပ်တန့်မသွားဘဲ budget ထည့်တဲ့အခါ run တစ်ခုက သတ်မှတ်ထားတဲ့ step အရေတွက်နဲ့ ရပ်တန့်သည်။

## လေ့ကျင့်ခန်း ၆ — Checkpointer, threads နှင့် server နှစ်ခု

`lab_8_two_servers.py` ကို အခြေခံပြီး checkpointer (`MemorySaver`) နဲ့ `thread_id` သုံးပြီး graph တစ်ခုကိu ဒုတိယ turn မှာ ပြန် run ပါ။ ဒုတိယ turn မှာ state ထဲ ဘာတွေ ပြန်ပါလာသလဲဆိုတာကို တိုင်းတာပြပါ။ ပြီးရင် server နှစ်ခုကို graph တစ်ခုထဲ တွဲဆက်ပြီး `lab_3_hand_adapter.py` က လက်ဖြင့်ရေးထားတဲ့ MCP → LangChain adapter သုံးပြီး tool list ကို တစ်ဆင့် စစ်ကြည့်ပါ။

**Hints:** `thread_id` မပါလျှင် ဘာဖြစ်သလဲဆိုတဲ့ error ကို tutorial 08 ရဲ့ အပိုင်း ၅ မှာ တိုင်းထားပြထားပါတယ်။ Adapter မှာ Pydantic model အဖြစ် schema ပြောင်းတဲ့ နည်းက tutorial 05 ရဲ့ အပိုင်း ၃ ပါ။
**Expected behavior:** ဒုတိယ turn က ပထမ turn ရဲ့ messages တွေကို state ထဲ ပြန်မြင်ရပြီး server နှစ်ခုက tool တွေကိu တစ်ပြိုင်တည်း အသုံးပြုနိုင်သည်။
