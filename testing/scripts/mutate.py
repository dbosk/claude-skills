#!/usr/bin/env python3
"""Check that the tests catch a deliberate break, then undo it.

    mutate.py [--no-baseline] FILE OLD NEW -- TEST COMMAND [ARG ...]
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

Exit status: 0 the mutant was killed (the command failed), 1 it survived
(the command passed: no test noticed the change), 2 usage error (OLD not
found, or found more than once: make it longer) or a red baseline.  If the process is
killed hard, the original is in the backup file this script names.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def run(command: list[str]) -> int:
    """Run with a fresh bytecode cache: a mutant written in the same second
    as the last run, with the same size, would otherwise load stale .pyc."""
    with tempfile.TemporaryDirectory(prefix="mutate-pycache-") as cache:
        return subprocess.run(command, env={**os.environ,
                                            "PYTHONPYCACHEPREFIX": cache}).returncode


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    baseline = "--no-baseline" not in argv[:argv.index("--")] if "--" in argv else True
    if not baseline:
        argv.remove("--no-baseline")
    if "--" not in argv or argv.index("--") != 3 or len(argv) < 5:
        print(__doc__, file=sys.stderr)
        return 2
    path, old, new, command = Path(argv[0]), argv[1], argv[2], argv[4:]
    original = path.read_bytes()
    text = original.decode("utf-8")
    count = text.count(old)
    if count != 1:
        print(f"mutate: {old!r} occurs {count} times in {path}; need exactly one",
              file=sys.stderr)
        return 2
    if baseline and run(command) != 0:
        print("mutate: the baseline is red: the command fails without the mutation, "
              "so a failure would prove nothing; narrow it to passing tests",
              file=sys.stderr)
        return 2
    fd, backup = tempfile.mkstemp(prefix=f"mutate-{path.name}-")
    with os.fdopen(fd, "wb") as f:
        f.write(original)
    print(f"mutate: original saved in {backup} until the run ends", file=sys.stderr)
    try:
        path.write_bytes(text.replace(old, new).encode("utf-8"))
        status = run(command)
    finally:
        path.write_bytes(original)
        os.unlink(backup)
    if status == 0:
        print(f"mutant SURVIVED: {path}: {old!r} -> {new!r}; no test noticed")
        return 1
    print(f"mutant killed (exit {status}): {path}: {old!r} -> {new!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
