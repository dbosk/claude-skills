---
name: didactic-decks
description: Build and revise lecture decks that produce slides.pdf (beamer) and notes.pdf (memoir + beamerarticle) from one literate contents.nw with the didactic package, PythonTeX transcripts and a noweb/minted weave. Use proactively when (1) creating, converting or revising a directory holding contents.nw plus slides.tex plus notes.tex, (2) such a build fails or the two PDFs disagree (missing or wrong transcripts, literal MINTED placeholders, blank table-of-contents frames, "Float(s) lost", stuck latexmk, margin notes on the wrong page), (3) running the pre-review checks, (4) the user mentions deck, lecture notes, ltnote, runpython, beamerarticle, sidecaption, or "the deck standard", (5) writing or reviewing a Swedish-language deck (house style in references/house-style-sv.md), (6) writing an agent brief that converts or sweeps decks. Owns the composition, build and checks; load literate-programming for .nw editing, didactic-notes, variation-theory and try-first-tell-later for pedagogy, backing-claims for citations; project wording rules stay in the project's CLAUDE.md.
---

# Didactic decks: one source, two PDFs

A deck directory builds two documents from one literate source:

- `slides.pdf` — beamer, for the lecture;
- `notes.pdf` — memoir + beamerarticle: full lecture notes with the
  slides' content woven into flowing prose, instructor notes in the
  margin, and appendices backing the deck's claims.

Both `\input` the same `contents.tex`, which is **woven** from
`contents.nw`. The example programs are **tangled** from the same file into
`examples/`, so the program on a slide, the program in the notes and the
program that actually ran to produce the printed output are one text.

## When to use this skill

Load it before touching a directory that holds `contents.nw` together with
`slides.tex` and `notes.tex`, and whenever:

- starting a new deck, or converting an old `contents.tex` deck to the
  literate pattern;
- a build fails, hangs, or the two PDFs disagree;
- running the checks before a deck is reviewed;
- writing a brief for agents that convert or sweep decks.

Load it **with**, not instead of, the skills that own the neighbouring
concerns. This skill owns the composition, the build and the checks.

## Where the general rules live

A rule that would hold in another repository lives in a skill; a rule that
is a fact about one course lives in that project's `CLAUDE.md`. A rule in
two places is a defect.

| Subject | Where |
|---|---|
| Toolchain, build, checks, deck anatomy | this skill |
| Swedish house style for decks | `references/house-style-sv.md` (this skill) |
| Editing `.nw` files, chunk discipline, tangling | `literate-programming` |
| LaTeX markup, cleveref, csquotes, dual beamer/article | `latex-writing` |
| Instructor notes: what belongs in an `\ltnote` | `didactic-notes` |
| Contrast, generalisation, fusion; critical aspects | `variation-theory` |
| Try-first questions, exercise design | `try-first-tell-later` |
| Citations, provenance blocks, the claim audit | `backing-claims` |
| Review rounds on the tablet | `remarkable`, section "Transcribing a review round" |
| Agent briefs, parallel worktrees, resuming | `worktree-subagents`, sections "Reader and fix agents from a brief on disk" and "Session limits, resume and unreachable agents" |
| Course data: deck titles, example names, claim ledger | the project's `CLAUDE.md` |

## Reference files

Read the one you need; do not read them all.

| File | Read it for |
|---|---|
| `references/deck-anatomy.md` | which files exist, driver wiring, preamble requirements, `abstract.tex`, the appendices |
| `references/build-and-gotchas.md` | Makefile wiring, the convergence loop, every build symptom and its fix |
| `references/chunk-authoring.md` | chunks in frames, recaps, mode splits, `\cref` traps, citations |
| `references/runpython-and-output.md` | `\runpython` options, verifying transcripts |
| `references/floats-and-margins.md` | float placement, captions, the side-caption decision, the `\ltnote` queue |
| `references/review-checklist.md` | the checks with their exact commands and thresholds |
| `references/house-style-sv.md` | Swedish wording rules (load only for a Swedish deck) |

Quick ways in: `grep -n 'MINTED\|pytxcode\|_minted\|fdb_latexmk\|Mentipy' references/build-and-gotchas.md`
for a build symptom; `grep -n 'sidecaption\|extrafloats\|Float(s) lost' references/*.md`
for a margin or float problem.

## Anatomy of a deck

| File | Committed | Purpose |
|---|---|---|
| `contents.nw` | yes | the single source: prose, frames, chunks, `\ltnote`s |
| `contents.tex` | **no** | woven from `contents.nw` |
| `examples/` | **no** | tangled from `contents.nw` |
| `slides.tex` | yes | beamer driver |
| `notes.tex` | yes | memoir + beamerarticle driver |
| `preamble.tex` | yes | shared by both drivers |
| `abstract.tex` | yes | overview, learning objectives, prerequisites |
| `sokprotokoll.tex` | yes | method appendix plus one chapter per backed claim |
| `ltnotes.bib` | yes | sources, each with a provenance block |
| `litteratursokning/*.tex` | yes | generated hit-list tables, `\input` by the appendices |
| `Makefile`, `.gitignore`, `figs/` | yes | |
| `notes.pdf`, `slides.pdf`, `latexmkrc`, `ltxobj/` | **no** | build outputs |

**Never edit `contents.tex` or anything under `examples/`.** They are
regenerated on every build; an edit there is lost and misleads the next
reader. Data files a deck *reads* are tracked inputs and must be excluded
from the `examples/` ignore rule.

The two drivers are not interchangeable boilerplate. `slides.tex` guts the
noweb cross-referencing apparatus, because beamer overlays re-execute
frame bodies and would define the sub-page labels twice; `notes.tex` keeps
that apparatus and hides only the identifier index. `preamble.tex` must
carry `\extrafloats{200}` and `\ifdefined\setsidecappos\setsidecappos{b}\fi`
right after loading didactic, and must load minted **without**
`[outputdir=...]`. Details in `references/deck-anatomy.md`.

## Starting or converting a deck

Copy the template and replace its placeholders:

```bash
cp -r ~/.claude/skills/didactic-decks/assets/deck-template <module>/slides
```

`assets/deck-template/README.md` lists the placeholders (`TITLE`,
`AUTHOR`, `INSTITUTE`, the module name in the learning-objective labels,
the makefiles path) and the files the template deliberately omits
(`ltnotes.bib`, `figs/`, `litteratursokning/`). Lines marked `% PROJECT:`
are language- or project-specific.

When converting an existing deck, keep the old `contents.tex` only as a
reading copy until `contents.nw` reproduces it, then delete it and add it
to `.gitignore`. Every `\inputminted[firstline=...,lastline=...]` becomes a
chunk named after the file it tangles to, placed at its point of
presentation.

### Definition of done

1. `contents.nw` with prose lecture notes between the frames, try-first
   questions before explanations, and one `example` or `exercise`
   environment per case.
2. `abstract.tex` with the overview, the learning objectives as
   `restatable` `lo` environments labelled `<Module>LO<Aspect>` and
   restated where the notes meet them, and the prerequisites.
3. An `\ltnote` for every design choice: which objective, what varies and
   what stays invariant, which misconception the activity targets.
   `\parencite` appears only inside `\ltnote`s.
4. `ltnotes.bib` where every entry carries a provenance block, checked
   with the `backing-claims` scripts.
5. A **claim audit** before the appendices are called done: every
   imperative in the deck asserts a benefit, and that benefit is an
   empirical claim to back two-sidedly. An appendix sentence saying the
   deck makes no claims that needed a search is itself a claim, and is
   tested the same way.
6. `sokprotokoll.tex`: the method appendix, then one chapter per backed
   claim, each opening with the project's `\chapterprecis` sentence, its
   title the question it answers, and its conclusion answering that
   question in its first sentence.
7. A claim already backed in another deck is not searched again: cite the
   same source with the provenance block copied plus a `FOUND-VIA (here)`
   line, and point at the other deck's appendix in prose, saying what that
   appendix answers.
8. All the checks below passing, and every page read.

## Authoring rules

Each line points at the reference that explains it.

- A chunk replaces every `\inputminted` line range, is named after the file
  it tangles to, and sits at its point of presentation. `chunk-authoring.md`
- Frames holding a chunk or any minted output are `[fragile]`. `chunk-authoring.md`
- **Never** open a theorem-style environment with a chunk or a minted
  block: put a lead-in sentence first. `chunk-authoring.md`
- Recaps re-display the tangled file with `\inputminted{python}{examples/foo.py}`,
  the whole file, never a second chunk definition. `chunk-authoring.md`
- Python chunks are black-clean and every source line is at most 79
  characters. `chunk-authoring.md`
- Block and frame titles use `\texttt`, never `\mintinline`; an
  overflowing headline gets `\section[short]{long}`. `chunk-authoring.md`
- Notes-only structure goes in `\mode<article>{...}`, slide-only tweaks in
  `\mode<presentation>{...}`; verbatim does not survive the latter. `chunk-authoring.md`
- Overlay staging that hides an answer collapses in the notes: stage
  structurally instead. `chunk-authoring.md`
- `\cref` to an unnumbered didactic environment prints `??`, and to an
  `example` prints "sats" on slides: wrap it in `\only<article>{...}`. `chunk-authoring.md`
- An `example` shows its own output, as a terminal run with the command
  line first; an `exercise` keeps its answer separate. `runpython-and-output.md`
- Never combine `\pause` with PythonTeX content (`\runpython`, `pycode`, a
  Mentipy question) in one frame; after any change to such content, rebuild
  clean. `runpython-and-output.md`, `build-and-gotchas.md`
- Exercises as live Mentipy polls (QR on the slide, plain in the notes):
  venv, interpreter, placement and checks in `build-and-gotchas.md`.
- Floats sit right after the paragraph that references them, never on a
  float page, and their captions explain enough to stand alone. `floats-and-margins.md`
- Side captions only when the margin is free **and** the caption is not
  taller than the float; otherwise a normal caption with the same text. `floats-and-margins.md`
- `\textcite` and `\autocite` never go inside a float. `floats-and-margins.md`
- Long `\ltnote`s queue forward; drain them with `\mode<article>{\clearpage}`
  before the section, and before the last frame of a section that
  overflows. `floats-and-margins.md`

## Building

**One job at a time. Never build both PDFs of one deck concurrently** —
they share `ltxobj`.

```bash
~/.claude/skills/didactic-decks/scripts/build_deck.sh --deck <dir>
```

The script pre-cleans `ltxobj/_minted`, builds each job, converges the
cross references where latexmk stops short, runs every mechanical check
and exits non-zero on a hard failure. `--check-only` runs the checks on
existing PDFs; `--jobs notes` builds one job; `--exempt GLOB` excludes
hand-written inputs from `black --check`; `--makefiles DIR` sets
`INCLUDE_MAKEFILES`; `--log FILE` puts the build log somewhere other than
`ltxobj/`.

By hand it is:

```bash
make notes.pdf LATEXFLAGS="-shell-escape -interaction=nonstopmode"
```

`-interaction=nonstopmode` is not optional in an agent session: the shared
makefiles omit it so a human gets the interactive prompt, and a LaTeX
error would otherwise leave `pdflatex` hung at its `?` prompt.

For several decks, or a build longer than one tool call allows, run
`scripts/build_decks_detached.sh` under `nohup ... &` and watch its logs
for the `##### all done` marker.

| Symptom | Fix |
|---|---|
| Literal `<MINTED>` on every slide, or blank ToC frames | one more `pdflatex` pass |
| Notes show old output after a chunk changed | `rm -f ltxobj/*.pytx* ltxobj/*.fdb_latexmk didactic_output_*.txt; touch contents.nw` |
| Notes transcripts belong to the wrong example | a `\pause` in a `\runpython` frame; split it |
| "Nothing to do", nothing rebuilds | `rm ltxobj/notes.fdb_latexmk` |
| `<MINTED>` in the notes, stray `notes.pytxmcr` beside the sources | PythonTeX ran from the deck directory; delete the strays and `ltxobj/notes.*`, rebuild |
| Build hangs immediately | `rm -rf ltxobj/_minted` |
| "empty citation" or `??` after new bib keys | run biber by hand, touch a source, make again |
| "Too many unprocessed floats" | `\extrafloats{200}` missing from `preamble.tex` |
| "Float(s) lost", a `\label` gone with it | a citation inside a float |
| minted errors on `outputdir` | drop the package option |
| Submodule missing in a fresh worktree | `git submodule update --init --checkout makefiles` |

Each of these is spelled out, with its command, in
`references/build-and-gotchas.md`.

## Checks before review

These `scripts/build_deck.sh` runs itself:

| Check | Threshold |
|---|---|
| `^!` lines in `ltxobj/*.log` | 0, both jobs |
| `??` in `pdftotext` of both PDFs | 0 |
| "empty citation" in the logs | 0 |
| `Overfull \vbox` in `ltxobj/slides.log` | 0 |
| `MINTED` in `pdftotext` of both PDFs | 0 (in the notes it means a PythonTeX run from the wrong directory) |
| `wc -l ltxobj/*.pytxcode`, the two jobs | nearly equal |
| `black --check` on the tangled `.py` files | clean, `--exempt GLOB` for hand-written inputs |
| source lines over 79 characters | none |
| `check_provenance.py` on `ltnotes.bib` | `Result: OK` |
| blank-ish slides | reported, not failed: poster and section frames are legitimately sparse |

Every row but the last makes the script exit non-zero. It prints the
counts either way, so read its output rather than only its exit status.

**Five checks it does not run.** Do them yourself before calling a deck
reviewed:

0. **Clipped verbatim lines.** A long program line or transcript line in a
   frame without `shrink` runs off the slide's right edge and LaTeX logs
   nothing. `scripts/cutcheck.py <deck dir> slides notes` finds them two
   ways (a printed line that is a strict prefix of a tangled or
   transcript line; a word whose box passes the page width); it needs the
   deck built. Fix by shortening the text or `shrink`; a chunk frame at
   the decks' minted size shows about 69 characters.

1. **Margin notes.** Every margin footnote must print on the page carrying
   its marker; a note pushed to the next page is a layout defect.

   ```bash
   python3 ~/.claude/skills/didactic-decks/scripts/check_margin_notes.py \
           ltxobj/notes.pdf
   ```

   It warns when it cannot recognise one half of a pair, which means read
   that page by eye.
2. **`check_metadata.py` on `ltnotes.bib`** — left out of the script
   because it queries Crossref over the network. Run it once per revision,
   from the `backing-claims` skill.
3. **Running the tangled examples.** The build already ran every program
   carrying a `\runpython`, so for those the check is to read the
   transcripts against the tangled files. Programs without one are run by
   hand, with the input the deck feeds them —
   `python3 x.py < /dev/null` reports a false failure for anything that
   reads input. `references/review-checklist.md` has the recipe.
4. **Reading every slide and every notes page** — contact sheets with
   `pdftoppm -r 40` plus `montage`, then close reads of anything that
   looks wrong. No script replaces this.

`references/review-checklist.md` has every command in full, and the
warnings that are known to be harmless.

## Keeping the template in sync

`assets/deck-template/PROVENANCE.md` records where the build files came
from and carries a `diff -ru` one-liner. Re-sync when a project's build
wiring changes, and carry over build wiring only: content differences are
expected and must not be copied back.

## The review loop lives elsewhere

Once a deck builds and passes the checks it goes to the author for review.
That loop is documented in two other skills, and nothing about it is
repeated here:

- `remarkable`, section "Transcribing a review round" — uploading the
  notes PDF, reading the annotations back, and turning them into a fix
  list.
- `worktree-subagents`, sections "Reader and fix agents from a brief on
  disk" and "Session limits, resume and unreachable agents" — running the fix agents
  in isolated worktrees, resuming them after a session limit, and cleaning
  up afterwards.

Load those when the deck reaches that stage.
