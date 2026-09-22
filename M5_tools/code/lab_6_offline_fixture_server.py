"""M5_tools LAB 6 — the air-gapped fixture fallback, and honest source reporting.

Two behaviours are compared on the same unavailable upstream:

    fetch_service_status   falls back to a fixture and says so  (source: "fixture")
    fetch_service_strict    refuses, and returns a structured error explaining why

Both are correct. The wrong behaviour — and the one this lab exists to prevent — is a tool
that silently returns yesterday's data as if it were live. Run this with the network up or
down; the output is the same because the "upstream" here is a port nothing listens on.

Run:
    uv run python -m M5_tools.code.lab_6_offline_fixture_server
"""
from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx
from fastmcp import Client, FastMCP

mcp = FastMCP("lab6-offline-fixtures")

# Nothing listens here. Replace with a real URL to see the live path.
UPSTREAM = "http://127.0.0.1:9/status"
TIMEOUT = 1.5

FIXTURES: dict[str, Any] = {
    "checkout": {"service": "checkout", "status": "degraded", "latency_ms": 812,
                 "captured": "2026-09-18T10:00:00Z"},
    "payments": {"service": "payments", "status": "ok", "latency_ms": 41,
                 "captured": "2026-09-18T10:00:00Z"},
}


async def _probe(service: str) -> dict:
    """Return {'source': ..., 'payload': ...} — or raise, if the upstream is unreachable."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(UPSTREAM, params={"service": service},
                                    headers={"User-Agent": "fastmcp-course/0.1 (lab 6)"})
        response.raise_for_status()
        return {"source": "live", "payload": response.json()}


@mcp.tool
async def fetch_service_status(service: str) -> dict:
    """Read a service's health, falling back to a fixture and naming the source.

    Args:
        service: Service name, e.g. 'checkout' or 'payments'.
    """
    try:
        result = await _probe(service)
    except Exception as exc:  # noqa: BLE001 — an unreachable upstream is an expected state
        if service not in FIXTURES:
            return {"ok": False, "source": "none", "error": "no_fixture_for_service",
                    "hint": f"Known services: {', '.join(sorted(FIXTURES))}."}
        return {"ok": True, "source": "fixture",
                "note": f"live probe failed ({type(exc).__name__}); fixture is from "
                        f"{FIXTURES[service]['captured']} and may be stale",
                "stale": True, "service": service, "data": FIXTURES[service]}
    return {"ok": True, "source": "live", "note": None, "stale": False,
            "service": service, "data": result["payload"]}


@mcp.tool
async def fetch_service_strict(service: str) -> dict:
    """Read a service's health, refusing to guess when the upstream is unreachable.

    Args:
        service: Service name.
    """
    try:
        result = await _probe(service)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "source": "none", "error": "upstream_unreachable",
                "hint": f"{type(exc).__name__} reaching {UPSTREAM}. Retry when the network is "
                        "up, or call fetch_service_status for a labelled fixture."}
    return {"ok": True, "source": "live", "note": None, "stale": False,
            "service": service, "data": result["payload"]}


async def main() -> None:
    async with Client(mcp) as client:
        print("=== fixture mode: honest about where the data came from ===")
        for service in ("checkout", "payments"):
            result = await client.call_tool("fetch_service_status", {"service": service})
            print(f"\n--- {service}  is_error={result.is_error}")
            print(json.dumps(result.data, indent=2))

        print("\n=== an unknown service with no fixture to fall back to ===")
        result = await client.call_tool("fetch_service_status", {"service": "search"})
        print(json.dumps(result.data, indent=2))

        print("\n=== strict mode: refuses, and says what to do about it ===")
        result = await client.call_tool("fetch_service_strict", {"service": "checkout"})
        print(json.dumps(result.data, indent=2))
        print(f"is_error={result.is_error}   <- a refusal the agent can plan around")

        print("\n=== the same tool returning as though nothing was wrong (WRONG) ===")
        bad = {"ok": True, "source": "live", "service": "checkout",
               "data": FIXTURES["checkout"]}
        print(json.dumps(bad))
        print("    Nobody can tell this from a real reading. That is the bug this lab prevents.")


if __name__ == "__main__":
    asyncio.run(main())
