"""LAB 10 — the docstring is a contract, not a comment.

The model never sees this file. It sees a name, a JSON Schema and a description
that was lifted out of a docstring. So the docstring's FORMAT decides whether the
model gets parameter descriptions or gets nothing.

This lab parses two docstrings — one well-formed, one careless — and builds the
tool schema each one produces.

Run:
    uv run python -m M3_asyncio_decorators.code.lab_10_docstring_contract
"""
from __future__ import annotations

import inspect
import json
import re
from typing import Any


def parse_google_args(docstring: str) -> dict[str, str]:
    """Extract the Args: block of a Google-style docstring as {param: description}.

    Deliberately simple: this is the shape FastMCP and most docstring parsers
    look for. The lesson is that the FORMAT is a contract, not a style
    preference — an unparsable docstring silently becomes a tool with no
    parameter descriptions.
    """
    if not docstring:
        return {}
    lines = inspect.cleandoc(docstring).splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip().rstrip(":") == "Args")
    except StopIteration:
        return {}
    out: dict[str, str] = {}
    current: str | None = None
    for line in lines[start + 1:]:
        stripped = line.strip()
        if not stripped:
            continue
        # a new section ends Args
        if not line.startswith((" ", "\t")) and stripped.endswith(":"):
            break
        match = re.match(r"^(\w+)\s*(?:\([^)]*\))?\s*:\s*(.*)$", stripped)
        if match:
            current = match.group(1)
            out[current] = match.group(2).strip()
        elif current:
            out[current] = f"{out[current]} {stripped}".strip()
    return out


def parse_sections(docstring: str) -> dict[str, str]:
    """Return the summary plus each named section of a Google-style docstring."""
    if not docstring:
        return {"summary": "", "sections": {}}
    lines = inspect.cleandoc(docstring).splitlines()
    summary = lines[0].strip()
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines[1:]:
        stripped = line.strip()
        if stripped.endswith(":") and not line.startswith((" ", "\t")) and stripped:
            current = stripped.rstrip(":")
            sections[current] = []
            continue
        if current and stripped:
            sections[current].append(stripped)
    return {"summary": summary, "sections": {k: " ".join(v) for k, v in sections.items()}}


def tool_from_docstring(fn) -> dict[str, Any]:
    """Build the tool definition a schema generator would produce from `fn`."""
    doc = inspect.getdoc(fn) or ""
    summary = parse_sections(doc)["summary"]
    described = parse_google_args(doc)
    signature = inspect.signature(fn)
    properties: dict[str, dict] = {}
    required: list[str] = []
    for name, parameter in signature.parameters.items():
        spec: dict[str, Any] = {}
        if name in described:
            spec["description"] = described[name]
        if parameter.default is not inspect.Parameter.empty:
            spec["default"] = parameter.default
        else:
            required.append(name)
        properties[name] = spec
    return {
        "name": fn.__name__,
        "description": summary,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        },
    }


# --- a well-formed docstring -----------------------------------------------------------
def disk_usage(path: str, human: bool = True) -> dict:
    """Report disk usage for a filesystem path.

    Args:
        path: Absolute or relative path to inspect. Must exist on the server host.
        human: When true, scale the numbers to KB/MB/GB instead of raw bytes.

    Returns:
        A dict with total, used and free.

    Raises:
        FileNotFoundError: when the path does not exist on the server host.
    """
    return {}


# --- the same tool, written carelessly --------------------------------------------------
def careless_disk_usage(path: str, human: bool = True) -> dict:
    """Does the thing with the stuff."""
    return {}


# --- a docstring that is good prose but the wrong FORMAT --------------------------------
def wrong_format(path: str, human: bool = True) -> dict:
    """Report disk usage.

    :param path: the path
    :param human: whether to scale
    """
    return {}


def main() -> None:
    print("=== step 1: a well-formed docstring, taken apart ===")
    doc = inspect.getdoc(disk_usage) or ""
    parsed = parse_sections(doc)
    print(f"  summary  : {parsed['summary']}")
    for section, body in parsed["sections"].items():
        print(f"  {section:8} : {body[:60]}")
    print("  Args parsed:")
    for name, desc in parse_google_args(doc).items():
        print(f"    {name:6} -> {desc}")

    print("\n=== step 2: the schema it produces ===")
    print(json.dumps(tool_from_docstring(disk_usage), indent=2, ensure_ascii=False))

    print("\n=== step 3: the careless version ===")
    print(f"  docstring : {inspect.getdoc(careless_disk_usage)!r}")
    print(f"  summary   : {parse_sections(inspect.getdoc(careless_disk_usage) or '')['summary']!r}")
    print(f"  args      : {parse_google_args(inspect.getdoc(careless_disk_usage) or '') or '{} — no descriptions'}")
    print(json.dumps(tool_from_docstring(careless_disk_usage), indent=2, ensure_ascii=False))
    print("  -> the model gets `path` with no explanation and will guess")

    print("\n=== step 4: good prose, wrong format ===")
    print(f"  docstring : {inspect.getdoc(wrong_format)!r}")
    print(f"  args      : {parse_google_args(inspect.getdoc(wrong_format) or '') or '{} — no descriptions'}")
    print("  -> Sphinx `:param:` is a valid convention, and this parser ignores it entirely")
    print("  -> whichever style you pick, the whole file must use one style")

    print("\n=== step 5: what the model actually receives ===")
    for fn in (disk_usage, careless_disk_usage, wrong_format):
        tool = tool_from_docstring(fn)
        described = sum(1 for spec in tool["parameters"]["properties"].values() if "description" in spec)
        print(f"  {fn.__name__:24} summary={tool['description'][:28]!r:32} "
              f"documented params={described}/{len(tool['parameters']['properties'])}")
    print("  -> all three REGISTER fine. None of them raises. Only one is usable.")

    print("\n=== the four rules ===")
    print("  1. One-line summary, imperative: 'Report disk usage for a path.'")
    print("  2. A blank line, then `Args:` with one entry per parameter that has a meaning.")
    print("  3. Say WHAT a value must look like, not that it 'is a string'.")
    print("  4. Document the failure mode: 'Raises if the path does not exist.' An agent")
    print("     that knows a tool can fail can choose to check first.")


if __name__ == "__main__":
    main()
