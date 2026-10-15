#!/usr/bin/env python3
"""Check that the tests catch a deliberate break, then undo it.

    mutate.py [--no-baseline] [--timeout SECONDS] FILE OLD NEW -- TEST COMMAND [ARG ...]
    mutate.py [--no-baseline] [--timeout SECONDS] --batch MUTANTS -- TEST COMMAND [ARG ...]
    mutate.py src/mod.py "a + b" "a - b" -- pytest -q tests/test_mod.py
    mutate.py src/pkg/mod.nw "logger.info(" "logger.debug(" -- make test

Replaces the one occurrence of OLD in FILE with NEW, runs the command,
and restores FILE byte for byte, also on Ctrl-C.  In a literate project
mutate the .nw source and give the command that tangles and tests.

--batch tries several mutants, one at a time, each on the original file,
and prints a table; the command's output goes to one log per mutant
(LABEL.log, and baseline.log) in a directory it names.  Every mutant is checked (OLD found exactly once)
before anything runs.  The file holds blocks separated by blank lines; a
header `LABEL FILE` (or just `FILE`, relative to the working directory),
then the old text as `- ` lines and the new text as `+ ` lines, copied
as they are, so code with quotes, backslashes or several lines needs no
escaping (a bare `-` or `+` is an empty line; no `+` lines deletes):

    # lines starting with # are comments
    M1 src/pkg/hr.nw
    - if part_hour > QUARTER:
    + if part_hour >= QUARTER:

    M2 src/pkg/track.nw
    -     cur_end = max(cur_end, end)
    +     cur_end = end

The command is first run on the unchanged code and must pass: on a red
baseline every mutant would look killed.  Narrow the command to tests
that pass (pytest -k, or the make target's flag variable), or skip the
check with --no-baseline when you know it is green.  Choose mutations
that still run: a mutant that breaks the syntax is "killed" by any test.

--timeout ends a run that takes longer (default: none).  A mutant that
makes the tests hang counts as killed; a baseline that hangs is red.
The file is restored also when this script is stopped with SIGTERM or
SIGHUP (offline_run.py's timeout sends SIGTERM first).

Exit status: 0 the mutant was killed (the command failed; in a batch:
all were), 1 it survived (the command passed: no test noticed the
change; in a batch: at least one did), 2 usage error (OLD not found, or
found more than once: the lines are named, make it longer), a red
baseline, or a command that ran no tests (pytest's exit 5; a make target
may hide it, which the baseline catches).  On the command line OLD and
NEW may span lines ($'a\\nb' in bash); a batch file is easier.
The backup goes to $TMPDIR (default /tmp).  If the process is
killed hard (SIGKILL), the original is in the backup file this script names.
In a literate project the tangled files still hold the mutant after a
run, until the next build: rebuild before trying anything by hand.
"""

import contextlib
import os
import signal
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

HUNG = None  # run()'s result when the command timed out
NO_TESTS = 5  # pytest's exit status when the selection (-k, paths) is empty


@dataclass
class Mutant:
    label: str
    path: Path
    old: str
    new: str

    def describe(self) -> str:
        return f"{self.path}: {self.old!r} -> {self.new!r}"


def stop(signum, frame):
    raise SystemExit(128 + signum)  # unwinds through the finally that restores


def run(command: list[str], timeout: float | None, log: Path | None = None) -> int | None:
    """Run with a fresh bytecode cache: a mutant written in the same second
    as the last run, with the same size, would otherwise load stale .pyc.
    The command gets its own process group, so a hang or our own stop
    takes all of it down.  With `log`, its output goes there."""
    with tempfile.TemporaryDirectory(prefix="mutate-pycache-") as cache, \
            (open(log, "wb") if log else contextlib.nullcontext()) as out:
        process = subprocess.Popen(command, start_new_session=True, stdout=out, stderr=out,
                                   env={**os.environ, "PYTHONPYCACHEPREFIX": cache})
        try:
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            return HUNG
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()


def parse_batch(text: str) -> list[Mutant]:
    mutants, block = [], []
    for line in [*text.splitlines(), ""]:
        if line.startswith("#"):
            continue
        if line.strip():
            block.append(line)
            continue
        if block:
            header, body = block[0].split(), block[1:]
            if not 1 <= len(header) <= 2 or any(b[:1] not in "-+" or b[1:2] not in ("", " ")
                                                  for b in body):
                raise ValueError(f"bad block starting {block[0]!r}: want `LABEL FILE`, "
                                 "then `- old` and `+ new` lines")
            label = header[0] if len(header) == 2 else f"M{len(mutants) + 1}"
            mutants.append(Mutant(label, Path(header[-1]),
                                  "\n".join(b[2:] for b in body if b[0] == "-"),
                                  "\n".join(b[2:] for b in body if b[0] == "+")))
            block = []
    return mutants


def check(mutant: Mutant) -> str | None:
    """Why the mutant cannot be applied, or None.  Sets nothing."""
    try:
        text = mutant.path.read_bytes().decode("utf-8")
    except OSError as err:
        return f"cannot read {mutant.path}: {err.strerror}"
    if not mutant.old:
        return "no `-` lines: nothing to replace"
    starts, i = [], text.find(mutant.old)
    while i >= 0:
        starts.append(text.count("\n", 0, i) + 1)
        i = text.find(mutant.old, i + 1)
    if len(starts) != 1:
        where = f" (lines {', '.join(map(str, starts))})" if starts else ""
        return (f"{mutant.old!r} occurs {len(starts)} times in {mutant.path}{where}; "
                "need exactly one: make it longer")
    return None


def line_of(mutant: Mutant) -> int:
    text = mutant.path.read_text(encoding="utf-8")
    return text.count("\n", 0, text.index(mutant.old)) + 1


def try_mutant(mutant: Mutant, command: list[str], timeout: float | None,
               log: Path | None = None) -> int | None:
    """Apply, run, restore.  The command's exit status, or HUNG."""
    original = mutant.path.read_bytes()
    text = original.decode("utf-8")
    fd, backup = tempfile.mkstemp(prefix=f"mutate-{mutant.path.name}-")
    with os.fdopen(fd, "wb") as f:
        f.write(original)
    print(f"mutate: original saved in {backup} until the run ends", file=sys.stderr)
    try:
        mutant.path.write_bytes(text.replace(mutant.old, mutant.new).encode("utf-8"))
        return run(command, timeout, log)
    finally:
        mutant.path.write_bytes(original)
        os.unlink(backup)


def verdict(status: int | None, timeout: float | None) -> str:
    if status == NO_TESTS:
        return "error: the command ran no tests (pytest exit 5: check -k and the paths)"
    if status == 0:
        return "SURVIVED"
    if status is HUNG:
        return f"killed (timeout after {timeout:g} s: it hangs)"
    return f"killed (exit {status})"


def parse_args(argv: list[str]):
    if "--" not in argv:
        return None
    head, command = argv[:argv.index("--")], argv[argv.index("--") + 1:]
    baseline, timeout, batch = True, None, None
    while head and head[0] in ("--no-baseline", "--timeout", "--batch"):
        flag = head.pop(0)
        if flag == "--no-baseline":
            baseline = False
        elif not head:
            return None
        elif flag == "--timeout":
            timeout = float(head.pop(0))
        else:
            batch = Path(head.pop(0))
    if not command or len(head) != (0 if batch else 3):
        return None
    return baseline, timeout, batch, head, command


def main(argv=None) -> int:
    parsed = parse_args(list(sys.argv[1:] if argv is None else argv))
    if parsed is None:
        print(__doc__, file=sys.stderr)
        return 2
    baseline, timeout, batch, head, command = parsed
    try:
        mutants = (parse_batch(batch.read_text(encoding="utf-8")) if batch
                   else [Mutant("", Path(head[0]), head[1], head[2])])
    except (OSError, ValueError) as err:
        print(f"mutate: {err}", file=sys.stderr)
        return 2
    problems = [(m, check(m)) for m in mutants]
    problems = [(m, why) for m, why in problems if why]
    for m, why in problems:
        print(f"mutate: {m.label + ': ' if m.label else ''}{why}", file=sys.stderr)
    if problems or not mutants:
        if batch:
            print("mutate: nothing was run", file=sys.stderr)
        return 2
    for signum in (signal.SIGTERM, signal.SIGHUP):
        signal.signal(signum, stop)
    logs = Path(tempfile.mkdtemp(prefix="mutate-logs-")) if batch else None
    if logs:
        print(f"mutate: the command's output for each mutant: logs in {logs}", flush=True)
    if baseline and run(command, timeout, logs and logs / "baseline.log") != 0:
        print("mutate: the baseline is red: the command fails (or hangs) without "
              "the mutation, so a failure would prove nothing; narrow it to "
              "passing tests", file=sys.stderr)
        return 2

    if not batch:
        mutant = mutants[0]
        result = verdict(try_mutant(mutant, command, timeout), timeout)
        if result.startswith("error"):
            print(f"mutate: {result[7:]}, so the mutant was not tried", file=sys.stderr)
            return 2
        if result == "SURVIVED":
            print(f"mutant SURVIVED: {mutant.describe()}; no test noticed")
            return 1
        print(f"mutant {result}: {mutant.describe()}")
        return 0

    rows = []
    for mutant in mutants:
        where = f"{mutant.path}:{line_of(mutant)}"
        log = logs / f"{mutant.label}.log"
        result = verdict(try_mutant(mutant, command, timeout, log), timeout)
        rows.append((mutant.label, where, result))
        print(f"{mutant.label}\t{where}\t{result}", flush=True)
    killed = sum(r.startswith("killed") for _, _, r in rows)
    errors = sum(r.startswith("error") for _, _, r in rows)
    print(f"{killed} of {len(rows)} killed"
          + (f", {errors} not tried (errors)" if errors else ""))
    if errors:
        return 2
    return 0 if killed == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
