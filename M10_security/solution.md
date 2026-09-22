# solution.md — M10 Production Security & Hardening (အဖြေများ)

## LAB 1 — threat model ကို code အဖြစ်ရေးပါ

``python
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))
from lab_1_threat_model import model_summary

# Run the threat model: assets, trust boundaries, actors, STRIDE rows.
summary = model_summary()
for section, items in summary.items():
    print(section)
    for item in items:
        print("  -", item)
``

**အဓိကအယူအဆ** — threat model သည် စာရွက်စာတမ်း မဟုတ်ဘဲ run လုပ်ပြီး စစ်နိုင်သော code ဖြစ်သင့်သည်။

## LAB 2 — indirect injection bench တည်ဆောက်ပါ

``python
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))
from lab_2_injection_bench import run_bench

# Each carrier sample is loaded, then checked against the detector.
# The bench shows indirect injection arriving through tool results.
results = run_bench()
for name, caught in results.items():
    print(f"{name}: {'caught' if caught else 'MISSED'}")
``

**အဓိကအယူအဆ** — injection ကို sanitize လုပ်၍ မရဘဲ သဘာဝတရားကိုယ်တိုင်က ကာကွယ်ရမည်။

## LAB 3 — tool-surface manifest နှင့် rug-pull ဖမ်းပါ

``python
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))
from lab_3_tool_manifest import compare_manifests

# Compare the pinned manifest against the current tool surface.
# Any drift (a rug-pull) is reported with the tool name.
drift = compare_manifests()
for tool, change in drift.items():
    print(f"{tool}: {change}")
assert drift, "expected the rug-pull to be detected"
``

**အဓိကအယူအဆ** — tool description သည် model အလိုက် ပြောင်းလဲနိုင်သော code ဖြစ်၍ manifest ဖြင့် တိုင်းတာရမည်။

## LAB 4 — capability budget တိုင်းပါ

``python
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))
from lab_4_capability_inventory import inventory

# List each tool with its declared scope: paths, commands, network.
report = inventory()
for tool, scopes in report.items():
    print(tool, sorted(scopes))
``

**အဓိကအယူအဆ** — least privilege ကို host level တစ်ခုတည်းဖြင့် မဟုတ်ဘဲ tool တစ်ခုချင်းစီရဲ့ scope အဖြစ် တိုင်းတာရမည်။

## LAB 5 — unbounded tool ပြန်လုပ်ပြပါ

``python
import subprocess

# THE ANTI-PATTERN — never ship this. Five structural problems:
# whole shell language, no allowlist, no path confinement,
# no timeout, unbounded return.
result = subprocess.run(
    "cat /var/log/system.log", shell=True, capture_output=True, text=True
)
print(len(result.stdout), "bytes returned — no bound")
``

**အဓိကအယူအဆ** — `shell=True` ဖြင့် command တစ်ခုလုံးကို ဖွင့်ပေးလိုက်ခြင်းသည် ဖြေရှင်းနိုင်စွမ်းမရှိသော ကွက်လပ်ဖြစ်သည်။

## LAB 6 — confinement harness တည်ဆောက်ပါ

``python
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))
from lab_6_confinement import probe
from path_validation import _resolve_within, LOG_ROOT

# Raw string checks can be fooled by ../ traversal and symlinks;
# resolve() first, then compare against LOG_ROOT.
probe()
print(_resolve_within(LOG_ROOT / ".." / "etc" / "passwd"))  # refused
``

**အဓိကအယူအဆ** — စစ်ဆေးခြင်းမတိုင်မခင် `Path.resolve()` ဖြင့် အစစ်အမှန်လမ်းကြောင်းကို ရယူပြီးမှ allowlist root နှင့် နိုင်းယှဉ်ရမည်။

## LAB 7 — bound သုံးခုကို တိုင်းပါ

``python
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))
from lab_7_output_bounds import measure_bounds

# Three honest limits: no shell, hard output cap, declared timeout.
limits = measure_bounds()
print("shell used:", limits["shell"])
print("max bytes:", limits["max_bytes"])
print("timeout seconds:", limits["timeout"])
``

**အဓိကအယူအဆ** — output bounding သည် တိုင်းတာထားသော ကန့်သတ်ချက်များဖြင့် ဖွဲ့စည်းရမည်၊ မမှန်းဆဘဲ ကြေညာရမည်။

## LAB 8 — refusal contract ကို သက်သေပြပါ

``python
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))
from lab_8_refusal_contract import check_contract

# Every refusal must be {ok: False, error: <closed set>, hint: ...}.
result = check_contract()
assert result["ok"], result
print("contract holds:", result["checked_tools"], "tools")
``

**အဓိကအယူအဆ** — refusal ဆိုတာ closed error set ဖြင့် ဖွဲ့စည်းထားသော data ဖြစ်ပြီး ကြုံလာ့ရှင်းမဟုတ်ပါ။

## LAB 9 — attack matrix လည်ပတ်ပြီး ချဲ့ထွင်ပါ

``python
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))
from lab_9_attack_matrix import run_matrix

# Seven attacks, each with the exact control that stops it.
for attack, outcome in run_matrix().items():
    print(f"{attack}: {outcome}")
``

**အဓိကအယူအဆ** — attack matrix ရဲ့ တန်ဖိုးက တိုက်ခိုက်မှုတစ်ခုစီကို ဘယ် control က ရပ်တန့်သည်ဆိုာ်ကို တိကျစွာ ဖော်ပြနိုင်ခြင်းဖြစ်သည်။

## LAB 10 — Docker မပါဘဲ image recipe စစ်ပါ

``python
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))
from lab_10_container_smoke import check_recipe

# Verify the four Dockerfile decisions from the recipe text:
# base image pin, non-root user, read-only layers, dropped capabilities.
for decision, ok in check_recipe().items():
    print(f"{decision}: {'PASS' if ok else 'FAIL'}")
``

**အဓိကအယူအဆ** — container သည် kernel ၏ ဒုတိယနယ်နိမိတ်ဖြစ်သော်လည်း Dockerfile တစ်ခုတည်းဖြင့် ပရိုဆက် အဆင့်ရဲ့ privilege များကို မဖျောက်နိုင်ပါ။

## LAB 11 — incident ပြဿနာများကို ဖြေနိုင်သော audit trail တည်ဆောက်ပါ

``python
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))
from lab_11_audit_log import build_trail

# JSON Lines, one event per line; secrets are redacted before writing.
trail = build_trail()
for event in trail:
    print(event)  # who called which tool, when, with what outcome
``

**အဓိကအယူအဆ** — audit log သည် incident ကို ဖြေရမည်ဖြစ်ပြီး ကိုယ်တိုင်က လျှို့ဝှက်ချက်များ မယိုစေရ။
