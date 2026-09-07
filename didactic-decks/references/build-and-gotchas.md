# Building a deck, and the gotchas

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
rm -f ltxobj/*.pytx* ltxobj/*.fdb_latexmk didactic_output_*.txt
touch contents.nw
```

Then rebuild and check the rebuilt transcripts against the tangled
programs.

### The shared PythonTeX cache

Both jobs write into `ltxobj`. Two consequences:

- `PYTHONTEXFLAGS= --interpreter python:python3 --rerun=always` so the
  second job does not reuse the first job's cache.
- A frame that combines `\pause` with `\runpython` doubles the slides job's
  PythonTeX instance count, because the overlays re-execute the frame body,
  and the shared cache then prints the wrong outputs in the notes. Check
  with:

  ```bash
  wc -l ltxobj/notes.pytxcode ltxobj/slides.pytxcode
  ```

  The two line counts must be nearly equal.

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
