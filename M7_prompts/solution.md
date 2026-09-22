# M7 — Workflow Steering Prompts (`@mcp.prompt`) — Solution

## လေ့ကျင့်ခန်း ၁ — Prompt အခြေခံဖွဲ့စည်းပုံ (LAB 1)


```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("m7_solution")

# A prompt is a template the host offers before the task starts.
@mcp.prompt
def first_prompt(topic: str) -> str:
    """Explain a topic in three sentences."""
    return f"Explain {topic} in exactly three sentences."

# Server declares; the host lists and renders.
prompts = mcp.list_prompts()
print([p.name for p in prompts])

result = mcp.render_prompt("first_prompt", {"topic": "MCP prompts"})
print(result)
```

**အဓိကအယူအဆ** — Server သည် prompt ကို ကြေညာရုံသာ လုပ်ပြီး စာရင်းပြသခြင်းနှင့် render လုပ်ခြင်းကို host က သေချာစွာ ဆက်ဆောင်ပေးရမည်။

## လေ့ကျင့်ခန်း ၂ — Argument များ (LAB 2)


```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("m7_solution_args")

@mcp.prompt
def rca_prompt(service: str, depth: int = 3) -> str:
    """Run a five-step RCA on a failing service."""
    return f"Investigate the failure of {service} in {depth} steps."

# Every function parameter becomes a prompt argument.
prompts = mcp.list_prompts()
for p in prompts:
    print(p.name, p.arguments)

# Required argument missing: the host must report this cleanly.
try:
    mcp.render_prompt("rca_prompt", {})
except Exception as e:
    print("missing-arg error:", e)
```

**အဓိကအယူအဆ** — Function signature သည် prompt ၏ argument contract ဖြစ်ပြီး required argument လျော့လျှင် render ချိန်မှာသာ ပျက်သည်။

## လေ့ကျင့်ခန်း ၃ — Multi-turn Prompt (LAB 3)


```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("m7_solution_highlight")

@mcp.prompt
def highlight_sections_prompt(service: str, section: str) -> str:
    """Read only one section of a log file, then report."""
    return (
        "You are guiding a multi-turn investigation.\n"
        f"Target service: {service}. Target section: {section}.\n"
        "1. Call the highlight tool to read the section.\n"
        "2. Summarize only what the section contains.\n"
        "3. Stop after one section. Do not invent contents you did not read.\n"
        "If the section is empty, say so and stop."
    )

result = mcp.render_prompt(
    "highlight_sections_prompt", {"service": "billing-api", "section": "errors"}
)
print(result)
```

**အဓိကအယူအဆ** — Numbered procedure၊ forced ordering နှင့် stop condition တို့ကို တစ်ပေါင်းတည်းထည့်ခြင်းဖြင့် multi-turn လုပ်ငန်းစဉ်ကို တည်ငြိမ်စွာ ဦးဆောင်နိုင်သည်။

## လေ့ကျင့်ခန်း ၄ — Custom-Type Trap (LAB 4)


```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("m7_solution_trap")

class FancyReport:
    # A custom class registers fine but does not render.
    def __init__(self, text):
        self.text = text

@mcp.prompt
def broken_prompt(service: str) -> FancyReport:
    """This will register but fail at render time."""
    return FancyReport(f"Report for {service}")

# Registry shows the prompt — the trap fires late.
print([p.name for p in mcp.list_prompts()])

try:
    mcp.render_prompt("broken_prompt", {"service": "api"})
except Exception as e:
    print("render error:", e)

# Fix: return plain text or an MCP Message type instead.
@mcp.prompt
def fixed_prompt(service: str) -> str:
    """This renders fine."""
    return f"Report for {service}"
```

**အဓိကအယူအဆ** — Register ဖြစ်သည်မှာ render ဖြစ်သည်မဟုတ်ပါ။ return type သည် string (သို့မဟုတ် `Message`) ဖြစ်ကြောင်း render self-test ဖြင့် အလိုအလျောက် စစ်ဆေးပါ။

## လေ့ကျင့်ခန်း ၅ — RCA Prompt Library (LAB 5)


```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("m7_solution_library")

ANTI_HALLUCINATION = (
    "If you did not read it in a tool result, say you do not know. "
    "Never invent log lines, error codes, or timestamps."
)

STEPS = [
    "1. Read the alert text only.",
    "2. Read the service's error section.",
    "3. Read the service's recent-changes section.",
    "4. Form one hypothesis with evidence.",
    "5. Report findings or say the evidence is insufficient.",
]

@mcp.prompt
def rca_step_prompt(step: int, service: str) -> str:
    """Guide one numbered RCA step with a stop condition."""
    if step < 1 or step > 5:
        return "Invalid step. Stop."
    return f"{STEPS[step - 1]}\nService: {service}.\n{ANTI_HALLUCINATION}"

# Consistency: same clause, same wording, for every step.
for s in range(1, 6):
    print(mcp.render_prompt("rca_step_prompt", {"step": s, "service": "billing"}))
```

**အဓိကအယူအဆ** — Prompt library ၏ တန်ဖိုးအားလုံးသည် consistency မှာဖြစ်ပြီး anti-hallucination clause ကို အဆင့်တိုင်းတွင် စာလုံးတွဲတူညီစွာ ထည့်သွင်းရမည်။

## လေ့ကျင့်ခန်း ၆ — Host Contract (LAB 6)


```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("m7_solution_host")

@mcp.prompt
def deploy_prompt(env: str, region: str = "us-east") -> str:
    """Prepare a deployment checklist for one environment."""
    return f"Deployment checklist for {env} in {region}."

# Host side: read the argument schema before asking the user.
for p in mcp.list_prompts():
    for a in p.arguments:
        print(a.name, "required" if a.required else "optional")

# Host side: render and handle the four must-handle errors.
try:
    result = mcp.render_prompt("deploy_prompt", {"env": "staging"})
    print(result)
except Exception as e:
    print("host-side error handling:", e)
```

**အဓိကအယူအဆ** — Host သည် `prompt.arguments` မှ argument schema ကို ဖတ်ပြီး render ရလဒ်နှင့် error လေးမျိုးကို မဖြစ်မနေ ကိုင်တွယ်ရမည်။
