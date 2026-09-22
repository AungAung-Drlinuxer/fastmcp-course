"""LAB 5 — why `subprocess.run(command, shell=True)` is a structural problem.

This lab never removes a file, never reaches the network, and never reads a secret. It only
*echoes*. The point is to watch, with your own eyes, that the string you hand to `shell=True`
is not one command — it is a tiny program in a language you did not agree to accept.

Run:
    uv run python -m M10_security.code.lab_1_unbounded_tool
"""
from __future__ import annotations

import os
import shlex
import subprocess
import sys
from pathlib import Path

# The chaining operator is a property of the HOST shell, not of Python.
#   cmd.exe (Windows)  :  &   &&   |   and %VAR%
#   sh      (POSIX)    :  ;   &&   |   and $(...)  `...`  ${VAR}
CHAIN = "&" if os.name == "nt" else ";"


def run_with_shell(command: str) -> tuple[int, str, str]:
    """The pattern under test: one string, handed to a shell."""
    completed = subprocess.run(command, shell=True, capture_output=True, text=True)  # noqa: S602
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def run_as_argv(argv: list[str]) -> tuple[int, str, str]:
    """The refactor: a list of words, no shell, no interpretation layer."""
    completed = subprocess.run(argv, shell=False, capture_output=True, text=True)
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def show(label: str, returncode: int, stdout: str, stderr: str) -> None:
    print(f"  {label}")
    print(f"    returncode : {returncode}")
    print(f"    stdout     : {stdout!r}")
    if stderr:
        print(f"    stderr     : {stderr.strip().splitlines()[0]!r}")


def main() -> None:
    print(f"platform      : {sys.platform}  (chain operator used: {CHAIN!r})")
    print(f"interpreter   : {sys.executable}")

    # ---------------------------------------------------------------------------------
    # 1. ONE string, MORE than one command.
    # ---------------------------------------------------------------------------------
    print("\n=== 1. one string is a program, not a command ===")
    single = f"echo first{(' && ' if os.name == 'nt' else ' && ')}echo second"
    show(f"input was: {single!r}  (one 'command')", *run_with_shell(single))

    # ---------------------------------------------------------------------------------
    # 2. The user-supplied NAME is where the injection lives.
    #    This is the `read_log(name)` shape: a tool parameter flows into the string.
    # ---------------------------------------------------------------------------------
    print("\n=== 2. a tool parameter flows into the shell string ===")
    name = f"postgres.log {CHAIN} echo PWNED"
    command = f"echo reading {name}"
    print(f"  tool argument (name) : {name!r}")
    print(f"  shell string built   : {command!r}")
    show("shell=True result", *run_with_shell(command))

    # ---------------------------------------------------------------------------------
    # 3. The same bytes, without a shell: the metacharacter is just a character.
    # ---------------------------------------------------------------------------------
    print("\n=== 3. the same bytes with shell=False ===")
    payload = "postgres.log %s echo PWNED" % CHAIN
    show("argc list result", *run_as_argv([sys.executable, "-c",
                                           f"print({payload!r})"]))

    # ---------------------------------------------------------------------------------
    # 4. `shlex.split` is NOT a fix. It tokenises; it does not validate.
    # ---------------------------------------------------------------------------------
    print("\n=== 4. shlex.split does not make a string safe ===")
    print(f"  shlex.split({f'cat x{CHAIN} id'!r}) -> {shlex.split(f'cat x{CHAIN} id')}")
    print("  three tokens, all still attacker-chosen: shlex is a lexer, not a policy.")

    # ---------------------------------------------------------------------------------
    # 5. No timeout: the call has no upper bound on how long it may hold the worker.
    # ---------------------------------------------------------------------------------
    print("\n=== 5. no timeout means no upper bound ===")
    blocker = (f"{sys.executable} -c \"import time; time.sleep(2)\"" if os.name != "nt"
               else f"{sys.executable} -c \"import time; time.sleep(2)\"")
    print(f"  command: {blocker!r}")
    import time
    started = time.perf_counter()
    rc, _, _ = run_with_shell(blocker)
    print(f"  returncode={rc} after {time.perf_counter() - started:.1f}s")
    print("  with no timeout= argument, a 2-second block is allowed to be a 2-day block.")

    # ---------------------------------------------------------------------------------
    # 6. Unbounded return: stdout is handed back whole.
    # ---------------------------------------------------------------------------------
    print("\n=== 6. the return value is unbounded ===")
    rc, out, _ = run_as_argv([sys.executable, "-c", "print('x' * 200000)"])
    print(f"  returncode={rc}  len(stdout)={len(out)} characters returned unresolved")
    print("  one call can carry ~200,000 characters into the caller's context window.")

    print("\n=== the five structural problems of shell=True ===")
    for number, problem in enumerate([
        "the whole command language is available, not one binary",
        "no allowlist: any binary, any argument",
        "no path confinement: any file the process can read",
        "no timeout: one call can hold the worker forever",
        "no bound on the return: one call can exhaust the context window",
    ], 1):
        print(f"  {number}. {problem}")

    # A closing note that the confinement part is taught in LAB 2.
    print("\nnext: LAB 6 builds the allowlist root and the resolve-before-check rule.")


if __name__ == "__main__":
    main()
