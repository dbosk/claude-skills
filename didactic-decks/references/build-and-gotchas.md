# Building a deck, and the gotchas

See also `literate-programming/references/build-pythontex-biber.md` for the
general latexmk, PythonTeX and biber mechanics; this file keeps what is
specific to a deck with two jobs sharing one `ltxobj`.

Contents: [Makefile wiring](#makefile-wiring) · [Running a build](#running-a-build) ·
[The convergence loop](#the-convergence-loop) ·
[Symptom to fix](#symptom-to-fix) · [Each gotcha in full](#each-gotcha-in-full)

## Makefile wiring

Include `${INCLUDE_MAKEFILES}/tex.mk` **and** `noweb.mk` at the bottom, as
usual. The essentials above that:

```makefile
LATEXFLAGS+=	-shell-escape
TEX_PYTHONTEX=	yes
PYTHONTEXFLAGS=	--interpreter python:python3 --rerun=always
```

`-shell-escape` is minted's. `PYTHONTEXFLAGS` matters because both jobs
share `ltxobj`: without `--rerun=always` the second job reuses the first
job's PythonTeX cache.

`contents.tex: contents.nw` — the pattern rule in `noweb.mk` does the
weave. The default weave runs the dbosk noweb fork's `autolang` +
`tominted` pipeline, so chunks come out as syntax-highlighted `minted`
environments. `tominted` finds its bundled Pygments lexer itself; nothing
depends on `noweb_lexer.py`.

**Tangle rules must be spelled out per suffix**, because the generic
`%.py: %.nw` pattern does not match across the `examples/` directory
boundary:

```makefile
examples/%.py: contents.nw
	@mkdir -p ${@D}
	${NOTANGLE.py}
```

Declare any suffix `noweb.mk` does not already know before including it:

```makefile
NOWEB_SUFFIXES+=	.s .js .lean
```

For teaching decks, empty the tangle flags of compiled languages —
the default `-L` injects `#line` directives into the tangled source, and
the file must match the slide byte for byte:

```makefile
NOTANGLEFLAGS.c=
NOTANGLEFLAGS.cpp=
NOTANGLEFLAGS.hs=
```

The PDFs depend on `${SRC}` and `${EXAMPLES}`, so recaps and hit lists are
always fresh. `SRC` includes `preamble.tex`, `abstract.tex`,
`contents.tex`, `sokprotokoll.tex`, `ltnotes.bib` and
`$(wildcard litteratursokning/*-full.tex)` — a regenerated hit-list table
must trigger a rebuild even when no `.tex` source changed.

## Running a build

**One job at a time. Never build both PDFs of one deck concurrently** —
they share `ltxobj`.

```bash
make notes.pdf LATEXFLAGS="-shell-escape -interaction=nonstopmode"
make slides.pdf LATEXFLAGS="-shell-escape -interaction=nonstopmode"
```

`-interaction=nonstopmode` is essential in an agent session: the shared
makefiles deliberately omit it so a human gets the interactive prompt, and
a LaTeX error would otherwise leave `pdflatex` hung at its `?` prompt
forever. Passing it on the command line replaces the Makefile's `+=`
value, so keep `-shell-escape` in the same string.

`scripts/build_deck.sh` does the whole sequence — pre-clean, both jobs,
the convergence loop, all the checks — and exits non-zero on a hard
failure.

## The convergence loop

The make-driven latexmk can stop before the final passes. After each job,
read `ltxobj/<job>.log`: while it still says "Rerun to get
cross-references right", "There were undefined references", "Please
(re)run Biber" or "Rerun LaTeX", run biber and another pdflatex pass by
hand, up to four times:

```bash
biber --output-directory ltxobj ltxobj/notes
pdflatex -8bit -shell-escape -interaction=nonstopmode \
         -output-directory=ltxobj notes.tex
```

On slides the symptom of a build that stopped short is blank
table-of-contents frames at every section and subsection, which didactic
adds.

A permanent two-cycle of "Rerun to get cross-references right" caused by a
margin citation at a page boundary is harmless as long as the `??` count
is 0.

## Symptom to fix

| Symptom | Cause | Fix |
|---|---|---|
| Literal `<MINTED>` placeholders on every slide | the make stopped one pass short | one more `pdflatex` pass |
| Blank ToC frames at every section | same | same |
| Notes show old program output after a chunk changed | `.pytxcode` unchanged, so latexmk never invoked PythonTeX | the stale-transcript recipe below |
| Notes transcripts belong to the wrong example | `\pause` and `\runpython` in one frame | split the frame; see `runpython-and-output.md` |
| `Nothing to do` after an error, nothing rebuilds | stuck `ltxobj/<job>.fdb_latexmk` | `rm ltxobj/notes.fdb_latexmk` |
| `<MINTED>` in the *notes*, `! Package minted Error: Cannot find input file "didactic_output_…txt"`, and stray `notes.pytxmcr`, `notes.pytxpyg`, `notes.unq`, `pythontex_data.pkl`, `py_default_default_*.stderr` in the deck directory | latexmk ran PythonTeX with the deck directory as cwd | delete the strays, `ltxobj/notes.*` and `didactic_output_*.txt`; rebuild (below) |
| The checks report the *previous* build's numbers | the PDF was up to date, so no pass ran and the log is stale | `rm ltxobj/<job>.pdf` (or touch a source), rerun |
| Build hangs immediately | a killed run left `ltxobj/_minted` | `rm -rf ltxobj/_minted` |
| "empty citation" / `??` after adding bib keys | latexmk under `-use-make` did not rerun biber | run biber by hand, touch a source, make again |
| "Too many unprocessed floats", pages after the cause | margin notes exhausted the float pool | `\extrafloats{200}` in `preamble.tex` |
| "Float(s) lost", a `\label` gone with it | `\textcite`/`\autocite` inside a float | `\parencite` in floats; see `floats-and-margins.md` |
| minted errors on `outputdir` | minted v3 rejects the package option | plain `\usepackage{minted}` |

## Each gotcha in full

### Literal MINTED placeholders

Check with:

```bash
pdftotext ltxobj/slides.pdf - | grep -c MINTED
```

Must be 0. A non-zero count means the make stopped one pass short and left
placeholders on every slide; one more `pdflatex` pass clears it.

### Stale PythonTeX transcripts

When only the tangled programs change (a name in a chunk, nothing in the
frames), the `.pytxcode` is unchanged and latexmk never invokes PythonTeX,
so the notes keep the old transcripts. didactic's `didactic_output_*.txt`
files are named by output content, so the stale ones stay referenced.
Removing the PythonTeX files alone leaves latexmk with "nothing to do", so
touch the source as well:

```bash
rm -f ltxobj/*.pytx* ltxobj/*.fdb_latexmk *.pytxcode didactic_output_*.txt \
      ltxobj/pythontex_data.pkl ltxobj/py_*.stdout ltxobj/py_*.stderr
rm -rf ltxobj/pythontex-files-* pythontex-files-*
touch contents.nw
```

The `py_default_default_*.stdout` files and `pythontex_data.pkl` are the
part people forget: `rm ltxobj/*.pytx*` leaves them, and a stale one is
silently replayed at a block that should print something else — that is how
a poll question or a transcript ends up on the wrong slide. Run this clean
recipe after **every** change to PythonTeX content (`\runpython` calls,
`pycode` blocks, a Mentipy question's text or options), not only after a
tangled program changed, and before the final checks.

Then rebuild and check the rebuilt transcripts against the tangled
programs.

### The shared PythonTeX cache

Both jobs write into `ltxobj`. Two consequences:

- `PYTHONTEXFLAGS= --interpreter python:python3 --rerun=always` so the
  second job does not reuse the first job's cache.
- A frame that combines `\pause` (any overlay) with PythonTeX content —
  `\runpython`, a `pycode` block, a Mentipy question — doubles the slides
  job's PythonTeX instance count, because the overlays re-execute the frame
  body, and the shared cache then prints the wrong outputs in the notes (or
  a question on the wrong slide). Either drop the overlays or move the
  `pycode` out of the frame (see the Mentipy section). Check with:

  ```bash
  wc -l ltxobj/notes.pytxcode ltxobj/slides.pytxcode
  ```

  The two line counts must be nearly equal.

### Mentipy live questions

An `exercise` can be a live poll: a Mentipy question with a QR code on the
slide and a plain exercise in the notes. Verified pattern (intropy decks
*Algoritmiskt tänkande* and *Hello, World!*, 2026-09-08):

- `import mentipy` fails in the system `python3` that PythonTeX runs (pipx
  isolates the CLI), so PythonTeX runs in a deck-local virtualenv that the
  Makefile creates on the first build (never a manual "run once" step: it
  is gitignored, so every fresh checkout or worktree would fail the build):

  ```make
  MENTIPY_VENV=	$(CURDIR)/.venv
  PYTHONTEXFLAGS=	--interpreter python:${MENTIPY_VENV}/bin/python3 --rerun=always

  ${MENTIPY_VENV}/bin/python3:
  	mentipy init --venv ${MENTIPY_VENV}

  notes.pdf slides.pdf: | ${MENTIPY_VENV}/bin/python3
  ```

  Order-only (`|`) so the venv's timestamp never triggers a rebuild.
  `mentipy init` is idempotent and installs the released mentipy from
  PyPI. Gitignore `.venv/`, `mentipy.json` (it collects the students'
  answers) and `mentipy-obj/`.
- One `pycode` block at the top of `contents.nw`, inside `\mode<all>` … `\mode*`,
  defines the common kwargs: `Store("mentipy.json")` (the deck directory is
  PythonTeX's working directory), `qr_dir="mentipy-obj"`, `layout="auto"`
  (`\mode<presentation>` gets text + QR columns, `\mode<article>` the flat
  question; `show_url=False` keeps the URL out of the notes),
  `environment=""` and the `exercise` environment written by hand around
  the call, so titles and `\label`s survive, and an explicit `base_url`
  (the public poll URL; a LAN address resolved at compile time breaks in
  the lecture hall).
- Question text and options are LaTeX-escaped by Mentipy: plain text only
  (no macros, no `\cref`, no `"` under babel); code stays in the frame's
  chunk and the question names the file.
- Placement: a `pycode` inside a frame is safe only if the frame has no
  overlays. To keep overlays, put the block at top level right before the
  frame (in `\mode<all>`), let it write `mentipy-obj/<name>.tex`, and
  `\input` that file inside the exercise (`\IfFileExists` guard for the
  first pass).
- `lock=True` (default) paces a question with the slides; `lock=False` for a
  second question on the same slide; `next=False` on the deck's last one.
- The flat article layout (the `\mode<article>` branch of `auto`) is
  transparent since 2026-09-08: the notes show the prompt alone, in the
  running text's weight — no options, no "Choose exactly one", type, limit
  or range, no bold. The exercise reads as it did before Mentipy, so a
  prompt that only works with its options ("vilket stämmer?") must be
  rephrased for both surfaces. On the slides Mentipy still prints English
  labels; the decks swap them in a small helper on the returned LaTeX.
- The address under the QR lives in the sidecar `mentipy-obj/Q-*.pdf_tex`,
  which `mentipy serve` rewrites together with the image. **Never
  post-process the sidecar `\input` into literal text** (the copy freezes
  at compile time and the caption stops following the server, while the
  QR image keeps updating). To make the URL fit the narrow QR column,
  redefine Mentipy's hook (mentipy ≥ 0.12) in `\mode<all>` before the
  first question: `\newcommand{\mentipyqrcaption}[1]{{\tiny\url{#1}}}`
  (`\url` breaks after `:`, `.` and `/`). And make the PDFs depend on the
  sidecars, or `make` after `mentipy serve` says nothing to do:
  `notes.pdf slides.pdf: $(wildcard mentipy-obj/Q-*.pdf_tex)`.
- Checks: the clean recipe above before the final build; pytxcode counts
  equal; `mentipy list --store mentipy.json` lists the questions in slide
  order and matches the prefixes printed under the QR codes; `pdftotext
  notes.pdf - | grep -c <base host>` is 0; every question slide rendered
  and read.

### A PythonTeX run from the deck directory

Seen once in a campaign of a hundred builds: latexmk's `pytxcode → pytxmcr`
custom dependency (in the shared `latexmkrc`) ran `pythontex` with the
*deck* directory as its working directory instead of `ltxobj`. That run
wrote `notes.pytxmcr`, `notes.pytxpyg`, `notes.unq`, `pythontex_data.pkl`
and `py_default_default_*.stderr` beside the sources (none of them
gitignored), failed with `FileNotFoundError: … 'examples'` because its
`chdir` resolved one level up, and left `notes.pdf` with a minted error per
transcript and a `<MINTED>` placeholder on each. The slides-only MINTED
check does not see it, and the `^!` count is the only symptom in the log.
Cure:

```bash
rm -f notes.pytxmcr notes.pytxpyg notes.unq pythontex_data.pkl \
      py_default_default_*.std* ltxobj/notes.* didactic_output_*.txt
make notes.pdf LATEXFLAGS="-shell-escape -interaction=nonstopmode"
```

After the rebuild `ltxobj/notes.pytxmcr` exists and the errors are gone.
Do not gitignore the strays: their presence is the diagnosis.

### The checks reading a stale log

After a failed build, a second `make` often finds the PDF up to date, runs
no `pdflatex`, and leaves `ltxobj/<job>.log` from the failed run in place,
so every log-based check reports the old numbers. `build_deck.sh` says when
a job's log did not change during the build (harmless when nothing changed:
the log belongs to the PDF); after a failed run, `rm ltxobj/<job>.pdf` or
touch a source before rerunning.

### Stuck latexmk

A run that "gave an error in previous invocation ... Nothing to do" needs
its fdb removed:

```bash
rm ltxobj/notes.fdb_latexmk
```

### Killed run leaves _minted

A killed build leaves `ltxobj/_minted`, which hangs the next one:

```bash
rm -rf ltxobj/_minted
```

Do this before every build; `build_deck.sh` pre-cleans it.

### biber under -use-make

latexmk driven by make may not rerun biber after new bib keys appear. Run
it by hand, touch a source and make again:

```bash
biber --output-directory ltxobj ltxobj/notes
touch contents.nw
make notes.pdf LATEXFLAGS="-shell-escape -interaction=nonstopmode"
```

### The shared makefiles submodule

In a fresh worktree the submodule is not checked out, because the repo
config sets `submodule.makefiles.update=none`:

```bash
git submodule update --init --checkout makefiles
```

The submodule must be on a lineage where the highlighted weave is the
default; the project's own CLAUDE.md records which commit.

### Long builds and the Bash timeout

A full deck build can outrun a 10-minute tool call. Use
`scripts/build_decks_detached.sh` under `nohup ... &` and watch its log,
rather than blocking on a foreground build:

```bash
nohup ~/.claude/skills/didactic-decks/scripts/build_decks_detached.sh \
      --makefiles "$PWD/makefiles" --logdir /tmp/build \
      modules/exceptions/slides modules/iterations/slides \
      > /tmp/build/driver.log 2>&1 &
```

The script writes one log per deck and a final `##### all done` marker
line to watch for.
