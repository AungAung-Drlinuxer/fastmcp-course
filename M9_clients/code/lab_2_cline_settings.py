"""LAB 2 — read Cline's MCP settings, audit them, and prove the stdio command really launches.

`cline_mcp_settings.json` is not documentation: every field in it is an instruction to a host
application. This lab turns each field into the concrete thing it controls, then does the one
check that matters — it spawns the process the settings describe and speaks MCP to it.

Run:
    uv run python -m M9_clients.code.lab_2_cline_settings
"""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import StdioTransport, UvStdioTransport

SETTINGS = Path(__file__).with_name("cline_mcp_settings.json")
ROOT = Path(__file__).parents[2]

# What the host does with each key. This is the whole file format, stated once.
FIELD_ROLE = {
    "command": "the executable to spawn; for stdio this is the transport's first half",
    "args": "its argv; the two together ARE the stdio transport",
    "env": "extra variables for the child; merged over the inherited environment",
    "disabled": "false = the host offers this server's tools to the model at all",
    "autoApprove": "tool names the host may call WITHOUT asking the human first",
}
# Measured in mcp 2.2.0 (mcp/client/stdio.py:128):
#     env=get_default_environment() | (server.env or {})
# get_default_environment() inherits only a safe allowlist (PATH and friends on POSIX,
# SystemRoot and friends on Windows) and refuses values that start with "()" — exported bash
# functions. So the env block ADDS to a filtered environment; it does not replace it.
ENV_MERGE_NOTE = "env is merged over a filtered inherited environment, not substituted for it"


def audit_server(name: str, spec: dict) -> list[str]:
    """Return the findings a reviewer should see before this server is enabled."""
    findings: list[str] = []
    if not spec.get("command"):
        findings.append("no `command`: the host cannot build a transport at all")
    if spec.get("disabled"):
        findings.append("disabled: true — the host will not offer this server")
    approve = spec.get("autoApprove") or []
    if "*" in approve or approve == ["*"]:
        findings.append("WILDCARD autoApprove: every tool runs with no human review step")
    elif approve:
        findings.append(f"autoApprove={approve}: only these skip the prompt")
    else:
        findings.append("autoApprove=[]: every call prompts the human — the safe default")
    if spec.get("command") == "uv" and "--directory" not in (spec.get("args") or []):
        findings.append("uv without --directory: the child inherits the host's cwd, "
                        "so it may resolve a different project")
    return findings


def show_settings(data: dict) -> dict[str, dict]:
    print("=== the file, field by field ===")
    for key, role in FIELD_ROLE.items():
        print(f"  {key:12} {role}")
    print(f"  env          {ENV_MERGE_NOTE}")

    servers = data.get("mcpServers", {})
    print(f"\n=== {len(servers)} server(s) declared ===")
    for name, spec in servers.items():
        print(f"\n  [{name}]")
        print(f"    command {spec.get('command')!r}")
        print(f"    args    {spec.get('args')}")
        print(f"    env     {spec.get('env')}")
        print(f"    transport = stdio: the host runs this program and speaks JSON-RPC")
        print(f"                over its stdin/stdout. Nothing listens on a port.")
        for finding in audit_server(name, spec):
            print(f"    audit   {finding}")
    return servers


async def prove_it_launches(spec: dict) -> None:
    """The only real test of a settings entry: run it."""
    print("\n=== proving the entry works (no editor required) ===")
    transport = StdioTransport(command=spec["command"], args=spec["args"],
                               env=spec.get("env"), keep_alive=False)
    print(f"  StdioTransport(command={transport.command!r}, args={transport.args})")
    async with Client(transport) as client:
        tools = await client.list_tools()
        print(f"  handshake ok, tools = {[t.name for t in tools]}")
        print(f"  ping -> {(await client.call_tool('ping', {})).data!r}")


async def the_uv_shortcut(module: str) -> None:
    """The same `uv run --directory <root>` translated into FastMCP's own transport class."""
    print("\n=== the same command, as UvStdioTransport ===")
    # NOTE: project_directory must be a Path, not a str. With a str you get, at import time:
    #   AttributeError: 'str' object has no attribute 'exists'
    # because the constructor calls project_directory.exists() to validate it.
    transport = UvStdioTransport(command="python", args=["-m", module],
                                 project_directory=ROOT, keep_alive=False)
    print(f"  UvStdioTransport -> uv {transport.args}")
    async with Client(transport) as client:
        print(f"  tools -> {[t.name for t in await client.list_tools()]}")


def what_a_wildcard_would_do() -> None:
    print("\n=== what a wildcard would change ===")
    reviewed = {"command": "uv", "args": ["run"], "disabled": False, "autoApprove": ["ping"]}
    wildcard = {"command": "uv", "args": ["run"], "disabled": False, "autoApprove": ["*"]}
    for label, spec in (("explicit list", reviewed), ("wildcard", wildcard)):
        print(f"  {label:14} review step: "
              f"{'REMOVED for every tool' if '*' in spec['autoApprove'] else 'kept for unlisted tools'}")
    print("  A wildcard is not a convenience setting. It is the deletion of the human review")
    print("  step that the whole security module (M10) is about.")


async def main() -> None:
    data = json.loads(SETTINGS.read_text(encoding="utf-8"))
    servers = show_settings(data)

    enabled = {n: s for n, s in servers.items() if not s.get("disabled")}
    print(f"\n  enabled servers: {sorted(enabled)}")
    print(f"  cwd the host would use if you omit --directory: {os.getcwd()}")

    if "course-hello" in enabled:
        await prove_it_launches(enabled["course-hello"])
    await the_uv_shortcut("M4_fastmcp_basics.code.hello_server")
    what_a_wildcard_would_do()

    print("\n=== translate this to any host ===")
    print("  Cline, Claude Desktop, Zed, an IDE plugin: same fields, different file name.")
    print("  If you can describe a server as command + args, you can register it anywhere.")


if __name__ == "__main__":
    asyncio.run(main())
