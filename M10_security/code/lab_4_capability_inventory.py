"""LAB 4 — the capability budget: what the PROCESS may touch (host-level least privilege).

Server-level least privilege (which path a tool may read) is taught in LAB 6. This lab is about
the layer underneath it: the operating-system identity the server process runs as. A tool
boundary is only as strong as the process it runs inside. If the process is `root`, then a single
bug in the boundary is a whole-host compromise.

The lab MEASURES the five capabilities that matter, then prints them against the budget a
production deployment should meet:

    identity   who the process is        (uid 0 -> everything below is weaker)
    writable   what it can write         (a writable code directory is a persistence path)
    readable   what it can read          (keys, shadow, cloud credentials)
    env        which secrets are in the environment (the process inherits ALL of them)
    egress     whether it could reach out (a tool that can POST is an exfiltration path)

It never prints a secret VALUE — only the names of secret-shaped environment variables, the same
rule LAB 11 applies to the audit trail.

Run:
    uv run python -m M10_security.code.lab_4_capability_inventory
"""
from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

SECRET_HINTS = ("token", "secret", "password", "passwd", "api_key", "apikey", "credential",
                "aws_", "private", "key")


def identity() -> dict:
    """Who am I? `os.getuid` does not exist on Windows, so both shapes are handled."""
    getuid = getattr(os, "getuid", None)
    getgid = getattr(os, "getgid", None)
    uid = getuid() if getuid else None
    return {
        "platform": os.name,
        "uid": uid,
        "gid": getgid() if getgid else None,
        "is_root": uid == 0 if uid is not None else None,
        "user": os.environ.get("USERNAME") or os.environ.get("USER") or "?",
        "cwd": os.getcwd(),
    }


def can_write(path: Path) -> bool:
    """Probe a directory by actually creating and removing a file — `os.access` lies on Windows."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".capability_probe"
        probe.write_text("x", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False


def can_read(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            handle.read(1)
        return True
    except OSError:
        return False


def env_surface() -> list[str]:
    """The NAMES of secret-shaped environment variables. Never the values."""
    return sorted(
        name for name in os.environ
        if any(hint in name.lower() for hint in SECRET_HINTS)
    )


@dataclass(frozen=True)
class Budget:
    capability: str
    measured: str
    target: str
    how: str


def main() -> None:
    who = identity()
    home = Path.home()
    writable = {
        "cwd": can_write(Path.cwd()),
        "home": can_write(home),
        "temp": can_write(Path(tempfile.gettempdir())),
        "repository": can_write(Path(__file__).resolve().parents[2]),
    }
    probe_read = [Path("/etc/shadow"), home / ".ssh" / "id_rsa",
                  home / ".aws" / "credentials", Path("/etc/passwd"), home / ".bashrc"]
    readable = {str(p): can_read(p) for p in probe_read if p.exists() or p.parent.exists()}

    print("=== identity ===")
    for key, value in who.items():
        print(f"  {key:9} {value}")

    print("\n=== writable directories (measured by writing a probe file) ===")
    for name, allowed in writable.items():
        mark = "WRITABLE" if allowed else "read-only"
        print(f"  {name:11} {mark}")

    print("\n=== readable files that a log reader has NO business opening ===")
    for path, allowed in readable.items():
        print(f"  {'READABLE' if allowed else 'blocked':9} {path}")

    print("\n=== environment: secret-shaped variable NAMES only (no values) ===")
    names = env_surface()
    print(f"  {len(names)} variable(s) match a secret pattern: {names}")
    print("  ⭐ every one of these is inherited by the server process. A tool that returns")
    print("     `os.environ` would hand the model all of them at once.")

    print("\n=== the capability budget ===")
    rows = [
        Budget("identity", f"uid={who['uid']} user={who['user']}",
               "a dedicated non-root uid (10001)",
               "USER 10001:10001 in the image; a systemd service account on bare metal"),
        Budget("writable", "cwd=" + ("yes" if writable["cwd"] else "no")
               + " home=" + ("yes" if writable["home"] else "no")
               + " repo=" + ("yes" if writable["repository"] else "no"),
               "logs directory only",
               "--read-only rootfs + one volume (LAB 10); never the code directory"),
        Budget("readable", f"{sum(readable.values())} of {len(readable)} probes readable",
               "the allowlist root only",
               "allowlist root + Path.resolve() confinement (LAB 6) + mount-level limits"),
        Budget("env", f"{len(names)} secret-shaped names present",
               "none needed at runtime",
               "pass configuration as files/volumes; do not bake secrets into ENV"),
        Budget("egress", "not probed in this lab",
               "none, for a file-reading server",
               "--network=none (LAB 10); egress as a deliberate decision, not a default"),
    ]
    for row in rows:
        print(f"\n  capability : {row.capability}")
        print(f"  measured   : {row.measured}")
        print(f"  target     : {row.target}")
        print(f"  how        : {row.how}")

    print("\n=== the rule ===")
    print("  server-level least privilege asks 'what may this TOOL do?'")
    print("  host-level    least privilege asks 'what may this PROCESS do?'")
    print("  ⭐ the second one is the floor. If the process is root, the tool boundary is")
    print("     the only thing standing between a bug and the whole machine.")

    # Assertions that make this file a deploy-time gate on Linux/WSL.
    if who["is_root"] is not None:
        assert not who["is_root"], "the MCP server is running as root — refuse to deploy"
    if writable["repository"]:
        print("\n  WARN  the repository is writable. Expected in a dev checkout; the image")
        print("        makes the code read-only (LAB 10). Not a failure here, never ship it.")
    print(f"\nverdict : PASS — process is not root (uid={who['uid']}); capability budget reported")


if __name__ == "__main__":
    main()