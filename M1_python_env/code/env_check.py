"""Lesson 1.1 — prove the environment before writing any MCP code.

Students lose more time to a wrong interpreter than to any MCP concept. This script answers
the three questions that cause that: which Python is running, which packages can it see, and
is the project layout the one uv created.

Run:
    uv run python -m M1_python_env.code.env_check
"""
from __future__ import annotations

import importlib.util
import json
import platform
import sys
from pathlib import Path


def describe_interpreter() -> dict:
    """Report the facts that decide whether the rest of the course will work."""
    return {
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "implementation": platform.python_implementation(),
        "os": f"{platform.system()} {platform.release()}",
        "in_venv": sys.prefix != getattr(sys, "base_prefix", sys.prefix),
        "supported": sys.version_info >= (3, 11),
    }


def find_project_root(start: Path | None = None) -> Path | None:
    """Walk up until a pyproject.toml appears — the same way uv decides what a project is."""
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "pyproject.toml").is_file():
            return candidate
    return None


def has_module(name: str) -> bool:
    """True when the current interpreter can import `name`."""
    return importlib.util.find_spec(name) is not None


def main() -> None:
    info = describe_interpreter()
    print("=== interpreter ===")
    for key, value in info.items():
        print(f"  {key:14} {value}")

    root = find_project_root()
    print("\n=== project ===")
    print(f"  project root   {root}")
    if root:
        text = (root / "pyproject.toml").read_text(encoding="utf-8")
        print(f"  pyproject      {len(text)} bytes")
        print("  has [project]  ", "[project]" in text)

    print("\n=== packages this course needs ===")
    for mod in ("fastmcp", "pydantic", "mcp", "langgraph"):
        print(f"  {mod:12} {'present' if has_module(mod) else 'MISSING'}")

    print("\n=== verdict ===")
    if not info["supported"]:
        print(f"  FAIL: Python {info['python']} is too old; the examples use `X | Y` unions.")
    elif not info["in_venv"]:
        print("  WARN: not running inside a virtual environment — use `uv run`.")
    else:
        print("  OK: run the rest of the course with `uv run ...`")


if __name__ == "__main__":
    main()
