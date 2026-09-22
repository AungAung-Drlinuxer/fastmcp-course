"""LAB 8 — the refusal contract: make rejection a SHAPE, and test it as a shape.

Lesson 2.2 taught the contrast that matters here, and VERIFIED.md records it:

    a tool RETURNING {"ok": false, "error": "division_by_zero"}
        -> CallToolResult(..., structured_content={...}, is_error=False)   # data
    a tool RAISING ZeroDivisionError
        -> ToolError, and the model gets an error string with no plan        # failure

A refusal is a DECISION, and a decision is data. This lab turns that into a contract:

  for every tool, and every hostile or malformed input:
      the return is a dict
      ok        is exactly False
      error     is a code from a CLOSED set the caller can switch on
      hint      is a non-empty human/model-readable string
      and no exception escapes

The closed set is the part people skip. An ad-hoc `error` string means the caller writes
`if "not allowed" in str(result)` — which breaks the day someone rewords the message. A closed
set means the caller writes `if error == "path_not_allowed"`.

Run:
    uv run python -m M10_security.code.lab_8_refusal_contract
"""
from __future__ import annotations

import asyncio
from typing import Any

from fastmcp import Client

from M10_security.code.path_validation import mcp

# The closed set. Every refusal in this server must name one of these.
ERROR_CODES = {
    "path_not_allowed",   # the boundary held: the path resolved outside the allowlist root
    "not_found",          # the path was legal but names nothing
    "bad_argument",       # a value was out of range or the wrong shape
    "unavailable",        # a dependency (file, socket, upstream) was not reachable
}

# (tool, arguments, expected code). The last column is the point of the whole file: the caller
# can test for a SPECIFIC refusal, not merely for "something went wrong".
CASES: list[tuple[str, dict[str, Any], str]] = [
    ("read_log",  {"name": "postgres.log"},                        "OK"),
    ("read_log",  {"name": "../../etc/shadow"},                    "path_not_allowed"),
    ("read_log",  {"name": "/etc/passwd"},                         "path_not_allowed"),
    ("read_log",  {"name": "..\\..\\windows\\win.ini"},            "path_not_allowed"),
    ("read_log",  {"name": "no-such-file.log"},                    "not_found"),
    ("read_log",  {"name": "postgres.log; rm -rf /"},              "not_found"),
    ("read_log",  {"name": "$(id)"},                               "not_found"),
    ("grep_log",  {"name": "../../etc/shadow", "pattern": "x"},    "path_not_allowed"),
    ("grep_log",  {"name": "postgres.log", "pattern": "ERROR"},    "OK"),
    ("list_logs", {},                                              "OK"),
]


def shape_of(data: Any) -> tuple[str, str, str]:
    """Classify a tool return as (kind, code_or_detail, hint).

    kind is one of:
        "OK"         a successful result (ok is True)
        "REFUSED"    a refusal that satisfies the contract (ok is False + a known code + a hint)
        "VIOLATION"  a return that breaks the contract, with the reason in the second slot
    """
    if not isinstance(data, dict):
        return "VIOLATION", f"not a dict: {type(data).__name__}", ""
    if data.get("ok") is True:
        return "OK", "", ""
    if data.get("ok") is not False:
        return "VIOLATION", f"ok is {data.get('ok')!r}, expected False", ""
    code = data.get("error")
    hint = data.get("hint")
    if code not in ERROR_CODES:
        return "VIOLATION", f"error {code!r} is outside the closed set {sorted(ERROR_CODES)}", ""
    if not isinstance(hint, str) or not hint.strip():
        return "VIOLATION", "hint is missing or empty", ""
    return "REFUSED", code, hint


async def main() -> None:
    print(f"closed error set : {sorted(ERROR_CODES)}\n")
    print(f"{'tool':11} {'arguments':44} {'expected':17} got")
    print("-" * 108)

    violations: list[str] = []
    raised: list[str] = []

    async with Client(mcp) as client:
        for tool, args, expected in CASES:
            label = str(args) if len(str(args)) <= 42 else str(args)[:41] + "…"
            try:
                data = (await client.call_tool(tool, args)).data
            except Exception as exc:                       # must never happen for these cases
                raised.append(f"{tool}{args} raised {type(exc).__name__}")
                print(f"{tool:11} {label:44} {expected:17} RAISED {type(exc).__name__}")
                continue
            kind, code, detail = shape_of(data)
            got = code if kind == "REFUSED" else kind + (f" ({code})" if code else "")
            flag = "" if got == expected else "   <-- MISMATCH"
            print(f"{tool:11} {label:44} {expected:17} {got}{flag}")
            if kind == "VIOLATION":
                violations.append(f"{tool}{args}: {code}")
            elif got != expected:
                violations.append(f"{tool}{args}: expected {expected}, got {got}")

    # A malformed argument is a different refusal shape: the framework raises ToolError BEFORE
    # the tool body runs (VERIFIED.md). That is correct — it is a protocol-level validation
    # failure, not a decision the tool made. The key point is that it is DETERMINISTIC.
    print("\n=== the framework-level case: an argument the schema forbids ===")
    async with Client(mcp) as client:
        try:
            await client.call_tool("read_log", {"name": "postgres.log", "max_lines": "lots"})
        except Exception as exc:
            print(f"  max_lines='lots' -> {type(exc).__name__}")
            print(f"  {str(exc).splitlines()[0]}")
            print("  ⭐ raised, not returned: a schema violation is not a tool decision.")

    print("\n=== why the hint matters as much as the code ===")
    async with Client(mcp) as client:
        refused = (await client.call_tool("read_log", {"name": "../../etc/shadow"})).data
    print(f"  error: {refused['error']}")
    print(f"  hint : {refused['hint']}")
    print("  the model reads the hint and can correct course; an empty refusal makes it retry")
    print("  the same call, or give up on a task it could have finished.")
    print("  the hint must NOT leak the resolved path of anything outside the root.")

    print("\n=== contract checks ===")
    print(f"  cases run          : {len(CASES)}")
    print(f"  shape violations   : {len(violations)}")
    for item in violations:
        print(f"    {item}")
    print(f"  unexpected raises  : {len(raised)}")

    assert not violations, violations
    assert not raised, raised
    print("\nverdict : PASS — every refusal is a dict with a closed-set code and a usable hint")


if __name__ == "__main__":
    asyncio.run(main())