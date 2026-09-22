# M2 — Type Hints, Introspection & Pydantic (ရှင်းလင်းချက်)

M1 တွင် Python ပတ်ဝန်းကျင်ကို ပြင်ဆင်ခဲ့ပြီးဖြစ်သည်။ M2 တွင် MCP tool တစ်ခု၏ input schema ကို အလိုအလျောက် ထုတ်ယူနိုင်ရန် လိုအပ်သည့် အခြေခံ သုံးရပ်ကို သင်မည်ဖြစ်သည် — type hints၊ `inspect` module နှင့် Pydantic တို့ဖြစ်သည်။

---

## အချက် ၁ — Type Hints ဆိုတာ Data ဖြစ်သည်

### ဘာကို ဆိုလိုတာလဲ

Type hint ဆိုသည်မှာ comment သက်သက် မဟုတ်ပါ။ function တစ်ခုပေါ်တွင် ရေးထားသော `def provision(vm_name: str, cpu: int) -> dict:` ကဲ့သို့သော မှတ်စုများသည် runtime တွင် `__annotations__` attribute ထဲ အမှန်တကယ် သိမ်းဆည်းထားသော object များ ဖြစ်သည်။ ဆိုလိုသည်မှာ ကုဒ်ကို လူဖတ်နိုင်သလို စက်လည်း ဖတ်နိုင်သည် — schema generator တစ်ခု ရေးနိုင်ရန် အခြေခံ အုတ်မြစ် ဖြစ်သည်။

### ဘာကြောင့် လဲ

MCP server တစ်ခုက tool တစ်ခုကို client ထံ ကြေညာရာတွင် JSON Schema ပုံစံဖြင့် ပြောကြားရသည်။ parameter အမည်၊ အမျိုးအစား၊ မဖြစ်မနေ လိုအပ်ချက်တို့ကို function ကိုယ်တိုင်မှ ထုတ်ယူနိုင်ပါက schema ကို လက်ဖြင့် နှစ်ကြိမ်ရေးစရာ မလိုတော့ပါ။ ကြေညာချက်တစ်ခုတည်းနှင့် ရပါမည်။ သို့မဟုတ်လျှင် function ရေးထားသော type နှင့် schema ထဲ ရေးထားသော type ကွဲလွဲသွားမည် — ဒီကိစ္စကို M2 နှောင်းပိုင်းတွင် "drift" ဟုခေါ်မည်ဖြစ်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

Function ပေါ်ရှိ `__annotations__` dict ကို တိုက်ရိုက် ဖတ်နိုင်သည်။ သို့သော် `from __future__ import annotations` ကို သုံးထားပါက hint အားလုံးသည် string ဖြစ်နေမည် — ထို့ကြောင့် `typing.get_type_hints()` ကို သုံး၍ string များကို တကယ့် type object များအဖြစ် ပြန်ပြောင်းရသည်။ ထို့နောက် `typing.get_origin()` နှင့် `typing.get_args()` ဖြင့် generic type များကို ခွဲခြမ်းစိတ်ဖြာ ဖတ်နိုင်သည် — ဥပမာ `list[dict[str, int]]` ကို ထပ်ခါထပ်ခါ ဖတ်ရန် recursive reader လိုအပ်သည်။

### ဥပမာ

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

MCP တွင် tool တစ်ခု၏ schema သည် လုံးဝ မှန်ရန် လိုသည်။ client က `cpu` ကို `int` အဖြစ် ပို့မည်လား ဆုံးဖြတ်သည့်အခါ schema ကိုသာ ကြည့်သည်။ type hints မှ ထုတ်ယူလျှင် function ရေးသူ ပြောင်းလိုက်သည်နှင့် schema လည်း အလိုအလျောက် လိုက်ပြောင်းမည်။ `../code/type_hints.py` နှင့် `../code/lab_1_annotation_report.py` တွင် ဒီနည်းလမ်းကို အသုံးပြုထားသည်။

---

## အချက် ၂ — `Literal` သည် `str` ထက် သာသည်

### ဘာကို ဆိုလိုတာလဲ

`str` ကို parameter အဖြစ် သုံးပါက client ဘက်မှ မည်သည့် စာသားမဆို လက်ခံရမည်ဖြစ်သည်။ `Literal["small", "medium", "large"]` ကို သုံးပါက ရွေးချယ်နိုင်သော တန်ဖိုး သုံးခုတွင် တစ်ခုခုသာ ခွင့်ပြုသည်ဟု ကြေညာချက်တွင်း ထည့်သွင်းနိုင်သည်။

### ဘာကြောင့် လဲ

`"smal"` ဟု ရိုက်မှားသော input တစ်ခုသည် `str` parameter တွင် အလွယ်တကူ လက်ခံခံရပြီး အလုပ်ချိန်နှောင်းမှ ပျက်စီးသွားမည်။ `Literal` ဖြင့် ရေးထားပါက schema ထဲ ဖြစ်စေ၊ validation အဆင့်ဖြစ်စေ အမှားကို ချက်ချင်း ဖမ်းနိုင်သည်။ အရေးအကြီးဆုံးမှာ client UI များစွာက schema ထဲရှိ enum ကို မြင်သည်နှင့် dropdown တစ်ခုအဖြစ် ပြသပေးလေ့ရှိသည် — အသုံးပြုသူ အမှားရိုက်စရာ အခွင့်အလမ်းပင် မရှိတော့ပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

`Literal` ကို `typing` မှ import လုပ်၍ parameter တွင် တွဲသုံးရသည်။ ခွင့်ပြုတန်ဖိုးများကို Python object တွင် ကြေညာပြီးနောက် အဲဒီတန်ဖိုးများကိုပင် validation တွင် အသုံးပြုသောကြောင့် နှစ်ခု ကွဲလွဲစရာ မရှိပါ။ သတိပြုရန်မှာ dynamic အားဖြင့် ပြောင်းလဲနိုင်သော တန်ဖိုးစုများအတွက် `Literal` ကို တိုက်ရိုက် မသုံးသင့်ချေ — အဲဒီအခါမျိုးတွင် သီးခြား enum-style validator တစ်ခု ရေးရမည်။

### ဥပမာ

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

MCP tool တစ်ခုသည် ကွန်ပျူတာတစ်လုံး လုပ်ဆောင်စေသော အန္တရာယ်ရှိသော လုပ်ဆောင်ချက်များ ဖြစ်တတ်သည် — instance ပြောင်းခြင်း၊ ပိတ်ခြင်းစသည်။ မှားယွင်းသော တန်ဖိုးတစ်ခု အလယ်တန်းခုတ်ကြောင်း မရောက်ရေအောင် အဝင်ဝတွင် တားဆီးရန် `Literal` သည် အလွန် သင့်တော်သည်။ `../code/lab_2_literal_contract.py` တွင် `str` နှင့် `Literal` ကို တိုက်စစ်ထားသည်။

---

## အချက် ၃ — `inspect` ဖြင့် Function ကို Object ကဲ့သို့ ဖတ်ခြင်း

### ဘာကို ဆိုလိုတာလဲ

`inspect` module သည် function တစ်ခု၏ signature — parameter အမည်များ၊ default တန်ဖိုးများ၊ annotation များ — ကို structured object များအဖြစ် ထုတ်ပေးသည်။ `__annotations__` တစ်ခုတည်းနှင့် မလုံလောက်သောအခါ default ရှိ/မရှိ၊ positional/keyword ကွဲပြားချက်တို့ကို `inspect.signature()` မှ ရယူနိုင်သည်။

### ဘာကြောင့် လဲ

JSON Schema တစ်ခုတွင် `required` list သည် အရေးကြီးသော အပိုင်း ဖြစ်သည်။ default တန်ဖိုး မရှိသော parameter များသာ required ဖြစ်သည်။ ဒီအချက်ကို parameter တစ်ခုချင်းစီ၏ default ကို စစ်ဆေးမှသာ သိနိုင်သည် — ထို့ကြောင့် `inspect` ကို သေချာ နားလည်ရန် လိုသည်။

### ဘယ်လို အလုပ်လုပ်လဲ

`inspect.signature(func)` သည် `Signature` object တစ်ခု ပြန်သည်။ ထို object ၏ `.parameters` မှ `Parameter` object များကို ရရှိသည်။ သတိထားရန်မှာ "default မရှိ" ကို စစ်ရာတွင် `None` နှင့် နှိုင်းယှဉ်၍ မရပါ — default အဖြစ် `None` ထားထားသော parameter နှင့် ရှုပ်ထွေးမည်ဖြစ်သည်။ မှန်ကန်သည့် နည်းမှာ `param.default is inspect.Parameter.empty` ဖြင့် စစ်ဆေးရန် ဖြစ်သည်။ Docstring အတွက် `inspect.getdoc()` သည် indentation ကို သန့်ရှင်းပေးသောကြောင့် `__doc__` ထက် ပိုအသုံးဝင်သည်။

### ဥပမာ

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

`../code/introspect.py` နှင့် `../code/lab_3_signature_schema.py` တွင် `inspect` ကို အသုံးပြု၍ function တစ်ခုမှ JSON Schema ကို ကိုယ်တိုင် ဆောက်သည်။ ဒီလမ်းကြောင်းအတွင်း PEP 563 ၏ trap ကိုလည်း တွေ့မည် — `from __future__ import annotations` သုံးထားပါက annotation များ အားလုံး string ဖြစ်နေပြီး `get_type_hints()` မခေါ်ပါက schema ပျက်သွားမည်။ ထို့အပြင် လက်ဖြင့် ဆောက်သော schema သည် description ကို မမြင်နိုင် — docstring မှ ဆွဲထုတ်ရန် ထပ်ဆောင်း လုပ်ဆောင်ချက် လိုသည်။

---

## အချက် ၄ — Pydantic `BaseModel` ဖြင့် ကြေညာချက်တစ်ခုတည်း

### ဘာကို ဆိုလိုတာလဲ

Pydantic ၏ `BaseModel` သည် field များကို type နှင့် `Field()` keyword များဖြင့် ကြေညာရုံသာ လိုသော class ဖြစ်သည်။ ထိုကြေညာချက်တစ်ခုတည်းမှ — (၁) validation စစ်ဆေးမှု၊ (၂) JSON Schema ထုတ်ယူမှု နှစ်ခုလုံးကို ရရှိသည်။

### ဘာကြောင့် လဲ

`Field()` တွင် `default`၊ `description`၊ `ge=`၊ `le=` ကဲ့သို့သော keyword များ ရှိသည်။ ကိန်းဂဏန်း ကန့်သတ်ချက်ကို `ge=1` ဖြင့် ကြေညာရုံနှင့် validation နှင့် schema နှစ်ခုလုံးတွင် အလိုအလျောက် ပါဝင်သွားမည် — `if cpu < 1: raise ...` ကဲ့သို့ လက်ဖြင့် စစ်ဆေးရန် မလိုတော့ပါ။ Required ဖြစ်စေရန်မှာ default မထည့်ရုံသာ လိုသည် — ဒီသဘောတရားကို သေချာ မှတ်ယူရမည်။

### ဘယ်လို အလုပ်လုပ်လဲ

Class ကို ဆောက်ပြီး input payload ကို class ထဲ လွှတ်လိုက်ပါက မှန်ကန်ပါက instance ရရှိမည်၊ မှားပါက `ValidationError` ထွက်မည်။ Error ကို `exc.errors()` ဖြင့် list အဖြစ် ဖတ်နိုင်သည် — အရေးကြီးဆုံး field မှာ `loc` ဖြစ်ပြီး error ဖြစ်သည့် နေရာကို လမ်းညွှန်သည် (nested model ဖြစ်ပါက အလွှာများစွာ ရှိမည်)၊ `type` က error အမျိုးအစားကို ဖော်ပြသည်၊ `input` က ထည့်လိုက်သော တန်ဖိုးဖြစ်သည်။ `ValidationError` သည် error တစ်ခုတည်း အစား စစ်ဆေးမှု မအောင်မြင်သည့် field အားလုံးကို တစ်ပြိုင်နက် စုဆောင်းပြီး ပြသသောကြောင့် အသုံးပြုသူထံ အချက်အလက် ပြည့်စုံစွာ ပြန်လည် အကြောင်းကြားနိုင်သည်။

### ကုဒ် ဥပမာ

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

FastMCP တွင် tool function ၏ parameter အဖြစ် Pydantic model တစ်ခုကို တိုက်ရိုက် ထည့်ပါက framework သည် အလိုအလျောက် input schema ထုတ်ပေးပြီး client မှ လာသော payload ကိုလည်း စစ်ဆေးပေးသည်။ ထို့ကြောင့် tool အတွင်းဘက်တွင် validation ကုဒ် တစ်ကြောင်းမျှ ရေးစရာ မလိုတော့ဘဲ business logic အပေါ်တွင်သာ အာရုံ စိုက်နိုင်သည်။ Model တစ်ခု ကြေညာပြီးပါက ထို model ကို tool၊ resource၊ အခြား model တို့တွင် ပြန်သုံးနိုင်သောကြောင့် ကုဒ် ထပ်ဆင့်ရေးခြင်းမှ ကာကွယ်ပေးသည်။

## အနှစ်ချုပ်

- Pydantic ၏ `BaseModel` ကြေညာချက် တစ်ခုတည်းမှ validation နှင့် JSON Schema ထုတ်ယူမှု နှစ်ခုလုံးကို တစ်ပြိုင်နက် ရရှိသည်။
- `Field()` ၏ keyword များ (`default`၊ `description`၊ `ge=`၊ `le=`) ဖြင့် ကန့်သတ်ချက်များကို ကြေညာရုံသာ လိုပြီး လက်ဖြင့် စစ်ဆေးသော ကုဒ် ရေးရန် မလိုတော့ပါ။
- Required field အဖြစ် သတ်မှတ်လိုပါက default တန်ဖိုး မထည့်ရုံသာ လိုသည် — ဒီစည်းမျဉ်းကို သေချာ မှတ်ယူပါ။
- `ValidationError` ကို `exc.errors()` ဖြင့် ဖတ်ပါက `loc`၊ `type`၊ `input` တို့မှ အမှားရှိနေသည့် နေရာ၊ အမျိုးအစား၊ တန်ဖိုးတို့ကို တိကျစွာ သိနိုင်သည်။
