#!/usr/bin/env python3
"""check_transcripts.py --- did a job print the transcripts of its own runs?

PythonTeX writes the output of instance N of a session to
OUTDIR/<family>_<session>_<restart>_N.stdout, a name that does not say
which job wrote it.  Jobs that share an output directory (the two jobs of
an edition, or two editions wrongly built into one directory) therefore
share those files, and a job that LaTeX typesets again without a PythonTeX
run of its own prints whatever the last run of another job left there.
When the other job runs different code at instance N (the other
edition's program, or a \\pause that shifted the slides' instances), the
PDF shows the wrong transcript, and nothing in the log says so.

Two checks, both on what the job's last pass actually read:

provenance  The job's last pass (the mtime of OUTDIR/JOB.log) read the
            .stdout files of the latest PythonTeX run in OUTDIR before it
            (the mtimes of the OUTDIR/*.pytxmcr files, which PythonTeX
            rewrites at the end of every run that ran code).  If that run
            was another job's, its code must equal this job's at every
            instance both have; otherwise this job printed that job's
            output.  Options that only set how a transcript is typeset
            (minted_opts, fullwidth, hlgrep) are left out of the
            comparison, since the slides often set a smaller font.

command     For each \\runpython (didactic_output) whose transcript shows
            the command line (transcript or showcommand, no commandtext),
            the transcript file the job read for that instance (from
            OUTDIR/JOB.fls, which lists the .stdout and then the
            didactic_output_<hash>.txt it names) must name the program the
            instance runs.  The file is read where the .fls says LaTeX read
            it: in OUTDIR since didactic v2.18.1, in the deck directory for
            a job built under an older didactic, so both kinds of build are
            checked the same way.

Usage: check_transcripts.py --job JOB --outdir OUTDIR   (run in the deck)

Exit 0: no wrong transcript found; 1: a wrong transcript; 2: bad usage.
A job without PythonTeX code passes with nothing to check.  When neither
check could read anything (no log, no run, transcript files a later run
deleted), the job still passes, since a later run deleting a job's
outputs is the normal state of some decks after a full build, but the
output says NOTHING CHECKED and why.  The remedy for a wrong transcript
is a PythonTeX run of the job's own: remove OUTDIR/JOB.pytxmcr and build
the job again (build_deck.sh does this before a rebuild by itself).
"""

import argparse
import ast
import os
import re
import sys

HEADER = re.compile(r"^=>PYTHONTEX#([^#]*)#([^#]*)#([^#]*)#(\d+)#([^#]*)#")
STDOUT = re.compile(r"^(.*)_(\d+)\.stdout$")
TRANSCRIPT = re.compile(r"didactic_output_[0-9a-f]+\.txt$")


def read_pytxcode(path):
    """Return {(family, session, restart, instance): code} for a job."""
    entries = {}
    key = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("=>PYTHONTEX:SETTINGS#"):
                break
            m = HEADER.match(line)
            if m:
                key = (m[1], m[2], m[3], int(m[4]))
                entries[key] = []
            elif key is not None:
                entries[key].append(line)
    return {k: "".join(v).strip() for k, v in entries.items()}


def read_fls(path):
    """Return {stdout stem + instance: transcript path} in reading order."""
    printed = {}
    pwd = os.path.dirname(os.path.abspath(path))
    current = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("PWD "):
                pwd = line[4:].strip()
                continue
            if not line.startswith("INPUT "):
                continue
            name = line[6:].strip()
            m = STDOUT.match(os.path.basename(name))
            if m:
                current = (m[1], int(m[2]))
                continue
            if current and TRANSCRIPT.search(name):
                printed.setdefault(current, os.path.join(pwd, name))
    return printed


# Keywords of didactic's run functions that change how a transcript is
# typeset, not what the program prints.
LAYOUT_ONLY = {"minted_opts", "fullwidth", "hlgrep"}


def identity(code):
    """Return what decides an instance's output, for comparing two jobs.

    A single call of a didactic_* function is compared without its
    layout-only keywords; any other code is compared as text.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return code
    if (len(tree.body) == 1 and isinstance(tree.body[0], ast.Expr)
            and isinstance(tree.body[0].value, ast.Call)
            and isinstance(tree.body[0].value.func, ast.Name)
            and tree.body[0].value.func.id.startswith("didactic_")):
        call = tree.body[0].value
        call.keywords = [k for k in call.keywords
                         if k.arg not in LAYOUT_ONLY]
        return ast.dump(call)
    return code


def program_of(code):
    """Return (program, shows command) for a didactic_output call."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None, False
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.Expr):
        return None, False
    call = tree.body[0].value
    if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
            and call.func.id == "didactic_output" and call.args):
        return None, False
    first = call.args[0]
    if not (isinstance(first, ast.Constant) and isinstance(first.value, str)
            and first.value.endswith(".py")):
        return None, False
    kw = {}
    for k in call.keywords:
        if k.arg and isinstance(k.value, ast.Constant):
            kw[k.arg] = k.value.value
        elif k.arg:
            kw[k.arg] = ...
    # didactic's own rule: transcript sets showcommand unless it is given
    shows = ("commandtext" not in kw
             and kw.get("showcommand", kw.get("transcript")) is True)
    return first.value, shows


def first_line(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.strip():
                return line.strip()
    return ""


def main():
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0] if __doc__ else None)
    ap.add_argument("--job", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()
    job, od = args.job, args.outdir

    code_file = os.path.join(od, job + ".pytxcode")
    if not os.path.isfile(code_file):
        print(f"{job}: no PythonTeX code, nothing to check")
        return 0
    code = read_pytxcode(code_file)
    wrong = []

    # --- provenance: whose PythonTeX run did the last pass read? ---
    log = os.path.join(od, job + ".log")
    runs = {}
    for f in os.listdir(od):
        if f.endswith(".pytxmcr"):
            runs[f[:-len(".pytxmcr")]] = os.path.getmtime(os.path.join(od, f))
    provenance = "not checked (no log or no PythonTeX run)"
    provenance_checked = False
    if os.path.isfile(log) and runs:
        typeset = os.path.getmtime(log)
        before = {k: t for k, t in runs.items() if t <= typeset}
        if not before:
            provenance = "not checked (every PythonTeX run is newer than the log)"
        else:
            last = max(before, key=lambda k: before[k])
            if last == job:
                provenance = "its own PythonTeX run"
                provenance_checked = True
            else:
                other_file = os.path.join(od, last + ".pytxcode")
                if not os.path.isfile(other_file):
                    provenance = (f"not checked (the last run was {last}'s, "
                                  "whose .pytxcode is gone)")
                else:
                    provenance_checked = True
                    other = read_pytxcode(other_file)
                    shared = sorted(set(code) & set(other))
                    differ = [k for k in shared
                              if identity(code[k]) != identity(other[k])]
                    provenance = (f"the PythonTeX run of {last} "
                                  f"({len(shared)} instances shared, "
                                  f"{len(differ)} differ)")
                    for k in differ:
                        wrong.append(
                            f"instance {k[3]} ({'#'.join(k[:3])}): {job} "
                            f"printed the output of {last}'s run, which runs "
                            f"other code there:\n"
                            f"    {job}: {code[k][:100]}\n"
                            f"    {last}: {other[k][:100]}")
    if provenance_checked:
        print(f"{job}: last pass read the outputs of {provenance}")
    else:
        print(f"{job}: provenance {provenance}")

    # --- command: does each printed command name its program? ---
    fls = os.path.join(od, job + ".fls")
    printed = read_fls(fls) if os.path.isfile(fls) else {}
    runs_py = shows = checked = gone = 0
    for key, text in sorted(code.items(), key=lambda kv: kv[0][3]):
        program, show = program_of(text)
        if not program:
            continue
        runs_py += 1
        if not show:
            continue
        shows += 1
        stem = (f"{key[0]}_{key[1]}_{key[2]}", key[3])
        path = printed.get(stem)
        if not path:
            continue
        if not os.path.isfile(path):
            gone += 1
            continue
        checked += 1
        line = first_line(path)
        names = {os.path.basename(t) for t in line.split()}
        if os.path.basename(program) not in names:
            wrong.append(f"instance {key[3]} runs {program}, but the "
                         f"transcript printed there begins: {line[:80]}")
    note = "" if os.path.isfile(fls) else f" (no {fls})"
    print(f"{job}: {runs_py} \\runpython, {shows} show their command, "
          f"{checked} checked against it{note}"
          + (f", {gone} transcript files gone" if gone else ""))

    # A later run that deleted a job's outputs (notes-only runs, after the
    # slides' run) is the normal state of some decks after a full build:
    # say so plainly, but it is no failure.
    if code and not provenance_checked and checked == 0:
        print(f"{job}: NOTHING CHECKED: provenance {provenance}; "
              f"no transcript showing its command could be read")

    for w in wrong:
        print(f"{job}: WRONG TRANSCRIPT: {w}")
    return 1 if wrong else 0


if __name__ == "__main__":
    sys.exit(main())
