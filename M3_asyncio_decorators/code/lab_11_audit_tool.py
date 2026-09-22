"""LAB 11 — an audit harness: catch the metadata failure before a client does.

Nothing in this stack raises when a tool loses its metadata. So you write the
checker yourself. `audit_tool` looks at a function exactly the way a registry
does and returns a verdict plus the reasons for it.

The last section of the lab reproduces a real ordering bug: `functools.wraps`
applied to a function whose metadata is ALREADY destroyed faithfully copies the
damaged metadata — garbage in, garbage copied.

Run:
    uv run python -m M3_asyncio_decorators.code.lab_11_audit_tool
"""
from __future__ import annotations

import functools
import inspect
from typing import Any


# --- the two decorators, once more ------------------------------------------------------
def naive_logger(fn):
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper


def logged(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper


# --- the audit --------------------------------------------------------------------------
MISSING = "<missing>"
PLACEHOLDER_NAMES = {"wrapper", "decorator", "inner", "wrapped", "func", "<lambda>"}


def audit_tool(fn) -> dict[str, Any]:
    """Report whether a function still carries the metadata a tool needs.

    A registry reads exactly three things off your function: `__name__`, the
    docstring and the annotations. Everything here checks one of those three, or
    checks the signature those annotations were written on.
    """
    name = getattr(fn, "__name__", MISSING)
    doc = inspect.getdoc(fn)
    annotations = getattr(fn, "__annotations__", {}) or {}
    signature = inspect.signature(fn)
    body_params = [
        p for p in signature.parameters.values()
        if p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
    ]
    problems: list[str] = []

    if name in PLACEHOLDER_NAMES:
        problems.append(f"name is a placeholder: {name!r}")
    if name == MISSING:
        problems.append("no __name__ at all")
    if not doc:
        problems.append("no docstring: the tool has no description")
    if not annotations:
        problems.append("no annotations: every parameter will be schema-unknown")
    if not body_params:
        problems.append("signature is only *args/**kwargs: no schema can be generated")
    if not hasattr(fn, "__wrapped__") and name in PLACEHOLDER_NAMES:
        problems.append("no __wrapped__: functools.wraps was not used")

    return {
        "name": name,
        "documented": bool(doc),
        "annotation_count": len(annotations),
        "body_parameters": [p.name for p in body_params],
        "has_wrapped": hasattr(fn, "__wrapped__"),
        "verdict": "OK" if not problems else "BROKEN",
        "problems": problems,
    }


def render(report: dict[str, Any]) -> str:
    lines = [
        f"  {report['name']:16} {report['verdict']:7} "
        f"doc={report['documented']} annotations={report['annotation_count']} "
        f"params={report['body_parameters']} wrapped={report['has_wrapped']}"
    ]
    for problem in report["problems"]:
        lines.append(f"      - {problem}")
    return "\n".join(lines)


def main() -> None:
    print("=== step 1: three functions, three verdicts ===")

    def good_tool(vm_name: str, cpu_cores: int = 2) -> dict:
        """Provision a virtual machine.

        Args:
            vm_name: Name of the virtual machine.
            cpu_cores: How many cores to allocate.
        """
        return {}

    def no_docstring(vm_name: str) -> dict:
        return {}

    def anonymous(*args, **kwargs):
        return {}

    for fn in (good_tool, no_docstring, anonymous):
        print(render(audit_tool(fn)))

    print("\n=== step 2: the same audit through the two decorators ===")
    print(render(audit_tool(naive_logger(good_tool))))
    print(render(audit_tool(logged(good_tool))))

    print("\n=== step 3: the ordering bug, reproduced ===")
    first = naive_logger(good_tool)   # metadata already destroyed here
    second = logged(first)            # wraps copies what is left: nothing useful
    print(render(audit_tool(second)))
    print("  -> functools.wraps copies metadata; if it was already gone, it stays gone")
    print("  -> FIX: decorate a FRESH function, or put the correct decorator innermost")
    print(render(audit_tool(logged(naive_logger(good_tool)))))
    print(render(audit_tool(naive_logger(logged(good_tool)))))

    print("\n=== step 4: the audit as a test you can run in CI ===")
    tools = {
        "good_tool": logged(good_tool),
        "bad_tool": naive_logger(no_docstring),
    }
    failures = {name: audit_tool(fn) for name, fn in tools.items()
                if audit_tool(fn)["verdict"] != "OK"}
    print(f"  audited {len(tools)} tool(s); {len(failures)} broken")
    for name, report in failures.items():
        print(f"    {name}: {report['problems']}")
    print("  -> assert not failures, and a metadata bug never reaches a model again")

    print("\n=== step 5: the three attributes that matter ===")
    for attribute in ("__name__", "__doc__", "__annotations__", "__wrapped__"):
        print(f"  {attribute:16} -> what a registry reads")


if __name__ == "__main__":
    main()
