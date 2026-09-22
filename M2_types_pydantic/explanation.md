# M2 — Type Hints, Introspection & Pydantic (ရှင်းလင်းချက်)

M1 မှာ Python ပတ်ဝန်းကျင်ကို ပြင်ဆင်ပြီးပါပြီ။ M2 မှာ MCP tool တစ်ခုရဲ့ input schema — ဆိုလိုတာ tool ခေါ်တဲ့အခါ ဘယ် parameter တွေ ဘယ် type တွေ လိုမလဲဆိုတဲ့ စာရင်း — ကို အလိုအလျောက် ထုတ်ချင်တဲ့ အခြေခံ သုံးချက် သင်မယ်နော်။ သုံးချက်ကတော့ type hints၊ `inspect` module နဲ့ Pydantic တွေပါ။

---

## အချက် ၁ — Type Hints ဆိုတာ Data ဖြစ်သည်

### ဘာကို ဆိုလိုတာလဲ

Type hint ဆိုတာ — function ရဲ့ parameter တွေ ဘယ် data အမျိုးအစားလဲဆိုတာ မှတ်ပေးတဲ့ အမှတ်အသားလေးပါ။ ဥပမာ `def provision(vm_name: str, cpu: int) -> dict:` လို့ ရေးလိုက်တာပေါ့။ ဒါက comment သက်သက် မဟုတ်ပါဘူးနော်။ Python က ဒီ hint တွေကို runtime မှာ `__annotations__` attribute ထဲ စစ်စစ်မှန်မှန် သိမ်းထားပေးတယ်။ လူဖတ်လို့ရသလို စက်လည်း ဖတ်လို့ရတဲ့ အချက်အလက်ကိစ္စပါ။

### ဘာကြောင့် လဲ

MCP server က tool တစ်ခုကို client ဆီ ကြေညာရင် JSON Schema ပုံစံနဲ့ ပြောရတယ်။ ကြေညာစာလိုက်ရင် parameter နာမည်၊ type၊ ဘယ်ဟာ မဖြစ်မနေလိုလဲဆိုတာ ရေးပေးရတယ်။ ဒါကို function ကနေ အလိုအလျောက် ထုတ်လို့ရရင် schema ကို လက်ဖြင့် နှစ်ခါ ရေးစရာ မလိုတော့ဘူး။ ရေးနေရင် ဘာဖြစ်မလဲဆိုတော့ function ထဲက type နဲ့ schema ထဲက type တွေ မတူတော့တဲ့အချိန် ရောက်လာတယ်။ ဒီလို ခြားနေတာကို "drift" လို့ ခေါ်တယ် — နောက်ပိုင်းမှာ ပြန်ပြောပါမယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Function ရဲ့ `__annotations__` dict ထဲက hint တွေကို အရင် ဖတ်တယ်။
၂။ `from __future__ import annotations` သုံးထားရင် hint တွေ အားလုံး string ဖြစ်နေတယ်။
၃။ ဒါကြောင့် `typing.get_type_hints()` နဲ့ string တွေကို တကယ့် type object အဖြစ် ပြန်ပြောင်းတယ်။
၄။ `typing.get_origin()` နဲ့ `typing.get_args()` နဲ့ generic type — ဆိုလိုတာ `list[...]` လို အထဲမှာ type နောက်ထပ်ပါတဲ့ ပုံစံ — ကို ခွဲကြည့်တယ်။
၅။ `list[dict[str, int]]` လို အထဲထဲ နောက်ထပ် နောက်ထပ်ပါရင် ထပ်ခါထပ်ခါ ဖတ်ရတဲ့ recursive reader လိုအပ်တယ်။

### ဥပမာ

ဒီ snippet မှာ `__annotations__` ထဲ ဘာသိမ်းထားလဲ တိုက်ရိုက် ပြထားတယ်။ သတိထားဖတ်ရမှာက hint တွေက တချို့အခါ string ဖြစ်နေတတ်တာပါ။
```python
from typing import get_type_hints, get_origin, get_args

def provision(vm_name: str, tags: list[str], cpu: int | None = None):
    return vm_name

# Read annotations as real objects, not strings
hints = get_type_hints(provision)
print(hints["vm_name"])
print(hints["tags"])

# Unwrap a generic: origin is the container, args are the parameters
print(get_origin(hints["tags"]), get_args(hints["tags"]))

# A union like int | None is detected via get_origin
cpu_hint = hints["cpu"]
print(get_origin(cpu_hint), get_args(cpu_hint))

# Expected output:
# <class 'str'>
# list[str]
# <class 'list'> (str,)
# typing.Union (<class 'int'>, <class 'NoneType'>)
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

MCP မှာ tool တစ်ခုရဲ့ schema က တိတိကျကျ မှန်ရတယ်။ client က `cpu` ကို `int` အဖြစ် ပို့မလား ဆုံးဖြတ်တဲ့အခါ schema ကိုပဲ ကြည့်ပါတယ်။ type hints ကနေ schema ကို အလိုအလျောက် ယူတာမို့ function ရေးသူက ပြောင်းလိုက်ရင် schema လည်း လိုက်ပြောင်းသွားတယ်။ `../code/type_hints.py` နဲ့ `../code/lab_1_annotation_report.py` မှာ ဒီနည်းကို သုံးထားပါတယ်။

---

## အချက် ၂ — `Literal` သည် `str` ထက် သာသည်

### ဘာကို ဆိုလိုတာလဲ

parameter ကို `str` လို့ ရေးရင် ဘယ်စာသားမဆို ဝင်လို့ရသွားတယ်။ `Literal["small", "medium", "large"]` ဆိုတာကတော့ ရွေးချယ်စရာ သုံးခုထဲကမှ တစ်ခုပဲ လက်ခံမယ်လို့ ကြေညာချက်ထဲ ရောက်နေတဲ့ နည်းလေးပါ။ မှန်တဲ့ အဆင့်မှာပဲ ဖမ်းပေးနိုင်တာက သူ့အားသာချက်ပါ။

### ဘာကြောင့် လဲ

`"smal"` လို့ ရိုက်မှားတဲ့ input တစ်ခုက `str` parameter ထဲ အလွယ်တကူ ဝင်သွားတယ်။ ပြီးရင် အလုပ်ချိန်နောက်ကျမှ ပျက်တယ်။ `Literal` နဲ့ ရေးရင်တော့ schema ထဲမှာဖြစ်စေ validation မှာဖြစ်စေ အမှားကို ချက်ချင်း ဖမ်းနိုင်တယ်။ အရေးကြီးဆုံးက client UI အများစုက schema ထဲက enum ကို မြင်ရင် dropdown အဖြစ် ပြပေးတတ်တာပါ — အသုံးပြုသူ အမှားရိုက်ဖို့ အခွင့်အလမ်းပင် မရှိတော့ဘူး။

### ဘယ်လို အလုပ်လုပ်လဲ

`Literal` ကို `typing` ကနေ import လုပ်ပြီး parameter မှာ တွဲသုံးရတယ်။ ခွင့်ပြုတဲ့ တန်ဖိုးတွေကို Python code တစ်ခုတည်းမှာ ကြေညာထားတာမို့ schema နဲ့ validation နှစ်ခုလုံး တူနေတယ်။ သတိထားရန်ကတော့ အလိုအလျောက်မရှိဘဲ runtime မှာ ပြောင်းချင်တဲ့ တန်ဖိုးစုတွေမှာ `Literal` ကို တိုက်ရိုက် မသုံးသင့်တာပါ — အဲ့ဒါဆို သီးခြား enum-style validator တစ်ခု ရေးရတယ်။

၁။ `typing` ကနေ `Literal` ကို import လုပ်ပါတယ်။
၂။ parameter မှာ `Literal["small", "medium", "large"]` ဆိုပြီး ခွင့်ပြုတဲ့ တန်ဖိုးတွေ ရေးပါတယ်။
၃။ FastMCP က type hint ကနေ schema ထဲ အဲ့ဒီတန်ဖိုးတွေကို ထည့်ပေးတယ်။
၄။ client က မှားတဲ့ တန်ဖိုး ပို့လာရင် schema အဆင့်မှာပဲ ပြန်ပစ်တယ်။
၅။ တန်ဖိုးတွေ ပြောင်းချင်ရင် code ထဲက ကြေညာချက်တစ်ခုတည်းကိုပဲ ပြင်ရတယ်။

### ဥပမာ

ဒီ snippet မှာ `Literal` ကို parameter မှာ သုံးထားပုံကို ပြထားတယ်။ ခွင့်ပြုတဲ့ တန်ဖိုးထဲက မဟုတ်တာ ပို့လာရင် ဘယ်အဆင့်မှာ ဖမ်းမလဲဆိုတာကို သတိထားကြည့်ပါ။
```python
from typing import Literal

Size = Literal["small", "medium", "large"]

def resize(vm_id: str, size: Size) -> dict:
    # By the time we get here, size is guaranteed valid
    return {"vm": vm_id, "size": size}

# A wrong value never reaches the function body
try:
    resize("vm-01", "smal")
except Exception as exc:
    print(type(exc).__name__)

# Expected output:
# ValidationError (from Pydantic) -- the typo is caught at the boundary
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

MCP tool တစ်ခုက ကွန်ပျူတာမှာ အန္တရာယ်ရှိတဲ့ အလုပ်တွေ လုပ်တတ်ပါတယ် — instance ပြောင်းတာ၊ ပိတ်တာ စတဲ့ အလုပ်တွေပေါ့။ ဒါကြောင့် မှားတဲ့ တန်ဖိုးတစ်ခု အဝင်မှာ ရောက်လာရင် တားဆီးဖို့ လိုပါတယ်။ `Literal` က အဝင်ကို ကန့်သတ်ပေးတဲ့အတွက် ဒီနေရာမှာ အတော်ကို သင့်တော်ပါတယ်။ `../code/lab_2_literal_contract.py` မှာ `str` နဲ့ `Literal` ရဲ့ ကွာခြားချက်ကို တိုက်ယှဉ်ပြထားပါတယ်။

---

## အချက် ၃ — `inspect` ဖြင့် Function ကို Object ကဲ့သို့ ဖတ်ခြင်း

### ဘာကို ဆိုလိုတာလဲ

`inspect` module ဆိုတာ — function တစ်ခုရဲ့ အချက်အလက်တွေကို ဖတ်နိုင်အောင် ပြောင်းပေးတဲ့ Python မော်ဂျူးပါ။ parameter နာမည်တွေ၊ default တန်ဖိုးတွေ၊ annotation တွေကို structured object အဖြစ် ထုတ်ပေးတယ်။ စာအုပ်တစ်အုပ်ရဲ့ အညွှန်း စာမျက်နှာကို ဖွင့်ပြီး ကြည့်သလိုမျိုးပေါ့။ `__annotations__` တစ်ခုတည်းနဲ့ မလုံလောက်ပါဘူး။ default ရှိ/မရှိ၊ positional/keyword ကွာခြားချက်တွေကိုတော့ `inspect.signature()` က ရယူပေးပါတယ်။

### ဘာကြောင့် လဲ

JSON Schema တစ်ခုမှာ `required` list က အရေးကြီးဆုံး အပိုင်းပါ။ default တန်ဖိုး မရှိတဲ့ parameter တွေပဲ required ဖြစ်ပါတယ်။ ဒါကို parameter တစ်ခုချင်းစီရဲ့ default ကို စစ်မှသာ သိနိုင်ပါတယ်။ ဒါကြောင့် `inspect` ကို နားလည်ဖို့ လိုအပ်တာပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ `inspect.signature(func)` ကို ခေါ်ပါတယ်။ အဲဒီက `Signature` object တစ်ခု ပြန်လာပါတယ်။
၂။ အဲ့ဒီ object ရဲ့ `.parameters` ကနေ `Parameter` object တွေ ရပါတယ်။
၃။ "default မရှိဘူး" လို့ စစ်ရင် `None` နဲ့ နှိုင်းယှဉ်တာ မှားပါတယ် — default အဖြစ် `None` ထားထားတဲ့ parameter နဲ့ ရှုပ်သွားနိုင်လို့ပါ။
၄။ မှန်ကန်တဲ့ နည်းက `param.default is inspect.Parameter.empty` နဲ့ စစ်တာပါ။
၅။ Docstring အတွက် `inspect.getdoc()` က indentation ကို သန့်ရှင်းပေးလို့ `__doc__` ထက် ပိုအသုံးဝင်ပါတယ်။

### ဥပမာ

ဒီ snippet မှာ `inspect.signature()` နဲ့ parameter တစ်ခုချင်းစီကို ဖတ်ပြထားတာ ဖြစ်ပါတယ်။ default ရှိ/မရှိ စစ်တဲ့ `inspect.Parameter.empty` နဲ့ နှိုင်းယှဉ်တဲ့ပုံစံကို သတိထားကြည့်ပါ။
```python
import inspect

def provision(vm_name: str, cpu: int = 2, region: str | None = None):
    """Provision a VM."""
    ...

sig = inspect.signature(provision)
required = []
for name, param in sig.parameters.items():
    # Parameter.empty means "no default was written", i.e. required
    if param.default is inspect.Parameter.empty:
        required.append(name)

print(required)
print(sig.parameters["vm_name"].annotation)
print(inspect.getdoc(provision))

# Expected output:
# ['vm_name']
# <class 'str'>
# Provision a VM.
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

`../code/introspect.py` နဲ့ `../code/lab_3_signature_schema.py` မှာ `inspect` ကိုသုံးပြီး function တစ်ခုကနေ JSON Schema ကို ကိုယ်တိုင် ဆောက်ကြည့်ရတယ်။ ဒီလမ်းကြောင်းမှာ PEP 563 ရဲ့ trap ကိုပါ တွေ့ရတယ် — `from __future__ import annotations` ထည့်ထားရင် annotation အားလုံး string ဖြစ်သွားတယ်။ `get_type_hints()` မခေါ်ရင် schema ပျက်ပြီး LLM ဘက်ကို မှားတဲ့ tool info ရောက်သွားနိုင်တယ်။ ဒါပေမယ့် လက်ဖြင့်ဆောက်တဲ့ schema က description ကို မမြင်ဘူး။ docstring ကနေ ဆွဲထုတ်ဖို့ နောက်ထပ် ရေးရဦးမယ်။ ဒါကြောင့် production မှာ debug အချိန် ပိုကုန်တတ်ပါတယ်။

---

## အချက် ၄ — Pydantic `BaseModel` ဖြင့် ကြေညာချက်တစ်ခုတည်း

### ဘာကို ဆိုလိုတာလဲ

Pydantic ရဲ့ `BaseModel` ဆိုတာ — field တွေကို type နဲ့ `Field()` keyword နဲ့ ကြေညာရုံပဲ လိုတဲ့ class ပါ။ ကြေညာချက်တစ်ခုတည်းကနေ (၁) validation စစ်ဆေးမှု၊ (၂) JSON Schema ထုတ်ယူမှု နှစ်ခုလုံး တစ်ပြိုင်နက်ရတယ်။ form တစ်ခု ဖြည့်လိုက်ရင် စစ်ပေးလိုက်တာနဲ့ တန်းတူပါပဲ။

### ဘာကြောင့် လဲ

`Field()` ထဲမှာ `default`၊ `description`၊ `ge=`၊ `le=` ဆိုတဲ့ keyword တွေ ရှိပါတယ်။ ကိန်းဂဏန်း ကန့်သတ်ချက်ကို `ge=1` နဲ့ ကြေညာလိုက်ရုံနဲ့ validation နဲ့ schema နှစ်ခုလုံးမှာ အလိုအလျောက် ပါသွားတယ်။ ဒါကြောင့် `if cpu < 1: raise ...` လို လက်ဖြင့် စစ်ရော မလိုတော့ပါဘူး။ Required ဖြစ်စေချင်ရင် default မထည့်ရုံပဲ — ဒီသဘောကို သေချာ မှတ်ထားပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Class တစ်ခု ဆောက်ပါ။
၂။ input payload ကို class ထဲ လွှတ်လိုက်ပါ။
၃။ မှန်ရင် instance ရပါတယ်။
၄။ မှားရင် `ValidationError` ထွက်ပါတယ်။
၅။ Error ကို `exc.errors()` နဲ့ list အဖြစ် ဖတ်လို့ရပါတယ်။
၆။ အရေးကြီးဆုံး field က `loc` ပါ — error ဖြစ်တဲ့နေရာကို ပြပါတယ် (nested model ဖြစ်ရင် အလွှာများစွာ ရှိပါတယ်)။ `type` က error အမျိုးအစား၊ `input` က ထည့်လိုက်တဲ့ တန်ဖိုးပါ။

`ValidationError` က error တစ်ခုတည်းမဟုတ်ဘူး — မအောင်မြင်တဲ့ field အားလုံးကို တစ်ပြိုင်နက် စုပြပါတယ်။ ဒါကြောင့် အသုံးပြုသူထံ အချက်အလက် ပြည့်ပြည့်စုံစုံ ပြန်ပြောလို့ရပါတယ်။

### ကုဒ် ဥပမာ

ဒီ snippet မှာ `BaseModel` နဲ့ field ကြေညာပြီး validation ဘယ်လို အလုပ်လုပ်လဲ ကြည့်ရမယ်။ အထူးသဖြင့် `ValidationError` ရဲ့ `loc`၊ `type`၊ `input` က ဘယ်နေရာမှာ ဘာမှားနေလဲ ပြောပြပုံကို သတိထားကြည့်ပါ။
```python
from pydantic import BaseModel, Field, ValidationError


class ServerSpec(BaseModel):
    # Required field: no default means the caller must provide it
    name: str = Field(description="Human-readable server name")

    # Optional field with a default value
    environment: str = Field(default="dev", description="Deployment environment")

    # Numeric constraints applied to both validation and schema
    cpu: int = Field(ge=1, le=64, description="Number of CPU cores")
    memory_gb: int = Field(ge=1, le=512, description="Memory in gigabytes")


# Valid payload: returns an instance
spec = ServerSpec(name="web-01", cpu=4, memory_gb=16)
print(spec.model_dump())

# Invalid payload: raises ValidationError
try:
    ServerSpec(name="web-02", cpu=0, memory_gb=16)
except ValidationError as exc:
    for error in exc.errors():
        print(error["loc"], error["type"], error["input"])
```

### MCP တွင် အသုံးချနည်း

Pydantic model ဆိုတာ — data ပုံစံကို ကြေညာတဲ့ class လေးပါ။ FastMCP မှာ tool function ရဲ့ parameter အနေနဲ့ ဒီ model ကို တိုက်ရိုက် ထည့်လိုက်ရင် framework က အလိုအလျောက် input schema ထုတ်ပေးတယ်။ Schema ဆိုတာ — "ဒီ tool ကို ခေါ်ရင် ဘယ် data ပုံစံ ပို့ရမလဲ" ဆိုတဲ့ စာရွက်လေးပါ။

မထည့်ခင် အခြေအနေက — tool ထဲ လူက data မှားပို့လိုက်ရင် program ထဲမှာ အမှားတွေ ခဏခဏ ဖြစ်တတ်တယ်။ Model တစ်ခု ကြေညာထားရင် client ဘက်က လာတဲ့ payload ကို framework က အလိုအလျောက် စစ်ပေးတယ်။ Payload ဆိုတာ — client က server ဆီ ပို့လိုက်တဲ့ data အစုလေးပါ။ ဒါကြောင့် tool ထဲမှာ validation ကုဒ် တစ်ကြောင်းမျှ ရေးစရာ မလိုတော့ဘူး။ Business logic — ဆိုတာ tool ရဲ့ အဓိက အလုပ်ပိုင်း — အပေါ်ပဲ အာရုံစိုက်ရတယ်။ Model တစ်ခုတည်းကို tool၊ resource၊ အခြား model တွေမှာလည်း ပြန်သုံးလို့ရတဲ့အတွက် ကုဒ် ထပ်ရေးစရာ မရှိတော့ပါဘူး။

အလုပ်လုပ်ပုံက ဒီလိုပါ —
၁။ `BaseModel` ကို ဆင့်ပြီး data class လေး တစ်ခု ကြေညာတယ်။
၂။ `Field()` နဲ့ ကန့်သတ်ချက်တွေ (ဥပမာ `ge=`၊ `description`) ထည့်ပေးတယ်။
၃။ Tool function ရဲ့ parameter မှာ ဒီ model ကို အမျိုးအစား အနေနဲ့ ရေးတယ်။
၄။ FastMCP က ဒီ class ကို ဖတ်ပြီး JSON Schema အဖြစ် ပြောင်းပေးတယ်။
၅။ Client က data ပို့လာရင် အလိုအလျောက် စစ်ပြီးမှ tool ထဲ ဝင်ခွင့်ပေးတယ်။
၆။ Data မှားရင် tool ထဲ မဝင်ခင် `ValidationError` ပြနိုင်တယ်။

## အနှစ်ချုပ်

- `BaseModel` ကြေညာချက် တစ်ခုတည်းနဲ့ validation နဲ့ JSON Schema ထုတ်ခြင်း နှစ်ခုလုံး တစ်ပြိုင်နက် ရပါတယ်။
- `Field()` ရဲ့ keyword တွေ (`default`၊ `description`၊ `ge=`၊ `le=`) နဲ့ ကန့်သတ်ချက် ကြေညာရုံပဲ လိုပါတယ် — လက်ဖြင့် စစ်တဲ့ ကုဒ် ရေးစရာ မလိုတော့ပါဘူး။
- Required field — ဆိုတာ မထည့်လို့မရတဲ့ ကွက် — လုပ်ချင်ရင် default တန်ဖိုး မထည့်ရုံပဲ လိုပါတယ်။ ဒီစည်းမျဉ်း လေးကို သေချာ မှတ်ထားပါနော်။
- `ValidationError` ကို `exc.errors()` နဲ့ ဖတ်ရင် `loc`၊ `type`၊ `input` တွေကနေ အမှားရှိတဲ့ နေရာ၊ အမျိုးအစား၊ တန်ဖိုးကို တိကျစွာ သိရပါတယ်။

ဒါက လက်တွေ့မှာ အရေးကြီးပါတယ်။ Model မသုံးဘူးဆိုရင် data မှားတွေကို tool ထဲထိ ရောက်သွားပြီး နောက်မှ ပြဿနာရှာရတဲ့ debug အချိန် ကြာရပါတယ်။ Field ကန့်သတ်ချက် မထည့်ထားရင် client က မှားတဲ့ တန်ဖိုးနဲ့ ခေါ်လိုက်ရင် မှားတဲ့ tool အလုပ်လုပ်သွားပြီး data ပျက်စီးနိုင်ပါတယ်။ အချက်အလက်တွေ လုံခြုံဖို့လည်း ဒီ validation က ပထမတန်းကားလို အလုပ်လုပ်ပေးပါတယ်။