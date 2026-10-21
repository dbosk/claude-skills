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

A class file's test program `tests()` grows with the class
(`chunk-authoring.md`), and each test shows its output beside it (author,
2026-09-24: "Should be fine … Add it to the skill"). Each test is a named
test function, the general rule in the `literate-programming` skill
(`references/testing-patterns.md`, "A test is a named test function").
A deck's program has no pytest to collect them, so it also calls them;
that call list is what this section adds. Author, 2026-10-21, beside a
`<<prova jämförelserna>>` chunk included into a test bucket: "Why this
indirection? Add directly to the bucket chunk." and "make each such test
a test function that we can call. Add the calls directly to the
`<<test ...>>` chunk. That also illustrates a better practice for tests.
Make this the rule."; on *Operatoröverlagring* v13: "Add directly to
⟨tester för Fraction⟩. Make this the default behaviour, unless there is a
compelling reason for adding this indirection."

1. In `contents.nw`, two buckets per class. `<<testfunktioner för X>>`
   collects the `def test_…():` definitions, each appended right after
   the part it tests; `<<kör tester för X>>` collects only the calls and
   sits inside `def tests():`. Append the call in the same display as the
   definition. Write the test straight into its bucket, never as a named
   chunk forwarded to the bucket ("No pass-through chunks",
   `chunk-authoring.md`). Each test builds its own objects, so it runs
   alone and in any order.

   ```noweb
   <<[[fraction.py]]>>=
   <<klasserna>>
   <<testfunktioner för [[Fraction]]>>

   def tests():
       """Testprogrammet"""
       <<kör tester för [[Fraction]]>>

   if __name__ == "__main__":
       tests()
   @
   ...
   <<testfunktioner för [[Fraction]]>>=
   def test_addition():
       print(Fraction(1, 2) + Fraction(1, 3))
   <<kör tester för [[Fraction]]>>=
   test_addition()
   @
   ```
2. The output beside a test comes from running just that test function.
   A second noweb file in the deck, `testkorningar.nw`, is **tangled but
   never woven**. It holds one root per shown run,
   `[[<stem>_test_<case>.py]]`, a driver that imports the test and calls
   it:

   ```python
   from fraction import test_addition

   test_addition()
   ```
   When the text shows the class in stages (before simplification, before
   `__radd__`, a first wrong attempt), the run must show the class as the
   text has it there, not the finished tangled file: the driver imports
   the class too, and between the import and the call it applies the
   stage's patches, each a named chunk in `testkorningar.nw`
   (`<<förenkla inte än>>`:
   `Fraction._Fraction__simplify = lambda self: None`; `<<utan radd>>`:
   `del Fraction.__radd__`). The prose beside the run says what is not
   there yet. When the class is not shown in stages (*Övning: Fler
   behållare*), the driver is just the import and the call. No
   `redirect_stdout` and no silent reruns of earlier tests: the tests are
   independent.

   Driver files, not `\runpython` on `python3 -c "…"`: a failing run's
   traceback prints the `-c` source, so the patches would show in the
   notes. Open `testkorningar.nw` with a paragraph saying why it exists. It
   is not woven because a woven root would print the harness in the
   notes, and a hidden one leaves the chunks' "used in" references
   pointing at missing labels (`??`).
3. Makefile: `TESTRUNS+= examples/…_test_….py` per program,
   `EXAMPLES+= ${TESTRUNS}` and `${TESTRUNS}: testkorningar.nw`, so the
   tangle rule reads both files (noweb joins chunk definitions across
   input files).
4. In the notes: a lead-in ("Testfallet skriver ut") and
   `\runpython[chdir, deps={examples/<stem>.py}]{examples/…_test_….py}`,
   without `showcommand`: the file name means nothing to the reader.
5. A test whose output answers a later try-first exercise gets no run
   beside it; show it after the exercise, or leave it to the exercise's
   final run.

Costs, accepted: two lines of driver per run; renaming a test function
means following it in `testkorningar.nw` (the run fails with an
`ImportError`). This replaces the shape of 2026-09-24 (one named chunk
per test case, the earlier cases rerun silently under `redirect_stdout`
so the objects were in the state `tests()` had there).

