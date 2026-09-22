"""LAB 6 — the allowlist root, and why the check must run AFTER `.resolve()`.

The lesson is one sentence long: **compare resolved paths, never raw strings.** This lab builds
a small sandbox on your own disk, puts a secret one directory ABOVE it, and then tries to reach
the secret through three different doors. Two of the three doors are invisible to a string
comparison, which is exactly why string comparison is the classic bypass.

Nothing here needs root, needs the network, or touches a file outside a temporary directory.

Run:
    uv run python -m M10_security.code.lab_2_confinement
"""
from __future__ import annotations

import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------------------
# The two checks. Same intent, different order of operations.
# ---------------------------------------------------------------------------------------


def check_raw(root: Path, user_path: str) -> Path:
    """The NAIVE check: build the string, compare it to the root string.

    This is what most first drafts do, and it is why `../../etc/shadow` gets through.
    """
    candidate = root / user_path          # no resolve()
    if not str(candidate).startswith(str(root)):
        raise ValueError(f"outside the root: {user_path!r}")
    return candidate


def check_resolved(root: Path, user_path: str) -> Path:
    """The CORRECT check: resolve first, then compare real, absolute locations."""
    candidate = (root / user_path).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"outside the root: {user_path!r}")
    return candidate


def verdict(label: str, path: str, fn, root: Path) -> None:
    try:
        result = fn(root, path)
    except ValueError as exc:
        print(f"  {label:26} {path!r:34} -> REFUSED ({exc})")
        return
    exists = "exists" if result.exists() else "does not exist"
    inside = result.is_relative_to(root)
    print(f"  {label:26} {path!r:34} -> allowed  resolved={result}")
    print(f"  {'':26} {'':34}    {exists}, lexical_inside_root={inside}")
    truth = result.resolve()
    if truth != result:
        print(f"  {'':26} {'':34}    ⭐ that path does NOT exist as written; it resolves to {truth}")


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        logs = base / "logs"
        logs.mkdir()
        (logs / "postgres.log").write_text("INFO checkpoint complete\n", encoding="utf-8")

        # The asset we are protecting: readable by this process, one level above the root.
        secret = base / "secret.env"
        secret.write_text("PGPASSWORD=correct-horse-battery-staple\n", encoding="utf-8")

        root = logs.resolve()
        print(f"sandbox base : {base}")
        print(f"allowlist ROOT: {root}")
        print(f"the asset     : {secret}  (one directory ABOVE the root)\n")

        attempts = [
            "postgres.log",           # legitimate
            "../secret.env",          # traversal
            "..\\secret.env",         # traversal with Windows separators
            str(secret),              # absolute path
        ]

        print("=== check_raw: compare the RAW string (the naive version) ===")
        for path in attempts:
            verdict("check_raw", path, check_raw, root)

        print("\n=== check_resolved: compare RESOLVED paths (the refactor) ===")
        for path in attempts:
            verdict("check_resolved", path, check_resolved, root)

        # ---------------------------------------------------------------------------------
        # The third door: a symlink INSIDE the root that points OUTSIDE it.
        # The name contains no "..", and the raw string genuinely lives under the root.
        # ---------------------------------------------------------------------------------
        print("\n=== the third door: a symlink inside the root pointing outside ===")
        link = logs / "shortcut.log"
        try:
            link.symlink_to(secret)
            symlink_made = True
        except (OSError, NotImplementedError) as exc:
            symlink_made = False
            print(f"  could not create a symlink here ({type(exc).__name__}); on Windows enable")
            print("  Developer Mode or run the lab on WSL/Ubuntu. The reasoning below still holds.")

        if symlink_made:
            verdict("check_raw", "shortcut.log", check_raw, root)
            verdict("check_resolved", "shortcut.log", check_resolved, root)
            print("  read `shortcut.log` with the naive check and you get:")
            print(f"    { (root / 'shortcut.log').read_text(encoding='utf-8').strip()!r}")
        else:
            print("  expected with the naive check : allowed  -> the secret is returned")
            print("  expected with the refactor    : REFUSED  -> .resolve() followed the link")

        # ---------------------------------------------------------------------------------
        # The rule, stated so it can be copied into a code review checklist.
        # ---------------------------------------------------------------------------------
        print("\n=== the rule ===")
        print("  1. join first:   candidate = ROOT / user_path")
        print("  2. resolve BEFORE the check:  candidate = candidate.resolve()")
        print("  3. compare resolved, absolute locations, and allow ROOT itself:")
        print("       candidate == ROOT or ROOT in candidate.parents")
        print("  4. return the resolved path, and read from THAT object — never from the input")
        print("     string a second time (a time-of-check / time-of-use gap hides there).")
        print("\n  A raw-string comparison misses `..` traversal AND symlink escapes.")
        print("  Resolving first closes both, because both are string tricks that resolution undoes.")


if __name__ == "__main__":
    main()
