# အဖြေများ — Action-Oriented Tools (`@mcp.tool`)

## လေ့ကျင့်ခန်း ၁ — Calculator Server ထဲသို့ Tool အသစ် ထည့်သွင်းခြင်း

Calculator server ထဲသို့ `divide` tool အသစ်ကို ထည့်သွင်းရန် အောက်ပါအတိုင်း ရေးသားနိုင်ပါသည်။ Tool ၏ အမည်ကို verb-first စနစ်ဖြင့် စတင်ပြီး docstring ထဲတွင် summary နှင့် `Args:` section ကို ပါဝင်စေရမည်ဖြစ်သည်။ ထို့အပြင် parameter တိုင်းအတွက် type annotation နှင့် return annotation အပြည့်အစုံ ထည့်သွင်းရမည်ဖြစ်ပြီး `@mcp.tool()` decorator ကို မမေ့ဘဲ ထည့်ပေးရန် လိုအပ်ပါသည်။ ထိုသို့ရေးသားခြင်းအားဖြင့် `mcp` object တွင် tool အသစ် ပေါ်လာမည်ဖြစ်ပြီး schema ထဲတွင်လည်း description များ အလိုအလျောက် ပါဝင်သွားမည် ဖြစ်သည်။

``python
# divide_tool.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Calculator")

@mcp.tool()
def divide(dividend: float, divisor: float) -> float:
    """Divide the dividend by the divisor and return the result.

    Args:
        dividend: The number to be divided.
        divisor: The number to divide by. Must not be zero.
    """
    if divisor == 0:
        raise ValueError("divisor must not be zero")
    return dividend / divisor

if __name__ == "__main__":
    mcp.run()
``

**အဓိကအယူအဆ** — စံချိန်မီ tool တစ်ခုဆိုသည်မှာ verb-first အမည်၊ summary နှင့် `Args:` ပါဝင်သော docstring၊ type annotations နှင့် return annotation အပြည့်အစုံ ပါဝင်ပြီး `@mcp.tool()` decorator ဖြင့် မှတ်ပုံတင်ထားသော function ဖြစ်သည်။

## လေ့ကျင့်ခန်း ၂ — Docstring ပုံစံ ၃ မျိုးကို တိုင်းတာခြင်း

Docstring သည် function ၏ description အဖြစ် JSON Schema ထဲသို့ ရောက်သွားသည်။ ဤလေ့ကျင့်ခန်းတွင် docstring လုံးဝမပါဝင်သော version၊ summary သာပါဝင်သော version နှင့် `Args:` section ပါဝင်သော version ဟူ၍ ၃ မျိုးကို တိုက်ရိုက် `Tool.from_function()` ဖြင့် ဖန်တီးကာ schema ကွာခြားချက်ကို လေ့လာပါမည်။

``python
# lab_8_docstring_contract.py
# Compare how three docstring styles produce different JSON Schemas.

import json
from mcp.server.fastmcp import Tool


# Version 1: no docstring at all
def multiply_plain(a: int, b: int) -> int:
    return a * b


# Version 2: summary line only
def multiply_summary(a: int, b: int) -> int:
    """Multiply two integers and return the product."""
    return a * b


# Version 3: summary plus Args: section
def multiply_args(a: int, b: int) -> int:
    """Multiply two integers and return the product.

    Args:
        a: The first integer factor.
        b: The second integer factor.
    """
    return a * b


def show_schema(label: str, func) -> None:
    # Build a Tool directly from the function and print its schema
    tool = Tool.from_function(func)
    print(f"\n=== {label} ===")
    print(json.dumps(tool.parameters, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    show_schema("Version 1 — no docstring", multiply_plain)
    show_schema("Version 2 — summary only", multiply_summary)
    show_schema("Version 3 — summary + Args:", multiply_args)
``

Version 1 နှင့် Version 2 တို့တွင် schema အတွင်း `"description"` field လုံးဝမပါဘဲ `a` နှင့် `b` parameter များသည် `type: "integer"` သာဖြစ်သည်။ Version 3 ၌သာ tool-level description အပြင် parameter တစ်ခုချင်းစီ၏ `description` များ ပါဝင်သည်ကို မြင်ရမည်ဖြစ်သည်။

**အဓိကအယူအဆ** — docstring တွင် `Args:` section ထည့်သွင်းသည်နှင့် JSON Schema ၌ parameter description များ ပါလာပြီး client များအတွက် ခေါ်ယူရန် ပိုမှုတိမ်မိုးလာစေသည်။

## လေ့ကျင့်ခန်း ၃ — Error Taxonomy ကို တိုင်းတာခြင်း

ဒီလေ့ကျင့်ခန်းမှာ error အမျိုးအစားနှစ်မျိုးကို ကွဲပြားစွာ ကိုင်တွယ်တာ လေ့လာရမှာ ဖြစ်ပါတယ်။ Bad REQUEST ဆိုတာက client က parameter မှားပို့လာတာမျိုး၊ ဥပမာ — နံပါတ်မဟုတ်တဲ့ string ပို့လာတာ — ဖြစ်ပြီး၊ ဒီလိုအခြေအနေမှာ MCP protocol အရ `isError=True` ဖြစ်တဲ့ error response ပြန်ဖို့ သင့်တော်ပါတယ်။ တစ်ဖက်မှာ Bad SITUATION ကတော့ request က မှန်ပေမယ့် အခြေအနေက မည့်မည် မဟုတ်တာ — ဥပမာ သုညနဲ့ စားခြင်း — ဖြစ်ပြီး၊ ဒါက tool ရဲ့ သဘာဝအရ ဖြစ်နိုင်တဲ့ ရလဒ်တစ်ခုဖြစ်လို့ structured data အနေနဲ့ ပြန်ဖို့ ပိုသင့်တော်ပါတယ်။ အောက်မှာ `_ok()` / `_fail()` helper နှစ်ခုနဲ့ စံချိန်မီ error code သုံးထားတဲ့ `calculator.py` စတိုင်ဖိုင်ကို ကြည့်ပါ။

``python
"""
Lab 1: Error Taxonomy — distinguishing Bad REQUEST from Bad SITUATION.
Server file: lab_1_error_taxonomy.py
Run: python lab_1_error_taxonomy.py
"""

import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("error-taxonomy")

mcp = FastMCP("ErrorTaxonomy")


# Standard error codes shared across all tools in this lab
ERR_NOT_A_NUMBER = "ERR_NOT_A_NUMBER"
ERR_DIVISION_BY_ZERO = "ERR_DIVISION_BY_ZERO"

# Helper: wrap a successful result in structured data
def _ok(data: Any) -> dict:
    return {"ok": True, "data": data}

# Helper: wrap a failure reason in structured data
def _fail(code: str, message: str) -> dict:
    return {"ok": False, "code": code, "message": message}


@mcp.tool()
def safe_divide(a: Any, b: Any) -> dict:
    """Divide a by b, distinguishing bad requests from bad situations.

    Bad REQUEST (wrong parameter type) -> raises ValueError,
    which FastMCP converts into isError=True response.
    Bad SITUATION (division by zero) -> returns structured data
    via _fail(), not an exception.
    """
    # --- Bad REQUEST check: parameters must be numbers ---
    # Letting the bad input reach `float()` raises naturally,
    # producing an isError=True result with the ValueError message.
    try:
        na = float(a)
        nb = float(b)
    except (TypeError, ValueError):
        # This is the caller's fault: wrong parameter type.
        # Raise so MCP reports isError=True for the request itself.
        raise ValueError(
            f"Both 'a' and 'b' must be numbers, got a={a!r}, b={b!r}"
        )

    # --- Bad SITUATION check: the situation is invalid ---
    if nb == 0.0:
        # The request is fine; the math situation is impossible.
        # Return structured data instead of raising an exception.
        return _fail(ERR_DIVISION_BY_ZERO, "Cannot divide by zero.")

    return _ok(na / nb)


if __name__ == "__main__":
    mcp.run()
``

Client ဘက်ကနေ စမ်းကြည့်တဲ့အခါ `raise_on_error=False` ထားပြီး `isError` flag နဲ့ structured result နှစ်ခုစလုံးကို စစ်နိုင်ပါတယ် — Bad REQUEST အတွက် `isError=True` ဖြင့် error message ပြန်လာပြီး၊ Bad SITUATION အတွက် `isError=False` ဖြင့် `{"ok": false, "code": "ERR_DIVISION_BY_ZERO", ...}` ဆိုတဲ့ structured data ပြန်လာမှာ ဖြစ်ပါတယ်။ အရေးကြီးတဲ့အချက်က tool function ထဲမှာ unhandled exception များ မဖြစ်စေရန် အမြဲတစ်စိတ်တစ်ဒေသန် စိတ်ရှုံ့ထားရမှာ ဖြစ်ပါတယ်။

**အဓိကအယူအဆ** — Bad REQUEST ကို `isError=True` ဖြင့် exception အသွင်ပြန်ပြီး Bad SITUATION ကို `_fail()` helper ဖြင့် structured data အဖြစ်ပြန်ခြင်းဖြင့် error နှစ်မျိုးကို တိကျစွာ ကွဲပြားစေရမည်။

## လေ့ကျင့်ခန်း ၄ — Hint မပါဝင်မှု၏ ကုန်ကျစရိတ်

ဤလေ့ကျင့်ခန်းတွင် hint ပါဝင်သော error message နှင့် hint မပါဝင်သော error message တို့၏ ကွာခြားမှုကို လက်တွေ့စမ်းသပ်ကြည့်ပါမည်။ LLM တစ်ခုသည် "Unknown function" ဟူသော message ကိုသာ ရရှိပါက ထို error ကို ပြင်ရန် ထပ်မံ မေးခွန်း ထုတ်ရန် လိုအပ်သည်။ သို့သော် "ဘာမှားသည်၊ ဘာလို့မှားသည်၊ ဘယ်လိုပြင်ရမည်၊ ဥပမာနှင့် retry ရမလား" ပါဝင်ပါက ချက်ချင်း ဆက်လက် အလုပ်လုပ်နိုင်သည်။

``python
"""
lab_2_hint_contract.py — Compare errors with and without hints.

Hint message contract must answer:
  1. What went wrong
  2. Why it went wrong
  3. How to fix it
  4. A working example
  5. Whether a retry makes sense
"""

from difflib import get_close_matches


class CalculatorError(Exception):
    """Base error for calculator tool failures."""

    def __init__(self, message, *, hint=None, retryable=None):
        super().__init__(message)
        self.message = message
        self.hint = hint
        self.retryable = retryable  # True = retry makes sense, False = permanent


# Registry of supported calculator operations
_OPERATIONS = {
    "add": lambda a, b: a + b,
    "subtract": lambda a, b: a - b,
    "multiply": lambda a, b: a * b,
    "divide": lambda a, b: a / b,
}


def _closest(bad_name, candidates):
    """Heuristic: find the closest valid name to suggest in the hint."""
    matches = get_close_matches(bad_name, candidates, n=1, cutoff=0.4)
    return matches[0] if matches else None


def calculate(operation, a, b):
    """Like an @mcp.tool: validate inputs, raise rich errors on failure."""
    if operation not in _OPERATIONS:
        closest = _closest(operation, _OPERATIONS.keys())
        if closest:
            # ERROR WITH HINT — full contract: what, why, how, example, retry
            raise CalculatorError(
                f"Unknown operation: '{operation}'.",
                hint=(
                    f"What: operation '{operation}' does not exist. "
                    f"Why: the tool only accepts one of {sorted(_OPERATIONS)}. "
                    f"How to fix: call calculate with operation='{closest}'. "
                    f"Example: calculate('{closest}', 2, 3) -> "
                    f"{_OPERATIONS[closest](2, 3)}. "
                    f"Retryable: yes — fix the name and call again."
                ),
                retryable=True,
            )
        # Unknown name with no close match — still give direction
        raise CalculatorError(
            f"Unknown operation: '{operation}'.",
            hint=(
                f"Valid operations are {sorted(_OPERATIONS)}. "
                f"Example: calculate('add', 2, 3) -> 5. "
                f"Retryable: yes — use a valid operation name."
            ),
            retryable=True,
        )
    if operation == "divide" and b == 0:
        # Permanent failure — retrying the same call will never work
        raise CalculatorError(
            "Division by zero.",
            hint=(
                "What: attempted to divide by zero. "
                "Why: math does not allow a / 0. "
                "How to fix: change b to a non-zero value, or check with "
                "the caller first. Example: calculate('divide', 10, 2) -> 5.0. "
                "Retryable: no — the same inputs will always fail; "
                "the caller must change b."
            ),
            retryable=False,
        )
    return _OPERATIONS[operation](a, b)


def main():
    # Case 1: error WITHOUT hint (what a bare raise looks like)
    print("=== Error WITHOUT hint ===")
    try:
        calculate("mulitply", 4, 5)  # typo on purpose
    except CalculatorError as e:
        # A model receiving only this must ask a follow-up question
        print(f"message : {e.message}")
        print(f"hint    : {e.hint}")
        print("-> model must ask a follow-up: cost of extra round trips\n")

    # Case 2: error WITH hint (full contract)
    print("=== Error WITH hint ===")
    try:
        calculate("mulitply", 4, 5)
    except CalculatorError as e:
        print(f"message : {e.message}")
        print(f"hint    : {e.hint}")
        print(f"retryable: {e.retryable}\n")
        # Model can self-correct immediately, no follow-up needed
        corrected = calculate("multiply", 4, 5)
        print(f"corrected call -> multiply(4, 5) = {corrected}\n")

    # Case 3: permanent error — retry does NOT make sense
    print("=== Permanent error (not retryable) ===")
    try:
        calculate("divide", 10, 0)
    except CalculatorError as e:
        print(f"message  : {e.message}")
        print(f"hint     : {e.hint}")
        print(f"retryable: {e.retryable}")


if __name__ == "__main__":
    main()
``

**အဓိကအယူအဆ** — Hint ထဲတွင် "ဘာမှား၊ ဘာလို့၊ ဘယ်လိုပြင်၊ ဥပမာ၊ retry ရမလား" ဆိုသော အချက်ငါးချက် ပါဝင်ပါက model သည် ထပ်မံ မေးခွန်း ထုတ်ရန် မလိုဘဲ error ကို ချက်ချင်း ပြင်၍ တန်ဖိုးကို ဆက်လက် တွက်နိုင်သည်။

## လေ့ကျင့်ခန်း ၅ — Validation Gate ကို ထိုးဖောက်စမ်းသပ်ခြင်း

ဤလေ့ကျင့်ခန်းတွင် request ၁၂ မျိုးကို `@mcp.tool` သို့ တိုက်ရိုက်ပို့ကာ Pydantic က ဖမ်းဆုပ်သော error နှင့် ကျွန်ုပ်တို့ ကိုယ်တိုင် စစ်ဆေးရမည့် domain rule ကိစ္စကို ခွဲခြားမှတ်တမ်းတင်ပါမည်။ Type မှားယွင်းမှုများသည် tool function အတွင်း လုံးဝ မရောက်ကြောင်း၊ function အတွင်း ရောက်လာပြီးသားဆိုလျှင် domain validation ကို ကိုယ်ပိုင် logic ဖြင့် စစ်ရမည်ကို အတည်ပြုနိုင်ပါသည်။

``python
# lab_3_validate_the_boundary.py
# Send 12 edge-case requests and record which layer rejects each one.
# Pydantic catches type errors BEFORE the function body runs;
# domain rules (e.g. "must be greater than zero") must be checked by us.

import json

# Simulated MCP tool registry: schema mirrors calculator.py style files
TOOL_SCHEMA = {
    "divide": {
        "dividend": "float",
        "divisor": "float",
    },
    "repeat_text": {
        "text": "string",
        "times": "integer",
    },
}


def pydantic_gate(tool_name: str, arguments: dict) -> dict:
    # Layer 1: Pydantic-style type validation (runs before the tool body)
    schema = TOOL_SCHEMA[tool_name]
    for key, expected in schema.items():
        if key not in arguments:
            return {"layer": "pydantic", "error": f"missing field: {key}"}
        value = arguments[key]
        if expected == "float" and not isinstance(value, (int, float)):
            return {"layer": "pydantic", "error": f"type error on {key}: expected number"}
        if expected == "string" and not isinstance(value, str):
            return {"layer": "pydantic", "error": f"type error on {key}: expected string"}
        if expected == "integer" and not isinstance(value, int):
            return {"layer": "pydantic", "error": f"type error on {key}: expected integer"}
    # Passed the gate: function body will now execute
    return {"layer": "function", "error": None}


def divide_tool(dividend: float, divisor: float) -> dict:
    # Domain rule: divisor must be greater than zero (checked by us, code 4004)
    if divisor <= 0:
        return {"status": "error", "code": 4004, "message": "divisor must be greater than zero"}
    return {"status": "ok", "code": 200, "result": dividend / divisor}


def repeat_text_tool(text: str, times: int) -> dict:
    # Domain rule: string must be at least 3 chars, times must be >= 1 (code 4004)
    if len(text) < 3:
        return {"status": "error", "code": 4004, "message": "text must be at least 3 characters"}
    if times < 1:
        return {"status": "error", "code": 4004, "message": "times must be at least 1"}
    return {"status": "ok", "code": 200, "result": text * times}


# ---- 12 probe requests ----
probes = [
    {"tool": "divide", "args": {"dividend": 10, "divisor": 2}},          # 1 ok
    {"tool": "divide", "args": {"dividend": 10, "divisor": 0}},         # 2 domain: zero divisor
    {"tool": "divide", "args": {"dividend": 10, "divisor": -3}},        # 3 domain: negative
    {"tool": "divide", "args": {"dividend": "ten", "divisor": 2}},      # 4 pydantic: wrong type
    {"tool": "divide", "args": {"dividend": 10}},                        # 5 pydantic: missing field
    {"tool": "repeat_text", "args": {"text": "hi", "times": 3}},         # 6 domain: short string
    {"tool": "repeat_text", "args": {"text": "hello", "times": 0}},     # 7 domain: zero times
    {"tool": "repeat_text", "args": {"text": "hello", "times": -1}},    # 8 domain: negative times
    {"tool": "repeat_text", "args": {"text": 123, "times": 3}},         # 9 pydantic: wrong type
    {"tool": "repeat_text", "args": {"text": "hello", "times": 2.5}},   # 10 pydantic: float not integer
    {"tool": "repeat_text", "args": {"text": "hello", "times": 4}},     # 11 ok
    {"tool": "repeat_text", "args": {}},                                # 12 pydantic: missing fields
]

for i, probe in enumerate(probes, 1):
    gate = pydantic_gate(probe["tool"], probe["args"])
    if gate["layer"] == "pydantic":
        outcome = f"caught by Pydantic BEFORE function: {gate['error']}"
    else:
        # Reached the function body -> domain rules are our responsibility
        if probe["tool"] == "divide":
            body = divide_tool(**probe["args"])
        else:
            body = repeat_text_tool(**probe["args"])
        if body["status"] == "ok":
            outcome = f"accepted, result: {body['result']}"
        else:
            outcome = f"domain violation, code {body['code']}: {body['message']}"
    print(f"request {i:2d}: {probe['tool']:<12} -> {outcome}")

print(json.dumps({"note": "type errors never reach the function body"}, indent=2))
``

**အဓိကအယူအဆ** — Type စစ်ဆေးမှုကို Pydantic က tool function အတွင်း မရောက်မီ ဖမ်းဆုပ်ပေးပြီး function အတွင်း ရောက်ရှိလာသော input များအတွက် domain rules များကိုမူ ကိုယ်ပိုင် code (ဥပမာ ၄-၄-၄) ဖြင့် ပြန်လည်စစ်ဆေးပေးရမည်။

## လေ့ကျင့်ခန်း ၆ — Sequential vs Concurrent နှင့် Tool Trio

ဤလေ့ကျင့်ခန်းတွင် `async def` tool သုံးခုကိ sync version နှင့် နှိုင်းယှဉ်တိုင်းတာပြီး၊ ထို့နောက် `search_articles` → `list_sections` → `get_content` ခေါ်ဆိုမှုကိ တစ်လျှောက်လုပ်ဆောင်သည့် tool trio ကို စမ်းသပ်ပါမည်။ Concurrent ခေါ်ဆိုမှုအတွက် `asyncio.gather()` ကို အသုံးပြပြီး coroutine အတွင်းမှ `asyncio.run()` ကို ထပ်ခေါ်ခြင်း မပြုရပါ။ Trio ၏ `get_content` တွင် `offset`/`limit` window ထည့်သွင်း၍ ကြီးမားသော document ကို အပိုင်းလိုက် ရယူနိုင်စေရန် စီမံထားပါသည်။

``python
import asyncio
import time

# Simulated article store (like wikipedia.py style)
ARTICLES = {
    "python_(language)": {
        "sections": ["History", "Syntax", "Libraries", "Concurrency"],
        "content": ("Python is a high-level programming language. " * 500),
    },
    "asyncio": {
        "sections": ["Overview", "Event Loop", "Gather"],
        "content": ("asyncio is a library for async programming. " * 400),
    },
    "mcp": {
        "sections": ["Introduction", "Tools", "Resources"],
        "content": ("The Model Context Protocol connects tools. " * 350),
    },
}


async def fetch_delayed(key: str) -> str:
    # Simulate network latency for the async version
    await asyncio.sleep(1)
    return ARTICLES[key]["content"]


def fetch_sync(key: str) -> str:
    # Sync version blocks for the same simulated latency
    time.sleep(1)
    return ARTICLES[key]["content"]


def run_sync(keys: list) -> float:
    # Measure total time for sequential sync calls
    start = time.perf_counter()
    for key in keys:
        fetch_sync(key)
    return time.perf_counter() - start


async def run_async_sequential(keys: list) -> float:
    # Measure total time for sequential await calls
    start = time.perf_counter()
    for key in keys:
        await fetch_delayed(key)
    return time.perf_counter() - start


async def run_async_concurrent(keys: list) -> float:
    # Measure total time using asyncio.gather()
    start = time.perf_counter()
    await asyncio.gather(*(fetch_delayed(key) for key in keys))
    return time.perf_counter() - start


def search_articles(query: str) -> list:
    # Trio step 1: search by substring match
    query = query.lower()
    return [k for k in ARTICLES if query in k]


def list_sections(title: str) -> list:
    # Trio step 2: list available sections of an article
    return ARTICLES[title]["sections"]


def get_content(title: str, offset: int = 0, limit: int = 100) -> dict:
    # Trio step 3: fetch a window of the document
    text = ARTICLES[title]["content"]
    return {
        "title": title,
        "offset": offset,
        "total_chars": len(text),
        "content": text[offset:offset + limit],
    }


async def main() -> None:
    keys = ["python_(language)", "asyncio", "mcp"]

    # Part 1: compare sync vs async sequential vs concurrent
    sync_time = run_sync(keys)
    seq_time = await run_async_sequential(keys)
    conc_time = await run_async_concurrent(keys)
    print(f"sync sequential   : {sync_time:.2f}s")
    print(f"async sequential  : {seq_time:.2f}s")
    print(f"async concurrent  : {conc_time:.2f}s")

    # Part 2: tool trio — search -> list_sections -> get_content
    query = "mcp"
    results = search_articles(query)
    print(f"search_articles('{query}') -> {results}")

    if results:
        title = results[0]
        print(f"list_sections('{title}') -> {list_sections(title)}")

        # Fetch a small window of a large document
        page = get_content(title, offset=0, limit=80)
        print(
            f"get_content: offset={page['offset']}, "
            f"total_chars={page['total_chars']}"
        )
        print(f"window preview: {page['content'][:60]}...")


if __name__ == "__main__":
    asyncio.run(main())
``

**အဓိကအယူအဆ** — `asyncio.gather()` ဖြင့် tool များကို concurrent ခေါ်ဆိုသည့်အခါ sequential နည်းထက် သိသိသာသာမြန်ပြီး tool trio ဖြင့် `offset`/`limit` window အသုံးပြု၍ ကြီးမားသော document ကို ခြုံငုံမှုအနည်းငယ်ဖြင့် ရယူနိုင်သည်။
