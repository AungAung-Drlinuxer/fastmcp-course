# M6 — Solution (`@mcp.resource`) — အဖြေများ

## လေ့ကျင့်ခန်း ၁ — Static text resource ရေးခြင်း


`.txt` endpoint တစ်ခုကို `@mcp.resource` ဖြင့် တည်ဆောက်ပြီး return type မှ `text/plain` shape ရရှိသည်ကို ပြသည်။

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("m6-solution")

@mcp.resource("config://summary.txt")
def summary() -> str:
    # A str return becomes text/plain content for the client.
    return "M6 solution server: static text resource."

if __name__ == "__main__":
    mcp.run()
```

**အဓိကအယူအဆ** — Static resource ဆိုသည်မှာ URI တစ်ခုတည်းနှင့် တန်ဖိုးတစ်ခုကို တိုက်ရိုက် ပြန်ပေးသည့် endpoint ဖြစ်သည်။

## လေ့ကျင့်ခန်း ၂ — Static JSON resource နှင့် mime_type


JSON content အတွက် `application/json` ကို ကြေညာခြင်းဖြင့် client မှ ခွဲခြားနိုင်စေသည်။

```python
import json

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("m6-solution")

@mcp.resource("inventory://hosts.json", mime_type="application/json")
def hosts() -> dict:
    # The declared mime_type must match the returned content.
    return {"web-01": "10.0.0.1", "web-02": "10.0.0.2"}

if __name__ == "__main__":
    mcp.run()
```

**အဓိကအယူအဆ** — `mime_type` သည် ကြေညာချက်သာဖြစ်ပြီး တကယ့် byte များကို ပြောင်းလဲပေးခြင်း မဟုတ်ပါ။

## လေ့ကျင့်ခန်း ၃ — URI template ရေးခြင်း


Template variable သည် function parameter အဖြစ် ပြောင်းလာပုံကို အသုံးချသည်။

```python
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
```

**အဓိကအယူအဆ** — URI template တစ်ခု၏ variable တစ်ခုစီသည် function parameter တစ်ခုစီ ဖြစ်လာသည်။

## လေ့ကျင့်ခန်း ၄ — Enumeration ထောင်ချောက် လေ့လာခြင်း


Template resource များသည် `list_resources` တွင် မပေါ်ပဲ `list_resource_templates` တွင်သာ ပေါ်သည်ကို client က နှစ်ခုလုံးဖြင့် ဖြေရှင်းသည်။

```python
async def enumerate_all(session):
    # Static resources appear in list_resources ...
    resources = await session.list_resources()
    # ... template resources appear in list_resource_templates.
    templates = await session.list_resource_templates()
    print("resources:", [r.uri for r in resources])
    print("templates:", [t.uriTemplate for t in templates])
```

**အဓိကအယူအဆ** — Server တစ်ခုလုံးကို enumerate လုပ်ရာတွင် list နှစ်မျိုးလုံးကို ဖတ်ရမည်၊ တစ်ခုတည်းဖြင့် အပြီးမသတ်နိုင်။


## လေ့ကျင့်ခန်း ၅ — Generic reader loop ရေးခြင်း

Generic reader တစ်ခုသည် **ဖော်ပြချက် (enumeration) နှင့် ဖတ်ခြင်း (read) ကို သီးသန့် အဆင့်နှစ်ခုအဖြစ်** ဆက်တိုက်
လုပ်သည် — အရင် `list_resources()` ဖြင့် URI စာရင်း ရယူပြီး၊ ထို့နောက် URI တစ်ခုချင်းကို `read_resource()` ဖြင့် ဖတ်သည်။
Item နှစ်မျိုး ပြန်လာနိုင်သည် — `TextResourceContents` (`.text`) နှင့် `BlobResourceContents` (`.blob`) — ဒါကြောင့်
ကုဒ်သည် `hasattr` ဖြင့် ပုံစံကို ခွဲပြီး ဖတ်ရသည်။

```python
def describe_item(item: object) -> str:
    """Return a one-line summary of whatever shape the server sent back."""
    mime = getattr(item, "mime_type", "?")
    if hasattr(item, "text"):
        text = str(getattr(item, "text"))
        return f"{{type(item).__name__}} mime={{mime}} chars={{len(text)}}"
    blob = str(getattr(item, "blob", ""))
    return f"{{type(item).__name__}} mime={{mime}} bytes={{len(blob)}}"


async def main() -> None:
    async with Client(mcp) as client:
        for resource in await client.list_resources():
            print(f"  {{str(resource.uri):20}} {{resource.mime_type}}")
            result = await client.read_resource(str(resource.uri))
            print(f"    -> {{describe_item(result[0])}}")

        for template in await client.list_resource_templates():
            uri = template.uri_template.replace("{{service}}", "postgres")
            result = await client.read_resource(uri)
            print(f"  {{uri}} -> {{describe_item(result[0])}}")

        for uri in ("runbook://postgres", "runbook://oracle"):
            try:
                result = await client.read_resource(uri)
                print(f"  {{uri:24}} -> ok, {{len(result[0].text)}} chars")
            except MCPError as exc:
                print(f"  {{uri:24}} -> MCPError: {{exc}}")
```

`read_resource()` သည် **list** တစ်ခု ပြန်သည် (`result[0]`) — URI တစ်ခုတည်းအတွက် item တစ်ခုသာ ပါသည်။
မရှိသည့် runbook ကို ဖတ်လျှင် traceback မထွက်ဘဲ `MCPError` အဖြစ် ရောက်လာသည် — error ကို data အဖြစ်
ကိုင်တွယ်လို့ရသည်။

**မျှော်မှန်ရလဒ်** (`uv run python -m M6_resources.code.lab_5_reader_loop`)

```text
=== 1. static resources ===
  inventory://hosts    application/json
    -> TextResourceContents mime=application/json chars=35
  logo://site          image/png
    -> BlobResourceContents mime=image/png bytes=24

=== 2. templates, materialised by hand ===
  runbook://postgres -> TextResourceContents mime=text/markdown chars=51

=== 4. a resource that fails, handled as data ===
  runbook://postgres       -> ok, 51 chars
  runbook://oracle         -> MCPError: Error reading resource 'runbook://oracle': no runbook for 'oracle'; available: kasm, nginx, postgres
```

**အဓိကအယူအဆ** — Generic reader ရဲ့ အခက်အခဲက loop မဟုတ်၊ **item ပုံစံ နှစ်မျိုးနှင့် error ပြန်လာပုံ** ကို
ကိုင်တွယ်ရခြင်း ဖြစ်သည် — `.text`/`.blob` ကို ခွဲဖတ်ပြီး၊ error ကို exception အဖြစ် ဖမ်းမှသာ client သည်
resource တစ်ခု ပျက်လျှင်လည်း ကျန်တာ ဆက်ဖတ်နိုင်သည်။

## လေ့ကျင့်ခန်း ၆ — Path confinement စမ်းသပ်ခြင်း


URI router အလွှာနှင့် `Path.resolve()` containment အလွှာကို တွဲသုံးသည် (M10 တွင် ပြီးမြောက်မည်)။

```python
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
```

**အဓိကအယူအဆ** — Confinement ကို အလွှာ နှစ်ခုဖြင့် တိုင်းတာရမည် — ပထမအလွှာက URI ကို စစ်၍ ဒုတိယအလွှာက resolved path ကို စစ်သည်။

## အပိုဆောင်း — မရှိသည့် runbook ကို error ဖြင့် ပြောခြင်း


Resource တွင် error channel မရှိသဖြင့် မရှိသည့်အရာများကို အမည်ပြောင်းဖြင့် raise လုပ်သည်။

```python
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
```

**အဓိကအယူအဆ** — Error message ကောင်းတစ်ခုသည် ဘာမရှိသလဲသာမဟုတ်ဘဲ ဘာရှိသလဲကိုပါ အမည်ပြောင်းပေးရသည်။

## အပိုဆောင်း — Resource နှင့် Tool ကို ခွဲခြားခြင်း


ခွဲခြားရန် စစ်ဆေးမှုကို function တစ်ခုအဖြစ် စုစည်းပြသည်။

```python
def classify(action: bool, cheap: bool, addressing: bool, side_effects: bool) -> str:
    # Q1: does the client address it by name (URI)? -> resource signal
    # Q2: is it read-only with no side effects? -> resource signal
    # Q3: is producing the value cheap? -> resource signal
    # Q4: does the server act, or merely serve data? -> tool signal if "act"
    resource_signals = sum([action is False, cheap, addressing, side_effects is False])
    return "resource" if resource_signals >= 3 else "tool"

print(classify(action=False, cheap=True, addressing=True, side_effects=False))
```

**အဓိကအယူအဆ** — မေးခွန်း ၄ ခုအဖြေအများစုသည် resource ဖက်သို့ ယိမ်းလျှင် ၎င်းကို `@mcp.resource` ဖြင့် ဖန်တီးရမည်။
