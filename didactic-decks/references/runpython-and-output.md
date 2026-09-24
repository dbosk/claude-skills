# Embedding program output with PythonTeX

A deck never hand-copies its own output. didactic's `\runpython` runs the
tangled program through PythonTeX at build time and embeds the real
terminal session, so code and output cannot drift apart.

## Requirements

In `preamble.tex`:

```latex
\usepackage[makestderr]{pythontex}
\setpythontexoutputdir{.}
\setpythontexworkingdir{..}
```

PythonTeX runs from `ltxobj` (the output directory); `workingdir=..` moves
it up to the deck directory so `examples/...` resolves.

In the Makefile: `TEX_PYTHONTEX= yes` and
`PYTHONTEXFLAGS= --interpreter python:python3 --rerun=always`.

## The options

| Form | Shows | Use for |
|---|---|---|
| `\runpython[showcommand, chdir]{examples/x.py}` | the command line, then the output | the normal case: a terminal run |
| `\runpython[transcript]{examples/x.py}` | the session transcript | when the command line is already on the slide |
| `\runpython[transcript, chdir]{examples/x.py}` | the same, run in the file's directory | programs that open data files by relative path |
| `\runpython[transcript, stdin={4}]{examples/x.py}` | the run with input fed in | programs that read input |
| `\runpython[transcript, stdin={Malvina}, stdin={1927}]{...}` | one `stdin` per prompt, in order | several prompts |
| `\runpython[transcript, stdinfile={examples/search.in}]{...}` | input from a file | long or awkward input |

`chdir` is what makes a program that reads its own data files work; without
it the program runs from the deck directory and the relative path misses.

## Rules

- **Program output is always a terminal run with the command line first**,
  never a bare output block. `[showcommand]` for a program that takes no
  input, `[transcript, stdin={...}]` for one that reads input.
- **When the section is about what the user sees, the run comes before
  the code** (author, 2026-09-22: "Show the outputs before the code"). A
  section on prompts, messages or error output is judged from the user's
  side: show the dialogue first, let the student judge it, then show the
  program. Elsewhere the code comes first, as usual.
- **Example programs do something with their input.** A program that only
  echoes what it read is no reason to read it; let it compute something
  small and realistic from it (length and weight → BMI; author,
  2026-09-22: "Use these numbers in a BMI calculation"), as long as the
  computation stays invariant across the contrast.
- An `example` shows its own output: code and transcript in the same
  environment. An `exercise` keeps its answer separate — the delay is the
  point.
- **Never combine `\pause` and `\runpython` in one frame.** The overlays
  re-execute the frame body, which shifts PythonTeX's instance numbering
  for every later transcript in the slides job, and the shared cache then
  prints the wrong outputs in the notes. Stage structurally instead.
- A running example the student is asked to run should be re-runnable with
  different data without editing it: read the value with `input` and feed
  it in the build with `stdin`, even when input is taught in a later deck.
- `help()` on a function without a docstring prints the `#` comment block
  directly above its `def` (pydoc's `getcomments` fallback, Python 3.14),
  so a docstring-versus-comment contrast puts the comment *inside* the
  body or the contrast vanishes. A failing program embeds fine: the
  transcript carries the traceback with the absolute path stripped.

## Verifying transcripts

Two checks catch the two ways transcripts go wrong.

Instance-count skew, from a `\pause` in a `\runpython` frame:

```bash
wc -l ltxobj/notes.pytxcode ltxobj/slides.pytxcode
```

The two counts must be nearly equal.

Stale output, after a chunk changed but no frame did: the `.pytxcode` is
unchanged, so latexmk never invokes PythonTeX and the old
`didactic_output_*.txt` files stay referenced (they are named by output
content).

```bash
rm -f ltxobj/*.pytx* ltxobj/*.fdb_latexmk didactic_output_*.txt
touch contents.nw
```

Rebuild, then read each rebuilt transcript against the tangled program it
claims to run. Run the tangled programs directly to confirm:

```bash
for f in examples/*.py; do python3 "$f" < /dev/null; done
```

## Output beside test cases (`testkorningar.nw`)

A class file's `tests()` grows with the class (chunk-authoring.md), and
each test case shows its output beside it (author, 2026-09-24: "Should be
fine … Add it to the skill"). The test lines are written once:

1. In `contents.nw` each test case is a named chunk (`<<byt namn på
   personen>>`), appended to the class's tests bucket (`<<tester för
   [[Person]]>>`) right after the part it tests.
2. A second noweb file in the deck, `testkorningar.nw`, is **tangled but
   never woven**. It holds one root per printing test case,
   `[[<stem>_test_<case>.py]]`: import the class, run the earlier cases of
   the same `tests()` silently, then the case itself, so the objects are
   in the state `tests()` has there and the output is exactly its lines:

   ```python
   from contextlib import redirect_stdout
   from io import StringIO

   from person import Person

   with redirect_stdout(StringIO()):
       <<skapa en person>>
       <<skriv ut personen>>
   <<byt namn på personen>>
   ```
   Open the file with a paragraph saying why it exists. It is not woven
   because a woven root would print the harness in the notes, and a hidden
   one leaves the chunks' "used in" references pointing at missing labels
   (`??`).
3. Makefile: `TESTRUNS+= examples/…_test_….py` per program,
   `EXAMPLES+= ${TESTRUNS}` and `${TESTRUNS}: testkorningar.nw`, so the
   tangle rule reads both files (noweb joins chunk definitions across
   input files).
4. In the notes: a lead-in ("Testfallet skriver ut") and
   `\runpython[chdir, deps={examples/<stem>.py}]{examples/…_test_….py}`,
   without `showcommand`: the file name means nothing to the reader.
5. A case whose output answers a later try-first exercise gets no run
   beside it; show it after the exercise, or leave it to the exercise's
   final run.
6. To show a class at an earlier stage than the tangled file (a
   pseudokod step not yet refined, e.g. a constructor that does not yet
   simplify), the harness may switch that step off
   (`Fraction._Fraction__simplify = lambda self: None`) with a comment
   saying why, and the prose beside the run must say the step is not
   there yet.

Costs, accepted: the harness lines repeat per program; renaming a test
chunk means following it in `testkorningar.nw` (noweb warns about an
undefined chunk); the shown output depends on the order of the earlier
cases, as `tests()` does. The alternative, independent test cases that
build their own objects, was considered and not chosen (2026-09-24).

