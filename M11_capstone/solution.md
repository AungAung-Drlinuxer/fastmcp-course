# M11 — Capstone: အဖြေများ (solution.md)

## လေ့ကျင့်ခန်း ၁ — Surface probe (LAB 1)
### Surface probe


```python
from devops_assistant import mcp

tools = []
resources = []
prompts = []

for item in mcp.list_tools():
    tools.append(item.name)

for item in mcp.list_resources():
    resources.append(str(item.uri))

for item in mcp.list_prompts():
    prompts.append(item.name)

print("TOOLS:", tools)
print("RESOURCES:", resources)
print("PROMPTS:", prompts)

# Expected surface: system_metrics, list_logs, read_log,
# restart_service, plus the three lab-6 extension tools.
assert "system_metrics" in tools
assert "restart_service" in tools
assert any(u.startswith("config://") for u in resources)
assert "rca_error_log" in prompts
print("LAB 1 OK")
```

**အဓိကအယူအဆ** — Server ကို ယုံကြည်ရန် မတင်မကြသေးခင် သူ့ surface (tool, resource, prompt) အားလုံးကို အရင်ရေတွက်၍ စစ်ဆေးရမည်။

## လေ့ကျင့်ခန်း ၂ — Metrics audit (LAB 2)
### Metrics audit


```python
from devops_assistant import system_metrics

result = system_metrics(host="web-01")

print("declared:", result)

# Honesty rule: values come from the standard library.
# If a metric cannot be measured, it must be null — never a guess.
cpu = result["cpu_percent"]
if cpu is None:
    print("cpu_percent is null — the server says it honestly")
else:
    assert isinstance(cpu, (int, float))
    print("measured cpu:", cpu)

assert "memory_percent" in result
print("LAB 2 OK")
```

**အဓိကအယူအဆ** — Metric tool တစ်ခုသည် တိုင်းလို့ ရသော တန်ဖိုးကိုသာ ပြောရမည်၊ တိုင်းလို့ မရပါက `null` ဟု ရိုးသားစွာ ဖော်ပြရမည်။

## လေ့ကျင့်ခန်း ၃ — Log forensics (LAB 3)
### Log forensics


```python
from devops_assistant import list_logs, read_log

files = list_logs()
print("log files:", files)

report = read_log(path="web-01/app.log", needle="ERROR")

# Bounded output: the tool returns a bounded slice, not the whole file.
assert len(report) > 0

# Find the FIRST anomalous event, not the loudest one.
first_line = report[0]
print("first anomalous event:", first_line)
print("LAB 3 OK")
```

**အဓိကအယူအဆ** — Log စုံစမ်းရာတွင် အသံအကြီးဆုံး event ကို မယူဘဲ ပထမဆုံး ထူးဆန်းသော event ကို ရှာရမည်၊ ထို့ပြင် output ကို ကန့်သတ်ထားရမည်။

## လေ့ကျင့်ခန်း ၄ — Confirm guard (LAB 4)
### Confirm guard


```python
from devops_assistant import restart_service

# Path 1: harmless service — allowed without elicitation.
r1 = restart_service(host="web-01", service="nginx")
print("harmless:", r1)

# Path 2: protected service — the guard must state what it did NOT do.
r2 = restart_service(host="db-01", service="postgres", mode="legacy")
print("protected:", r2)
assert "did not" in r2 or "NOT" in r2.upper()
print("LAB 4 OK")
```

**အဓိကအယူအဆ** — Protected service ကို ပြန်စတင်ရန် elicitation လမ်းကို သုံးရမည်၊ လုပ်ဆောင်ချက်ကို မလုပ်ခဲ့ပါက မလုပ်ခဲ့ကြောင်း ရလဒ်ထဲ ထင်ရှားစွာ ဖော်ပြရမည်။

## လေ့ကျင့်ခန်း ၅ — Autonomous client (LAB 5)
### Autonomous client


```python
from lab_5_autonomous_client import run_agent

# Part A: a scripted agent drives tools, resources and prompts
# in a fixed order, verifying each step before the next.
result = run_agent()

print("steps completed:", result["steps"])
assert result["status"] == "ok"

# A good autonomous client logs every call and never
# skips verification between steps.
for entry in result["log"]:
    print(entry)
print("LAB 5 OK")
```

**အဓိကအယူအဆ** — Autonomous client ဆိုသည်မှာ ချိန်းကြပ်မထားသော လမ်းညွှန်ချက်အလိုက် တစ်ဆင့်ချင်း စစ်ဆောင်းပြီးမှ ဆက်သွားသော scripted agent ဖြစ်သည်၊ anti-pattern ၆ မျိုးကို ရှောင်ရမည်။

## လေ့ကျင့်ခန်း ၆ — ကိုယ်ပိုင် extension (LAB 6 / LAB 7 / LAB 8)
### Estate memory tool


```python
from lab_6_estate_memory_tool import note_get, note_set, notes_list

# Store a fact about the estate, then read it back.
note_set(key="incident-2024-06-01", value="web-01 disk near limit")

value = note_get(key="incident-2024-06-01")
assert value == "web-01 disk near limit"

keys = notes_list()
assert "incident-2024-06-01" in keys
print("keys:", keys)
print("LAB 6 OK")
```

**အဓိကအယူအဆ** — Extension tool တိုင်းသည် ရိုးရိုးရှင်းရှင်း set/get/list စာချုပ်ဖြင့် အဖြေပေးရမည်၊ ချဲ့ထွင်မှုတိုင်းအတွက် စစ်ဆေးမှု ၅ ခုကို ဖြေရမည်။

### Estate resource guard


```python
from lab_7_estate_resource_guard import read_resource

# Reading a normal resource works.
r1 = read_resource(uri="runbook://deploy")
print("runbook:", r1)

# Reading outside the allowlist roots must fail loudly.
try:
    read_resource(uri="config://../etc/passwd")
    raise AssertionError("guard did not fire")
except ValueError as exc:
    print("guard blocked:", exc)

print("LAB 7 OK")
```

**အဓိကအယူအဆ** — Resource အသစ်တွင် allowlist root ပြင်ပကို ဖတ်လို့ မရစေရန် guard ထည့်ရမည်၊ ချိုးဖောက်မှုကို တိတ်တဆိတ် မထောက်ပါးဘဲ loud failure ဖြစ်ရမည်။

### Incident review prompt


```python
from lab_8_incident_review_prompt import incident_review
from devops_assistant import mcp

prompt = mcp.get_prompt("incident_review", arguments={"host": "web-01"})
print("prompt name:", prompt.name)
print("message count:", len(prompt.messages))

# The rendered text must contain the resolved host,
# not a literal {host} — the classic bug from tutorial 10.
body = prompt.messages[0].content.text
assert "web-01" in body
assert "{host}" not in body
print("LAB 8 OK")
```

**အဓိကအယူအဆ** — Prompt တစ်ခုကို ရေးပြီးတိုင်း ပုံစံပေါ်လာသော output ထဲတွင် argument တွေ တကယ်ပေါင်းစည်းသွားခဲ့ကြောင်း၊ `{host}` ကဲ့သို့ စာလုံး မကျန်ကြောင်း၊ စမ်းသပ်ရမည်။

---

## ကိုးကား


- `../code/devops_assistant.py` — Capstone server အဓိကဖိုင်
- `../code/my_self_test.py` — တစ် command ဖြင့် server အားလုံးကို စစ်ဆေးသည့် self-test
- `../../tests/test_m11_capstone.py`, `../../tests/test_m11_lab6_extension.py` — အသုံးပြုသင့်သော test များ

