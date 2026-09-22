# M6 Cheatsheet — Resources (`@mcp.resource`)

ဒီဖိုင်သည် ဒီ module တစ်ခုလုံး၏ အကျဉ်းချုပ်။ သင်ခန်းစာ ၁၁ ဖိုင်ကို ဖတ်ပြီးသူအတွက်
ပြန်လည်သတိရရန်။ လက်တွေ့ အလုပ်လုပ်သည့်အခါ ဒီဖိုင်ကို ဖွင့်ထားပါ။

---

## ၁။ Primitive နှစ်မျိုး

``text
@mcp.tool      → ACTION   "ငါ ဒါ လုပ်ပေးနိုင်တယ်"   model က ရွေးသည်
@mcp.resource  → THING    "ငါ့မှာ ဒါ ရှိတယ်"        URI ဖြင့် ညွှန်းသည်

@mcp.prompt    → TEMPLATE "ဒီလို လုပ်ပါ"           host/လူ က ရွေးသည် (M7)
``

## ၂။ မေးခွန်း ၄ ခု (resource or tool?)

``text
၁. ရှိပြီးသားလား? (exists?)        မဟုတ် → tool
၂. read-only လား?                  မဟုတ် → tool
၃. cheap လား? (< 200 ms)           မဟုတ် → tool
၄. state ပြောင်းလား?               ပြောင်း → tool
→ လေးခုလုံး ✅ → resource
``

| အရာ | ဆုံးဖြတ်ချက် |
|---|---|
| a runbook | resource |
| the host inventory | resource |
| restart a service | tool (state) |
| search the wiki | tool (query + ဈေးကြီး) |
| the current cluster version | cheap ရင် resource, ဈေးကြီးရင် tool |
| log တစ်ခုရဲ့ နောက်ဆုံး ၂၀ လိုင်း | resource (`log://x/tail`) ✅ |
| export ၂ နှစ်စာ | tool (ကြီး၊ pagination) |

## ၃။ ဖိုင်တိုင်း၏ အကြောင်းအရာ

``text
01-resource-concept.md        tool vs resource, runbooks.py အပေါ်ပိုင်း
02-resource-or-tool.md        မေးခွန်း ၄ ခု, cheap ကို တိုင်းတာ, list ၃ မျိုး
03-uri-schemes.md             URI အစိတ်အပိုင်း, scheme, LAB 7
04-static-resources.md        static resource, return shapes, LAB 1/2/8
05-uri-templates.md           {var} → parameter, LAB 3/4
06-mime-types.md              mime_type, default, ကြေညာချက်သာ
07-read-and-enumerate.md      read_resource → list, LAB 5
08-pathlib-for-resources.md   Path, glob, is_file, read_text
09-failing-loudly.md          raise + available, LAB 9
10-confinement-preview.md     resolve() + containment, LAB 6
11-cheatsheet.md              ဒီဖိုင်
12-labs-answers.md            LAB 1–5 အဖြေများ
13-answers-exercises.md       LAB 6–9, bug ၈ ခု, design ၅ ခု, project
``

## ၃.၁။ တိုင်းတာချက် အစစ် ၁၀ ခု (မှတ်ထားရမည်)

``text
၁.  read_resource() → LIST; [0].text                     (LAB 1, 5)
၂.  template-only server → list_resources() == []        (LAB 4)
၃.  attribute က uri_template; .uriTemplate → AttributeError   (LAB 4)
၄.  template.matches('runbook://a/b') → None (slash မကိုက်)   (LAB 4)
၅.  template.parameters → JSON Schema (tool နှင့် တူ)     (LAB 4)
၆.  unknown URI → Resource not found (function မခေါ်)     (LAB 3, 9)
၇.  raise → Error reading resource 'uri': <message>      (LAB 3, 9)
၈.  return "" → SUCCESS, text='' len=0, is_error=False   (LAB 9)
၉.  custom exception type → MCPError, message ကျန်       (LAB 9)
၁၀. mime_type မထည့် → text/plain; ကြေညာချက် မစစ်ခံ       (LAB 8)
``

## ၄။ Decorator နှစ်မျိုး

``python
# STATIC — fixed URI, no arguments   -> list_resources()
@mcp.resource("inventory://hosts", mime_type="application/json")
def host_inventory() -> dict:
    """The current host inventory, as structured data."""
    return json.loads((DATA / "inventory.json").read_text(encoding="utf-8"))


# TEMPLATE — URI pattern, has parameters   -> list_resource_templates()
@mcp.resource("runbook://{service}", mime_type="text/markdown")
def runbook(service: str) -> str:
    """The runbook for a named service.

    Args:
        service: The service whose runbook to read, e.g. 'postgres'.
    """
    path = DATA / f"{service}.md"
    if not path.is_file():
        available = sorted(p.stem for p in DATA.glob("*.md"))
        raise FileNotFoundError(
            f"no runbook for {service!r}; available: {', '.join(available) or 'none'}")
    return path.read_text(encoding="utf-8")
``

## ၅။ Return type → content shape (တိုင်းတာချက်)

| Return | Item | `.text` | ဥပမာ |
|---|---|---|---|
| `str` | Text | ✅ | `'line one\nline two\n'` |
| `dict` | Text | ✅ | `'{"hosts": ["pve01"], "count": 1}'` (compact) |
| `list[str]` | Text | ✅ | `'["pve01", "kasm-agent1"]'` |
| `int` | Text | ✅ | `'2'` |
| `bytes` | **Blob** | ❌ (`.blob`) | `'iVBORw0KGgpsYWI4'` |
| `list[BaseModel]` | ❌ error | — | `TypeError: Object of type Host is not JSON serializable` |
| `async def` | Text | ✅ | `'async resource ok'` |
| `mime_type` မထည့် | Text | ✅ | mime = `text/plain` |

⭐ `list[BaseModel]` အတွက် `[m.model_dump() for m in models]`။

## ၆။ Enumeration — ထောင်ချောက်

``python
async with Client(mcp) as client:
    await client.list_tools()                 # actions
    await client.list_resources()             # ⭐ templates are absent here: []
    await client.list_resource_templates()    # ⭐ templates appear here
``

| Server-side | Client-side |
|---|---|
| `FunctionResource` (`.uri`, `.mime_type`) | `Resource` (`.uri`, `.mime_type`) |
| `FunctionResourceTemplate` (`.uri_template`, `.parameters`, `.matches(uri)`) | `ResourceTemplate` (`.uri_template`) |

``text
⭐ attribute က `uri_template` (snake_case) — `.uriTemplate` သည် AttributeError
⭐ server resource.uri သည် AnyUrl; client resource.uri သည် str → `str(r.uri)` သုံးပါ
⭐ mcp.list_resource_templates() = server object; client.… = wire object
``

## ၇။ Read — contract

``python
items = await client.read_resource("runbook://postgres")   # LIST
text  = items[0].text                                      # ⭐ [0]
mime  = items[0].mime_type
uri   = items[0].uri
``

| လက္ခဏာ | အကြောင်းရင်း | ဖြေရှင်းနည်း |
|---|---|---|
| `'list' object has no attribute 'text'` | `[0]` မေ့ | `(...)[0].text` |
| `'BlobResourceContents' ... 'text'` | binary | `hasattr(item, "text")` |
| `AttributeError: ... 'uriTemplate'` | 2.x | `uri_template` |
| `FastMCPDeprecationWarning` `.mimeType` | 2.x | `.mime_type` |

## ၈။ Error taxonomy (တိုင်းတာချက်)

``text
Resource not found: 'runbook://a/b'                     → URI မကိုက် (router), function မခေါ်
Error reading resource 'runbook://oracle': no runbook   → function ခေါ်ခဲ့သည်၊ raise လုပ်ခဲ့သည်
Error reading resource '...': 1 validation error        → type hint မကိုက်
(exception မရှိ) text='' len=0                           → ⭐ SILENT FAILURE
``

## ၉။ mime_type

``text
type/subtype — text/plain | text/markdown | application/json | image/png | …

default = text/plain        (မထည့်လျှင်)
⭐ ဒါက ကြေညာချက် သာ — FastMCP က content ကို မစစ်ပါ
   shape://mismatch: mime=application/json, text='this is not JSON at all'
``

| Content | mime | return |
|---|---|---|
| runbook / policy | `text/markdown` | `str` |
| config / log | `text/plain` | `str` |
| inventory / schema | `application/json` | `dict` / `list` |
| ရုပ်ပုံ | `image/png` | `bytes` |
| မသိသည့် binary | `application/octet-stream` | `bytes` |

⭐ config ဖိုင်ကို `text/markdown` မထည့်ပါ (`#` သည် comment ဖြစ်နေလျက် heading ဖြစ်သွားသည်)။

## ၁၀။ URI စည်းမျဉ်း

``text
၁. noun သုံး, verb မသုံး        inventory://hosts ✅   get://hosts ❌
၂. စုစည်းမှု plural            inventory://hosts ✅
၃. lowercase (path အထူးသဖြင့်) config://MOTD → FAIL
၄. hyphen, space မဟုတ်        config://nginx/site-enabled ✅
၅. scheme ထဲ version မထည့်     runbook:// ✅  runbook-v2:// ❌
၆. path ၂ အဆင့်ထက် မပို
၇. variable ကို ကြိုသိနိုင်      runbook://{service} ✅  runbook://{anything} ❌
``

| URI | ရလဒ် |
|---|---|
| `runbook://postgres` | ✅ |
| `runbook://POSTGRES` | ✅ (authority case ခံ) |
| `CONFIG://motd` | ✅ (scheme case ခံ) |
| `config://MOTD` | ❌ path case မခံ |
| `runbook://postgres/` | ❌ trailing slash |
| `config://motd?x=1` | ❌ query |
| `runbook://a/b` | ❌ variable သည် တစ် segment |
| `runbook://..%2F..%2Fetc%2Fpasswd` | ❌ |

## ၁၁။ pathlib

``python
DATA = Path(__file__).with_name("data")     # ⭐ independent of the CWD
DATA.mkdir(exist_ok=True)

path = DATA / f"{service}.md"               # / operator
if not path.is_file():                      # is_file > exists
    ...

available = sorted(p.stem for p in DATA.glob("*.md"))   # stem + sorted (determinism)
text = path.read_text(encoding="utf-8")                 # ⭐ always pass an encoding
data = json.loads(text)                                 # verify it really is JSON
blob = path.read_bytes()                                # binary
``

| Method | အသုံး |
|---|---|
| `.name` / `.stem` / `.suffix` | `postgres.md` / `postgres` / `.md` |
| `.parent` / `.parents` | directory / အပေါ်ဘက်အားလုံး |
| `.is_file()` / `.is_dir()` | ⭐ မှန်ကန်သည့် စစ်ဆေးမှု |
| `.glob("*.md")` | non-recursive (`.rglob` = recursive) |
| `.resolve()` | absolute + `..` + symlink — **security** |
| `.with_name("data")` | sibling ဖိုင်နာမည် အစားထိုး |

## ၁၂။ Failing loudly

``python
if not path.is_file():
    available = sorted(p.stem for p in DATA.glob("*.md"))
    raise FileNotFoundError(
        f"no runbook for {service!r}; available: {', '.join(available) or 'none'}")
``

``text
✅ တန်ဖိုး အတိအကျ: {service!r}
✅ ဆက်လုပ်လို့ရသည့် အချက်: available: ...
✅ server-side path မပေါက်
❌ return "" / return None  → model က "အလွတ်" ဟု ဖတ်သည်, log တွင်လည်း မပေါ်
❌ {"ok": false}            → content သည် document; error channel မရှိ
⭐ custom exception type သည် wire မဖြတ် → message ထဲ အမည် ထည့်ပါ
⭐ raise ... from exc       → client: message ကောင်း; server log: အကြောင်းရင်း အပြည့်
``

## ၁၃။ Confinement

``python
ROOT = DATA.resolve()
candidate = (ROOT / name).resolve()          # resolve FIRST
if ROOT not in candidate.parents:            # the containment check SECOND
    raise ValueError(f"path escapes the runbook directory: {name!r}")
return candidate
``

``text
အလွှာ ၁: router — segment variable တွင် `/` မကိုက် → `matches('runbook://a/b') -> None`
အလွှာ ၂: resolve() + containment — path လက်ခံသည့် resource/tool အတွက် တစ်ခုတည်း
မူ: ".. တားမြစ်" မဟုတ် — "ရလဒ်သည် root အတွင်း ရှိရမည်"
⭐ root ကိုယ်တိုင်: `candidate != ROOT and ROOT not in candidate.parents` (M10)
⚠️ symlink escape ကို M6 တွင် တိုင်းတာထားခြင်း မရှိ
``

## ၁၄။ Lab များ (run command များ)

``bash
uv run python -m M6_resources.code.runbooks                 # the module's main code
uv run python -m M6_resources.code.lab_1_static_text        # static text (.txt)
uv run python -m M6_resources.code.lab_2_static_json        # static JSON (.json)
uv run python -m M6_resources.code.lab_3_runbook_template   # URI template
uv run python -m M6_resources.code.lab_4_enumeration_trap   # the two lists
uv run python -m M6_resources.code.lab_5_reader_loop        # generic reader
uv run python -m M6_resources.code.lab_6_confinement        # confinement
uv run python -m M6_resources.code.lab_7_uri_edges          # URI edges
uv run python -m M6_resources.code.lab_8_return_shapes      # return shapes
uv run python -m M6_resources.code.lab_9_failure_shapes     # four failure shapes
``

## ၁၅။ အမှား ၁၂ ခု — လက္ခဏာ → ဖြေရှင်းနည်း

| လက္ခဏာ | အကြောင်းရင်း | ဖြေရှင်းနည်း |
|---|---|---|
| `'list' object has no attribute 'text'` | `[0]` မေ့ | `(...)[0].text` |
| `list_resources()` ဗလာ | template ရှိသည် | `list_resource_templates()` |
| `AttributeError: 'uriTemplate'` | 2.x | `uri_template` |
| `Resource not found:` | URI မကိုက် | URI စစ် (LAB 7) |
| `Error reading resource ... no runbook` | ဖိုင် မရှိ | `available` ထဲက ရွေး |
| `1 validation error` | type hint မကိုက် | တန်ဖိုး ပြင် သို့ `str` |
| `TypeError: ... not JSON serializable` | model စာရင်း ပြန်သည် | `.model_dump()` |
| `AttributeError: 'Blob...' 'text'` | binary | `hasattr(item, "text")` |
| `FileNotFoundError` (ဖိုင်) | relative path | `Path(__file__)` |
| `UnicodeDecodeError` | encoding | `encoding="utf-8"` |
| `Resource not found: '.../'` | trailing slash | `/` ဖယ် |
| `IsADirectoryError` | `exists()` သုံး | `is_file()` |

## ၁၆။ Code review checklist (resource တစ်ခုစီအတွက်)

``text
☐ primitive မှန်သလဲ? (resource vs tool — မေးခွန်း ၄ ခု)
☐ URI သည် noun, lowercase, version မပါ, path ≤ 2 segment?
☐ template ဖြစ်လျှင် variable ကို ကြိုသိနိုင်သလဲ? တန်ဖိုး စာရင်း ပေးသလဲ?
☐ mime_type ထည့်သလဲ? return type နှင့် ကိုက်သလဲ?
☐ docstring ရှိသလဲ? (description ဖြစ်လာသည်)
☐ ဖိုင်မရှိ / data မရှိလျှင် raise လုပ်သလဲ? ဗလာ ပြန်သလား? ⭐
☐ error message တွင် တန်ဖိုး + available ပါသလဲ?
☐ path ကို `Path(__file__)` ဖြင့် anchor လုပ်သလဲ?
☐ encoding="utf-8" ထည့်သလဲ?
☐ traversal ကာကွယ်မှု (confinement) ရှိသလဲ?
☐ state မပြောင်းစေကြောင်း သေချာသလဲ? (read-only ကတိ)
☐ ဈေးကြီးလျှင် cache / TTL ရှိသလဲ?
``

## ၁၇။ VERIFIED.md နှင့် ကိုက်ညီမှု

``text
✅ @mcp.resource("runbook://{service}") registers a TEMPLATE, not a resource
✅ await mcp.list_resources() → [] for a template-only server
✅ await mcp.list_resource_templates() → objects whose uri_template is runbook://{service}
✅ await client.read_resource("runbook://postgres") → a list; take [0].text
✅ A resource with no content raises clearly (FileNotFoundError: no runbook for 'nginx';
   available: postgres, redis) — which is more useful to a model than an empty string
✅ 2.x template.uriTemplate → 4.x template.uri_template
``

⭐ မှတ်ချက်: `VERIFIED.md` က `FileNotFoundError` ဟု ရေးထားသည်; **client လက်ခံသည့်
အရာမှာ `MCPError`** ဖြစ်ပြီး message ထဲတွင် မူရင်း `FileNotFoundError` ၏ စာသား
ပါသည် (LAB 9 တွင် တိုင်းတာ)။ Server log တွင် `FileNotFoundError` အတိုင်း ပေါ်သည်။

## ၁၈။ သင့် server ၏ contract ကို README တွင် ရေးခြင်း

``markdown
# runbooks server

## Resources (read-only, addressed by URI)

| URI | Kind | Read cost | Notes |
|---|---|---|---|
| `runbook://{service}` | template | cheap (local file) | services: postgres, redis, nginx, kasm |
| `inventory://hosts` | static | cheap | `application/json` |
| `config://motd` | static | cheap | `text/plain` |

⚠️ `runbook://{service}` raises `FileNotFoundError` for an unknown service and lists the
available ones in the message.

## Tools (actions, chosen by the model)

| Tool | What it changes |
|---|---|
| `restart_service(name)` | restarts a service; requires an allowlist |
``

⭐ ဒီ table နှစ်ခုသည် **host developer အတွက် လုံလောက်သည့် integration spec** ဖြစ်သည်။
M11 capstone တွင် ဒီပုံစံကို တိုက်ရိုက် သုံးမည်။

## ၁၉။ နောက် module များသို့ ချိတ်ဆက်မှု

``text
M5 (ရှေ့)   → tool ၏ structured error; M6 ၏ raise နှင့် ဘာကြောင့် မဆန့်ကျင်သလဲ
M7 (နောက်)  → @mcp.prompt — host/လူ ရွေးသည့် စာသား; resource နှင့် ကွာခြားချက်
M8          → elicit — resource ၏ read-only ကတိကို ချိုးဖောက်လိုလျှင် tool လိုသည်
M9          → orchestrating client — LAB 5 ၏ reader loop ကို ချဲ့သည်
M10         → confinement ပြီးဆုံး; allowlist; MAX_BYTES; no shell
M11         → capstone — resource စာရင်း + tool စာရင်း = server ၏ contract
``

## ကိုးကား

- [`../code/runbooks.py`](code/runbooks.py) — module ၏ ပင်မ code
- [`../code/`](code/) — lab ဖိုင် ၉ ခု
- [`../../VERIFIED.md`](../VERIFIED.md) — တိုင်းတာပြီး အတည်ပြုထားသည့် API
- [`../TUTORIAL_SPEC.md`](../TUTORIAL_SPEC.md) — ဖွဲ့စည်းပုံ
- `12-labs-answers.md` — lab အဖြေများ
