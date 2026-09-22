"""LAB 7 — EXTEND THE CAPSTONE: add a resource template and a guard to go with it.

Lab 6 added tools. This lab adds the two other kinds of extension a real server needs:

  A RESOURCE with a URI TEMPLATE, so the estate's notes become addressable data a client can
  fetch by reference rather than by calling a tool:

      @mcp.resource("estate://{kind}/{name}", mime_type="text/markdown")

  A GUARD, i.e. the small function that decides what the template is even allowed to resolve.
  A template is a promise that ALL of its URIs are meaningful; the guard is what makes that
  promise true instead of aspirational. Here the guard is a two-part allowlist:

      kind  must be one of a fixed set      ('note', 'runbook', 'config')
      name  must match a conservative pattern, so '..%2F..' never reaches a filesystem call

Failures must be LOUD AND USEFUL. A resource that returns an empty string for an unknown name
teaches a model that unknown things look empty. Raising `FileNotFoundError` with the list of
alternatives is the M6 lesson, and the client sees it as a real error:

    MCPError: Error reading resource 'estate://note/nope': no note 'nope'; available: ...

Run:
    uv run python -m M11_capstone.code.lab_7_estate_resource_guard
"""
from __future__ import annotations

import asyncio
import re

from fastmcp import Client

from M11_capstone.code.devops_assistant import CONF, HOME, RUNBOOKS, _resolve, mcp

MEMORY = HOME / "data" / "memory"

# The guard, part 1: the kinds this template has meaning for. Anything else is not a 404 —
# it is a URI the server never promised to serve, and saying so is more useful than guessing.
KINDS = {"note": MEMORY, "runbook": RUNBOOKS, "config": CONF}
EXTENSIONS = {"note": ".md", "runbook": ".md", "config": ".yaml"}

# The guard, part 2: an allowlist on the NAME, applied BEFORE anything touches the filesystem.
# _resolve is still the real boundary; this rejects the obviously hostile shapes earlier so the
# error message can be about the name rather than about a path that escaped.
SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def _guard(kind: str, name: str) -> "tuple":
    """Return (root, filename) or raise ValueError with an explanation a caller can act on."""
    if kind not in KINDS:
        raise ValueError(f"unknown kind {kind!r}; allowed kinds: {', '.join(sorted(KINDS))}")
    if not SAFE_NAME.match(name):
        raise ValueError(f"illegal name {name!r}: letters, digits, dot, dash, underscore only")
    return KINDS[kind], f"{name}{EXTENSIONS[kind]}"


@mcp.resource("estate://{kind}/{name}", mime_type="text/markdown")
def estate_document(kind: str, name: str) -> str:
    """A note, runbook or config addressed as estate://<kind>/<name>.

    Args:
        kind: One of 'note', 'runbook', 'config'.
        name: Document name without the extension.
    """
    try:
        root, filename = _guard(kind, name)
        target = _resolve(root, filename)
    except ValueError as exc:
        raise FileNotFoundError(str(exc)) from exc
    if not target.is_file():
        available = sorted(p.stem for p in root.glob(f"*{EXTENSIONS[kind]}"))
        raise FileNotFoundError(
            f"no {kind} {name!r}; available: {', '.join(available) or 'none'}")
    return target.read_text(encoding="utf-8")


@mcp.resource("allowlist://estate", mime_type="text/plain")
def estate_allowlist() -> str:
    """The server's own rules, published as data so a client can read them instead of guessing.

    A resource with no arguments has exactly ONE valid URI, so it is not a template — it appears
    in `list_resources()`, unlike the templates in `list_resource_templates()`.
    """
    lines = [
        "# devops-assistant allowlist",
        f"kinds      : {', '.join(sorted(KINDS))}",
        f"name rule  : {SAFE_NAME.pattern}",
        f"protected  : postgres-ha, redis-sentinel, kasm-app",
        "extension  : note=.md runbook=.md config=.yaml",
        "policy     : anything outside these roots raises, it does not return empty",
    ]
    return "\n".join(lines) + "\n"


async def main() -> None:
    async with Client(mcp) as client:
        print("=== 1. resources and templates are still two different lists ===")
        print(f"  list_resources()          : {[str(r.uri) for r in await client.list_resources()]}")
        print("  list_resource_templates() :")
        for t in await client.list_resource_templates():
            print(f"    {t.uri_template!r}")

        print("\n=== 2. the guard publishes its own rules ===")
        print((await client.read_resource("allowlist://estate"))[0].text)

        print("=== 3. a client can walk the whole estate through ONE template ===")
        for uri in ("estate://runbook/postgres-ha", "estate://config/pve01"):
            text = (await client.read_resource(uri))[0].text
            print(f"  {uri:32} -> {text.splitlines()[0]!r}")

        print("\n=== 4. loud failures, listing the alternatives ===")
        for uri in ("estate://runbook/nope", "estate://note/does-not-exist",
                    "estate://secret/passwords", "estate://note/../etc/passwd",
                    "estate://note/.hidden"):
            try:
                await client.read_resource(uri)
                print(f"  {uri:34} -> NO ERROR (a bug: this should have raised)")
            except Exception as exc:
                first = str(exc).splitlines()[0]
                print(f"  {uri:34} -> {type(exc).__name__}: {first[:88]}")

        print("\n=== 5. a note written by lab 6 is reachable here by URI ===")
        text = (await client.read_resource("estate://note/failover-drill"))[0].text
        print(f"  estate://note/failover-drill -> {text.splitlines()[0]!r}")
        print("  Lab 6 wrote it with a TOOL; lab 7 reads it as a RESOURCE. Same bytes, two")
        print("  interfaces, and the choice between them is a design decision: a tool is chosen")
        print("  by the model mid-task, a resource is addressed by the client by reference.")

    print("\n=== 6. your extension, beside the capstone's own ===")
    print("  new template : estate://{kind}/{name}")
    print("  new resource : allowlist://estate")
    print("  new guard    : _guard() — kinds allowlist + name pattern, before any filesystem call")
    print("  capstone file edited: none")


if __name__ == "__main__":
    asyncio.run(main())