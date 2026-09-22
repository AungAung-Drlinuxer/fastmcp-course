# M0 — လေ့ကျင့်ခန်း အဖြေများ

## လေ့ကျင့်ခန်း ၁ — MCP မရှိခင် ပြဿနာကို ဖော်ပြပါ

```python
# Three problems before MCP existed
problems = [
    "Every model/tool pair needed its own custom integration code.",
    "Switching to a different model or provider meant rewriting the glue code.",
    "The number of connections grew combinatorially and became costly to maintain.",
]

for i, problem in enumerate(problems, start=1):
    print(f"{i}. {problem}")
# Expected output:
# 1. Every model/tool pair needed its own custom integration code.
# 2. Switching to a different model or provider meant rewriting the glue code.
# 3. The number of connections grew combinatorially and became costly to maintain.
```

**အဓိကအယူအဆ** — MCP မရှိခင် integration တိုင်းက custom ဖြစ်ပြီး model တစ်မျိုးပြောင်းရင် တစ်ဖန် ပြန်ရေးရတာကြောင့် စျေးကြီးပြီး ထိန်းရခက်တယ်။

## လေ့ကျင့်ခန်း ၂ — JSON-RPC request တစ်ခု ဖန်တီးပါ

```python
# Build a JSON-RPC request and serialize it to a JSON string
import json

request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
}

json_string = json.dumps(request, indent=2)
print(json_string)
# Expected output:
# {
#   "jsonrpc": "2.0",
#   "id": 1,
#   "method": "tools/list"
# }
```

**အဓိကအယူအဆ** — JSON-RPC request ဆိုတာ `jsonrpc`, `id`, `method` key တွေပါဝင်တဲ့ သာမန် JSON message တစ်ခုသာဖြစ်တယ်။

## လေ့ကျင့်ခန်း ၃ — Host / Client / Server ကို ခွဲပြပါ

```python
# Map each situation to its MCP role
situations = {
    "(a) the chat app the user talks to": "Host",
    "(b) the part inside the app connecting to a server": "Client",
    "(c) the process exposing a database query tool": "Server",
}

for situation, role in situations.items():
    print(f"{situation} -> {role}")
# Expected output:
# (a) the chat app the user talks to -> Host
# (b) the part inside the app connecting to a server -> Client
# (c) the process exposing a database query tool -> Server
```

**အဓိကအယူအဆ** — Host က user နဲ့ထိတွေ့တဲ့ application၊ Client က Host ထဲမှာနေပြီး Server တစ်ခုနဲ့ချင်း ချိတ်ဆက်ပေးတဲ့ အစိတ်အပိုင်း၊ Server က tool တွေဖော်ထုတ်ပေးသူဖြစ်တယ်။

## လေ့ကျင့်ခန်း ၄ — LAB 1 လုပ်ပါ: protocol ကို ကိုယ်တိုင် မြင်ပါ

`../code/lab_1_see_the_protocol.py` ကို run ပါ:

```python
# How to run LAB 1 and what to look for
import subprocess

# Run the lab file that lets you watch raw JSON-RPC traffic
result = subprocess.run(
    ["python", "../code/lab_1_see_the_protocol.py"],
    capture_output=True,
    text=True,
)

print(result.stdout)
# Expected output:
# The raw JSON-RPC messages exchanged between client and server,
# including the initialize request/response and tool listing traffic.
```

LAB 1 run ပြီးရင် initialize message၊ request နဲ့ response တွေက JSON format အတိအကျ ဘယ်လိုပေါ်လဲဆိုတာကို စောင့်ကြည့်ပါ။

**အဓိကအယူအဆ** — MCP ဆိုတာ magic မဟုတ်ဘဲ client နဲ့ server ကြားမှာ JSON message တွေ ဖြတ်သန်းနေတာသာဖြစ်တယ်။

## လေ့ကျင့်ခန်း ၅ — LAB 2 လုပ်ပါ: surface ၄ မျိုးကို စစ်ပါ

`../code/lab_2_four_surfaces.py` ကို run ပါ:

```python
# How to run LAB 2 and inspect the exposed surfaces
import subprocess

# Run the lab file that shows what the server exposes
result = subprocess.run(
    ["python", "../code/lab_2_four_surfaces.py"],
    capture_output=True,
    text=True,
)

print(result.stdout)
# Expected output:
# The list of what the server exposes (tools, resources, prompts)
# and what it deliberately does NOT expose.
```

Output ထဲမှာ ပါဝင်တဲ့ tool တွေ၊ resource တွေကို မှတ်ပါ။ ပြီးရင် ဘာကို မဖော်ထုတ်ထားလဲဆိုတာနဲ့ ချိတ်ဆက်ဖတ်ပါ — ဒါက server design ရဲ့ ရည်ရွယ်ချက်ကို ပြတယ်။

**အဓိကအယူအဆ** — Server တစ်ခုက ဘာကို ဖော်ထုတ်ပြီး ဘာကို မဖော်ထုတ်ဘူးလဲဆိုတာ design ဆုံးဖြတ်ချက်တစ်ခုဖြစ်ပြီး လုံခြုံမှုနဲ့ ရည်ရွယ်ချက်နဲ့ ဆက်နွယ်တယ်။

## လေ့ကျင့်ခန်း ၆ — `@mcp.tool` pattern ကို ရှင်းပါ

```python
# The four things @mcp.tool() does for you, as runnable code
steps = [
    "1. Registers the function as an MCP tool on the server.",
    "2. Generates a JSON Schema for its parameters from the type hints.",
    "3. Advertises the tool so clients can discover it via tools/list.",
    "4. Handles the protocol plumbing so you only write the logic.",
]

for step in steps:
    print(step)
# Expected output:
# 1. Registers the function as an MCP tool on the server.
# 2. Generates a JSON Schema for its parameters from the type hints.
# 3. Advertises the tool so clients can discover it via tools/list.
# 4. Handles the protocol plumbing so you only write the logic.
```

**အဓိကအယူအဆ** — `@mcp.tool()` decorator က function တစ်ခုကို protocol နားလည်တဲ့ MCP tool တစ်ခုဖြစ်အောင် အလိုအလျောက် ကူးပြောင်းပေးလို့ logic အပေါ်မှာတည်း စိတ်ချလက်ချ ရေးနိုင်တယ်။
