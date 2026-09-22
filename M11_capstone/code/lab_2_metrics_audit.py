"""LAB 2 — audit the host metrics against what the estate DECLARES.

`system_metrics` reports what the machine IS. `config://<host>` reports what somebody SAID the
machine is. Neither is a lie; the gap between them is the whole of capacity management.

The honesty rule is exercised here from both sides:

  * a field the platform does not expose comes back as `null` — the lab prints `not exposed`,
    never a substituted guess
  * the lab refuses to compute a percentage when the denominator is `null`

That second rule is the one students get wrong. `null / anything` is not 0%: it is UNKNOWN, and a
capacity report that prints 0% for an unmeasured host is worse than one that prints nothing.

Run:
    uv run python -m M11_capstone.code.lab_2_metrics_audit
"""
from __future__ import annotations

import asyncio

from fastmcp import Client

from M11_capstone.code.devops_assistant import mcp


def parse_scalar_yaml(text: str) -> dict[str, str]:
    """A deliberately tiny reader for the two flat keys this lab needs.

    No PyYAML, because the point of this lab is not YAML: it is that the server reads the config
    through a RESOURCE and the lab compares it with a TOOL's measurement.
    """
    out: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith((" ", "-", "#")) or ":" not in line:
            continue
        key, _, rest = line.partition(":")
        out[key.strip()] = rest.strip()
    return out


def show(label: str, value: object, unit: str = "") -> str:
    """Render a possibly-null measurement without ever substituting for it."""
    if value is None:
        return f"{label:22} not exposed by this platform"
    return f"{label:22} {value}{unit}"


async def main() -> None:
    async with Client(mcp) as client:
        metrics = (await client.call_tool("system_metrics", {})).data

        print("=== 1. the raw measurement, nulls included ===")
        print(show("host", metrics["host"]))
        print(show("cpu_count", metrics["cpu_count"]))
        print(show("load_average", metrics["load_average"]))
        print(show("memory_total_gb", metrics["memory_total_gb"], " GB"))
        print(show("memory_available_gb", metrics["memory_available_gb"], " GB"))
        print(show("data_disk_total_gb", metrics["data_disk_total_gb"], " GB"))
        print(show("data_disk_free_gb", metrics["data_disk_free_gb"], " GB"))
        print(f"  note                   {metrics['note']}")

        print("\n=== 2. disk: both numbers present, so a percentage IS computable ===")
        total = metrics["data_disk_total_gb"]
        free = metrics["data_disk_free_gb"]
        if total and free is not None:
            used_pct = round((total - free) / total * 100, 1)
            verdict = "ABOVE 70% — investigate" if used_pct > 70 else "below 70% — nothing to do"
            print(f"  data disk used         {used_pct}%  -> {verdict}")
        else:
            print("  data disk used         cannot be computed: a null input")

        print("\n=== 3. memory: the honest branch ===")
        mem_total = metrics["memory_total_gb"]
        mem_available = metrics["memory_available_gb"]
        if mem_total is None or mem_available is None:
            print("  memory used            UNKNOWN — this platform does not expose /proc/meminfo")
            print("                         (correct answer: say so, do NOT print 0.0%)")
        else:
            print(f"  memory used            "
                  f"{round((mem_total - mem_available) / mem_total * 100, 1)}%")

        print("\n=== 4. declared vs measured, per host in the estate ===")
        configs = (await client.call_tool("list_runbooks", {})).data  # proves the tool is cheap
        print(f"  (sanity: runbooks available {configs['runbooks']})")
        for host in ("pve01", "kasm-agent1"):
            declared = parse_scalar_yaml((await client.read_resource(f"config://{host}"))[0].text)
            print(f"\n  --- {host} ---")
            print(f"    declared role        {declared.get('role', '?')}")
            print(f"    declared cpu_cores   {declared.get('cpu_cores', '?')}")
            print(f"    declared memory_gb   {declared.get('memory_gb', '?')}")
            print(f"    measured cpu_count   {metrics['cpu_count']}")
            print("    NOTE: the measured values belong to the machine this SERVER runs on, not")
            print("          necessarily to the declared host. In a lab VM they are the same")
            print("          box; in a real estate you point one server per host at that host.")

        print("\n=== 5. a capability probe, not a guess ===")
        print("  to populate load_average and memory on Linux, run the same lab on the lab VM:")
        print("    uv run python -m M11_capstone.code.lab_2_metrics_audit")
        print("  Same code, different platform, different — and equally truthful — nulls.")


if __name__ == "__main__":
    asyncio.run(main())
