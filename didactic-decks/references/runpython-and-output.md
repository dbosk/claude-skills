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
