"""LAB 5 — a client that reads EVERYTHING this server publishes.

The generic reader every MCP host needs, in about thirty lines:
    1. enumerate the static resources      -> read each one
    2. enumerate the templates             -> substitute a variable, then read
    3. cope with BOTH item shapes          -> TextResourceContents | BlobResourceContents
    4. cope with a resource that fails     -> MCPError, not a traceback

Run:
    uv run python -m M6_resources.code.lab_5_reader_loop
"""
from __future__ import annotations

import asyncio
import base64
from pathlib import Path

from fastmcp import Client, FastMCP

mcp = FastMCP("lab5-reader")

LAB_DATA = Path(__file__).with_name("lab_data")
LAB_DATA.mkdir(exist_ok=True)

(LAB_DATA / "postgres.md").write_text(
    "# PostgreSQL runbook\n\n1. `cnpg status postgres-ha`\n", encoding="utf-8")
(LAB_DATA / "logo.png").write_bytes(b"\x89PNG\r\n\x1a\nlab5-bytes")


@mcp.resource("inventory://hosts", mime_type="application/json")
def hosts() -> dict:
    """The host inventory, structured."""
    return {"hosts": ["pve01", "kasm-agent1"]}


@mcp.resource("logo://site", mime_type="image/png")
def logo() -> bytes:
    """A binary resource — the client receives a BLOB, not text."""
    return (LAB_DATA / "logo.png").read_bytes()


@mcp.resource("runbook://{service}", mime_type="text/markdown")
def runbook(service: str) -> str:
    """The runbook for a named service.

    Args:
        service: The service whose runbook to read.
    """
    path = LAB_DATA / f"{service}.md"
    if not path.is_file():
        available = sorted(p.stem for p in LAB_DATA.glob("*.md"))
        raise FileNotFoundError(
            f"no runbook for {service!r}; available: {', '.join(available) or 'none'}")
    return path.read_text(encoding="utf-8")


def describe_item(item: object) -> str:
    """Return a one-line summary of whatever shape the server sent back."""
    mime = getattr(item, "mime_type", "?")
    if hasattr(item, "text"):
        text = str(getattr(item, "text"))
        return f"{type(item).__name__} mime={mime} chars={len(text)}"
    blob = str(getattr(item, "blob", ""))
    return f"{type(item).__name__} mime={mime} bytes={len(blob)}"


async def main() -> None:
    async with Client(mcp) as client:
        print("=== 1. static resources ===")
        for resource in await client.list_resources():
            print(f"  {str(resource.uri):20} {resource.mime_type}")
            result = await client.read_resource(str(resource.uri))
            print(f"    -> {describe_item(result[0])}")

        print("\n=== 2. templates, materialised by hand ===")
        # A template is a rule; only YOUR code knows a valid value for {service}.
        sample_values = {"runbook://{service}": "postgres"}
        for template in await client.list_resource_templates():
            sample = sample_values.get(template.uri_template)
            if sample is None:
                print(f"  {template.uri_template} -- no sample value, skipping")
                continue
            uri = template.uri_template.replace("{service}", sample)
            result = await client.read_resource(uri)
            print(f"  {uri} -> {describe_item(result[0])}")

        print("\n=== 3. both item shapes, side by side ===")
        text_item = (await client.read_resource("inventory://hosts"))[0]
        blob_item = (await client.read_resource("logo://site"))[0]
        print("  text item .text  :", repr(text_item.text)[:60])
        print("  text item .blob  :", hasattr(text_item, "blob"))
        print("  blob item .text  :", hasattr(blob_item, "text"))
        print("  blob item .blob  :", blob_item.blob[:24], "...")
        print("  blob decodes to  :", base64.b64decode(blob_item.blob))
        print("  dict-shaped JSON :", text_item.text)

        print("\n=== 4. a resource that fails, handled as data ===")
        for uri in ("runbook://postgres", "runbook://oracle"):
            try:
                result = await client.read_resource(uri)
                print(f"  {uri:24} -> ok, {len(result[0].text)} chars")
            except Exception as exc:
                print(f"  {uri:24} -> {type(exc).__name__}: "
                      f"{str(exc).splitlines()[0][:120]}")

        print("\n=== 5. the deprecated spelling still works, but warns ===")
        import warnings

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _ = text_item.mimeType
            for warning in caught:
                print(f"  {warning.category.__name__}: {str(warning.message)[:100]}")


if __name__ == "__main__":
    asyncio.run(main())
