# M10 Cheatsheet — Production Security & Hardening in one page (and twelve)

## ဒီဖိုင်မှာ ဘာရှိလဲ

- ⭐ ဒီ module ရဲ့ **အဓိက စည်းမျဉ်း ၁၀ ချက်** (တစ်ကြောင်းစီ)
- ဖိုင် ၁၁ ဖိုင်ရဲ့ အကျဉ်းချုပ် — ဖိုင်တစ်ခုစီအတွက် ၃-၄ ကြောင်း
- command, error code, attack matrix, bound, container flag, audit field ဇယားများ
- ⭐ tool အသစ် တစ်ခု ထည့်မီ ဖြေရမည့် approval gate
- code review checklist (`rg` command များ)
- incident response checklist
- 4.0.5 API အချက်များ (VERIFIED.md မှ)
- glossary

---

## အပိုင်း ၁ — ⭐ အဓိက စည်းမျဉ်း ၁၀ ချက်

```text
၁. tool list = attack surface. @mcp.tool ရှိသည့် function တစ်ခုစီကို review လုပ်ပါ။
၂. tool argument သည် model-generated input ဖြစ်သည် — "user ရိုက်လိုက်တာ" မဟုတ်ပါ။
၃. ⭐ Path.resolve() ကို စစ်ဆေးမှု မတိုင်မီ လုပ်ပါ; string နှိုင်းယှဉ်ခြင်း သည် bypass ဖြစ်သည်။
၄. ⭐ shell တစ်ခု မရှိရ — subprocess.run(shell=True), os.system, eval အားလုံး မရှိရ။
၅. ⭐ output သည် input ကဲ့သို့ attack surface ဖြစ်သည် — max_lines, MAX_BYTES, line cap။
၆. ⭐ refusal သည် DATA (`{"ok": False, ...}`) — exception မဟုတ်ပါ; code သည် closed set ဖြစ်ရမည်။
၇. ⭐ process ကို non-root (numeric uid) အဖြစ် run ပါ; code directory သည် read-only ဖြစ်ရမည်။
၈. ⭐ audit trail သည် secret မပါရ — shape ကို မှတ်ပါ, value ကို မှတ်ပါနဲ့။
၉. ⭐ tool description/docstring သည် code — review, pin, hash လုပ်ပါ။
၁၀. ⭐ control တစ်ခုစီအတွက် "ဒါက ဘာကို မကာကွယ်သလဲ" ကို ဆိုနိုင်ရမည်။
```

---

## အပိုင်း ၂ — ဖိုင် ၁၁ ဖိုင် အကျဉ်းချုပ်

| ဖိုင် | အဓိက သင်ခန်းစာ (၃ ကြောင်း) |
|---|---|
| `01-threat-modelling-an-mcp-server.md` | tool list = attack surface · asset/actor/boundary/impact/control · သင်ခန်းစာကို dataclass အဖြစ် ရေးပြီး `assert` ဖြင့် CI gate လုပ်ပါ |
| `02-prompt-injection-direct-and-indirect.md` | direct (user) vs indirect (tool ဖတ်သည့် စာသား) · tool result ကို `system` role ထဲ မရောပါ · injection ကို ဖြေလို့မရ — **ဒဏ်** ကို ဖျက်ပါ |
| `03-tool-poisoning-and-rug-pulls.md` | description သည် model ဖတ်သည့် payload · approve ပြီးနောက် ပြောင်းလဲနိုင်သည် · name+description+`parameters` ကို hash လုပ်ပြီး drift ရှာပါ |
| `04-least-privilege-both-levels.md` | host-level (process) နှင့် server-level (tool) အလွှာ ၂ ခု · ambient authority (env, `.aws`) · measured/target/how ဖြင့် တိုင်းပါ |
| `05-the-unbounded-tool-antipattern.md` | `shell=True` ၏ ပြဿနာ ၅ ခု · `shlex.split` သည် fix မဟုတ် · tool အမည်ကို မယုံပါနဲ့ (read_log ဟု အမည်တပ်ထားသည့် EXECUTE tool) |
| `06-path-confinement.md` | `LOG_ROOT` allowlist root · **resolve before check** · sibling-prefix bypass · refusal ထဲ resolved path မထည့်ရ |
| `07-output-bounding-and-the-return-shape.md` | bound ၃ မျိုး (lines, bytes, per-line) · server-side clamp · `truncated_bytes` သည် correctness control · `errors="replace"` |
| `08-structured-refusal.md` | refusal = data / failure = exception · closed error set · `hint` သည် model UI (ဒါပေမယ့် info မပေါက်ကြားရ) · schema violation = `ToolError` |
| `09-the-attack-matrix.md` | ⭐ မိသားစု ၂ ခု: traversal (`path_not_allowed`) vs injection (`not_found`) · filter မထည့်ပါ · `""`/`"."` သည် `not_found` ဖြစ်သည် |
| `10-containerisation-and-non-root.md` | container = process တစ်ခု၊ kernel တစ်ခုတည်း · numeric non-root uid · Dockerfile သည် image ကို၊ runtime flags သည် process ကို · kernel mount ≠ Python check |
| `11-audit-logging.md` | JSON Lines append-only · subclass **substring** redaction (`token` သည် `api_token` ကို ဖမ်းသည်) · record before + after · `str(exc)` ကို မမှတ်ပါ |

---

## အပိုင်း ၃ — ⭐ command အားလုံး (copy-paste)

```bash
# ---- labs (run all from course root) ----
uv run python -m M10_security.code.lab_1_threat_model
uv run python -m M10_security.code.lab_2_injection_bench
uv run python -m M10_security.code.lab_3_tool_manifest          # write + verify
uv run python -m M10_security.code.lab_3_tool_manifest --drift  # rug-pull demo
uv run python -m M10_security.code.lab_4_capability_inventory
uv run python -m M10_security.code.lab_5_unbounded_tool
uv run python -m M10_security.code.lab_6_confinement
uv run python -m M10_security.code.lab_7_output_bounds
uv run python -m M10_security.code.lab_8_refusal_contract
uv run python -m M10_security.code.lab_9_attack_matrix
uv run python -m M10_security.code.lab_10_container_smoke
uv run python -m M10_security.code.lab_11_audit_log

# ---- this module's server itself ----
uv run python -m M10_security.code.path_validation

# ---- the test suite ----
uv run pytest -q tests/test_m10_security.py
uv run pytest -q

# ---- check the version (if hashes don't match, this may be why) ----
uv run python -c "import fastmcp, pydantic; print(fastmcp.__version__, pydantic.__version__)"
```

⭐ လိုအပ်သည့် version:

```text
fastmcp   4.0.5
pydantic  2.13.5
python    3.11.x
```

---

## အပိုင်း ၄ — ⭐ attack matrix (အတိုချုပ်)

| attempt | error | ⭐ ကျရသည့် အကြောင်းရင်း |
|---|---|---|
| `../../etc/shadow` | `path_not_allowed` | `.resolve()` က `..` ကို collapse → root ပြင်ပ |
| `..\..\windows\win.ini` | `path_not_allowed` | backslash separator ကိုပါ pathlib က ကိုင်တယ် |
| `/etc/passwd` | `path_not_allowed` | absolute path သည် `ROOT / path` ရဲ့ ဘယ်ဘက်ကို ပယ်ပြီး သူ့အစား ဝင်သည် |
| `logs/../../../etc/hosts` | `path_not_allowed` | subdir မှ တွန်းထုတ်သည် |
| `postgres.log; rm -rf /` | `not_found` | ⭐ shell မရှိ → `;` သည် စာလုံးတစ်လုံး |
| `$(id)` | `not_found` | ⭐ substitution လုပ်သည့် shell မရှိ |
| `postgres.log && curl evil` | `not_found` | ⭐ ဒုတိယ "command" ဆိုတာ မရှိပါ |
| `../secret.env` (raw check) | ⭐ **allowed (BUG)** | string သည် `...logs\..\secret.env` — root ဟု ပြနေသည် |
| `shortcut.log` → symlink အပြင် | `path_not_allowed` | `.resolve()` က symlink ကို ဖြေသည် |
| `""` / `"."` | `not_found` | root ကိုယ်တိုင် → `.is_file()` False |
| `".."` | `path_not_allowed` | parent directory |
| `"a\x00b"` | `path_not_allowed` | library က `ValueError` မြှင့် → `except ValueError` က ဖမ်းသည် |
| `./postgres.log` | ⭐ `ok: True` | legitimate! `./` ကို resolve က ဖျက်သည် |

⭐ မိသားစု ၂ ခု:

```text
traversal  → boundary (`_resolve_within`) က ကိုင်တွယ်သည် → path_not_allowed
injection  → shell မရှိခြင်း က ကိုင်တွယ်သည်       → not_found
⭐ filter (`if ";" in name`) မထည့်ပါ — false positive ကို ဖန်တီးသည်၊ အန္တရာယ်ကို မဖျက်ပါ
```

---

## အပိုင်း ၅ — ⭐ ပြဿနာ ၅ ခု → အဖြေ ၅ ခု

| # | `shell=True` ရဲ့ ပြဿနာ | ⭐ refactor ရဲ့ အဖြေ | code |
|---|---|---|---|
| ၁ | whole command language (`; & \| $() >` globbing) | shell ကို လုံးဝ ဖယ် | `in` ဖြင့် substring search |
| ၂ | allowlist မရှိ (binary/argument အားလုံး) | tool တစ်ခုစီ = အလုပ်တစ်ခု | `read_log` / `list_logs` / `grep_log` |
| ၃ | path confinement မရှိ | allowlist root + resolve | `_resolve_within()` |
| ၄ | timeout မရှိ | (ဒီ tool များတွင် subprocess မရှိ) ⭐ | grep ကို ၂၀၀ match တွင် ရပ် |
| ၅ | output bound မရှိ | `max_lines` + `MAX_BYTES` + `line[:300]` | `read_log` / `grep_log` |

⭐ နှင့် ပြောင်းလဲမှု ပဉ္စမ (code ထဲတွင် စာရင်းချထားသည်):

```text
("allowlist of files",        "reading anything on the host")
("Path.resolve() confinement","traversal and symlink escapes")
("no shell anywhere",         "command chaining and injection")
("max_lines / MAX_BYTES",     "context exhaustion from one call")
("a list_logs tool",          "the reason to guess paths at all")   ⭐
```

---

## အပိုင်း ၆ — ⭐ bound ဇယား

| bound | တန်ဖိုး | ဘယ်မှာ | ဘာကို ကာကွယ်သည် |
|---|---|---|---|
| `max_lines` | clamp `1..1000` | `read_log` | လိုင်း အရေအတွက် (context) |
| `MAX_BYTES` | `64 * 1024` | `read_log` (`content`) | byte ပမာဏ (⚡ `body[:MAX_BYTES]` — char-based) |
| `truncated_bytes` | `True`/`False` | `read_log` return | ⭐ correctness (false negative ကို ဖျက်) |
| `max_matches` | clamp `1..200` | `grep_log` | match အရေအတွက် |
| per-line cut | `line[:300]` | `grep_log` | တစ်လိုင်းစီရဲ့ အရှည် (minified JSON, stack trace) |
| `list_logs` names | (ဒီ lab တွင် မဖြတ်) | `list_logs` | ⚠️ production တွင် ဖြတ်ပါ (`[:300]` စသည်) |
| timeout | ⚠️ မရှိ | — | ⭐ ဒီ tool များတွင် subprocess မရှိလို့; subprocess ရှိလျှင် `timeout=` လိုသည် |
| memory | ⚠️ `read_text()` သည် ဖိုင်တစ်ခုလုံးကို ဖတ် | `read_log` | ⭐ host-level memory limit လိုသည် (file 10) |

⭐ clamp ရဲ့ ပုံစံ:

```python
max_lines = max(1, min(1000, max_lines))      # ⭐ server-side truth
```

---

## အပိုင်း ၇ — ⭐ error code ဇယား (closed set)

| code | အဓိပ္ပာယ် | caller/model က ဘာလုပ်သင့်သလဲ | alert? |
|---|---|---|---|
| `path_not_allowed` | boundary က ရပ် — root ပြင်ပ | ရပ် (သို့) `list_logs` ဖြင့် မှန်သည့် နာမည် | ⭐ YES (probing signal) |
| `not_found` | path မှန်၊ ဖိုင် မရှိ | `list_logs` ခေါ် | များလျှင် (typo vs fuzzing) |
| `bad_argument` | value range/shape မှား | argument ပြင် | ⭐ များလျှင် YES |
| `unavailable` | dependency မရ (ဖိုင်/socket/upstream) | နောက်မှ ပြန် | YES (availability) |

⭐ shape:

```python
{"ok": False, "error": "path_not_allowed", "hint": "path escapes the log directory: '...'"}
{"ok": True,  "name": "postgres.log", "lines": 2, "truncated_bytes": False, "content": "..."}
```

⭐ `hint` ထဲ မထည့်ရ: resolved absolute path · ဖိုင်စနစ် စာရင်း · `str(exc)` အပြည့် ·
user text ကို ပြန်ပေးခြင်း (injection carrier ဖြစ်လာသည်)။

---

## အပိုင်း ၈ — ⭐ container flag ဇယား

| Dockerfile (image) | ⭐ ဘာကြောင့် |
|---|---|
| `FROM ... AS builder` + `FROM python:3.11-slim AS runtime` | build tool များ မပါလာရ |
| `uv sync --frozen --no-dev` | lockfile ကို မပြင်ရ; dev dependency မပါ |
| `useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin mcp` | home မရှိ (`.aws` မရှိ), login shell မရှိ |
| `COPY --from=builder --chown=0:0 ...` | ⭐ process သည် ဖတ်နိုင်သည်၊ ရေးလို့ မရ |
| `USER 10001:10001` | ⭐ **numeric** uid (name ကို uid 0 သို့ ပြန်ညွှန်နိုင်သည်) |
| `VOLUME ["/var/log/mcp"]` | တစ်ခုတည်း ရေးနိုင်သည့် နေရာ |
| `LABEL org.opencontainers.image.*` | auditability (source, version) |
| ⚠️ `python:3.11-slim` | tag-pinned; production တွင် `@sha256:` digest ဖြင့် pin ပါ |

| Runtime (`docker run`) | ⭐ ဖျက်လိုက်သည့် အန္တရာယ် |
|---|---|
| `--read-only` | code ကို ပြင်ခြင်း (persistence) |
| `--tmpfs /tmp:rw,noexec,nosuid,size=16m` | /tmp ထဲက exec လုပ်ခြင်း |
| `--cap-drop=ALL` | `CAP_NET_RAW`, `CAP_SYS_ADMIN` |
| `--security-opt=no-new-privileges` | setuid ဖြင့် privilege ပြန်ရယူခြင်း |
| `--pids-limit=128` | fork bomb |
| `--memory=256m` | memory exhaustion |
| `--network=none` | exfiltration |
| `-v "$PWD/logs:/var/log/mcp:ro"` | ⭐ log ဖိုင် ပြင်ခြင်း — **kernel** က ငြင်းသည် |
| `-i` | stdio transport အတွက် stdin |

⭐ defence in depth ၏ စည်းမျဉ်း: **control ၂ ခု တူညီသည့် assumption အပေါ် မမှီခိုရ။**

---

## အပိုင်း ၉ — ⭐ audit field ဇယား

| field | ဥပမာ | ⭐ ဘာကြောင့် |
|---|---|---|
| `ts` | `2026-09-19T15:16:45.384+00:00` | ⭐ UTC, ms — host/upstream log များနှင့် တွဲရန် |
| `event` | `tool_call` / `tool_result` / `tool_exception` | record before + after |
| `actor` / `session` | `lab-student` / `m10-lab-11` | "ဘယ်သူ / ဘယ် conversation" |
| `tool` | `read_log` | ဘယ် tool |
| `args` | `{"name": "postgres.log"}` | ⭐ shape — secret-shaped များကို redact |
| `host_context` | `{"api_token": {"redacted": true, ...}}` | host application ရဲ့ ကိုယ်ပိုင် material |
| `verdict` | `ok` / `refused:path_not_allowed` | ⭐ decision — alert rule ရဲ့ အခြေခံ |
| `is_error` | `false` | ⭐ VERIFIED.md: refusal သည် `is_error=False` |
| `ms` | `5.3` | performance + timeout detection |
| `kind` | `ToolError` | ⭐ exception ၏ **အမည်သာ** (`str(exc)` မဟုတ်!) |

⭐ redaction ပုံစံ:

```python
{"redacted": True, "sha256_16": "8b503cb9c94107b3", "length": 22}
```

⭐ `is_sensitive` သည် **substring** match ဖြစ်ရမည်:

```python
SENSITIVE = ("password", "passwd", "pwd", "token", "secret", "api_key", "apikey",
             "authorization", "auth", "credential", "connection_string", "private_key")
return any(hint in key.lower() for hint in SENSITIVE)     # ⭐ not `key in SENSITIVE`
```

---

## အပိုင်း ၁၀ — ⭐ tool အသစ် approval gate (ဖြေရမည့် မေးခွန်း ၈ ခု)

```text
tool အသစ် တစ်ခု ထည့်မီ — ဒီ ၈ ခုလုံးကို ဖြေပါ:

၁. ဒီ tool သည် STRANGER တစ်ဦးကို ဘာလုပ်ခွင့် ပေးသလဲ?            (ဖိုင် 01)
၂. အာဏာ အမျိုးအစား = READ / WRITE / EXECUTE / DELETE / NETWORK?     (ဖိုင် 04)
၃. argument တစ်ခုစီသည် ဘယ် bound ကို ထိနိုင်သလဲ?                  (ဖိုင် 07)
၄. argument မှားလျှင် ဘာဖြစ်မလဲ — ဒဏ် (blast radius) က ဘယ်လောက်လဲ?  (ဖိုင် 06)
၅. refusal ရဲ့ code က ဘာလဲ — closed set ထဲ ပါသလား?                (ဖိုင် 08)
၆. description သည် model ကို ဘာဆိုသလဲ — hidden instruction ရှိလား?   (ဖိုင် 03)
၇. output ထဲတွင် instruction-like စာသား ပါနိုင်လား?               (ဖိုင် 02)
၈. ဒီ tool ရဲ့ call များကို audit trail တွင် ဘယ်လို မြင်မလဲ?        (ဖိုင် 11)

⭐ ၈ ခုလုံး ဖြေလို့ရပြီဆိုမှ `@mcp.tool` ကို ရေးပါ။
```

---

## အပိုင်း ၁၁ — ⭐ code review checklist

```bash
# 1. no shell allowed
rg -n "shell\s*=\s*True" .
rg -n "os\.system|os\.popen|commands\.getoutput" .
rg -n "eval\(|exec\(" .
rg -n "pickle\.loads?" .

# 2. if subprocess exists — must use list argv and a timeout
rg -n -A3 "subprocess\.(run|call|Popen|check_output)"

# 3. path confinement
rg -n "startswith\(.*root|startswith\(.*ROOT" .        # ⚠️ sibling-prefix bypass
rg -n "is_relative_to" .                               # ⚠️ without resolve, it's lexical
rg -n "\.resolve\(\)" .                                # ✅ look for this

# 4. bound
rg -n "read_text\(|\.read\(\)" .                       # ⚠️ without bound
rg -n "max_|MAX_" .                                    # ✅ bound constants

# 5. refusal shape
rg -n '"error":' .                                     # are the codes within the closed set
rg -n 'raise ' .                                       # ⚠️ raises from within a tool (may be a refusal)

# 6. audit / secret
rg -n "str\(exc\)|traceback" .                         # ⚠️ arg value may leak through
rg -n "os\.environ" .                                  # ⚠️ ambient authority
```

⭐ ဒီ command များသည် **တစ်ခုတည်းသော code review pass** ဖြစ်သည် — အချိန် ၅ မိနစ်။

---

## အပိုင်း ၁၂ — ⭐ incident response checklist

```text
tool တစ်ခုက မမျှော်မှန်းသည့် အရာ လုပ်ခဲ့သည်ဟု သံသယ ရှိလျှင်:

၁. audit trail ကို ဖတ်ပါ — verdict column ကို အရင် ကြည့်ပါ
      jq -c 'select(.verdict | startswith("refused:"))' audit.jsonl
   ⭐ "refused" များလျှင် boundary က ရပ်ခဲ့သည်; "ok" များလျှင် အလုပ်လုပ်ခဲ့သည်

၂. args column ကို ကြည့်ပါ — ဒါက "ဘယ်ဖိုင် ပေါက်ကြား" ကို ဖြေသည်
      jq -c 'select(.tool == "read_log") | .args' audit.jsonl

၃. session/actor ကို ခွဲပါ — ဒါက "ဘယ် user/conversation" ကို ဖြေသည်

၄. ⭐ container பக்கம் ကြည့်ပါ — process သည် read-only rootfs ဖြစ်ခဲ့သလား?
      docker inspect <ctr> --format '{{.Config.User}}'
      docker inspect <ctr> --format '{{.HostConfig.ReadonlyRootfs}}'
      docker inspect <ctr> --format '{{.HostConfig.CapDrop}}'
   ⭐ ဒါက "ကိုယ်ပိုင် code ကို ပြင်ခဲ့သလား (persistence)" ကို ဖြေသည်

၅. ⭐ ဖြေရှင်းရာတွင်: code ကို ပြင်ခြင်းထက် ⭐ REACH ကို လျှော့ပါ
      (tool ကို ခေတ္တ ဖယ်၊ allowlist ကို ကျဉ်း၊ mount ကို ro လုပ်)
   ⭐ ဒါသည် ဒီ module တစ်ခုလုံးရဲ့ သင်ခန်းစာ — အာဏာကို ချုပ်ပါ။
```

---

## အပိုင်း ၁၃ — ⭐ 4.0.5 API အချက်များ (VERIFIED.md)

| 2.x documentation says | What 4.0.5 actually has | error |
|---|---|---|
| `ElicitationResult` | `AcceptedElicitation` / `DeclinedElicitation` / `CancelledElicitation` | `ImportError` |
| `tool.inputSchema` | `tool.parameters` | `AttributeError: 'FunctionTool' object has no attribute 'inputSchema'` |
| `template.uriTemplate` | `template.uri_template` | `AttributeError` |
| `await mcp.get_tools()` | `await mcp.list_tools()` | `AttributeError: 'FastMCP' object has no attribute 'get_tools'` |

⭐ schema ကို ဖတ်သည့် နာမည် — အခြမ်းအလိုက် ကွာသည်:

| Where | Object type | Read as |
|---|---|---|
| server: `await mcp.list_tools()` | `FunctionTool` | `.parameters` |
| client: `await client.list_tools()` | `mcp_types._types.Tool` | `.input_schema` |

```text
AttributeError: 'Tool' object has no attribute 'parameters'
FastMCPDeprecationWarning: Accessing `Tool.inputSchema` is deprecated; ... renamed this field
                           to `input_schema`.
```

⭐ ဒီ module အတွက် အရေးကြီးဆုံး တိုင်းတာချက်:

```text
tool RETURNING {"ok": false, "error": "..."}
    -> CallToolResult(..., structured_content={...}, is_error=False)   # data
tool RAISING ZeroDivisionError
    -> ToolError, model သည် error string ကိုသာ ရသည် — plan မရှိပါ
argument သည် schema ကို ချိုးလျှင် (max_lines="lots")
    -> ToolError  1 validation error for call[read_log]  [type=int_parsing]
```

---

## အပိုင်း ၁၄ — glossary (English → Burmese အနှစ်ချုပ်)

| term | ⭐ အဓိပ္ပာယ် (ဒီ module အလိုက်) |
|---|---|
| attack surface | model က တိုက်ရိုက် ခေါ်နိုင်သည့် tool များ |
| allowlist root | tool များ ဖတ်ခွင့်ရှိသည့် တစ်ခုတည်းသော directory (`LOG_ROOT`) |
| confinement | "ဒီနေရာအတွင်းသာ" ဆိုသည့် reach ကို စစ်ဆေးမှုဖြင့် ချုပ်ခြင်း |
| traversal (`..`) | path string ဖြင့် directory အဆင့် ကျော်ခြင်း |
| symlink escape | root အတွင်းမှ ဖိုင် အမည်တစ်ခုက root ပြင်ပကို ညွှန်ခြင်း |
| TOCTOU | စစ်ဆေးချိန် နှင့် အသုံးချချိန် ကြား path ပြောင်းခြင်း |
| prompt injection (direct) | user ရဲ့ message ထဲ ပါလာသည့် instructions |
| prompt injection (indirect) | tool ဖတ်လိုက်သည့် document/log/page ထဲ ပါလာသည့် instructions |
| confused deputy | အာဏာရှိသည့် server ကို အာဏာမရှိသူက ခိုင်းခြင်း |
| tool poisoning | tool description ထဲတွင် hidden instruction ထည့်ခြင်း |
| rug-pull | approve ပြီးနောက် description/အပြုအမူ ပြောင်းခြင်း |
| ambient authority | ကိုယ်တိုင် ပေးလိုက်သည်မဟုတ်ဘဲ ရလာသည့် အာဏာ (env, home) |
| unbounded tool | reach မရှိ — feature မှန်သည်၊ boundary မရှိ |
| clamp | client ရဲ့ တောင်းဆိုချက်ကို server ရဲ့ ceiling ဖြင့် ဖြတ်ခြင်း |
| refusal | tool ရဲ့ ဆုံးဖြတ်ချက် — data အဖြစ် ပြန်သည် |
| closed set | caller က `==` ဖြင့် စစ်နိုင်သည့် error code များ |
| context exhaustion | output ကြီးတစ်ခုက model ၏ context ကို ဖြည့်ခြင်း (DoS) |
| redaction | secret-shaped value ကို fingerprint ဖြင့် အစားထိုးခြင်း |
| defence in depth | control ၂ ခု — တစ်ခုက ကျသည့်အခါ ကျန်တစ်ခု ဆက်ရပ် |
| blast radius | boundary ကျလျှင် ဆိုးနိုင်သည့် အတိုင်းအတာ |

---

## အပိုင်း ၁၅ — ⭐ နောက်ဆုံး ၅ ကြောင်း

```text
၁. ⭐ အန္တရာယ်သည် tool ရဲ့ အမည်တွင် မရှိပါ — signature နှင့် body ကို ဖတ်ပါ။
၂. ⭐ injection ကို ဖြေလို့ မရပါ — ဒဏ်ကို ဖျက်ပါ (reach, bound, provenance)။
၃. ⭐ string ကို မစစ်ပါနဲ့ — တည်နေရာ (resolved path) ကို စစ်ပါ။
၄. ⭐ refusal သည် DATA ဖြစ်ရမည်; code သည် closed set ဖြစ်ရမည်; hint သည် model UI ဖြစ်ရမည်။
၅. ⭐ "ဒီ control က ဘာကို မကာကွယ်သလဲ" ကို ဆိုနိုင်လျှင် ဒါသည် control တစ်ခု;
   မဆိုနိုင်လျှင် ဒါသည် မျှော်လင့်ချက် တစ်ခု။
```

## ကိုးကား

- [`../code/path_validation.py`](code/path_validation.py) — module ရဲ့ server
- [`../deploy/Dockerfile`](deploy/Dockerfile) — image recipe
- `13-labs-answers.md` — lab အားလုံးရဲ့ အဖြေ
- `01-threat-modelling-an-mcp-server.md` → `11-audit-logging.md` — ဖိုင် ၁၁ ဖိုင်
- [`../../VERIFIED.md`](../VERIFIED.md) — 4.0.5 API အချက်များ
- [`../TUTORIAL_SPEC.md`](../TUTORIAL_SPEC.md) — ဒီ tutorial ရဲ့ ရေးနည်းစည်းမျဉ်း