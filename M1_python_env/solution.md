# M1 — လေ့ကျင့်ခန်း အဖြေများ

## လေ့ကျင့်ခန်း ၁ — uv နဲ့ project အသစ် တည်ဆောက်ခြင်း

``python
# Shell steps (shown together for clarity):
#   uv init my-mcp-project
#   cd my-mcp-project
#   uv add mcp
#   uv run python env_check.py
# Then a Python check that the required files exist:

from pathlib import Path

# Project root must contain these after uv init / uv add
required = ["pyproject.toml"]
optional = [".venv"]

for name in required:
    if Path(name).exists():
        print(f"OK: {name} found")
    else:
        print(f"MISSING: {name} not found")

for name in optional:
    print(f"{name}: {'exists' if Path(name).exists() else 'not created yet'}")

# Expected output:
# OK: pyproject.toml found
# .venv: exists
``

**အဓိကအယူအဆ** — `uv init` နဲ့ `uv add` က project ဖိုင်တွေနဲ့ `.venv` ကို တစ်ပြိုင်တည်း တည်ဆောက်ပေးလို့ လက်တွေ့ စစ်ဆေးရလွယ်သည်။

## လေ့ကျင့်ခန်း ၂ — Version ချုပ်ခြင်းကို စမ်းသပ်ခြင်း

``python
# In pyproject.toml set:
#   requires-python = ">=3.11"
# Then try running with an older interpreter:

import subprocess
import sys

# Check the current interpreter against our requirement
MIN_MAJOR, MIN_MINOR = 3, 11
major, minor = sys.version_info[0], sys.version_info[1]

if (major, minor) >= (MIN_MAJOR, MIN_MINOR):
    print(f"PASS: Python {major}.{minor} satisfies >=3.11")
else:
    print(f"FAIL: Python {major}.{minor} does NOT satisfy >=3.11")

# Expected output:
# PASS: Python 3.11.9 satisfies >=3.11
# (uv itself also refuses to run the project on an older Python)
``

**အဓိကအယူအဆ** — `requires-python` က Python version အနည်းဆုံး လိုအပ်ချက်ကို သတ်မှတ်ပြီး `uv` က အလိုအလျောက် စစ်ဆေးပေးသည်။

## လေ့ကျင့်ခန်း ၃ — pyproject.toml ကို ဖတ်ခြင်း

``python
# Minimal parser reading pyproject.toml dependencies with stdlib only

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # for Python < 3.11

with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)

project = data.get("project", {})
print("Project name:", project.get("name", "unknown"))
print("Requires Python:", project.get("requires-python", "not set"))

deps = project.get("dependencies", [])
print(f"Dependencies ({len(deps)}):")
for dep in deps:
    print(" -", dep)

# Expected output:
# Project name: my-mcp-project
# Requires Python: >=3.11
# Dependencies (1):
#  - mcp>=1.0.0
``

**အဓိကအယူအဆ** — `pyproject.toml` က machine-readable project metadata ဖြစ်လို့ Python stdlib (သို) `uv` ဖြင့် တိုက်ရိုက် ဖတ်နိုင်သည်။

## လေ့ကျင့်ခန်း ၄ — Interpreter လမ်းကြောင်း စစ်ခြင်း

``python
# which_python.py — show exactly which interpreter is running

import sys

print("Executable:", sys.executable)
print("Version:", sys.version.split()[0])
print("Prefix:", sys.prefix)

if ".venv" in sys.executable or ".venv" in sys.prefix:
    print("Mode: VIRTUAL ENVIRONMENT (.venv)")
else:
    print("Mode: SYSTEM / OTHER interpreter")

# Expected output under uv run:
# Executable: /path/to/project/.venv/bin/python
# Version: 3.11.9
# Mode: VIRTUAL ENVIRONMENT (.venv)
``

**အဓိကအယူအဆ** — `sys.executable` က လက်ရှိ interpreter ရဲ့ တိကျတဲ့ လမ်းကြောင်းကို ပြပေးလို့ environment မှားနေမှုကို ချက်ချင်း သိနိုင်သည်။

## လေ့ကျင့်ခန်း ၅ — env_check.py ကို တစ်လိုင်းချင်း ဖတ်ခြင်း

``python
# A condensed version of ../code/env_check.py showing its structure:

import sys
import importlib.metadata as metadata

# 1. Imports: sys for interpreter info, metadata for package versions

# 2. Show the interpreter this script is actually running on
print("Python executable:", sys.executable)
print("Python version:", sys.version.split()[0])

# 3. Check key packages inside this environment only
for package in ["mcp", "pydantic"]:
    try:
        version = metadata.version(package)
        print(f"{package}: {version}")
    except metadata.PackageNotFoundError:
        print(f"{package}: not installed in this environment")

# Expected output:
# Python executable: .../.venv/bin/python
# Python version: 3.11.9
# mcp: 1.x.x
# pydantic: 2.x.x
``

**အဓိကအယူအဆ** — `env_check.py` ရဲ့ structure က import → interpreter ထုတ်ပြ → package version စစ်ဆေး ဆိုတဲ့ အစဉ်အတိုင်း ဖွဲ့စည်းထားသည်။

## လေ့ကျင့်ခန်း ၆ — Environment ပြဿနာ ရှာဖွေခြင်း

``python
# Simulate the "clone and rebuild" workflow with a verification step

import subprocess
import sys

def run(cmd):
    # Run a shell command and print its output
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"$ {cmd}")
    print(result.stdout.strip() or result.stderr.strip())

# Steps a teammate runs after cloning your project:
run("git clone <your-repo-url>")
print("Then inside the project:")
run("uv sync")  # rebuilds .venv exactly from uv.lock

# Verify the rebuild worked:
print("Executable:", sys.executable)

# Expected output:
# $ uv sync
# Installed <n> packages in ...
# Executable: .../.venv/bin/python
``

**အဓိကအယူအဆ** — `uv.lock` က dependency version တွေရဲ့ အတိအကျ မှတ်တမ်းဖြစ်လို့ `uv sync` တစ်ခုတည်းနဲ့ တူညီတဲ့ environment ကို ဘယ်နေရာမှာမဆို ပြန်တည်ဆောက်နိုင်သည်။
