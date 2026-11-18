#!/usr/bin/env python3
"""Fail when a \\runpython (or another didactic run) is missing its
transcript in a job's PDF, the transcript is empty, or it is another
run's.

Where a transcript lives, per job (read from didactic.sty and
pythontex.sty):

  1. <outdir>/<job>.pytxcode lists every PythonTeX instance the job's
     last pdflatex pass met, as
     "=>PYTHONTEX#<family>#<session>#<group>#<n>#c#..." followed by its
     code.  \\runpython, \\runshell and the pair commands are \\pyc
     instances whose code is a call such as
     didactic_output('examples/x.py', ...), didactic_shell(...) or
     didactic_pair(...).  A frame the job never typesets (a notes-only
     \\begin{frame}<article> in the slides) has no instance in that job.
     <outdir> is ltxobj, and ltxobj-sv for the -sv jobs of a bilingual
     deck (each edition builds in its own directory).
  2. PythonTeX writes what instance n printed to
     <outdir>/<family>_<session>_<group>_<n>.stdout, and pdflatex
     \\inputs it: one or more lines \\didacticinputminted[...]{lang}{<file>}.
  3. <file> (didactic_output_<hash>.txt, didactic_pair_<hash>.txt) holds
     the text minted typesets: in <outdir> since didactic v2.18.1 (the
     .stdout names it as ltxobj/didactic_output_...txt, relative to the
     deck directory), in the deck directory before that.  Either is read
     where the .stdout says.  <hash> is the start of the SHA-256 of the
     content, so the empty transcript has a fixed name,
     ..._e3b0c44298fc1c14.txt.

Both jobs of an edition write the same .stdout names into their shared
output directory, and PythonTeX deletes the files it no longer needs when
it reruns.  After a full build the slides' PythonTeX run has deleted the
.stdout files of the notes-only runs; the next notes pass that does not
rerun PythonTeX (an incremental build, latexmk sees the .pytxcode
unchanged) then finds no file and prints nothing at all: no ??, no error,
no MINTED.  Measured on Klasser och objekt, 2026-11-16: 16 of 27
transcripts gone, every other check green.

What a pass read is in its recorder file, <outdir>/<job>.fls (latexmk
runs pdflatex with -recorder).  For each run instance the check fails
when

  - the last pass did not read its .stdout (not in <job>.fls): the
    transcript is missing from the PDF;
  - the .stdout names no transcript file (an empty .stdout);
  - a named transcript is empty (the empty hash, or an empty file);
  - a didactic_output run that shows its command line (showcommand, or
    transcript without showcommand=False; no commandtext) has a
    transcript whose first line names another program: another run's
    output.

It also fails, by provenance, when the job's last pass (the mtime of its
.log) came after another job's PythonTeX run in the same directory (the
mtimes of the <outdir>/*.pytxmcr files, which PythonTeX rewrites at the
end of every run that ran code) and that job runs other code at an
instance both have: the pass then printed that job's output there, which
the command-line test sees only when the command is shown.  Options that
only set how a transcript is typeset (minted_opts, fullwidth, hlgrep) are
left out of that comparison.  This catches the two editions of a bilingual
deck built into one directory, and a job typeset again after the other
job's run without one of its own.

It warns, without failing, when a .stdout the pass read has since been
deleted, or rewritten (newer than <job>.fls), by the other job: the PDF
has the transcript, but the next pass of this job without PythonTeX will
lose it or print another run's output in its place (rebuild clean, the
recipe in references/build-and-gotchas.md, "Stale PythonTeX
transcripts").  build_deck.sh runs the check right after each job, before
the other job's PythonTeX run can change the files.  When every run's
.stdout has been deleted since the pass and the provenance could not be
judged, it says NOTHING CHECKED and why, and still passes: the PDF may
well be right, and that is the normal state of some decks after a full
build.

What it cannot see: a stale but plausible transcript (read the transcripts
against the programs); the provenance test relies on mtimes, so a tree
copied without them misleads it.

Usage: check_transcripts.py <deck dir> [notes|slides|notes-sv|slides-sv ...]
Exit 0 when every run has a non-empty transcript of its own, 1 when one
does not, 2 when there is nothing to check (no .pytxcode: build the job
first).
"""
import ast
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

# The editions other than the main one, by job suffix, and so their
# output directories: notes-sv builds in ltxobj-sv.  Keep in step with
# OTHER_EDITIONS in build_deck.sh.
OTHER_EDITIONS = ("-sv",)

# Keywords of didactic's run functions that change how a transcript is
# typeset, not what the program prints.
LAYOUT_ONLY = {"minted_opts", "fullwidth", "hlgrep"}


def outdir(deck, job):
    """The job's output directory: ltxobj, or ltxobj<suffix>."""
    for sfx in OTHER_EDITIONS:
        if job.endswith(sfx):
            return os.path.join(deck, "ltxobj" + sfx)
    return os.path.join(deck, "ltxobj")


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


def read_entries(pytxcode):
    """[(header, code lines)] of every instance in a .pytxcode."""
    out, head, code = [], None, []
    with open(pytxcode, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("=>PYTHONTEX:SETTINGS#"):
                break
            if line.startswith("=>PYTHONTEX"):
                if head:
                    out.append((head, code))
                head = header(line)
                code = []
            elif head is not None:
                code.append(line)
    if head:
        out.append((head, code))
    return out


def instances(entries):
    """[(stdout name, where, call)] of the run instances."""
    out = []
    for head, code in entries:
        if head["cmd"] == "c" and code and RUN_RE.match(code[0]):
            name = "{family}_{session}_{group}_{n}.stdout".format(**head)
            where = head["file"] + (":" + head["line"] if head["line"] else "")
            out.append((name, where, code[0].strip()))
    return out


def codes(entries):
    """{(family, session, group, n): code} of every instance."""
    return {(h["family"], h["session"], h["group"], int(h["n"])):
            "".join(c).strip() for h, c in entries}


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


def parse_call(code):
    """The ast.Call of a single didactic_* call, or None."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    if (len(tree.body) == 1 and isinstance(tree.body[0], ast.Expr)
            and isinstance(tree.body[0].value, ast.Call)
            and isinstance(tree.body[0].value.func, ast.Name)
            and tree.body[0].value.func.id.startswith("didactic_")):
        return tree.body[0].value
    return None


def identity(code):
    """What decides an instance's output, for comparing two jobs: a
    didactic_* call without its layout-only keywords, other code as
    text."""
    call = parse_call(code)
    if call is None:
        return code
    call.keywords = [k for k in call.keywords if k.arg not in LAYOUT_ONLY]
    return ast.dump(call)


def shown_program(code):
    """The program a didactic_output call runs, if its transcript shows
    the command line naming it; else None.  didactic's own rule:
    transcript sets showcommand unless showcommand is given; commandtext
    replaces the command shown."""
    call = parse_call(code)
    if call is None or call.func.id != "didactic_output" or not call.args:
        return None
    first = call.args[0]
    if not (isinstance(first, ast.Constant) and isinstance(first.value, str)
            and first.value.endswith(".py")):
        return None
    kw = {k.arg: (k.value.value if isinstance(k.value, ast.Constant)
                  else ...) for k in call.keywords if k.arg}
    if "commandtext" in kw:
        return None
    if kw.get("showcommand", kw.get("transcript")) is not True:
        return None
    return first.value


def faults(deck, stdout, call):
    """What is wrong with one run's output as the files stand now, and the
    transcript files its .stdout names."""
    files = INPUT_RE.findall(read(stdout))
    if not files:
        return [f"{os.path.basename(stdout)} names no transcript (empty "
                f"output)"], files
    found = []
    program = shown_program(call)
    for fname in files:
        # Relative to the deck directory, where LaTeX runs: a bare name
        # (didactic before v2.18.1) or ltxobj/... (v2.18.1 and later).
        path = os.path.join(deck, fname)
        text = read(path) if os.path.exists(path) else None
        if (os.path.splitext(fname)[0].endswith("_" + EMPTY_HASH)
                or (text is not None and not text.strip())):
            found.append(f"{fname} is empty")
        elif text is not None and program:
            first = text.lstrip().split("\n", 1)[0]
            # A word of the command line, not a substring: data.py must
            # not pass for a.py.
            if os.path.basename(program) not in {
                    os.path.basename(w) for w in first.split()}:
                found.append(f"{fname} begins {first!r}, not a run of "
                             f"{os.path.basename(program)}")
    return found, files


def provenance(od, job, code):
    """(checked, description, problems): whose PythonTeX run the job's
    last pass read, and the instances where that run's code differs."""
    log = os.path.join(od, job + ".log")
    runs = {f[:-len(".pytxmcr")]: os.path.getmtime(os.path.join(od, f))
            for f in os.listdir(od) if f.endswith(".pytxmcr")}
    if not os.path.isfile(log) or not runs:
        return False, "no log or no PythonTeX run", []
    typeset = os.path.getmtime(log)
    before = {k: t for k, t in runs.items() if t <= typeset}
    if not before:
        return False, "every PythonTeX run is newer than the log", []
    last = max(before, key=lambda k: before[k])
    if last == job:
        return True, "its own PythonTeX run", []
    other_file = os.path.join(od, last + ".pytxcode")
    if not os.path.isfile(other_file):
        return False, (f"the last run was {last}'s, whose .pytxcode is "
                       f"gone"), []
    other = codes(read_entries(other_file))
    shared = sorted(set(code) & set(other))
    differ = [k for k in shared if identity(code[k]) != identity(other[k])]
    problems = [f"instance {k[3]} ({'#'.join(k[:3])}): the last pass "
                f"printed the output of {last}'s PythonTeX run, which runs "
                f"other code there: {job}: {code[k][:100]} / {last}: "
                f"{other[k][:100]}" for k in differ]
    return True, (f"the PythonTeX run of {last} ({len(shared)} instances "
                  f"shared, {len(differ)} differ)"), problems


def check_job(deck, job):
    """Print the job's problems; return (runs, ok, problems), or None
    when the job has no .pytxcode."""
    od = outdir(deck, job)
    rel = os.path.relpath(od, deck)
    pytxcode = os.path.join(od, job + ".pytxcode")
    if not os.path.exists(pytxcode):
        print(f"{job}: no {pytxcode}: build the job first")
        return None
    entries = read_entries(pytxcode)
    runs = instances(entries)
    fls = os.path.join(od, job + ".fls")
    inputs = recorded_inputs(fls)
    if inputs is None:
        print(f"{job}: no {rel}/{job}.fls: judging by the files present now")
    passed = os.path.getmtime(fls) if inputs is not None else None
    ok, problems, warnings = 0, [], []
    verified = 0  # runs whose files could be read and judged
    for name, where, call in runs:
        stdout = os.path.join(od, name)
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
        verified += 1
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
            # inputs holds base names; the .stdout may name the transcript
            # with a directory (didactic 2.18.1 writes it to ltxobj/).
            found += [f"the last pass did not read {n} ({name} names it)"
                      for n in files if os.path.basename(n) not in inputs]
        if not found:
            ok += 1
        elif changed:
            ok += 1
            warnings += [f"{where}: {f}, changed since the last pass: {call}"
                         for f in found]
        else:
            problems += [f"{where}: {f}: {call}" for f in found]
    checked, prov, wrong = provenance(od, job, codes(entries))
    if checked:
        print(f"{job}: last pass read the outputs of {prov}")
    else:
        print(f"{job}: provenance not checked ({prov})")
    for p in problems:
        print(f"{job}: EMPTY {p}")
    for w in wrong:
        print(f"{job}: WRONG TRANSCRIPT {w}")
    for w in warnings:
        print(f"{job}: WARNING {w}")
    if warnings:
        print(f"{job}: {len(warnings)} warning(s): {job}.pdf has these "
              f"transcripts, but the next {job} pass without PythonTeX "
              f"would print what the warnings say; rebuild clean before "
              f"relying on an incremental build")
    # Every .stdout was read, then deleted by the other job's run, and the
    # provenance could not be judged: the PDF may be right, but nothing
    # about it was verified.  A normal state after some full builds, so a
    # pass, but said plainly.
    if runs and not verified and not problems and not checked:
        print(f"{job}: NOTHING CHECKED: every run's .stdout is gone since "
              f"the last pass, and provenance not checked ({prov})")
    print(f"{job}: {len(runs)} runs, {ok} with a transcript, "
          f"{len(problems) + len(wrong)} problem(s)")
    return len(runs), ok, len(problems) + len(wrong)


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
