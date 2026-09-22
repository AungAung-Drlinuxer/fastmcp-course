# M10 — Production Security & Hardening

> **ကြာမြင့်ချိန်:** 2.5 နာရီ · **Phase:** Phase 4 — Hardening & Capstone

## ဤသင်ခန်းစာတွင် ဘာရမည်လဲ

MCP server တစ်ခုကို production တွင် တည်ငြိမ်စွာ လည်ပတ်စေရန် လိုအပ်သည့် security နည်းပညာများကို လက်တွေ့ ကိုင်တွယ်မည်။ ဒီ module ရဲ့ အဓိက အချက်မှာ — **tool ဟာ attack surface ဖြစ်သည်** ဆိုတာပါ။

- **Threat modelling** — asset, trust boundary, actor တို့ကို သတ်မှတ်ပြီး threat model ကို code အဖြစ် ရေးခြင်း (`lab_1_threat_model.py`)
- **Prompt injection** — direct နှင့် indirect injection ကို ကွာခြားစွာ နားလည်ပြီး injection bench တည်ဆောက်ခြင်း (`lab_2_injection_bench.py`)
- **Tool poisoning နှင့် rug-pull** — tool description သည် model လည်ပတ်သည့် code ဖြစ်သဖြင့် tool surface ကို manifest အဖြစ် မှတ်ခြင်း (`lab_3_tool_manifest.py`)
- **Least privilege (အလွှာ ၂ ခု)** — host level နှင့် server level ရဲ့ capability budget ကို တိုင်းတာခြင်း (`lab_4_capability_inventory.py`)
- **Unbounded tool anti-pattern** — `subprocess.run(command, shell=True)` ရဲ့ ပြဿနာ ၅ ချက်ကို ပြန်လည် သုံးသပ်ခြင်း (`lab_5_unbounded_tool.py`)
- **Path confinement** — allowlist root နှင့် `Path.resolve()` ကို check မတိုင်မီ သုံးခြင်း (`lab_6_confinement.py`, `path_validation.py`)
- **Output bounding** — shell လုံးဝ ဖယ်ရှားခြင်း၊ hard limit သုံးခြင်း (`lab_7_output_bounds.py`)
- **Structured refusal** — `{ok: False, error: ..., hint: ...}` return shape နှင့် closed error set (`lab_8_refusal_contract.py`)
- **Attack matrix** — တိုက်ခိုက်မှု ၇ မျိုးကို စမ်းသပ်ပြီး တစ်ခုစီ ဘာကြောင့် ကျဆုံးသည်ကို ဖော်ပြခြင်း (`lab_9_attack_matrix.py`)
- **Containerisation** — Dockerfile ဆုံးဖြတ်ချက် ၄ ချက်၊ non-root user (`lab_10_container_smoke.py`)
- **Audit logging** — JSON Lines ပုံစံ၊ redaction၊ incident မေးခွန်းများကို ဖြေနိုင်သည့် audit trail (`lab_11_audit_log.py`)

## သင်ခန်းစာများ

1. Threat model ကို code အဖြစ် ရေးခြင်း — STRIDE ကို MCP ပေါ် တင်ကြည့်ခြင်း
2. Prompt injection — indirect injection သည် confused deputy ပြဿနာ ဖြစ်ပုံ
3. Tool poisoning နှင့် rug-pull — version pin က ဘာကာကွယ်ပြီး ဘာမကာကွယ်လဲ
4. Least privilege — process အလွှာနှင့် tool အလွှာ
5. Unbounded tool anti-pattern ၅ ချက်နှင့် `shlex.split()` က ဘာကြောင့် fix မဖြစ်လဲ
6. Path confinement — symlink escape ကိုပါ ဖမ်းနိုင်သည့် `Path.resolve()` နည်း
7. Output bounding နှင့် return shape — honest limits
8. Structured refusal — schema violation သည် refusal မဟုတ်ပါ
9. Attack matrix — တိုက်ခိုက်မှုတစ်ခုစီက ဘယ် control က ရပ်တန့်သလဲ
10. Containerisation နှင့် non-root user — kernel သည် ဒုတိယ နယ်နိမိတ်
11. Audit logging — incident ကို ကူညီပြီး ဘာမှ leak မလုပ်သည့် မှတ်တမ်း

## လိုအပ်ချက်များ (Prerequisites)

- **M9_clients** အပြီး — MCP client ချိတ်ဆက်မှုကို နားလည်ထားရမည်
- Python 3.10+၊ `subprocess`, `pathlib` အခြေခံ အသုံးအနှုန်း
- pytest — test suite လည်ပတ်ရန်
- Docker (LAB 10 အတွက် — မရှိလည်း lab က recipe ကို Docker မလိုဘဲ စစ်နိုင်သည်)

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- MCP server တစ်ခုကို development မှ production သို့ မြှင့်တင်မည့်အချိန်
- Tool အသစ် တစ်ခု ထည့်တိုင်း မေးရမည့် မေးခွန်းများ လိုအပ်သည့်အခါ
- Security review တစ်ခု လုပ်ဆောင်ရန် checklist လိုအပ်သည့်အခါ
- M11_capstone အတွက် hardened server အခြေခံကို ပြင်ဆင်ရာတွင်

## ဖိုင်ဖွဲ့စည်းပုံ

| ဖိုင် | အသုံး |
|---|---|
| `explanation.md` | သင်ခန်းစာ အပြည့်အစုံ — concept ၁၁ ချက်ရဲ့ ရှင်းလင်းချက် |
| `exercise.md` | လေ့ကျင့်ခန်း ၆ ချက် — threat model မှ audit trail အထိ |
| `solution.md` | လေ့ကျင့်ခန်းအဖြေများ — တိုင်းတာထားသည့် output နှင့်အတူ |
| `cheatsheet.md` | Quick reference — စည်းမျဉ်း ၁၀ ချက်၊ bound ဇယား၊ error code ဇယား |
| `../code/` | Lab ဖိုင် ၁၃ ဖိုင် — `lab_1` မှ `lab_11` အထိ |

## ကိုးကား

- အရင် module — [../M9_clients/README.md](../M9_clients/README.md)
- နောက် module — [../M11_capstone/README.md](../M11_capstone/README.md)
- Test suite — [../../tests/test_m10_security.py](../tests/test_m10_security.py)
