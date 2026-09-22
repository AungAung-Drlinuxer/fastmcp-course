"""M5_tools LAB 9 — httpx hygiene: timeouts, User-Agent, raise_for_status, offline testability.

This lab needs no internet. Two mechanisms are used on purpose, because they test different
things:

  * a loopback HTTP server  — a REAL socket, so `timeout=` really fires;
  * `httpx.MockTransport`   — no socket at all, so the 200/403 paths are exact and fast.

The behaviour reproduced here was measured against Wikipedia first: without a custom
User-Agent the request is refused with 403. A tool that does not set one works on your laptop
and fails on the server that matters.

Run:
    uv run python -m M5_tools.code.lab_9_http_client_hygiene
"""
from __future__ import annotations

import asyncio
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httpx

UA = "fastmcp-course/0.1 (lab 9)"


class _Handler(BaseHTTPRequestHandler):
    """A tiny upstream: one happy route, one slow route, one failing route."""

    def do_GET(self) -> None:  # noqa: N802 — the stdlib names this method
        if "fastmcp-course" not in self.headers.get("User-Agent", ""):
            self._send(403, {"error": {"code": "forbidden",
                                       "info": "set a descriptive User-Agent"}})
            return
        if self.path.startswith("/slow"):
            time.sleep(1.0)
            self._send(200, {"ok": True, "route": "slow"})
            return
        if self.path.startswith("/flaky"):
            self._send(503, {"error": {"code": "service_unavailable"}})
            return
        self._send(200, {"ok": True, "route": "ok"})

    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args: object) -> None:
        pass  # keep the lab output clean

    def handle_one_request(self) -> None:
        try:
            super().handle_one_request()
        except ConnectionAbortedError:
            pass  # the client walked away after its timeout; that is the point of the test


class _Server(ThreadingHTTPServer):
    def handle_error(self, request: object, client_address: object) -> None:
        pass  # a timed-out client is an expected outcome here, not a stack trace


def _start_server() -> tuple[ThreadingHTTPServer, str]:
    server = _Server(("127.0.0.1", 0), _Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"


async def _attempt(label: str, coro) -> None:
    try:
        response = await coro
        print(f"    {label:34} -> {response.status_code} {json.dumps(response.json())}")
    except httpx.HTTPStatusError as exc:
        print(f"    {label:34} -> HTTPStatusError: {str(exc).splitlines()[0][:64]}")
    except httpx.TimeoutException as exc:
        print(f"    {label:34} -> {type(exc).__name__}")
    except httpx.HTTPError as exc:
        print(f"    {label:34} -> {type(exc).__name__}: {exc}")


async def mock_transport_demo() -> None:
    """No socket: the 200 and 403 paths, exactly and instantly."""
    def handler(request: httpx.Request) -> httpx.Response:
        if "fastmcp-course" not in request.headers.get("User-Agent", ""):
            return httpx.Response(403, json={"error": {"code": "forbidden"}})
        return httpx.Response(200, json={"ok": True, "echo_ua": request.headers["User-Agent"]})

    print("=== MockTransport: the User-Agent contract, no network needed ===")
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler), timeout=5.0) as client:
        await _attempt("with a descriptive User-Agent",
                       client.get("https://upstream.invalid/api", headers={"User-Agent": UA}))
        await _attempt("without one (httpx default)",
                       client.get("https://upstream.invalid/api"))

        print("\n=== raise_for_status turns a bad status into an exception ===")
        response = await client.get("https://upstream.invalid/api")
        print(f"    status without raise_for_status   {response.status_code}")
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            print(f"    raise_for_status                  {type(exc).__name__}")
            print(f"    what it tells you                 {exc.response.status_code} "
                  f"{json.dumps(exc.response.json())}")


async def loopback_demo(base: str) -> None:
    print("\n=== a real socket, so `timeout=` really fires ===")
    async with httpx.AsyncClient(timeout=0.2) as impatient:
        await _attempt("good route, timeout=0.2", impatient.get(f"{base}/ok", headers={"User-Agent": UA}))
    async with httpx.AsyncClient(timeout=0.2) as impatient:
        await _attempt("slow route, timeout=0.2", impatient.get(f"{base}/slow", headers={"User-Agent": UA}))
    async with httpx.AsyncClient(timeout=5.0) as patient:
        await _attempt("slow route, timeout=5.0", patient.get(f"{base}/slow", headers={"User-Agent": UA}))
    async with httpx.AsyncClient(timeout=5.0) as client:
        await _attempt("failing route", client.get(f"{base}/flaky", headers={"User-Agent": UA}))
    async with httpx.AsyncClient(timeout=5.0) as client:
        await _attempt("no User-Agent, loopback", client.get(f"{base}/ok"))


async def main() -> None:
    server, base = _start_server()
    try:
        await mock_transport_demo()
        await loopback_demo(base)

        print("\n=== the three habits, in one place ===")
        print("    timeout=      every request gets a deadline; without it a hung upstream hangs the tool")
        print("    User-Agent    identifies your client; Wikimedia answers 403 without one")
        print("    raise_for_status()  a 4xx/5xx is not silently parsed as JSON and returned as data")
    finally:
        server.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
