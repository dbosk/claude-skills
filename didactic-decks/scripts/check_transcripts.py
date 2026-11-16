#!/usr/bin/env python3
"""Fail when a \\runpython (or another didactic run) is missing its
transcript in a job's PDF, or the transcript is empty.

Where a transcript lives, per job (read from didactic.sty and
pythontex.sty):

  1. ltxobj/<job>.pytxcode lists every PythonTeX instance the job's last
     pdflatex pass met, as "=>PYTHONTEX#<family>#<session>#<group>#<n>#c#..."
     followed by its code.  \\runpython, \\runshell and the pair commands
     are \\pyc instances whose code is a call such as
     didactic_output('examples/x.py', ...), didactic_shell(...) or
     didactic_pair(...).  A frame the job never typesets (a notes-only
     \\begin{frame}<article> in the slides) has no instance in that job.
  2. PythonTeX writes what instance n printed to
     ltxobj/<family>_<session>_<group>_<n>.stdout, and pdflatex \\inputs
     it: one or more lines \\didacticinputminted[...]{lang}{<file>}.
  3. <file> (didactic_output_<hash>.txt, didactic_pair_<hash>.txt) sits in
     the deck directory and holds the text minted typesets.  <hash> is the
     start of the SHA-256 of the content, so the empty transcript has a
     fixed name, ..._e3b0c44298fc1c14.txt.

Both jobs write the same .stdout names into the shared ltxobj/, and
PythonTeX deletes the files it no longer needs when it reruns.  After a
full build the slides' PythonTeX run has deleted the .stdout files of the
notes-only runs; the next notes pass that does not rerun PythonTeX (an
incremental build, latexmk sees the .pytxcode unchanged) then finds no
file and prints nothing at all: no ??, no error, no MINTED.  Measured on
Klasser och objekt, 2026-11-16: 16 of 27 transcripts gone, every other
check green.

What a pass read is in its recorder file, ltxobj/<job>.fls (latexmk runs
pdflatex with -recorder).  For each run instance the check fails when

  - the last pass did not read its .stdout (not in <job>.fls): the
    transcript is missing from the PDF;
  - the .stdout names no transcript file (an empty .stdout);
  - a named transcript is empty (the empty hash, or an empty file);
  - a run that shows its command line (showcommand) has a transcript
    whose first line does not name the program: another run's output.

It warns, without failing, when a .stdout the pass read has since been
deleted, or rewritten (newer than <job>.fls), by the other job: the PDF
has the transcript, but the next pass of this job without PythonTeX will
lose it or print another run's output in its place (rebuild clean, the
recipe in references/build-and-gotchas.md, "Stale PythonTeX
transcripts").  build_deck.sh runs the check right after each job, before
the other job's PythonTeX run can change the files.

What it cannot see: a stale but plausible transcript (read the transcripts
against the programs), and a run without showcommand that shows another
run's output.

Usage: check_transcripts.py <deck dir> [notes|slides ...]
Exit 0 when every run has a non-empty transcript, 1 when one does not,
2 when there is nothing to check (no .pytxcode: build the job first).
"""
import os
import re
import sys

# The didactic commands whose output is typeset from a file.  Each prints
# \didacticinputminted (didactic_mint, didactic_pair).
RUN_RE = re.compile(r"^\s*didactic_(output|shell|run_code|pydoc|help|"
                    r"source|pair)\s*\(")
INPUT_RE = re.compile(
    r"\\didacticinputminted(?:\[[^\]]*\])?\{[^}]*\}\{([^}]*)\}")
# didactic_write_file names a file by sha256(content)[:16].
EMPTY_HASH = "e3b0c44298fc1c14"
MODULE_RE = re.compile(r"""^\s*didactic_output\(\s*['"]([^'"]+)['"]""")


def header(line):
    """The fields of an instance header, or None for another line.
    "=>PYTHONTEX#py#default#default#13#c####contents.tex#379#": family,
    session, group, instance, command, then option and context fields
    whose number varies, then the source file (empty when the instance
    comes from a beamer frame's temporary file) and line."""
    parts = line.rstrip("\n").split("#")
    if len(parts) < 9 or not parts[4].isdigit():
        return None
    return {"family": parts[1], "session": parts[2], "group": parts[3],
            "n": parts[4], "cmd": parts[5], "file": parts[-3] or "(frame)",
            "line": parts[-2]}


def instances(pytxcode):
    """[(stdout name, where, call)] of the run instances in a .pytxcode."""
    out, head, code = [], None, []

    def flush():
        if head and head["cmd"] == "c" and code and RUN_RE.match(code[0]):
            name = "{family}_{session}_{group}_{n}.stdout".format(**head)
            where = head["file"] + (":" + head["line"] if head["line"] else "")
            out.append((name, where, code[0].strip()))

    with open(pytxcode, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("=>PYTHONTEX"):
                flush()
                head = header(line)
                code = []
            elif head is not None:
                code.append(line)
    flush()
    return out


def recorded_inputs(fls):
    """Base names of the files a pdflatex pass read, from its .fls, or
    None without one."""
    try:
        with open(fls, encoding="utf-8", errors="replace") as f:
            return {os.path.basename(line[6:].strip())
                    for line in f if line.startswith("INPUT ")}
    except OSError:
        return None


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def faults(deck, stdout, call):
    """What is wrong with one run's output as the files stand now, and the
    transcript files its .stdout names."""
    files = INPUT_RE.findall(read(stdout))
    if not files:
        return [f"{os.path.basename(stdout)} names no transcript (empty "
                f"output)"], files
    found = []
    module = MODULE_RE.match(call)
    for fname in files:
        path = os.path.join(deck, fname)
        text = read(path) if os.path.exists(path) else None
        if (os.path.splitext(fname)[0].endswith("_" + EMPTY_HASH)
                or (text is not None and not text.strip())):
            found.append(f"{fname} is empty")
        elif (text is not None and module and "showcommand=True" in call
                and "commandtext=" not in call):
            first = text.lstrip().split("\n", 1)[0]
            prog = os.path.basename(module.group(1))
            if prog not in first:
                found.append(f"{fname} begins {first!r}, not a run of {prog}")
    return found, files


def check_job(deck, job):
    """Print the job's problems; return (runs, ok, problems), or None
    when the job has no .pytxcode."""
    ltxobj = os.path.join(deck, "ltxobj")
    pytxcode = os.path.join(ltxobj, job + ".pytxcode")
    if not os.path.exists(pytxcode):
        print(f"{job}: no {pytxcode}: build the job first")
        return None
    runs = instances(pytxcode)
    fls = os.path.join(ltxobj, job + ".fls")
    inputs = recorded_inputs(fls)
    if inputs is None:
        print(f"{job}: no ltxobj/{job}.fls: judging by the files present now")
    passed = os.path.getmtime(fls) if inputs is not None else None
    ok, problems, warnings = 0, [], []
    for name, where, call in runs:
        stdout = os.path.join(ltxobj, name)
        exists = os.path.exists(stdout)
        if not (name in inputs if inputs is not None else exists):
            problems.append(f"{where}: the last pass found no {name}, so "
                            f"the transcript is missing from {job}.pdf: {call}")
            continue
        if not exists:
            warnings.append(f"{where}: {name} was read, then deleted (the "
                            f"other job's PythonTeX run): {call}")
            ok += 1
            continue
        found, files = faults(deck, stdout, call)
        # Changed since the pass (the other job's PythonTeX rewrites the
        # shared files, mostly with the same content): what is wrong now
        # is what the next pass without PythonTeX would print, not what
        # the PDF shows.
        changed = passed is not None and any(
            os.path.getmtime(f) > passed
            for f in [stdout] + [os.path.join(deck, n) for n in files]
            if os.path.exists(f))
        if inputs is not None and not changed:
            found += [f"the last pass did not read {n} ({name} names it)"
                      for n in files if n not in inputs]
        if not found:
            ok += 1
        elif changed:
            ok += 1
            warnings += [f"{where}: {f}, changed since the last pass: {call}"
                         for f in found]
        else:
            problems += [f"{where}: {f}: {call}" for f in found]
    for p in problems:
        print(f"{job}: EMPTY {p}")
    for w in warnings:
        print(f"{job}: WARNING {w}")
    if warnings:
        print(f"{job}: {len(warnings)} warning(s): {job}.pdf has these "
              f"transcripts, but the next {job} pass without PythonTeX "
              f"would print what the warnings say; rebuild clean before "
              f"relying on an incremental build")
    print(f"{job}: {len(runs)} runs, {ok} with a transcript, "
          f"{len(problems)} problem(s)")
    return len(runs), ok, len(problems)


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 2
    deck = argv[1]
    jobs = argv[2:] or ["notes", "slides"]
    checked = [r for r in (check_job(deck, j) for j in jobs) if r]
    if not checked:
        return 2
    if any(problems or ok < runs for runs, ok, problems in checked):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
