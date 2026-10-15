#!/usr/bin/env python3
"""Check that the tests catch a deliberate break, then undo it.

    mutate.py [--no-baseline] [--timeout SECONDS] FILE OLD NEW -- TEST COMMAND [ARG ...]
    mutate.py src/mod.py "a + b" "a - b" -- pytest -q tests/test_mod.py
    mutate.py src/pkg/mod.nw "logger.info(" "logger.debug(" -- make test

Replaces the one occurrence of OLD in FILE with NEW, runs the command,
and restores FILE byte for byte, also on Ctrl-C.  In a literate project
mutate the .nw source and give the command that tangles and tests.

The command is first run on the unchanged code and must pass: on a red
baseline every mutant would look killed.  Narrow the command to tests
that pass (pytest -k, or PYTESTFLAGS for a make target), or skip the
check with --no-baseline when you know it is green.  Choose mutations
that still run: a mutant that breaks the syntax is "killed" by any test.

--timeout ends a run that takes longer (default: none).  A mutant that
makes the tests hang counts as killed; a baseline that hangs is red.
The file is restored also when this script is stopped with SIGTERM or
SIGHUP (offline_run.py's timeout sends SIGTERM first).

Exit status: 0 the mutant was killed (the command failed), 1 it survived
(the command passed: no test noticed the change), 2 usage error (OLD not
found, or found more than once: make it longer) or a red baseline.  If the process is
killed hard (SIGKILL), the original is in the backup file this script names.
In a literate project the tangled files still hold the mutant after a
run, until the next build: rebuild before trying anything by hand.
"""

import os
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

HUNG = None  # run()'s result when the command timed out


def stop(signum, frame):
    raise SystemExit(128 + signum)  # unwinds through the finally that restores


def run(command: list[str], timeout: float | None) -> int | None:
    """Run with a fresh bytecode cache: a mutant written in the same second
    as the last run, with the same size, would otherwise load stale .pyc.
    The command gets its own process group, so a hang or our own stop
    takes all of it down."""
    with tempfile.TemporaryDirectory(prefix="mutate-pycache-") as cache:
        process = subprocess.Popen(command, start_new_session=True,
                                   env={**os.environ, "PYTHONPYCACHEPREFIX": cache})
        try:
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            return HUNG
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--" not in argv:
        print(__doc__, file=sys.stderr)
        return 2
    head, command = argv[:argv.index("--")], argv[argv.index("--") + 1:]
    baseline, timeout = True, None
    while head and head[0] in ("--no-baseline", "--timeout"):
        flag = head.pop(0)
        if flag == "--no-baseline":
            baseline = False
        elif head:
            timeout = float(head.pop(0))
    if len(head) != 3 or not command:
        print(__doc__, file=sys.stderr)
        return 2
    for signum in (signal.SIGTERM, signal.SIGHUP):
        signal.signal(signum, stop)
    path, old, new = Path(head[0]), head[1], head[2]
    original = path.read_bytes()
    text = original.decode("utf-8")
    count = text.count(old)
    if count != 1:
        print(f"mutate: {old!r} occurs {count} times in {path}; need exactly one",
              file=sys.stderr)
        return 2
    if baseline and run(command, timeout) != 0:
        print("mutate: the baseline is red: the command fails (or hangs) without "
              "the mutation, so a failure would prove nothing; narrow it to "
              "passing tests", file=sys.stderr)
        return 2
    fd, backup = tempfile.mkstemp(prefix=f"mutate-{path.name}-")
    with os.fdopen(fd, "wb") as f:
        f.write(original)
    print(f"mutate: original saved in {backup} until the run ends", file=sys.stderr)
    try:
        path.write_bytes(text.replace(old, new).encode("utf-8"))
        status = run(command, timeout)
    finally:
        path.write_bytes(original)
        os.unlink(backup)
    if status == 0:
        print(f"mutant SURVIVED: {path}: {old!r} -> {new!r}; no test noticed")
        return 1
    if status is HUNG:
        print(f"mutant killed (timeout after {timeout:g} s: it hangs): "
              f"{path}: {old!r} -> {new!r}")
        return 0
    print(f"mutant killed (exit {status}): {path}: {old!r} -> {new!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
