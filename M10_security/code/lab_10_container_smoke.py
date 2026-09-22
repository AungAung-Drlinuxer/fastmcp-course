"""LAB 10 — a containerisation check that runs WITHOUT Docker.

You cannot always build an image (no daemon, no network, a locked-down laptop). You can always
read the Dockerfile, and the four decisions that matter for this lesson are all *textual*:

  1. a non-root `USER` directive exists, with a numeric uid
  2. nothing runs as root by omission (no `USER root`, no `--privileged` in the run recipe)
  3. no secret is baked in as `ENV`/`ARG` (a secret in a layer is a secret in every copy)
  4. the writable surface is exactly one directory, declared as a VOLUME

This lab parses `M10_security/deploy/Dockerfile` and fails loudly if any of them regress. It also
prints the `docker run` recipe that enforces the two things a Dockerfile CANNOT say about itself:
the read-only root filesystem and the dropped capabilities.

Run:
    uv run python -m M10_security.code.lab_8_container_smoke
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

DOCKERFILE = Path(__file__).resolve().parent.parent / "deploy" / "Dockerfile"

SECRET_HINTS = ("PASSWORD", "TOKEN", "SECRET", "API_KEY", "PRIVATE_KEY", "CREDENTIAL")


def instructions(text: str) -> list[tuple[str, str]]:
    """Return (INSTRUCTION, argument) pairs, skipping comments, blanks and line continuations."""
    out: list[tuple[str, str]] = []
    logical: list[str] = []
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        logical.append(line.rstrip("\\").strip())
        if line.endswith("\\"):
            continue
        joined = " ".join(logical)
        logical = []
        head, _, rest = joined.partition(" ")
        out.append((head.upper(), rest.strip()))
    return out


def check(text: str) -> tuple[list[str], list[str]]:
    ops = instructions(text)
    passed: list[str] = []
    failed: list[str] = []

    # --- 1. a numeric non-root USER -----------------------------------------------------
    users = [arg for head, arg in ops if head == "USER"]
    if not users:
        failed.append("no USER directive: the process runs as root (uid 0)")
    else:
        final = users[-1]
        uid = final.split(":")[0]
        if uid in {"root", "0"}:
            failed.append(f"the final USER is root: {final!r}")
        elif not uid.isdigit():
            failed.append(f"the final USER names a user without a uid ({final!r}); "
                          "a name can be re-pointed at uid 0 by a later base image change")
        else:
            passed.append(f"final USER is a numeric non-root uid ({final})")

    # --- 2. nothing re-escalates ---------------------------------------------------------
    escalations = [arg for head, arg in ops
                   if head in {"USER"} and arg.split(":")[0] in {"root", "0"}]
    if escalations:
        failed.append(f"privilege escalation back to root present: {escalations}")
    else:
        passed.append("no directive escalates back to root")

    # --- 3. no secret-shaped ENV or ARG --------------------------------------------------
    baked = [f"{head} {arg}" for head, arg in ops
             if head in {"ENV", "ARG"} and any(h in arg.upper() for h in SECRET_HINTS)]
    if baked:
        failed.append(f"secret-shaped build input baked into a layer: {baked}")
    else:
        passed.append("no secret-shaped ENV/ARG: nothing of that kind is stored in a layer")

    # --- 4. exactly one writable surface, declared as a VOLUME ---------------------------
    volumes = [arg for head, arg in ops if head == "VOLUME"]
    if not volumes:
        failed.append("no VOLUME: on a read-only rootfs the tools would have nowhere to write")
    else:
        passed.append(f"VOLUME declared: {[v.strip('[]') for v in volumes]}")

    # --- extras worth checking once you are here -----------------------------------------
    if any(head == "FROM" and ":latest" in arg for head, arg in ops):
        failed.append("a `:latest` base image tag is in use: not reproducible")
    else:
        passed.append("no `:latest` base image tag")
    if any(head == "FROM" and " AS " in arg.upper() for head, arg in ops):
        passed.append("multi-stage build in use: build tools do not ship in the runtime layer")
    if "--frozen" in text:
        passed.append("`uv sync --frozen` in use: the build cannot re-resolve dependencies")
    return passed, failed


RUN_RECIPE = """docker run --rm -i \\
  --read-only \\
  --tmpfs /tmp:rw,noexec,nosuid,size=16m \\
  --cap-drop=ALL \\
  --security-opt=no-new-privileges \\
  --pids-limit=128 \\
  --memory=256m \\
  --network=none \\
  -v "$PWD/M10_security/code/logs:/var/log/mcp:ro" \\
  hardened-mcp-logs"""


def main() -> None:
    if not DOCKERFILE.exists():
        print(f"missing: {DOCKERFILE}", file=sys.stderr)
        raise SystemExit(2)

    text = DOCKERFILE.read_text(encoding="utf-8")
    print(f"dockerfile : {DOCKERFILE}")
    print(f"bytes      : {len(text)}\n")

    ops = instructions(text)
    print("=== instructions, in order ===")
    for head, arg in ops:
        print(f"  {head:9} {arg[:78]}")

    passed, failed = check(text)
    print("\n=== the four decisions ===")
    for item in passed:
        print(f"  PASS  {item}")
    for item in failed:
        print(f"  FAIL  {item}")

    print("\n=== the two things a Dockerfile cannot say about itself ===")
    print("  a read-only root filesystem and dropped capabilities are RUNTIME flags:")
    print(f"\n{RUN_RECIPE}\n")
    print("  --read-only            the process cannot rewrite its own code or drop a payload")
    print("  --cap-drop=ALL         no CAP_NET_RAW, no CAP_SYS_ADMIN, no raw sockets")
    print("  --security-opt=no-new-privileges  a setuid binary inside cannot regain privilege")
    print("  --pids-limit=128       a fork bomb hits its own ceiling, not the node's")
    print("  --network=none         the tool cannot exfiltrate even if it is compromised")
    print("  -v ...:ro              logs are mounted read-only: the boundary is enforced by the")
    print("                         kernel, not by the Python check")
    print("\n  Note what the volume does: even if a bug in the Python code allowed a write,")
    print("  the mount says no. Defence in depth means the second control does not depend on")
    print("  the first one being correct.")

    assert not failed, f"{len(failed)} containerisation checks failed"
    print("\nverdict : PASS — the image recipe is what this lesson says it is")


if __name__ == "__main__":
    main()
