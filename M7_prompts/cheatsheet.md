# Cheatsheet — Lesson 2.4 (Prompts), FastMCP 4.0.5

## ဒီဖိုင်မှာ ဘာသင်မလဲ

- Lesson တစ်ခုလုံး၏ **ကျုံ့ထားသည့်ရည်ညွှန်း** — လိုသည့်အခါ ပြန်ကြည့်ရန်
- Decorator, argument, return type, host API, error — အားလုံး တစ်နေရာတည်း
- Copy-paste လုပ်နိုင်သည့် snippets
- ဘယ်အခါ ဘာသုံးမလဲ ဆိုသည့် ဆုံးဖြတ်ချက်ဇယား

---

## အပိုင်း ၁ — သုံးမျိုးကို တစ်ချက်တည်း

| Kind | Decorator | Who chooses | When | Returns |
|---|---|---|---|---|
| tool | `@mcp.tool` | the **model** | mid-task | a result (data / side effect) |
| resource | `@mcp.resource("uri://{x}")` | the **client** | by reference | content |
| prompt | `@mcp.prompt` | the **user** | before the task | instructions |

``text
💡 prompt ဟုတ်/မဟုတ် စစ်သည့်မေးခွန်း:
   "ဒါက user က task မစခင် ရွေးရမည့်အရာလား?"
   → ဟုတ် ဆိုလျှင် prompt
``

---

## အပိုင်း ၂ — Decorator နှစ်မျိုး

``python
# 1. Bare: the function name becomes the prompt name.
@mcp.prompt
def rca_over_logs(service: str, window_minutes: int = 15) -> str:
    """Produce a root-cause analysis outline over a service's recent logs.

    Args:
        service: The service to analyse.
        window_minutes: How far back to look.
    """
    return f"RCA for {service} over {window_minutes} minutes."


# 2. Named: the wire name is set explicitly.
@mcp.prompt("rca")
def build_rca(service: str) -> str:
    """Short menu name, stable wire name."""
    return f"RCA for {service}."
``

``text
✓ bare  = function အမည် = wire အမည် → အမည်ပြောင်းလျှင် host ကျိုးသည်
✓ named = wire အမည် သီးသန့် → Python အမည် လွတ်လပ်စွာ ပြောင်းနိုင်သည်
✓ အမည်များ: snake_case၊ verb_noun_over_subject၊ collision မရှိရ
``

---

## အပိုင်း ၃ — Return type

``python
# ✅ ALL VALID
return "one string"                              # single message, role=user
return ["step one", "step two"]                  # list[str] → one message per item
return [Message("turn 1"), Message("turn 2")]    # explicit roles
return [Message(step) for step in dataclasses]   # ✅ custom type WRAPPED
return [Message("ok", role="assistant")]         # pre-filled conversation

# ❌ INVALID
return [GuidedStep("a", "b")]     # MCPError: messages[0] must be Message or str, got GuidedStep
return None                       # MCPError: Prompt must return str, list[Message], or
                                  #           PromptResult, got NoneType
``

``python
from fastmcp.prompts import Message     # ⭐ ONLY this import
Message("text")                          # role defaults to "user"
Message("text", role="assistant")
``

``text
⚠️ list → list[Message] ပြောင်းခြင်းသည် trap ကို မဖြေပါ
   annotation သည် runtime တွင် မစစ်ခံရပါ — Message(...) သာ အလုပ်လုပ်သည်
``

---

## အပိုင်း ၄ — Argument စာချုပ်

``python
@mcp.prompt
def triage_alert(
    alert_name: str,               # required string
    service: str,                  # required string
    window_minutes: int = 30,      # optional, default 30
    include_dashboards: bool = False,   # optional boolean
) -> str:
    """Triage one alert with a fixed evidence order.

    Args:
        alert_name: The alert that fired.
        service: The service the alert belongs to.
        window_minutes: How far back the reviewer should look.
        include_dashboards: Whether to ask for dashboard links in the answer.
    """
    ...
``

| Python | Host form |
|---|---|
| `name: str` | required string |
| `n: int = 3` | optional integer, `default: 3` |
| `flag: bool = False` | optional boolean |
| `sev: Literal["sev1","sev2"]` | string + `enum` |
| `items: list[str] = []` | optional array of string |
| `w: Model = Model()` | optional object (Pydantic schema) |
| `x: Annotated[str, Field(description="...")]` | string + description |

``text
✓ docstring ပထမလိုင်း = prompt.description
✓ docstring Args: = argument description (client ဆီ တကယ်ရောက်သည်)
✓ docstring မရေးလျှင် description = None
✓ default ရှိ/မရှိ = required False/True
``

---

## အပိုင်း ၅ — Host API

``python
async with Client(mcp) as client:
    # 1. the menu
    for prompt in await client.list_prompts():
        print(prompt.name, prompt.description)
        for argument in prompt.arguments or []:
            print(argument.name, argument.required, argument.description)

    # 2. the pick
    rendered = await client.get_prompt("rca_over_logs", {"service": "postgres-ha"})
    for message in rendered.messages:
        print(message.role, message.content.text)
``

``text
prompt.arguments        → list | None   ⚠️ .arguments or []
argument.name           → wire name
argument.required       → bool
argument.title          → str | None
argument.description    → str | None (docstring + JSON schema hint)

rendered.messages             → list
rendered.messages[i].role     → 'user' / 'assistant'
rendered.messages[i].content.text   → the text
``

``text
⚠️ messages[0] သာ ဖတ်လျှင် အဆင့်များ ပျောက်သည် — message အားလုံး loop ပါ
``

---

## အပိုင်း ၆ — Error များ (တိုင်းတာပြီး)

``text
MCPError: Unknown prompt: 'nope'
MCPError: Error rendering prompt 'rca': Missing required arguments: {'service'}
MCPError: Could not convert argument 'services' with value 'a,b' to expected type list[str].
          Error: 1 validation error for list[str] Invalid JSON: expected value at line 1 column 1
MCPError: Could not convert argument 'severity' with value 'sev9' to expected type
          typing.Literal['sev1', 'sev2', 'sev3']
MCPError: Error rendering prompt 'bare_steps': messages[0] must be Message or str, got
          GuidedStep. Use Message(GuidedStep(...)) to wrap the value.
MCPError: Error rendering prompt 'returns_none': Prompt must return str, list[Message], or
          PromptResult, got NoneType
``

| Symptom | Fix |
|---|---|
| `Unknown prompt` | `list_prompts()` မှ အမည်ယူပါ |
| `Missing required arguments: {'x'}` | form ကို `prompt.arguments` မှ ဆောက်ပါ (အမည်မှားလျှင်လည်း ဒီ error) |
| `Could not convert argument` | `json.dumps(...)` ဖြင့် ပို့ပါ |
| `messages[i] must be Message or str` | `Message(value)` ဖြင့် ပတ်ပါ |
| `Prompt must return ...` | `return` ထည့်ပါ |
| `desc=None` | docstring ထည့်ပါ |
| Extra argument မှား (error မတက်) | host ဘက်တွင် argument စစ်ပါ |

---

## အပိုင်း ၇ — Prompt တစ်ခုရဲ့ ပုံစံ (house style)

``text
1. Role / subject line        → "You are performing a root cause analysis for `X`..."
2. Scope                      → "over the last N minutes"
3. Forcing                    → "Work in this order and do not skip a step:"
4. Numbered steps             → 1..5၊ တစ်ဆင့်စီတွင် ကာကွယ်သည့်အမှားရှိသည်
5. Output shape               → "give: title, a two-sentence summary, one line saying WHY"
6. Stop condition             → "If rejected, stop and say so"
7. Guard / refusal            → "If the evidence does not support a conclusion, answer
                                 'insufficient evidence' and list what you would need.
                                 Do not speculate."
``

``python
NO_SPECULATION = (
    "If the evidence does not support a conclusion, answer 'insufficient evidence' and list "
    "what you would need. Do not speculate."
)
``

---

## အပိုင်း ၈ — Code snippets (copy-paste)

### ရိုးရှင်းဆုံး prompt

``python
from fastmcp import FastMCP

mcp = FastMCP("my-server")


@mcp.prompt
def explain_failure(symptom: str) -> str:
    """Explain a failure at a chosen depth.

    Args:
        symptom: The symptom the user reported.
    """
    return (
        f"Explain the failure {symptom!r} as:\n"
        "1. The cause, if known.\n"
        "2. The two checks that would confirm it.\n"
        "3. The check to run first, and why.\n"
        "If no cause is supported, say 'insufficient evidence' and list what is missing."
    )
``

### Structured steps

``python
from dataclasses import dataclass

from fastmcp.prompts import Message


@dataclass
class GuidedStep:
    """One step of a guided procedure."""

    title: str
    instruction: str


@mcp.prompt
def dns_lookup_failure(hostname: str, symptom: str = "name or service not known") -> list[Message]:
    """Walk through a DNS resolution failure, in order, without guessing.

    Args:
        hostname: The name that failed to resolve.
        symptom: The exact error text the user saw.
    """
    steps = [
        GuidedStep("Confirm the failure", f"Reproduce the lookup for {hostname}: {symptom!r}."),
        GuidedStep("Check the record", f"Query the authoritative server for {hostname}."),
        GuidedStep("Report", "Name the faulty layer, or say it is still unknown."),
    ]
    return [Message(step) for step in steps]
``

### Host contract

``python
async with Client(mcp) as client:
    form = [
        (a.name, a.required, (a.description or "").split("\n\n")[0])
        for p in await client.list_prompts()
        for a in (p.arguments or [])
    ]
    rendered = await client.get_prompt("dns_lookup_failure", {"hostname": "git.drlinuxer.com"})
    print("\n".join(m.content.text for m in rendered.messages))
``

### Render self-test (CI gate)

``python
failures = []
async with Client(mcp) as client:
    for prompt in await client.list_prompts():
        try:
            await client.get_prompt(prompt.name, SAMPLE_ARGUMENTS.get(prompt.name, {}))
        except Exception as exc:
            failures.append((prompt.name, str(exc)))
assert not failures, f"prompts that do not render: {failures}"
``

---

## အပိုင်း ၉ — Run commands

``bash
cd D:/fastmcp-course

uv run python -m M7_prompts.code.highlight                        # the lesson file
uv run python -m M7_prompts.code.lab_1_prompt_anatomy
uv run python -m M7_prompts.code.lab_2_prompt_arguments
uv run python -m M7_prompts.code.lab_3_highlight_sections_prompt
uv run python -m M7_prompts.code.lab_4_custom_type_trap
uv run python -m M7_prompts.code.lab_5_rca_prompt_library
uv run python -m M7_prompts.code.lab_6_host_contract
uv run python -m M7_prompts.code.extra_consistency_check
uv run python -m M7_prompts.code.extra_argument_tests
uv run python -m M7_prompts.code.extra_multiturn_prompt
uv run python -m M7_prompts.code.extra_render_selftest
uv run python -m M7_prompts.code.mini_exercise_trap
``

``text
uv run  → activate မလိုပါ
python -m M7_prompts.code.X   → working directory သည် D:/fastmcp-course ဖြစ်ရမည်
``

---

## အပိုင်း ၁၀ — ကျက်ထားရမည့် ငါးချက်

``text
1. Prompt သည် template — tool လည်းမဟုတ်၊ data လည်းမဟုတ်
2. ရွေးသူက model / client / user — အချိန်က mid-task / by reference / before
3. Signature သည် argument စာချုပ် — host form သည် အလိုအလျောက်
4. Custom type ကို Message(...) ဖြင့် ပတ်ရမည် — registration အောင်မြင်ခြင်းသည်
   render ရနိုင်ခြင်း မဟုတ်
5. messages[i].content.text — message အားလုံး ဖတ်ပါ
``

---

## အပိုင်း ၁၁ — File မြေပုံ

``text
D:/fastmcp-course/M7_prompts/
├── code/
│   ├── highlight.py                          ← lesson ရဲ့ မူရင်းဖိုင်
│   ├── lab_1_prompt_anatomy.py
│   ├── lab_2_prompt_arguments.py
│   ├── lab_3_highlight_sections_prompt.py
│   ├── lab_4_custom_type_trap.py
│   ├── lab_5_rca_prompt_library.py
│   ├── lab_6_host_contract.py
│   ├── extra_consistency_check.py
│   ├── extra_argument_tests.py
│   ├── extra_multiturn_prompt.py
│   ├── extra_render_selftest.py
│   └── mini_exercise_trap.py
└── tutorial/
    ├── 01-what-a-prompt-is.md
    ├── 02-tool-vs-resource-vs-prompt.md
    ├── 03-why-consistency-is-the-value.md
    ├── 04-declaring-prompts-decorator-and-signature.md
    ├── 05-argument-injection-in-depth.md
    ├── 06-multi-turn-guidance-format.md
    ├── 07-the-anti-hallucination-clause.md
    ├── 08-the-measured-trap-custom-return-types.md
    ├── 09-the-host-contract-list-and-render.md
    ├── 10-labs.md
    ├── 11-error-catalogue-and-troubleshooting.md
    ├── 12-cheatsheet.md          ← ဒီဖိုင်
    └── 13-labs-answers.md
``

---

## နိဒါန်း

- သုံးမျိုးကို ရွေးသူဖြင့် ခွဲပါ
- Return type လေးမျိုး ရသည်၊ custom type ကို `Message` ပတ်ရမည်
- Signature → argument စာချုပ်၊ docstring → description
- Host API နှစ်ခု — `list_prompts()`၊ `get_prompt(name, args)`
- Error ခြောက်မျိုး၊ ဖြေရှင်းနည်း ခြောက်ခု
- ပုံစံခုနစ်ဆင့် — role, scope, forcing, steps, shape, stop, guard

## ကိုးကား

- `M7_prompts/code/highlight.py`
- `M7_prompts/code/extra_render_selftest.py`
- `VERIFIED.md`
- `TUTORIAL_SPEC.md`