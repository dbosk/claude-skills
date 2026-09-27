# Binding decks into a book

A set of decks (each `contents.nw` → `notes.pdf`/`slides.pdf`) can be bound
into one memoir book that reads each deck's own woven files, so the decks
keep building standalone and the book never forks their text.

Worked example: intropy's `book/` (DD1317, 2026-09), weeks 37–39, eight
decks. Its names (`modules/`, *Den vetenskapliga grunden*, `bok.tex`)
appear below only where marked as the example.

Contents: [Layout decisions](#layout-decisions) ·
[Files](#files) · [The `\deck` macro](#the-deck-macro) ·
[The appendix part](#the-appendix-part) · [Paths](#paths) ·
[Unique names](#unique-names-across-decks) · [Makefile](#makefile) ·
[Adding a deck](#adding-a-deck) · [Checks and known issues](#checks-and-known-issues)

## Layout decisions

The author's decisions, with the reason each was taken:

- **A `book/` directory** at the repo root, beside the deck tree. It
  `\subimport`s the decks' files; it never copies them.
- **Two editions, one body.** The teacher edition keeps the `\ltnote`s;
  the student edition is the same body after `\ltnoteoff`. The drivers
  differ in that one line.
- **memoir `book` with didactic's layout** (outer margin notes, side
  captions, the semantic environments), loaded as in the decks, so a page
  of the book looks like a page of the notes.
- **One `\part` per unit** (a week, named after its LMS module), **one
  `\chapter` per deck** in the course's reading order: lectures, then the
  unit's tutorial.
- **Chapter opening**: heading; the deck's `abstract.tex` under an
  unnumbered `\section*{\abstractname}` at full text width (not memoir's
  `abstract` environment, whose centred title and narrowed block break
  the flush-left typography); `\clearpage`; the chapter's own full-depth
  ToC (etoc `\localtableofcontents*`, starred so it adds no ToC line);
  `\clearpage`; the text.
- **No forced page breaks inside a chapter.** The decks' `\clearpage`s
  were placed to drain the margin queue at standalone page positions; in
  the book they only leave short pages, so `\deck` neutralises them
  locally.
- **Main ToC: parts and chapters only** (`\etocsetnexttocdepth{chapter}`
  before `\tableofcontents*`). This is the book's deliberate exception to
  the decks' "memoir's default depth" rule: each chapter carries its own
  full-depth ToC.
- **The backing appendices in a final part** (example: *Den vetenskapliga
  grunden*), one chapter per deck in chapter order, named after the deck,
  its appendices as sections **lettered exactly as standalone** (A, B, …),
  so a cross-deck pointer "föreläsningen *X*, bilaga B" stays true.
- **A bibliography per chapter**: every text chapter and every appendix
  chapter is its own biblatex `refsection`, so verbose citations restart
  and each ends with its own list (`heading=subbibintoc`).
- **One preamble**: the union of the decks' preambles. The target is one
  joint preamble symlinked into every deck and used by the book; until
  then the book's `preamble.tex` is a copy and drifts (see known issues).
  A setting that conflicts between decks goes in `\deck`'s optional
  argument, never in the shared preamble.

## Files

| File | Holds |
|---|---|
| `bok.tex` | student edition: `memoir` options, `\input{preamble.tex}`, `\ltnoteoff`, `\input{book-body.tex}` (example names) |
| `bok-larare.tex` | teacher edition: the same without `\ltnoteoff` |
| `book-body.tex` | `\begin{document}`, front matter, the `\part`s and `\deck` lines, the appendix part |
| `preamble.tex` | the decks' union preamble, plus `beamerarticle`, `noweb`, etoc and the binding macros |
| `Makefile` | deck weave/tangle, bib merge, checks, both editions |
| `check_labels.py`, `check_bib.py` | cross-deck collision checks (below) |
| `.gitignore` | both PDFs, merged `ltnotes.bib`, `latexmkrc`, `*.pytxcode`, `pythontex-files-*`, `.venv/`, `didactic_output_*.txt` |

The driver class line: `\documentclass[a4paper,10pt,oneside,openany,oldfontcommands]{memoir}`.

## The `\deck` macro

`\deck[<setup>]{<unit>/<deck>}{<title>}` binds one deck as one chapter.
It is one `refsection` **and** one TeX group, so a deck's own
`\newcommand`s and `<setup>` stay in its chapter. `<setup>` holds the
deck-local settings that differ between decks (example: cleveref's name
for a list item, *steg* in one deck, *rad* in another). The same
`<setup>` is replayed in the deck's appendix chapter.

```latex
\deck{variables/slides-functions}{Funktioner}
\deck[%
  \crefname{enumi}{rad}{raderna}\Crefname{enumi}{Rad}{Raderna}%
]{variables/tutorial}{Övning: Funktioner och variabler}
```

The body of `\deck`, condensed (the `\label` lets the appendix chapter
point back; the `lo` reset restarts the learning objectives as standalone):

```latex
\NewDocumentCommand{\deck}{O{}mm}{%
  \begin{refsection}%
  \chapter{#3}\label{book:#2}%
  #1%
  \ifcsname c@lo\endcsname\setcounter{lo}{0}\fi
  \section*{\abstractname}
  \subimport{../modules/#2/}{abstract.tex}%
  \clearpage
  \localtableofcontents*
  \clearpage
  \let\clearpage\par            % the decks' in-chapter breaks
  \subimport{../modules/#2/}{contents.tex}%
  \printbibliography[heading=subbibintoc]%
  \end{refsection}%
  \g@addto@macro\book@appendixchapters{\book@appendixchapter{#1}{#2}{#3}}%
}
```

A counter the book restarts per chapter needs chapter-qualified hyperref
anchors, or hyperref links to the first chapter's objective:
`\AtBeginDocument{\def\theHlo{\theHchapter.\arabic{lo}}}`.

Dropping the in-chapter `\clearpage`s costs margin space on dense pages.
The example compensates by setting margin notes one size smaller
(`\renewcommand{\foottextfont}{\scriptsize\mpjustification}`) and letting
the margin column run into the empty bottom margin
(`\marginheightadjustment=48pt`, marginfix; the page number is in the
running head).

## The appendix part

`\deck` queues each deck; the last part calls the queue:

```latex
\part{Den vetenskapliga grunden}   % example name
\scienceappendices
```

Each queued chapter is a `refsection` named after the deck, opening with
one sentence pointing back to `\cref{book:<deck>}`, its
`\localtableofcontents*`, then `sokprotokoll.tex` inside an environment
that shifts the headings one level down, locally:

- `subappendices` with `\renewcommand{\setthesection}{\Alph{section}}` and
  `\crefalias{section}{appendix}`, so the sections are lettered A, B, …
  and `\cref` still says *bilaga*/*appendix*;
- `\chapter`→`\section`→`\subsection`→`\subsubsection`→`\paragraph`
  (save the originals first; starred forms follow);
- `\let\chapterprecis\chapterprecishere` and `\prechapterprecisshift=0pt`,
  so the precis prints under the section heading without memoir's pull-up
  and without a ToC line.

Labels are global, so the chapter text's `\cref`s to its appendices
resolve across parts.

## Paths

A deck's paths are relative to its own directory. What makes each kind
resolve under `\subimport`:

| Path kind | Mechanism |
|---|---|
| `\input`, `\includegraphics` | `import`'s `\subimport` |
| `\inputminted{...}{examples/x.py}` | minted prefixes the import path itself (checked with v3.8) |
| `\runpython`, `\runshell` (`cwd`, `stdinfile`, `deps`) | didactic ≥ 2.6: `\runbasedir{auto}` once in the preamble |
| Mentipy (`Store("mentipy.json")`, `qr_dir`) | `\mentipybasedir{auto}` from `mentipy.sty` (dbosk/mentipy PR #46; check that it is merged and released) |

Both `auto` forms follow `\import@path` and assume PythonTeX's working
directory is the main document's directory. With the deck-standard
`\setpythontexoutputdir{.}` plus `\setpythontexworkingdir{..}` under
`ltxobj/`, it is; with anything else, give the base directory explicitly.
didactic writes its transcript files (`didactic_output_*.txt`) in the
directory PythonTeX started in (the book's), whatever the base directory.

**Fallback only**, for a Mentipy without `\mentipybasedir`: change the
whole PythonTeX session into the deck's directory for each chapter
(`\pyc{book_enter_deck('../modules/#2')}` after the heading,
`\pyc{book_leave_deck()}` before `\end{refsection}`, the functions
`os.chdir`-ing relative to the book's directory saved at the first
`pycode`). PythonTeX runs all of a session's code in document order, so
the change holds until the next one. Drop it once the Mentipy release
has the base directory; didactic ≥ 2.6 no longer needs it, and its
`didactic_track` already makes the reported paths absolute.

## Unique names across decks

One document means one namespace. Fix collisions **at the source**, in
the deck, so the standalone build and the book agree:

- **noweb chunk labels** are named after the woven file, and every deck's
  file is `contents.nw`. Weave each deck under a path that names it (the
  same file, a different name):

  ```make
  NOWEB_NAME=	../../$(notdir $(abspath ..))/$(notdir ${CURDIR})/contents.nw
  contents.tex: contents.nw
  	noweave ${NOWEAVEFLAGS.tex} ${NOWEB_NAME} > $@
  ```

- **LaTeX labels**: every deck has a method appendix; give its label a
  per-deck suffix (`app:verifiera-<deck>`), and rename any other label two
  decks share (`sec:...`, `tab:...`). `restatable` names define macros
  and must be unique too. `check_labels.py` reads the `\deck` list, scans
  each deck's `abstract.tex`, woven `contents.tex` and `sokprotokoll.tex`
  for `\label`, `restatable` names and noweb `\sublabel`s, and fails on a
  name defined in two decks (LaTeX itself only warns).
- **Bib keys**: the book merges the decks' `ltnotes.bib` with bibtool
  (the makefiles' `ARCHIVE.bib` recipe: sort, drop duplicate keys), which
  keeps one entry per key blindly. So a key must be identical in every
  deck: make the entries identical at the source, the fuller verified
  entry winning, provenance blocks kept. `check_bib.py` compares entries
  field by field (whitespace and comments aside) and fails the merge on
  any key that differs. Delete the merged file before re-merging, since
  the recipe appends.

## Makefile

- **One deck list.** Read `DECKS` from the `\deck` lines of
  `book-body.tex` (the example uses `sed`), so adding a deck is one line.
  Keep every `\deck` in a form the parsers match: `\deck{<path>}{…}` on
  one line, or the optional argument over several lines with the closing
  `]{<path>}{…}` at the start of a line.
- **Decks first**: each deck's `contents.tex` depends on its
  `contents.nw` via `$(MAKE) -C <deck> contents.tex examples`, so the book
  reads exactly what the deck's notes read.
- `ltnotes.bib: <deck bibs> book-body.tex` runs `check_bib.py`, removes
  the old file, merges. `check-labels` is an order-only prerequisite of
  both PDFs.
- **`ltxobj/_minted` before the book build** (order-only): under
  `\subimport`, minted's `\IfFileExists` also finds a built deck's
  `ltxobj/_minted` style file, never creates the book's cache directory,
  and the book then shows `<MINTED>` placeholders.
- `LATEXFLAGS+= -shell-escape`, `TEX_PYTHONTEX=yes`,
  `--rerun=always` (both editions share `ltxobj/`), and for Mentipy decks
  a book-local venv made by `mentipy init --venv` as in the decks.
- **Raise latexmk's `max_repeat`.** didactic's citation-footnote reuse
  decides from the previous pass, so the book needs many passes from a
  clean `.aux` (example: 13 and 14 passes for eight decks, limit set to
  20; it grows with the book). The example overrides tex.mk's `PDFLATEX`
  with `-e '$$max_repeat=20'`. For a quick draft, load didactic with
  `footnotereuse=off` (the default under `draft`, which also blanks
  graphics): no extra passes. The final build keeps the default `fast`.
- **One job at a time**: never build the two editions concurrently; they
  share `ltxobj/`, `_minted` and the transcript files.

## Adding a deck

A deck enters when it is literate (`contents.nw`), merged, and published
to the students. Then, in the deck (committed there, one commit per deck):

1. Weave under the deck's path (`NOWEB_NAME` above).
2. Rename its method-appendix label per deck, and any label
   `check_labels.py` reports.
3. Reconcile every bib key `check_bib.py` reports.
4. Anything its preamble adds goes into the book's preamble; a setting
   that conflicts with another deck goes into its `\deck` `<setup>`.
5. The standalone build still passes `scripts/build_deck.sh`.

In the book: add the `\deck` line in reading order under its unit's
`\part` (a new unit gets a new `\part`), build both editions, run the
checks below.

## Checks and known issues

- **Convergence**: after the build, the last pass left the `.aux`
  unchanged: no `Rerun` / `rerun` requests in `ltxobj/bok*.log`, and no
  latexmk "Maximum runs … reached" in the build output. Otherwise run
  make again (it continues) or raise `max_repeat`.
- **The deck checks on the book PDFs**: 0 `^!`, 0 `??`, 0 `MINTED`, 0
  "empty citation"; `check_labels.py` clean; each appendix chapter's
  letters match the standalone notes; the student edition's `pdftotext`
  has no `\ltnote` text and the teacher edition has it.
- **Margin-note spills** (a note printed on the page after its marker):
  run `scripts/check_margin_notes.py` on **each book PDF**. A clean
  standalone deck says nothing about the book: its pages fall elsewhere
  and its `\clearpage`s are gone.
- **Teacher-edition crowding**: with every `\ltnote` on, dense pages run
  out of margin and notes queue forward; a didactic-side remedy is under
  investigation. Do not bring back forced page breaks to fix it.
- **Fragile points**: `\let\clearpage\par` also stops `\clearpage` from
  flushing floats inside a chapter; the book's preamble copy drifts from
  the decks' until the joint preamble exists; the `\deck`-list parsers
  (Makefile, both scripts) only match the two forms above.
