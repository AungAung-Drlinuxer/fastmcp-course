# solution.md — M2 အဖြေများ

## အလေ့ ၁ — Annotation Report

``python
# lab_1_solution.py — read annotations like a schema generator would
from typing import get_type_hints, get_origin, get_args

def provision(name: str, cpus: int = 2, tags: list[str] | None = None) -> dict:
    # The body is irrelevant; we only study the annotations.
    return {}

hints = get_type_hints(provision)
for pname, hint in hints.items():
    origin = get_origin(hint)
    args = get_args(hint)
    print(f"{pname}: origin={origin}, args={args}")

# Expected observations:
#   name: origin=None, args=()           -> plain scalar
#   cpus: origin=None, args=()           -> plain scalar with default
#   tags: origin=typing.Union, args=(list[str], NoneType)
#   -> a Union means "optional" to a schema generator
``

**အဓိကအယူအဆ** — `get_origin` နှင့် `get_args` ဖြင့် annotation တစ်ခုကို scalar၊ container၊ optional ဟု ခွဲခြားဖတ်နိုင်သည်။

## အလေ့ ၂ — `str` vs `Literal` စာချုပ်

``python
# lab_2_solution.py — show why Literal is a contract, str is a wish
from typing import Literal
from pydantic import BaseModel, ValidationError

class Loose(BaseModel):
    region: str

class Strict(BaseModel):
    region: Literal["us-east-1", "eu-west-1", "ap-southeast-1"]

# A plain str accepts anything, including typos:
print(Loose(region="us-east1"))      # accepted silently

# Literal rejects anything outside the allowed set:
try:
    Strict(region="us-east1")
except ValidationError as exc:
    for err in exc.errors():
        print(err["loc"], err["type"], err["input"])

# error type is 'literal_error' — the typo is caught at the boundary
``

**အဓိကအယူအဆ** — `str` ထက် `Literal` သုံးခြင်းက တစ်စလော စာလုံးမှားမှုကို validation နေရာမှာပဲ ဖမ်းပေးသည်။

## အလေ့ ၃ — Signature မှ JSON Schema

``python
# lab_3_solution.py — build a schema from a function signature
import inspect
from typing import get_type_hints, get_origin, get_args, Union

_PRIMITIVES = {str: "string", int: "integer", float: "number", bool: "boolean"}

def annotation_to_schema(hint):
    if hint in _PRIMITIVES:
        return {"type": _PRIMITIVES[hint]}
    origin, args = get_origin(hint), get_args(hint)
    if origin is Union:                       # X | None -> optional scalar
        non_none = [a for a in args if a is not type(None)]
        return annotation_to_schema(non_none[0])
    return {"type": "string"}                 # safe fallback

def function_to_schema(func):
    sig = inspect.signature(func)
    hints = get_type_hints(func)
    props, required = {}, []
    for name, param in sig.parameters.items():
        if param.annotation is inspect.Parameter.empty:
            continue
        props[name] = annotation_to_schema(hints[name])
        if param.default is inspect.Parameter.empty:
            required.append(name)
    return {"type": "object", "properties": props, "required": required}

def create_vm(name: str, cpus: int, pinned: bool = False):
    # Body omitted; the signature is the contract.
    ...

print(function_to_schema(create_vm))
# {"type": "object", "properties": {...}, "required": ["name", "cpus"]}
``

**အဓိကအယူအဆ** — function တစ်ခု၏ JSON Schema ကို `inspect.signature` နှင့် type hints မှ စက်ဖြင့် ထုတ်နိုင်သည်။

## အလေ့ ၄ — `ServerProvisionSchema`

``python
# lab_4_solution.py — the sibling of VMProvisionSchema
from typing import Literal
from pydantic import BaseModel, Field

class ServerProvisionSchema(BaseModel):
    name: str = Field(description="Server hostname, must be unique.")
    size: Literal["small", "medium", "large"] = Field(
        description="Fixed size tiers; no other values accepted."
    )
    cpus: int = Field(default=2, ge=1, le=64, description="vCPU count, 1-64.")
    region: Literal["us-east-1", "eu-west-1", "ap-southeast-1"] = Field(
        description="Region the server lives in."
    )

good = ServerProvisionSchema(name="web-01", size="small", cpus=4,
                             region="us-east-1")
print(good.model_dump())
print(ServerProvisionSchema.model_json_schema()["required"])  # ['name', 'size', 'region']
# cpus is absent from required because it has a default
``

**အဓိကအယူအဆ** — Pydantic model တစ်ခုတည်းက validation rule များနှင့် JSON Schema နှစ်မျိုးလုံးကို တစ်ပြိုင်နက် ထုတ်ပေးသည်။

## အလေ့ ၅ — Validation Drill

``python
# lab_5_solution.py — read a ValidationError like a debugger
from typing import Literal
from pydantic import BaseModel, Field, ValidationError

class Item(BaseModel):
    count: int = Field(ge=1, le=10)
    mode: Literal["fast", "safe"]
    label: str

bad_payloads = [
    {"count": 0, "mode": "fast", "label": "a"},     # ge violation
    {"count": 5, "mode": "turbo", "label": "b"},    # literal_error
    {"count": 5, "mode": "fast"},                   # missing field
]

for payload in bad_payloads:
    try:
        Item(**payload)
    except ValidationError as exc:
        for err in exc.errors():
            # loc = path to the bad field; type = rule name; input = what was sent
            print(f"loc={err['loc']} type={err['type']} input={err['input']!r}")

# Each error is independent: loc pinpoints WHERE, type explains WHY.
``

**အဓိကအယူအဆ** — `loc`၊ `type`၊ `input` သုံးခုက error ဖြစ်သည့်နေရာ၊ အကြောင်းရင်းနှင့် ဝင်လာသောတန်ဖိုးကို ပြသည်။

## အလေ့ ၆ — Nested Models

``python
# lab_6_solution.py — nested models, $defs and $ref
from pydantic import BaseModel, Field, ValidationError

class Network(BaseModel):
    vpc_id: str = Field(description="VPC the disk lives in.")
    public: bool = Field(default=False)

class Disk(BaseModel):
    size_gb: int = Field(ge=10, le=1000)
    network: Network

schema = Disk.model_json_schema()
print(schema["$defs"])               # Network schema stored under $defs
print(schema["properties"]["network"])  # uses $ref: '#/$defs/Network'

# A nested error points at the inner field with a multi-part loc:
try:
    Disk(size_gb=50, network={"vpc_id": "", "public": "yes"})
except ValidationError as exc:
    for err in exc.errors():
        print(err["loc"])   # ('network', 'public') — path into the child model
``

**အဓိကအယူအဆ** — nested model များက schema ထဲတွင် `$defs` နှင့် `$ref` ဖြင့် ချိတ်ဆက်ပြီး error ၏ `loc` က child field အထိ လမ်းညွှန်သည်။

## အလေ့ ၇ — Drift Check

``python
# lab_7_solution.py — verify the model still matches reality
from lab_4_solution import ServerProvisionSchema

EXPECTED_REQUIRED = {"name", "size", "region"}
EXPECTED_KEYS = {"name", "size", "cpus", "region"}

schema = ServerProvisionSchema.model_json_schema()

actual_keys = set(schema["properties"].keys())
actual_required = set(schema["required"])

# Three drift checks: fields, required set, and an unknown extra field.
assert actual_keys == EXPECTED_KEYS, f"field drift: {actual_keys ^ EXPECTED_KEYS}"
assert actual_required == EXPECTED_REQUIRED, f"required drift: {actual_required}"
assert "deprecated_zone" not in schema["properties"], "stale field detected"

print("No drift — the declaration and the contract still agree.")
``

**အဓိကအယူအဆ** — declaration တစ်ခုတည်းနှင့် schema ကို မွေးထုတ်ပြီး test များဖြင့် စစ်ဆေးခြင်းက drift ဖြစ်မှုကို အလိုအလျောက် ဖမ်းပေးသည်။
