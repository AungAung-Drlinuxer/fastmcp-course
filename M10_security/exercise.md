# လေ့ကျင့်ခန်း — M10 Production Security & Hardening

## လေ့ကျင့်ခန်း ၁ — Threat Model ကို code အဖြစ် ရေးပါ

`lab_1_threat_model.py` ကို အခြေခံပြီး MCP server တစ်ခုအတွက် threat model ကို Python dictionary ဖြင့် ရေးပါ။ asset အနည်းဆုံး ၃ ခု၊ trust boundary ၂ ခု၊ actor ၃ မျိုး (user, model, tool) ကို ထည့်သွင်းပြီး STRIDE အတန်းအစားများကို ချိတ်ဆက်ပေးပါ။ ထို့နောက် tool အသစ်တစ်ခု ထည့်ချင်ပါက မေးရမည့် မေးခွန်းသုံးခုကို comment အဖြစ် ရေးပါ။

**Hints:** asset = အကာအရံပေးရမည့် အရာ၊ trust boundary = privilege ပြောင်းလဲသည့် နေရာ၊ actor = စကားလုံးကို လှုပ်ရှားစေနိုင်သူဟု သတ်မှတ်ပါ။ Threat, vulnerability, risk သုံးခု ကွာခြားချက်ကို docstring တွင် ရှင်းပါ။

**Expected behavior:** script ကို run လျှင် တစ်ခုချင်းစီ၏ asset/boundary/actor mapping ကို စဉ်းနားနိုင်သော output ရရှိပြီး၊ မည့်သည့် tool မဆို `@mcp.tool` အဖြစ် ထည့်ခင်း မေးခွန်းသုံးခု ရှိသည်။

## လေ့ကျင့်ခန်း ၂ — Indirect injection bench ဆောက်ပါ

`lab_2_injection_bench.py` ကို ကိုယ်တိုင်ပြန်ရေးပါ — carrier ဖိုင် (log file, web page, code comment) ထဲမှ prompt ကို tool result မှတဆင့် model ဆီ ပြောင်းလဲပို့နိုင်သည့် ဇယားတစ်ခု ဆောက်ပါ။ Direct injection နှင့် indirect injection ကို ခွဲခြားပြပြီး confused deputy ဖြစ်စဉ်ကို comment ဖြင့် ရှင်းပါ။

**Hints:** Injection ကို sanitize လုပ်၍ မရရခြင်း အကြောင်းရင်း ၄ ချက်ထဲမှ တစ်ခုကို comment တွင် ရေးပါ။ ကာကွယ်မှုသည် string filter မဟုတ်ဘဲ ၃ ဆင့် pattern (အမှတ်အသား၊ ခွဲခြားမှု၊ confirmation) ဖြစ်သည်ကို သတိပြုပါ။

**Expected behavior:** bench ကို run လျှင် carrier တစ်ခုချင်းစီအတွက် injection ဖြစ်နိုင်ခြေနှင့် ကာကွယ်ရမည့် အဆင့်ကို output ပြသည်။

## လေ့ကျင့်ခန်း ၃ — Tool manifest ဖြင့် rug-pull ဖမ်းပါ

`lab_3_tool_manifest.py` ပုံစံအတိုင်း tool surface အားလုံးကို JSON manifest အဖြစ် မှတ်တမ်းတင်ပါ — tool name, docstring hash, parameter schema တို့ပါဝင်စေပါ။ ထို့နောက် docstring တွင် prompt ထည့်သွင်းထားသော poisoned version တစ်ခုနှင့် hash ပြောင်းလဲထားသော rug-pull version တစ်ခုကို ဖမ်းတတ်သော check ရေးပါ။

**Hints:** Docstring သည် code ဖြစ်သည် — model ဖတ်ပြီး လိုက်လုပ်နိုင်သည်။ Version pin သည် အပြောင်းအလဲကို ကာကွယ်ပေးသော်လည်း ပထမဆုံး install တွင် ရှိပြီးသား poisoning ကို မကာကွယ်နိုင်ဟု သတိပြုပါ။

**Expected behavior:** poisoned docstring ပါသော tool တစ်ခုကို ဖမ်းပြီး၊ manifest နှင့် current surface မတူပါက warning output ထုတ်ပြသည်။

## လေ့ကျင့်ခန်း ၄ — Unbounded tool ကို bounded tool ဖြစ်အောင် ပြင်ပါ

`lab_5_unbounded_tool.py` ရှိ `read_log_UNSAFE` (shell=True, allowlist မရှိ, path confinement မရှိ, timeout မရှိ, return limit မရှိ) ကို ပြဿနာ ၅ ခုလုံး ဖြေရှင်းပါ — `lab_6_confinement.py` ရှိ `_resolve_within()` pattern နှင့် `Path.resolve()` ကို အသုံးပြုပါ၊ `lab_7_output_bounds.py` ရှိ bound သုံးခု (line count, byte size, list length) ကို ထည့်ပါ။

**Hints:** `shlex.split()` သည် fix မဟုတ် — shell ဖယ်ရှားခြင်းသာ ဖြေရှင်းချက်။ Symlink escape ကို ဖယ်ရှားရန် resolve လုပ်ပြီးမှ `LOG_ROOT` နှင့် နှိုင်းယှဉ်ပါ။ `list_logs` သည်လည်း security control တစ်ခုဖြစ်သည် — အမည်များကို အတန်းအစားခွဲနိုင်စွာ ပြန်ပေးပါ။

**Expected behavior:** `../etc/passwd` ကဲ့သို့ path escape ကို refusal ဖြင့် ငြင်းပြီး၊ timeout ဖြင့် ရပ်တန့်ပြီး၊ return သည် သတ်မှတ် limit ထက် ကျော်လွန်မည်မဟုတ်ပါ။

## လေ့ကျင့်ခန်း ၅ — Attack matrix ကို run လုပ်ပြီး ချဲ့ထွင်ပါ

`lab_9_attack_matrix.py` ရှိ တိုက်ခိုက်မှု ၇ ခုကို run လုပ်ပါ — ၎င်းတို့သည် မိသားစု ၂ မျိုး (path family, shell family) တွင် ရှိသည်ကို သတိပြုပါ။ ထို့နောက် တိုက်ခိုက်မှုအသစ် တစ်ခု (ဥပမာ — `LOG_ROOT` အတွင်းရှိ symlink တစ်ခုမှတဆင့် အပြင် file ဖတ်ရန် ကြိုးစားခြင်း) ထည့်သွင်းပြီး အဘယ်ကြောင့် မအောင်မြင်သည်ကို ရှင်းပါ။

**Hints:** Matrix တစ်ခုစီတွင် attack name, input, မျှော်မှန်းရလဒ် (blocked), ဘယ် control က ဘယ်လို block လုပ်သည် ဆိုသည့် အချက်လေးခု ပါဝင်သင့်သည်။ Refusal သည် `{ok: False, error: ..., hint: ...}` shape ဖြင့် ထွက်သင့်သည် — `lab_8_refusal_contract.py` ရှ contract အတိုင်း။

**Expected behavior:** တိုက်ခိုက်မှုအားလုံး blocked ဟု ပြပြီး၊ တစ်ခုချင်းစီအတွက် တာဝန်ရှိသော control (path confinement, no-shell, output bound) ကို ဖော်ပြသည်။

## လေ့ကျင့်ခန်း ၆ — Audit trail ဆောက်ပြီး container recipe စစ်ပါ

`lab_11_audit_log.py` ရှိ ပုံစံအတိုင်း JSON Lines format ဖြင့် audit log တစ်ခု ရေးပါ — tool name, actor, timestamp, argument hash တို့ ပါဝင်စေပြီး redaction ဖြင့် တောင်းဆိုမှုအတွင်း ကိုယ်ရေးအချက်အလက်များ မ leaked စေပါ။ ထို့နောက် `lab_10_container_smoke.py` ဖြင့် Dockerfile recipe ကို Docker မပါဘဲ စစ်ဆေးပါ — non-root user, read-only flag များ ပါဝင်မှုကို 确认 လုပ်ပါ။

**Hints:** Audit log သည် incident မေးခွန်း ၃ ခု (ဘယ်သူ၊ ဘယ် tool၊ ဘယ်အချိန်) ကို ဖြေရမည်၊ error message မဟုတ်။ Dockerfile သည် runtime privilege ကို အပြည့်အဝ မသက်သောပေါက်နိုင် — kernel boundary သည် ဒုတိယ အလွှာဖြစ်သည်။

**Expected behavior:** Tool ခေါ်ဆိုမှုတိုင်းသည် JSON Lines တစ်ကြောင်း ထုတ်ပြီး argument တွင် path နှင့် parameter ချုံ့ပြသည်၊ ပြီးလျှင် recipe check က container ဆုံးဖြတ်ချက် ၄ ခုလုံး pass ဖြစ်ကြောင်း ဖော်ပြသည်။
