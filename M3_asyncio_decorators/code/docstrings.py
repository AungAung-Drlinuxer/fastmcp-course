"""Lesson 1.3 (part 3) — the docstring IS the tool description.

The model never sees your code. It sees the name, the JSON Schema, and the description that
came from your docstring. Vague docstring, vague tool. This file parses a Google-style
docstring so you can see exactly which text a schema generator can lift for each parameter.

Run:
    uv run python -m M3_asyncio_decorators.code.docstrings
"""
from __future__ import annotations

import inspect
import re


def parse_google_args(docstring: str) -> dict[str, str]:
    """Extract the Args: block of a Google-style docstring as {param: description}.

    Deliberately simple: this is the shape FastMCP and most docstring parsers look for. The
    lesson is that the FORMAT is a contract, not a style preference — an unparsable docstring
    silently becomes a tool with no parameter descriptions.
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


def disk_usage(path: str, human: bool = True) -> dict:
    """Report disk usage for a filesystem path.

    Args:
        path: Absolute or relative path to inspect. Must exist on the server host.
        human: When true, scale the numbers to KB/MB/GB instead of raw bytes.

    Returns:
        A dict with total, used and free.
    """
    return {}


def bad_tool(vm: str) -> dict:
    """Does the thing with the stuff."""
    return {}


def main() -> None:
    print("=== a well-formed docstring ===")
    print("  summary  :", (inspect.getdoc(disk_usage) or "").splitlines()[0])
    for name, desc in parse_google_args(inspect.getdoc(disk_usage) or "").items():
        print(f"  {name:8} -> {desc}")

    print("\n=== the same thing written carelessly ===")
    print("  docstring:", inspect.getdoc(bad_tool))
    print("  parsed   :", parse_google_args(inspect.getdoc(bad_tool) or {}) or "{} — no descriptions")
    print("  -> the model gets `vm` with no explanation and will guess.")

    print("\n=== the four rules ===")
    print("  1. One-line summary, imperative: 'Report disk usage for a path.'")
    print("  2. A blank line, then `Args:` with one entry per parameter that has a meaning.")
    print("  3. Say WHAT a value must look like, not that it 'is a string'.")
    print("  4. Document the failure mode: 'Raises if the path does not exist.' An agent that")
    print("     knows a tool can fail can choose to check first.")


if __name__ == "__main__":
    main()
