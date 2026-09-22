# M2 Cheatsheet — Type Hints, Introspection & Pydantic

> Lesson 1.2 ၏ အမြန် ကိုးကား။ ဒီဖိုင်ကို **ဖတ်ရန်** မဟုတ်ပါ — အလုပ်လုပ်နေရင်း
> လှန်ကြည့်ရန် ဖြစ်သည်။ သင်ခန်းစာ အပြည့်အစုံအတွက် ဖိုင် ၀၁–၁၀ ကို ဖတ်ပါ။

---

## 1. အခြေခံ သဘောတရား — သုံးလိုင်း

```text
★ Type hint သည် DATA ဖြစ်သည် — `f.__annotations__` မှ တကယ် ဖတ်လို့ရသည်
★ Hint သည် inert — သူ့အလိုလို ဘာမှ validate မလုပ်ပါ
★ MCP သည် annotation ကို ဖတ်ပြီး JSON Schema ဆောက်သည် → annotation တိကျရမည်
```

```python
# Read annotations as data
def f(vm_name: str, cpu_cores: int = 2) -> dict:
    """Doc."""
    return {}

f.__annotations__          # {'vm_name': <class 'str'>, 'cpu_cores': <class 'int'>, 'return': <class 'dict'>}
```

---

## 2. Hint → JSON Schema (တိုင်းတာပြီး)

| Python hint | JSON Schema |
|---|---|
| `str` | `{"type": "string"}` |
| `int` | `{"type": "integer"}` |
| `float` | `{"type": "number"}` |
| `bool` | `{"type": "boolean"}` |
| `list[str]` | `{"type": "array", "items": {"type": "string"}}` |
| `dict[str, int]` | `{"type": "object", "additionalProperties": {"type": "integer"}}` |
| `dict[str, Any]` | `{"type": "object", "additionalProperties": true}` ⚠️ |
| `Any` | `{}`(title သာ) ❌ |
| `int \| None` | `{"anyOf": [{"type": "integer"}, {"type": "null"}]}` |
| `Literal["x","y"]` | `{"enum": ["x","y"], "type": "string"}` ⭐ |
| `Literal["x"]` | `{"const": "x", "type": "string"}` |
| `Literal["x", 1]` | `{"enum": ["x", 1]}` — ⚠️ `type` မပါ |
| `Literal[True, False]` | `{"enum": [true,false], "type": "boolean"}` |
| `list[dict[str,int]]` | `{"type":"array","items":{"type":"object","additionalProperties":{"type":"integer"}}}` ⚠️ |
| `Disk` (nested model) | `{"$ref": "#/$defs/Disk"}` + `$defs` ⭐ |

```text
⭐ ရွေးချယ်ရာတွင်: Literal > str ; nested model > dict[str, Any] ; list[Model] > list[dict]
```

---

## 3. `typing` API — ဖတ်သည့် function များ

| Function | ဘာပြန်သည် | ဥပမာ |
|---|---|---|
| `get_origin(x)` | container class / union marker | `list[str]` → `list`; `str\|int` → `types.UnionType` |
| `get_args(x)` | အတွင်းဘက် hint များ | `dict[str,int]` → `(str, int)` |
| `get_type_hints(fn)` | **ဖြေရှင်းပြီး** annotation dict | `'int'` → `<class 'int'>` |
| `inspect.signature(fn, eval_str=True)` | ဖြေရှင်းပြီး Signature | `param.annotation` ကို တိုက်ရိုက် သုံးလို့ရ |
| `isinstance(x, type)` | bare class ဖြစ်/မဖြစ် | `str` → True; `list[str]` → False |

```python
import types, typing
from typing import Any, Literal, get_args, get_origin

get_origin(str)                 # None
get_origin(list[str])           # <class 'list'>
get_origin(dict[str, Any])      # <class 'dict'>
get_origin(str | int)           # <class 'types.UnionType'>
get_origin(typing.Union[str,int])  # typing.Union
get_origin(Literal["a","b"])    # typing.Literal
get_args(str | int)             # (<class 'str'>, <class 'int'>)
get_args(int | None)            # (<class 'int'>, <class 'NoneType'>)
get_args(Literal["a","b"])      # ('a', 'b')      ← values, not a type
```

### ⭐⭐ Union ကို ဖမ်းခြင်း — အသုံးအများဆုံး snippet

```python
import types, typing

if get_origin(annotation) is typing.Union or get_origin(annotation) is types.UnionType:
    parts = get_args(annotation)
    non_none = [p for p in parts if p is not type(None)]   # ⚠️ do not use `is not None`
    nullable = len(non_none) != len(parts)
```

| လုပ်ဆောင်ချက် | ❌ မှား | ✅ မှန် |
|---|---|---|
| list စစ် | `isinstance(x, list[str])` | `get_origin(x) is list` |
| Union စစ် | `isinstance(x, Union)` | `get_origin(x) in (typing.Union, types.UnionType)` |
| nullable စစ် | `None in get_args(x)` | `any(p is type(None) for p in get_args(x))` |
| Literal စစ် | `isinstance(x, Literal)` | `get_origin(x) is Literal` |
| class စစ် | `x.__name__` | `isinstance(x, type)` |
| `Optional[X]` == `X \| None` | — | `True` (တူညီသည့် object) |

### ⚠️ PEP 563 trap — `from __future__ import annotations`

```python
from __future__ import annotations

def f(cpu_cores: int) -> None: ...

f.__annotations__["cpu_cores"]   # 'int'     ← STRING
get_origin('int')                # None      ← not resolved
'int' in {int: "integer"}        # False     ← string ≠ class
```

```text
အကျိုးဆက်: naive schema generator သည် parameter တိုင်းအတွက် {"type": "object"} ထုတ်သည်
          → ⚠️ ERROR မပေါ်ပါ — SILENT WRONG SCHEMA
ဖြေရှင်းနည်း: get_type_hints(fn) သို့ inspect.signature(fn, eval_str=True)
```

---

## 4. `inspect` API

```python
import inspect

sig = inspect.signature(fn)
sig.parameters                      # mapping; order is preserved
sig.return_annotation               # return annotation
for name, p in sig.parameters.items():
    p.name, p.annotation, p.default, p.kind
```

| Attribute | Default မရှိလျှင် | မှတ်ချက် |
|---|---|---|
| `p.default` | `inspect.Parameter.empty` | sentinel — `None` နှင့် မရောရ |
| `p.annotation` | `inspect.Parameter.empty` | PEP 563 ဆိုလျှင် string |

| `p.kind` | MCP tool တွင် |
|---|---|
| `POSITIONAL_OR_KEYWORD` | ✅ |
| `KEYWORD_ONLY` | ✅ |
| `VAR_POSITIONAL` (`*args`) | ❌ |
| `VAR_KEYWORD` (`**kwargs`) | ❌ |
| `POSITIONAL_ONLY` | ❌ |

```python
inspect.getdoc(fn)     # dedented docstring — use this for MCP
fn.__doc__             # raw (with indentation)
inspect.Parameter.empty
```

⭐ `required` ကို ဆောက်သည့် snippet:

```python
required = [n for n, p in sig.parameters.items()
            if p.default is inspect.Parameter.empty]
```

---

## 5. Schema ကို လက်ဖြင့် ဆောက်ခြင်း — skeleton

```python
import inspect
from typing import Literal, get_args, get_origin, get_type_hints

PRIMITIVES = {str: "string", int: "integer", float: "number", bool: "boolean"}


def fragment(annotation: object) -> dict:
    origin = get_origin(annotation)
    if origin is Literal:
        values = list(get_args(annotation))
        inner = {int: "integer", str: "string", bool: "boolean"}.get(type(values[0]), "string")
        return {"type": inner, "enum": values}
    if origin is not None:
        parts = get_args(annotation)
        non_none = [p for p in parts if p is not type(None)]
        if len(non_none) == 1:
            return fragment(non_none[0])                      # X | None
        return {"anyOf": [fragment(p) for p in non_none]}
    if origin is list:
        (item,) = get_args(annotation)
        return {"type": "array", "items": fragment(item)}
    if origin is dict:
        _key, value = get_args(annotation)
        return {"type": "object", "additionalProperties": fragment(value)}
    if annotation in PRIMITIVES:
        return {"type": PRIMITIVES[annotation]}
    return {}


def build(fn) -> dict:
    sig = inspect.signature(fn)
    hints = get_type_hints(fn)              # ⭐ resolves PEP 563
    props, required = {}, []
    for name, p in sig.parameters.items():
        piece = fragment(hints.get(name, p.annotation))
        if p.default is not inspect.Parameter.empty:
            piece["default"] = p.default
        else:
            required.append(name)
        props[name] = piece
    out = {"type": "object", "properties": props, "additionalProperties": False}
    if required:
        out["required"] = required
    return out
```

⭐ လက်ဖြင့် ဆောက်ခြင်းက မဖြေနိုင်သည့် အရာ **နှစ်ခု**:

```text
၁. ge= / le= — Field ကို ဖတ်လို့ မရ
၂. VALIDATION — ဒါက describe သာ လုပ်သည်; မှား call သည် function ကိုယ်ထဲ ရောက်သည်
```

---

## 6. Pydantic — model declaration

```python
from typing import Literal
from pydantic import BaseModel, Field, ValidationError


class VMProvisionSchema(BaseModel):
    """A request to provision a virtual machine."""

    vm_name: str = Field(description="Name of the virtual machine")
    cpu_cores: int = Field(default=2, ge=1, le=16, description="Virtual cores to assign (1-16)")
    os_type: Literal["ubuntu", "rocky", "windows"] = Field(description="Operating System")
    memory_gb: int | None = Field(
        default=None, ge=1,
        description="Memory in GB. Omit to let the platform choose a default for the OS.",
    )
```

### `Field(...)` keyword → schema key

| keyword | schema key | စစ်သည့် |
|---|---|---|
| `description=` | `description` | — (model အတွက်) |
| `default=` | `default` | — |
| `default_factory=` | *(မပါ)* ⚠️ | instance အသစ် |
| `ge=` / `le=` | `minimum` / `maximum` | `>=` / `<=` |
| `gt=` / `lt=` | `exclusiveMinimum` / `exclusiveMaximum` | `>` / `<` |
| `min_length=` (str) | `minLength` | အရှည် |
| `max_length=` (str) | `maxLength` | အရှည် |
| `min_length=` (list) | `minItems` | element အရေအတွက် |
| `max_length=` (list) | `maxItems` | element အရေအတွက် |
| `pattern=` | `pattern` | regex |
| `multiple_of=` | `multipleOf` | ဆတိုး |
| `strict=True` | *(မပြ)* | coercion ပိတ် |

### ⭐⭐ required ဇယား (အမှား အများဆုံး)

| Declaration | `is_required()` | `required` ထဲ | `default` |
|---|---|---|---|
| `x: str` | **True** | ✅ | မပါ |
| `x: str = "a"` | False | ❌ | `"a"` |
| `x: str = Field(description="d")` | **True** ⚠️ | ✅ | မပါ |
| `x: str = Field(default="a")` | False | ❌ | `"a"` |
| `x: list[str] = Field(default_factory=list)` | False | ❌ | **မပါ** ⚠️ |
| `x: int \| None = None` | False | ❌ | `null` |
| `x: int \| None` | **True** ⚠️ | ✅ | မပါ |

⭐ စည်းမျဉ်း: **`Field()` ခေါ်ခြင်းသည် default ရှိသည်ဟု မဆိုလိုပါ။**
⭐ `is_required()` ကို သုံးပါ — `.default` သည် `PydanticUndefined` ဖြစ်နိုင်သည်။

### Class docstring → object description; `title` → Pydantic ဆောက်သည်

```text
class M(BaseModel):
    """This text becomes schema["description"]."""
    vm_name: str         → "title": "Vm Name"   (သင် မရေးခဲ့)
```

### အလုပ်လုပ်သည့်နည်းလမ်းများ

```python
VMProvisionSchema.model_json_schema()          # dict
VMProvisionSchema.model_json_schema()["required"]
VMProvisionSchema.model_fields                 # metadata for each field
VMProvisionSchema.model_fields["cpu_cores"].is_required()
VMProvisionSchema.model_fields["cpu_cores"].annotation    # resolved

vm = VMProvisionSchema(vm_name="kasm-agent1", os_type="ubuntu")
str(vm)                                        # vm_name='kasm-agent1' ...
vm.model_dump()                                # dict
vm.model_dump(exclude_none=True)               # remove Nones
vm.model_dump_json()                           # JSON string
```

---

## 7. `ValidationError` — ဖတ်နည်း

```python
try:
    VMProvisionSchema(vm_name="x", cpu_cores=99, os_type="ubuntu")
except ValidationError as exc:
    exc.errors()          # [{...}, ...]
    exc.error_count()     # 1
    str(exc)              # human-readable text
```

### Error dict ၏ key

| key | ဥပမာ | အဓိပ္ပာယ် |
|---|---|---|
| `type` | `less_than_equal` | ကျိုးသည့် စည်းမျဉ်း |
| `loc` | `('cpu_cores',)` | field path |
| `loc` (nested) | `('disks', 0, 'size_gb')` | လမ်းကြောင်း တစ်ခုလုံး |
| `msg` | `Input should be less than or equal to 16` | လူ ဖတ်ရမည့် |
| `input` | `99` | မှားသည့် တန်ဖိုး |
| `ctx` | `{'le': 16}` | bound ၏ တန်ဖိုး (⚠️ အမြဲ မပါ) |
| `url` | `https://errors.pydantic.dev/2.13/v/...` | docs |

```python
first = exc.errors()[0]
loc = ".".join(str(p) for p in first["loc"])       # 'disks.0.size_gb'
first.get("input")                                  # ⭐ use .get()
```

### `type` ဇယား — အသုံးအများဆုံး

| `type` | Trigger | `ctx` |
|---|---|---|
| `missing` | required field မပေး | — (input = payload တစ်ခုလုံး!) |
| `string_type` | `str` လိုသည် | — |
| `int_type` | strict mode | — |
| `int_parsing` | `int` parse မရ (`"eight"`) | — |
| `int_from_float` | `int` လိုသည်၊ float ရ (`8.5`) | — |
| `less_than_equal` / `greater_than_equal` | `le=` / `ge=` | `{'le': N}` |
| `less_than` / `greater_than` | `lt=` / `gt=` | `{'lt': N}` |
| `literal_error` | `Literal[...]` မပါ | — |
| `string_too_short` / `string_too_long` | `min_length` / `max_length` | `{'min_length': N}` |
| `string_pattern_mismatch` | `pattern=` | `{'pattern': ...}` |
| `bool_parsing` | `bool` parse မရ | — |
| `finite_number` | `NaN` | — |

### ⭐ အရေးကြီးသည့် အချက်

```text
★ Pydantic သည် error အားလုံးကို တစ်ချိန်တည်း ပေးသည် (round trip တစ်ခုတည်း) ✅
★ errors()[0] သည် "အရေးကြီးဆုံး" မဟုတ် — အစောဆုံး FIELD ၏ error
★ ValidationError ⊂ ValueError — ဒါပေမယ့် ValidationError ဖြင့် ဖမ်းပါ
★ errors() ထဲ model class အမည် မပါ — log တွင် ကိုယ်တိုင် ရေးပါ
```

### Coercion (တိုင်းတာပြီး)

| value → `int` field | ရလဒ် |
|---|---|
| `8` / `"8"` / `8.0` / `" 8 "` | ✅ `8` |
| `True` | ✅ `1` |
| `"8.5"` / `"eight"` | ❌ `int_parsing` |
| `8.5` | ❌ `int_from_float` |
| `NaN` | ❌ `finite_number` |

| value → `bool` field | ရလဒ် |
|---|---|
| `True` / `1` / `"yes"` / `"on"` / `"true"` / `"1"` / `"y"` | ✅ `True` |
| `0` / `"no"` / `"off"` / `"false"` / `"0"` / `"n"` | ✅ `False` |
| `2` / `""` / `"maybe"` | ❌ `bool_parsing` |

---

## 8. Drift — ဘယ်လို ကာကွယ်မည်

```text
★ rule တစ်ခုကို နေရာတစ်ခုတည်းတွင် ရေးပါ
★ bound နှင့် ဆက်စပ်သည့် နံပါတ်ကို f-string + constant ဖြင့် ရေးပါ
     cpu_cores: int = Field(default=2, ge=1, le=MAX,
                            description=f"Virtual cores to assign (1-{MAX})")
★ test ဖြင့် ဖမ်းပါ:
     assert props["cpu_cores"]["maximum"] == 16
     assert props["vm_name"]["description"]
     assert set(schema["required"]) == {"vm_name", "os_type"}
★ description တွင် required/optional ကို မရေးပါ — schema က ဆိုသည်
★ description ကို တစ်နေရာတည်းတွင် ရေးပါ (Field(description=...) ကို ရွေးပါ)
```

### ⭐ FastMCP သည် ရင်းမြစ် နှစ်ခုကို ပေါင်းသည် (`VERIFIED.md`)

| Source | Appears as |
|---|---|
| parameter name | the property key |
| annotation (`int`, `Literal[...]`) | `type` / `enum` |
| `Field(ge=1, le=16)` | `minimum` / `maximum` |
| `Field(default=2)` | `default` |
| `Field(description=...)` | `description` |
| docstring `Args:` | the parameter `description` |

```text
FastMCP က ထုတ်သည့် schema တွင် တိုင်းတာပြီး မြင်ရသည့် ကွာခြားချက် (VERIFIED.md):
  additionalProperties: false  ← Pydantic ၏ schema ထဲ မပါပါ; FastMCP output တွင် ပါသည်
  title key များ မပါ            ← ⚠️ ဒါကို FastMCP က ဖယ်သည်ဟု ဆိုနိုင်သော်လည်း
                                 ဒီ course တွင် implementation ကို မစစ်ပါ —
                                 တိုင်းတာချက်တွင် မပါသည်သာ အတည်ပြုထားသည်
```

---

## 9. အမှား ရှာသည့် ဇယား — လက္ခဏာ → အကြောင်းရင်း → ဖြေရှင်းနည်း

| လက္ခဏာ | အကြောင်းရင်း | ဖြေရှင်းနည်း |
|---|---|---|
| property အားလုံး `{"type":"object"}` | PEP 563 — string annotation ဖတ်နေသည် | `get_type_hints(fn)` |
| `enum` မပါ | `Literal` အစား `str` | `Literal[...]` သုံးပါ |
| `minimum` မပါ | `ge=` မရေးထား သို့ `gt=` ရေးထား | `ge=` သုံးပါ |
| required ထဲ မဖြစ်သင့်သည့် field ပါ | `Field(description=...)` ထဲ default မရေး | `default=` ထည့်ပါ (သို့ ဖယ်ပါ) |
| required ထဲ မပါသင့်သည့် field မပါ | `default=` ရေးမိ | `default=` ဖယ်ပါ |
| `null` ပို့လို့ရသည်ကို schema မဆို | `X \| None` ကို `required` မှ ဖယ်ခြင်းဖြင့် ဖော်ပြသည် | Pydantic သုံးပါ (`anyOf` + `null`) |
| `TypeError: subscripted generics ...` | `isinstance(x, list[str])` | `get_origin(x) is list` |
| `AttributeError: 'types.UnionType' has no '__name__'` | `(str \| int).__name__` | `get_origin` / `get_args` |
| `TypeError: unhashable type: 'list'` | `Literal[["x"]]` ကို dict key အဖြစ် | hashable တန်ဖိုး / `tuple` |
| `list[str].__name__` → `"list"` | GenericAlias က origin ဆီ လွှဲသည် | `get_args` ဖတ်ပါ |
| `p is not None` ဖြင့် `NoneType` မဖယ် | `NoneType` class ≠ `None` | `p is not type(None)` |
| `KeyError: 'ctx'` | error တိုင်းတွင် ctx မရှိ | `.get("ctx")` |
| `TypeError: sequence item 0: expected str` | `".".join(loc)` — int ပါသည် | `str(p) for p in loc` |
| `TypeError: NotImplemented` / `default=[]` error | mutable default | `default_factory=list` |
| `PydanticUserError: needs a type annotation` | annotation မရေး | `x: str = Field(...)` |
| `NameError: name 'X' is not defined` | docstring/annotation eval မရ | module scope ထဲ import |
| `KeyError: 'return'` | `get_type_hints` dict ကို params အဖြစ် သုံး | `hints.get(name, p.annotation)` |

---

## 10. Tool parameter ဒီဇိုင်း — checklist

```text
[ ] parameter တိုင်းတွင် type hint ရှိသည်
[ ] enum ဖြစ်နိုင်သည့် အရာအားလုံးကို Literal ဖြင့် ရေးထားသည်
[ ] bound ရှိသည့် ကိန်းတိုင်းတွင် ge=/le= ရှိသည်
[ ] optional field တိုင်းတွင် default ရှိသည်
[ ] `int | None` ဖြစ်လျှင် `= None` ရှိသည်
[ ] field တိုင်းတွင် description ရှိသည် — model အတွက် ရေးထားသည်
[ ] optional field ၏ description တွင် "omit လုပ်လျှင် ဘာဖြစ်မည်" ရှိသည်
[ ] `dict[str, Any]` မသုံးပါ — nested model သုံးသည်
[ ] `*args` / `**kwargs` မသုံးပါ
[ ] schema ကို test ဖြင့် assert လုပ်ထားသည်
[ ] `required` list ကို မျက်လုံးဖြင့် စစ်ပြီးပြီ
```

---

## 11. Snippet စုစည်းမှု — ကူးယူရန် အသင့်

```python
# ── 1. Resolve annotations (resolves PEP 563) ─────────────────────────────
from typing import get_type_hints
hints = get_type_hints(fn)

# ── 2. Read the signature ───────────────────────────────────────────────────
import inspect
sig = inspect.signature(fn, eval_str=True)

# ── 3. required list ────────────────────────────────────────────────────────
required = [n for n, p in sig.parameters.items()
            if p.default is inspect.Parameter.empty]

# ── 4. Check for Union ────────────────────────────────────────────────────────────
import types, typing
from typing import get_args, get_origin
origin = get_origin(ann)
if origin in (typing.Union, types.UnionType):
    non_none = [p for p in get_args(ann) if p is not type(None)]

# ── 5. Check for Literal ─────────────────────────────────────────────────────────
from typing import Literal
if get_origin(ann) is Literal:
    values = list(get_args(ann))

# ── 6. Define the model ────────────────────────────────────────────────────
from typing import Literal
from pydantic import BaseModel, Field

class Params(BaseModel):
    """What this tool does, for the model."""
    name: str = Field(description="Name of the thing, e.g. web01")
    count: int = Field(default=2, ge=1, le=16, description="How many (1-16)")
    mode: Literal["a", "b"] = Field(description="Which mode")

# ── 7. Validate + read ───────────────────────────────────────────────────────
from pydantic import ValidationError
try:
    params = Params(**payload)
except ValidationError as exc:
    for err in exc.errors():
        print(err["loc"], err["type"], err.get("input"), err["msg"])
else:
    print(params.model_dump())
```

---

## 12. ဤ module ၏ ဖိုင်များ

| ဖိုင် | ဘာပြသည် |
|---|---|
| `code/type_hints.py` | hint သည် data; `get_origin`/`get_args` ဖြင့် `explain()` |
| `code/introspect.py` | signature မှ schema ကို လက်ဖြင့် ဆောက်; description မမြင်နိုင် |
| `code/schema_demo.py` | `VMProvisionSchema` — schema + validation တစ်နေရာတည်း |
| `code/lab_1_annotation_report.py` | hint catalog → report |
| `code/lab_2_literal_contract.py` | `str` vs `Literal` တိုက်စစ် |
| `code/lab_3_signature_schema.py` | naive → `get_type_hints` → descriptions |
| `code/lab_4_server_schema.py` | `ServerProvisionSchema` + ရှစ်ချက် စစ် |
| `code/lab_5_validation_drill.py` | bad payload ကိုးခု → error ဇယား |
| `code/lab_6_nested_models.py` | `$defs`/`$ref`, nested error path |
| `code/lab_7_drift_check.py` | drift = True vs False |
| `tests/test_m2_schema.py` | schema ကို assert (6 tests) |

---

## ကိုးကား

- `01 — Type Hints Are Data` · `02 — Every Hint Form`
- `03 — get_origin & get_args` · `04 — Literal Beats str`
- `05 — The inspect Module` · `06 — Hand-rolled JSON Schema`
- `07 — Pydantic BaseModel & Field` · `08 — Reading a ValidationError`
- `09 — VMProvisionSchema Worked Example` · `10 — One Declaration, No Drift`
- `12 — Labs Answers` · [`../../VERIFIED.md`](../VERIFIED.md)