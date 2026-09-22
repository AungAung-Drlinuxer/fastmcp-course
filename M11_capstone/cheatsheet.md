# Cheatsheet — M11 Capstone

⭐ ဒီဖိုင်သည် ကိုးကားရန် ဖြစ်သည်။ သင်ခန်းစာ မဟုတ်ပါ — ကျက်ရန် မလိုပါ။
Run လုပ်နေစဉ် ဖွင့်ထားပြီး ရှာပါ။

---

## 1. Server ဖိုင်၏ skeleton

```python
"""One paragraph: what this server is, and how to run it.

Run:
    uv run python -m M11_capstone.code.your_server          # self-test
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("devops-assistant")

# ---- configuration paths --------------------------------------------------
HOME = Path(__file__).parent              # ⭐ never depend on cwd
DATA = HOME / "data"
LOGS, CONF, RUNBOOKS = DATA / "logs", DATA / "conf", DATA / "runbooks"
for directory in (LOGS, CONF, RUNBOOKS):
    directory.mkdir(parents=True, exist_ok=True)     # ⭐ parents=True, exist_ok=True

PROTECTED_SERVICES = {"postgres-ha", "redis-sentinel", "kasm-app"}   # set
MAX_BYTES = 48 * 1024

# ---- shared helpers -------------------------------------------------------
def _resolve(root: Path, name: str) -> Path:
    candidate = (root / name).resolve()               # ⭐ resolve BEFORE the check
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"path escapes {root.name}/: {name!r}")
    return candidate


def _fail(code: str, hint: str, **extra: Any) -> dict:
    return {"ok": False, "error": code, "hint": hint, **extra}

# ---- tools ---------------------------------------------------------------
# ---- resources -----------------------------------------------------------
# ---- prompts -------------------------------------------------------------
# ---- self-test -----------------------------------------------------------
async def main() -> None:
    from fastmcp import Client
    async with Client(mcp) as client:
        ...

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 2. လေးမျိုးသော primitive

| | Tool | Resource | Prompt | Elicitation |
|---|---|---|---|---|
| Decorator | `@mcp.tool` | `@mcp.resource("scheme://{x}")` | `@mcp.prompt` | (tool အတွင်း) |
| ဘယ်သူ ရွေး | model | client | လူ | server က လူကို မေး |
| Return type | `dict` | **`str`** | **`str`** | `T \| dict \| ElicitResult` |
| ကျရှုံးလျှင် | `return _fail(...)` | `raise FileNotFoundError(...)` | — | return value |
| ပြန်ရသည့်နေရာ | `(await client.call_tool(...)).data` | `(await client.read_resource(uri))[0].text` | `(await client.get_prompt(...)).messages[0].content.text` | tool ၏ ရလဒ် |
| စာရင်း | `list_tools()` | `list_resources()` **နှင့်** `list_resource_templates()` | `list_prompts()` | — |

### ဘယ်ဟာ ရွေးရမလဲ

```text
runtime argument လိုလား?             → tool
URI ဖြင့် ရည်ညွှန်းလိုလား?            → resource
လုပ်ငန်းစဉ် လမ်းညွှန်လိုလား?           → prompt
လူသာ ဖြေနိုင်သည့် ဆုံးဖြတ်ချက်လား?    → elicitation
```

---

## 3. နာမည် ဇယား — server ဘက် vs client ဘက်

⭐ **ဒီဇယားသည် အလွန်အဖြစ်များသည့် အမှားများကို ဖြေသည်။**

| ဘာကို ဖတ်မလဲ | Server ဘက် (`await mcp.…`) | Client ဘက် (`await client.…`) |
|---|---|---|
| Tool schema | `.parameters` | `.input_schema` |
| Resource template URI | `.uri_template` | `.uri_template` |
| Resource template mime | `.mime_type` | `.mime_type` |
| Resource စာရင်း | `await mcp.list_resources()` | `await client.list_resources()` |
| Tool စာရင်း | `await mcp.list_tools()` | `await client.list_tools()` |
| Prompt စာရင်း | `await mcp.list_prompts()` | `await client.list_prompts()` |

### 2.x နာမည် → 4.x နာမည်

| 2.x documentation | 4.0.5 | ဟောင်းသည့် နာမည် သုံးလျှင် |
|---|---|---|
| `ElicitationResult` | `AcceptedElicitation` / `DeclinedElicitation` / `CancelledElicitation` | `ImportError: cannot import name 'ElicitationResult'` |
| `tool.inputSchema` | `tool.parameters` | `AttributeError: 'FunctionTool' object has no attribute 'inputSchema'` |
| `template.uriTemplate` | `template.uri_template` | `AttributeError` |
| `await mcp.get_tools()` | `await mcp.list_tools()` | `AttributeError: 'FastMCP' object has no attribute 'get_tools'` |
| `Client("path/to/server.py")` | `Client(Path(...))` | `FastMCPDeprecationWarning` |
| `ResourceTemplate.mimeType` | `.mime_type` | `FastMCPDeprecationWarning` |

---

## 4. Elicitation — လိုအပ်သည့်အရာ အားလုံး

```python
# SERVER — inside the tool
class Confirm(BaseModel):
    """Confirmation before an action that affects live traffic."""

    proceed: bool = Field(description="True to continue, false to stop")
    reason: str = Field(default="", description="Optional note explaining the decision")


@mcp.tool
async def restart_service(service: str, ctx: Context, reason: str = "") -> dict:
    answer = await ctx.elicit(
        message=f"About to restart the PROTECTED service {service!r}. Proceed?",
        response_type=Confirm,
    )
    action = getattr(answer, "action", "accept")     # ⭐ version-agnostic
    if action != "accept":
        return {"ok": False, "status": action,
                "hint": "Nothing was restarted. Do not retry without asking the user."}
    if not answer.data.proceed:
        return {"ok": False, "status": "refused_by_user", "reason": answer.data.reason or "no reason given"}
    return {"ok": True, "status": "confirmed"}
```

```python
# CLIENT — ⭐ mode="legacy" is required, ⭐ four parameters, ⭐ async
from fastmcp.client.elicitation import ElicitResult

async def handler(message: str, response_type: Any, params: Any = None,
                  context: Any = None) -> Any:
    if DECISION == "accept":
        return {"proceed": True, "reason": "approved"}      # accept
    if DECISION == "refuse":
        return {"proceed": False, "reason": "not approved"} # accept + user said no
    if DECISION == "decline":
        return ElicitResult(action="decline")                # do not ask again
    return ElicitResult(action="cancel")                     # the user left


async with Client(mcp, mode="legacy", elicitation_handler=handler) as client:
    print(client.protocol_version)          # "2025-11-25"
```

### အဖြေ ၄ မျိုး

| Client ပြန်သည် | `action` | Server ရသည် |
|---|---|---|
| `{"proceed": True, ...}` | accept | `status: "confirmed"` |
| `{"proceed": False, ...}` | accept | `status: "refused_by_user"` |
| `ElicitResult(action="decline")` | decline | `status: "decline"` |
| `ElicitResult(action="cancel")` | cancel | `status: "cancel"` |

### ဒီဇယားကို မှတ်ထားပါ

| အခြေအနေ | Error |
|---|---|
| `Client(mcp)` (default `auto`) | `ToolError: elicitation via server-initiated requests is unavailable on 2026-07-28 connections.` |
| Handler တွင် parameter ၃ ခု | `MCPError: ... takes from 2 to 3 positional arguments but 4 were given` |
| `def` (sync) handler | `ToolError: ... object dict can't be used in 'await' expression` |
| `return None` | `MCPError: Invalid request parameters` |
| `mode="2025-06-18"` | `ValueError: mode must be 'legacy', 'auto', or one of ['2026-07-28']` |

### ⭐ Handler ထဲတွင် `response_type` သည် ဘာလဲ

```python
response_type.__name__             # 'Confirm'      ← your class name
response_type.__module__           # 'types'        ← ⭐ NOT your module
list(response_type.__dataclass_fields__)   # ['proceed', 'reason']   ✅
response_type.model_fields         # ❌ AttributeError — it is not a pydantic model
type(params).__name__              # 'ElicitRequestFormParams'
```

---

## 5. အမှား → အကြောင်းရင်း → ဖြေရှင်းနည်း

| Error / လက္ခဏာ | အကြောင်းရင်း | ဖြေရှင်းနည်း |
|---|---|---|
| `AttributeError: 'Tool' object has no attribute 'parameters'` | Client ဘက်မှ ဖတ်နေသည် | `.input_schema` |
| `AttributeError: 'FunctionTool' object has no attribute 'input_schema'` | Server ဘက်မှ ဖတ်နေသည် | `.parameters` |
| `AttributeError: 'FastMCP' object has no attribute 'get_tools'` | 2.x API | `await mcp.list_tools()` |
| `KeyError: 'required'` | Argument မရှိသည့် tool | `schema.get("required") or []` |
| `list_resources()` က `[]` | Template-only server | `list_resource_templates()` |
| `MCPError: Resource not found: 'runbook://../etc/passwd'` | Framework routing က ပိတ်သည် | ဒါက မှန်သည်; `_resolve` ကလည်း ပိတ်သည် |
| `MCPError: ... no runbook for 'x'; available: ...` | သင့် `FileNotFoundError` | `available` စာရင်းမှ ရွေးပါ |
| `ToolError: ... 1 validation error for call[read_log] name Missing required argument input_value={}` | LangGraph တွင် `args_schema` မပေး | `args_schema=args_model(...)` |
| `NameError: name 'Annotated' is not defined` | `GraphState` သည် function အတွင်း | Module level တွင် ထားပါ |
| `MCPError: messages[0] must be Message or str, got X` | Custom type ပြန်သည် | `str` သာ ပြန်ပါ / `Message(...)` wrap |
| Prompt ထဲ `{place}` ကျန်သည် | ထိုလိုင်းတွင် f-prefix မပါ | `f"..."` ထည့်ပါ |
| `ModuleNotFoundError: No module named 'M11_capstone'` | cwd မှား | `uv run` ကို repo root မှ run |
| `UnicodeDecodeError` log ဖတ်ရာတွင် | binary ရောသည် | `errors="replace"` |
| `UnicodeEncodeError` ရေးရာတွင် | Windows default `cp1252` | `encoding="utf-8"` |
| Disk တွင် `0%` ပြသည် | `null` ကို 0 လုပ်နေသည် | `if x is not None:` |
| `886` → `8.86` မဟုတ်ပါ | unit ရောသည် | Field နာမည်ထဲ `_gb` ထည့်ပါ |
| `lines: 1000` သို့ `content` ထဲ ၃၂၆ | bound နှစ်ခု တိုက်သည် | `truncated` ကို စစ်ပါ |
| `NotADirectoryError` | `LOGS` မရှိ | `mkdir(parents=True, exist_ok=True)` ကို import အချိန်တွင် |

---

## 6. စစ်ဆေးမှု command များ

```bash
# ⭐ 1. Self-test — no client needed
uv run python -m M11_capstone.code.devops_assistant

# ⭐ 2. the test suite
uv run pytest -q
uv run pytest -q tests/test_m11_capstone.py

# ⭐ 3. Health check — exit code
uv run python -m M11_capstone.code.health_check ; echo "exit code: $?"

# ⭐ 4. inventory the surface
uv run python -m M11_capstone.code.lab_1_surface_probe

# ⭐ 5. autonomy (scripted + LangGraph)
uv run python -m M11_capstone.code.lab_5_autonomous_client
uv run python -m M11_capstone.code.lab_5_autonomous_client --graph

# ⭐ 6. the Inspector (interactive UI)
uv run fastmcp dev inspector M11_capstone/code/devops_assistant.py

# ⭐ 7. component count
uv run fastmcp inspect M11_capstone/code/devops_assistant.py
#   Tools: 5   Prompts: 2   Resources: 0   Templates: 2
```

### `fastmcp inspect` ၏ output (တိုင်းထားသည်)

```text
Server
  Name:         devops-assistant
  Version:      4.0.5
  Generation:   2

Components
  Tools:        5
  Prompts:      2
  Resources:    0
  Templates:    2

Environment
  FastMCP:      4.0.5
  MCP:          2.2.0
```

---

## 7. ကိန်းဂဏန်းများ — capstone ၏ တန်ဖိုးများ

| အမည် | တန်ဖိုး | ဘယ်နေရာ | ဘာကြောင့် |
|---|---|---|---|
| `MAX_BYTES` | `48 * 1024` (49 152) | module level | တစ်ခေါ်တည်း ပြန်သည့် byte |
| `max_lines` clamp | `1..1000` | `read_log` အတွင်း | လိုင်းအရေအတွက် |
| `max_lines` default | `100` | signature | default-safe |
| `MAX_CHARS` (LAB 6) | `8 * 1024` | note tool | သေးငယ်သည့်အရာအတွက် သေးငယ်သည့် bound |
| per-line bound | `line[:300]` | `grep_log` | Stack trace တစ်လိုင်း 1 MB |
| `window_minutes` default | `30` | prompt | လူ၏ သဘာဝ အချိန်အတိုင်းအတာ |
| capacity threshold | `70%` | prompt | တိကျသည့် သတ်မှတ်ချက် → တည်ငြိမ်သည် |
| `PROTECTED_SERVICES` | ၃ ခု | module level | version control ထဲ |

---

## 8. Seed ထားသည့် estate

```text
data/conf/pve01.yaml         host: pve01          role: hypervisor  cpu_cores: 72  memory_gb: 270
data/conf/kasm-agent1.yaml   host: kasm-agent1    role: lab-agent   cpu_cores: 16  memory_gb: 48
data/runbooks/postgres-ha.md ၄ အဆင့် — "2. Check replication lag before anything else."
data/runbooks/kasm-agent.md  ၃ အဆင့် — "1. `docker ps` …"
data/logs/postgres-ha.log    ၈ လိုင်း — WARN lag (02:01:50)၊ ERROR kasm-app x2၊ WARN failover
data/logs/kasm-agent.log     ၃ လိုင်း — INFO၊ WARN pull slow၊ ERROR session start failed
```

⭐ **ပထမဆုံး anomalous event** = `2026-09-19 02:01:50 WARN  replication lag 3.1s on postgres-ha-3`
⭐ **အကျယ်လောင်ဆုံး** = `ERROR could not connect to host kasm-app` (x2)
⭐⭐ **ဤနှစ်ခုသည် မတူပါ** — RCA prompt ၏ အဆင့် ၂ သည် ဒီအတွက် ရှိသည်။

---

## 9. Template များနှင့် URI များ

| URI | အမျိုးအစား | ပြန်သည် |
|---|---|---|
| `config://{host}` | template | YAML စာသား (`application/yaml`) |
| `runbook://{name}` | template | Markdown (`text/markdown`) |
| `estate://{kind}/{name}` | template (LAB 7) | Markdown |
| `allowlist://estate` | **static** resource (LAB 7) | စည်းမျဉ်းများ (`text/plain`) |
| `config://pve01` | instance | ✅ |
| `config://pve01.yaml` | ❌ | `no config for 'pve01.yaml'` — extension ကို မထည့်ပါ |
| `runbook://../etc/passwd` | ❌ | `MCPError: Resource not found` (framework) |
| `runbook://..` | ❌ | `FileNotFoundError: path escapes runbooks/: '..'` (သင့် `_resolve`) |

---

## 10. Prompt များ

| Prompt | Args | ပါသည့် စည်းမျဉ်း |
|---|---|---|
| `rca_error_log` | `log_name`, `window_minutes=30` | Forced order ၆ ဆင့်၊ FIRST not loudest၊ runbook before advising၊ DISPROVE၊ smallest change၊ `insufficient evidence` |
| `capacity_review` | `host` | declared vs measured၊ 70%၊ one action or nothing၊ **number before upgrade** |
| `incident_review` (LAB 8) | `service`, `minutes=60` | အားလုံး + `list_logs` before guessing |

⭐ တိုင်းထားသည့် ကတိ: `assert "insufficient evidence" in text` နှင့် `assert "do not invent" in text.lower()`

---

## 11. Client ၏ တာဝန် ၁၀ ခု

```text
1  list_tools() ဖြင့် ရှာဖွေခြင်း
2  list_resource_templates() ဖြင့် ရှာဖွေခြင်း
3  list_prompts() နှင့် ရွေးချယ်ခြင်း
4  prompt ကို ဖတ်ပြီး အစီအစဉ်ကို လိုက်နာခြင်း
5  read_resource ဖြင့် grounding
6  {"ok": false} ကို fail-fast ဖြင့် ကိုင်တွယ်ခြင်း
7  available စာရင်းမှ ရွေးချယ်ခြင်း
8  elicitation handler ပေးခြင်း
9  ⭐ action_taken ကို လူထံ ပို့ခြင်း
10 ⭐ truncated ကို စစ်ခြင်း
```

---

## 12. Client ကို ဖွဲ့စည်းခြင်း (Cline)

```json
{
  "mcpServers": {
    "devops-assistant": {
      "command": "uv",
      "args": ["run", "--directory", "D:/fastmcp-course",
               "python", "-m", "M11_capstone.code.devops_assistant"],
      "disabled": false,
      "autoApprove": ["list_logs", "list_runbooks", "system_metrics", "read_log"]
    }
  }
}
```

⚠️ Path/key များသည် version အလိုက် ပြောင်းနိုင်သည် — သင့် Cline documentation ကို အတည်ပြုပါ။
⭐ `--directory` မဖြစ်မနေ။ ⭐ `autoApprove` တွင် read-only tool များသာ — `restart_service` မထည့်ပါ။

---

## 13. Test အလွတ်များ

```python
# every promise — the surface
assert {"system_metrics", "read_log", "restart_service"} <= {t.name for t in await client.list_tools()}

# every promise — templates
assert {"config://{host}", "runbook://{name}"} <= {t.uri_template
        for t in await client.list_resource_templates()}

# ⭐ security — it must fail with the RIGHT error code
data = (await client.call_tool("read_log", {"name": "../../etc/passwd"})).data
assert data["error"] == "path_not_allowed"          # not "not_found"

# ⭐ absence — it must list what exists
data = (await client.call_tool("read_log", {"name": "nope.log"})).data
assert data["error"] == "not_found" and data["available"]

# ⭐ prompt — the escape hatch and the prohibition
text = (await client.get_prompt("rca_error_log", {"log_name": "x"})).messages[0].content.text
assert "insufficient evidence" in text and "do not invent" in text.lower()

# ⭐ prompt — no placeholder may survive
text = (await client.get_prompt("capacity_review", {"host": "pve01"})).messages[0].content.text
assert "pve01" in text and "{host}" not in text     # ← FAILS on the capstone

# ⭐ the guard — both branches
async with Client(mcp, mode="legacy", elicitation_handler=accept) as c:
    assert (await c.call_tool("restart_service", {"service": "postgres-ha"})).data["status"] == "confirmed"
async with Client(mcp) as c:
    assert (await c.call_tool("restart_service", {"service": "gitea"})).data["protected"] is False

# ⭐ metrics — both answers are correct
assert data["load_average"] is None or isinstance(data["load_average"], list)
```

---

## 14. Platform ကွာဟမှု — Windows vs Linux

| Field | Windows | Linux |
|---|---|---|
| `host` | `COMPUTERNAME` | `os.uname().nodename` |
| `load_average` | `null` (`hasattr(os,"getloadavg")` = False) | `[0.42, 0.31, 0.28]` |
| `memory_total_gb` | `null` (`/proc/meminfo` မရှိ) | `62.82` |
| `data_disk_*` | ✅ ရသည် | ✅ ရသည် |
| `note` | **တူညီသည်** | **တူညီသည်** |

⭐ `null` သည် **မှားခြင်း မဟုတ်ပါ** — platform က မပေးခြင်း ဖြစ်သည်။

---

## 15. မလုပ်ရမည့်အရာ ၆ ခု

```text
❌ တန်ဖိုးကို default ဖြင့် အစားထိုးခြင်း            → null ကို null ထားပါ
❌ path ကို string startswith ဖြင့် စစ်ခြင်း          → (root / name).resolve()
❌ ကျရှုံးမှုကို raise ဖြင့် ပုံသွင်းခြင်း (tool)      → _fail + available
❌ bound မထည့်ခြင်း                                → clamp + MAX_BYTES
❌ prompt တွင် လွတ်လမ်း မထည့်ခြင်း                   → "insufficient evidence"
❌ tool က မလုပ်ခဲ့သည်ကို "လုပ်ပြီး" လို့ ဆိုခြင်း      → action_taken: "none"
❌ `protected_service_add` ကဲ့သို့ guard ဖျက်သည့် tool  → ဘယ်တော့မှ
```

---

## 16. နာမည်ရွေးချယ်မှုများ — ဘာကြောင့် ဒီအမည်လဲ

| အမည် | ဘာကြောင့် |
|---|---|
| `status: "would_restart"` | conditional — "restarted" မဟုတ်ပါ |
| `action_taken: "none — …"` | လုပ်ခဲ့သည့်အရာကို ရိုးသားစွာ ဆိုသည် |
| `error: "path_not_allowed"` | machine ခွဲခြားနိုင်သည်; `hint` က လူ့အတွက် |
| `available: [...]` | ခန့်မှန်းခြင်းကို ဖျက်သည် |
| `truncated: bool` | "content သည် ဖိုင်တစ်ခုလုံး မဟုတ်" ကို ဆိုသည် |
| `note: "null means …"` | output ကို ကိုယ်တိုင် ရှင်းပြသည် |
| `config_seen: [...]` | audit trail — ဘယ်အချက်အလက်ကို ကြည့်ခဲ့သည် |
| `_resolve`, `_fail` | `_` ဖြင့် စသည်၊ ဒါပေမယ့် ချဲ့ထွင်ရန် ရည်ရွယ်သည် |

---

## 17. အလွတ်ကျက်ရမည့် စည်းမျဉ်း ၅ ချက်

```text
⭐ ၁။ ဖတ်လို့ရသည့်နေရာဖြင့် စစ်ပါ — documentation ကို မယုံပါနဲ့
       print(hasattr(obj, "parameters"), fastmcp.__version__)

⭐ ၂။ runs လုပ်ပြီး တိုင်းပါ — "ငါထင်တယ်" သည် အထောက်အထား မဟုတ်ပါ
       uv run python -m <module>  → output ကို ကူးပါ

⭐ ၃။ မရလျှင် null လို့ဆိုပါ — 0, default, ခန့်မှန်း ဘာမှ မဟုတ်ပါ
       ဒါသည် agent ကို ကာကွယ်သည့် တစ်ခုတည်းသော အရာ

⭐ ၄။ အတင်းအကြပ်ချက် တိုင်းအတွက် လွတ်လမ်းတစ်ခု
       "insufficient evidence" / "say plainly that there is nothing to do"

⭐ ၅။ tool က မလုပ်သည့်အရာကို ရှင်းရှင်းလင်းလင်း ဆိုပါ
       action_taken: "none — …"  → client က လူထံ ပို့ရမည်
```

---

## ကိုးကား

- `01-capstone-brief-and-production.md` — brief နှင့် "production-ready"
- `03-shared-helpers-resolve-and-fail.md` — helper နှစ်ခု၊ အသေးစိတ်
- `07-elicitation-mode-legacy-and-handler.md` — elicitation၊ အသေးစိတ်
- `10-writing-and-testing-prompts.md` — prompt pattern ၇ မျိုး
- [`../code/devops_assistant.py`](code/devops_assistant.py) — capstone server
- [`../../VERIFIED.md`](../VERIFIED.md) — တိုင်းထားသည့် API အချက်အားလုံး
- `17-labs-answers.md` — LAB ၈ ခု၏ အဖြေ
