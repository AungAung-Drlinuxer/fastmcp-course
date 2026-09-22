# M6 — Solution (`@mcp.resource`) — အဖြေများ

## Exercise 1 — Static text resource ကို ဖန်တီးပါ

`.txt` endpoint တစ်ခုကို `@mcp.resource` ဖြင့် တည်ဆောက်ပြီး return type မှ `text/plain` shape ရရှိသည်ကို ပြသည်။

``python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("m6-solution")

@mcp.resource("config://summary.txt")
def summary() -> str:
    # A str return becomes text/plain content for the client.
    return "M6 solution server: static text resource."

if __name__ == "__main__":
    mcp.run()
``

**အဓိကအယူအဆ** — Static resource ဆိုသည်မှာ URI တစ်ခုတည်းနှင့် တန်ဖိုးတစ်ခုကို တိုက်ရိုက် ပြန်ပေးသည့် endpoint ဖြစ်သည်။

## Exercise 2 — URI template `runbook://{service}` ကို ရေးပါ

Template variable သည် function parameter အဖြစ် ပြောင်းလာပုံကို အသုံးချသည်။

``python
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("m6-solution")
RUNBOOKS = Path(__file__).with_name("runbooks")

@mcp.resource("runbook://{service}")
def runbook(service: str) -> str:
    # The template variable arrives as a function parameter.
    path = RUNBOOKS / f"{service}.md"
    if not path.is_file():
        available = sorted(p.stem for p in RUNBOOKS.glob("*.md"))
        raise FileNotFoundError(
            f"No runbook for service '{service}'. Available: {available}"
        )
    return path.read_text(encoding="utf-8")

if __name__ == "__main__":
    mcp.run()
``

**အဓိကအယူအဆ** — URI template တစ်ခု၏ variable တစ်ခုစီသည် function parameter တစ်ခုစီ ဖြစ်လာသည်။

## Exercise 3 — Enumeration ထောင်ချောက်ကို ဖြေရှင်းပါ

Template resource များသည် `list_resources` တွင် မပေါ်ပဲ `list_resource_templates` တွင်သာ ပေါ်သည်ကို client က နှစ်ခုလုံးဖြင့် ဖြေရှင်းသည်။

``python
async def enumerate_all(session):
    # Static resources appear in list_resources ...
    resources = await session.list_resources()
    # ... template resources appear in list_resource_templates.
    templates = await session.list_resource_templates()
    print("resources:", [r.uri for r in resources])
    print("templates:", [t.uriTemplate for t in templates])
``

**အဓိကအယူအဆ** — Server တစ်ခုလုံးကို enumerate လုပ်ရာတွင် list နှစ်မျိုးလုံးကို ဖတ်ရမည်၊ တစ်ခုတည်းဖြင့် အပြီးမသတ်နိုင်။

## Exercise 4 — `mime_type` ကို ကြေညာပါ

JSON content အတွက် `application/json` ကို ကြေညာခြင်းဖြင့် client မှ ခွဲခြားနိုင်စေသည်။

``python
import json

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("m6-solution")

@mcp.resource("inventory://hosts.json", mime_type="application/json")
def hosts() -> dict:
    # The declared mime_type must match the returned content.
    return {"web-01": "10.0.0.1", "web-02": "10.0.0.2"}

if __name__ == "__main__":
    mcp.run()
``

**အဓိကအယူအဆ** — `mime_type` သည် ကြေညာချက်သာဖြစ်ပြီး တကယ့် byte များကို ပြောင်းလဲပေးခြင်း မဟုတ်ပါ။

## Exercise 5 — Failing loudly: မရှိသည့် runbook ကို error ထုတ်ပါ

Resource တွင် error channel မရှိသဖြင့် မရှိသည့်အရာများကို အမည်ပြောင်းဖြင့် raise လုပ်သည်။

``python
from pathlib import Path

RUNBOOKS = Path(__file__).with_name("runbooks")

def load_runbook(service: str) -> str:
    path = RUNBOOKS / f"{service}.md"
    if not path.is_file():
        # Name what IS available, not just what is missing.
        available = sorted(p.stem for p in RUNBOOKS.glob("*.md"))
        raise FileNotFoundError(
            f"Unknown service '{service}'. Available runbooks: {available}"
        )
    return path.read_text(encoding="utf-8")

print(load_runbook("web"))
``

**အဓိကအယူအဆ** — Error message ကောင်းတစ်ခုသည် ဘာမရှိသလဲသာမဟုတ်ဘဲ ဘာရှိသလဲကိုပါ အမည်ပြောင်းပေးရသည်။

## Exercise 6 — Path confinement အလွှာ ၂ ခုကို အသုံးချပါ

URI router အလွှာနှင့် `Path.resolve()` containment အလွှာကို တွဲသုံးသည် (M10 တွင် ပြီးမြောက်မည်)။

``python
from pathlib import Path

BASE = Path(__file__).parent.resolve()

def confined_read(service: str) -> str:
    # Layer 1: reject any input that is not a plain service name.
    if not service.replace("-", "").replace("_", "").isalnum():
        raise ValueError(f"Illegal service name: '{service}'")
    # Layer 2: resolve and check containment under BASE.
    path = (BASE / "runbooks" / f"{service}.md").resolve()
    if not path.is_relative_to(BASE):
        raise PermissionError(f"Path escapes the runbook root: {path}")
    return path.read_text(encoding="utf-8")

print(confined_read("web"))
``

**အဓိကအယူအဆ** — Confinement ကို အလွှာ နှစ်ခုဖြင့် တိုင်းတာရမည် — ပထမအလွှာက URI ကို စစ်၍ ဒုတိယအလွှာက resolved path ကို စစ်သည်။

## Exercise 7 — Resource ဟုတ်သည် သို့မဟုတ် Tool ဟုတ်သည်ကို မေးခွန်း ၄ ခုဖြင့် စစ်ပါ

ခွဲခြားရန် စစ်ဆေးမှုကို function တစ်ခုအဖြစ် စုစည်းပြသည်။

``python
def classify(action: bool, cheap: bool, addressing: bool, side_effects: bool) -> str:
    # Q1: does the client address it by name (URI)? -> resource signal
    # Q2: is it read-only with no side effects? -> resource signal
    # Q3: is producing the value cheap? -> resource signal
    # Q4: does the server act, or merely serve data? -> tool signal if "act"
    resource_signals = sum([action is False, cheap, addressing, side_effects is False])
    return "resource" if resource_signals >= 3 else "tool"

print(classify(action=False, cheap=True, addressing=True, side_effects=False))
``

**အဓိကအယူအဆ** — မေးခွန်း ၄ ခုအဖြေအများစုးသည် resource ဖက်သို့ ယိမ်းလျှင် ၎င်းကို `@mcp.resource` ဖြင့် ဖန်တီးရမည်။
