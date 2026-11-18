# Bilingual decks

One `contents.nw` holds an English and a Swedish edition: code, runs,
figures and structure are written once, the prose twice. The mechanism is
didactic's, and this file describes **didactic v2.18 or later**; its
documentation states it in full, in the sections **Bilingual documents**
and **Keeping the two languages in step** of `didactic.pdf` (next to the
installed package: `kpsewhich didactic.sty`; `texdoc didactic` may find an
older copy in TeX Live). This file holds what an author or agent must
have in hand for a deck.

**A source written for v2.17** (blocks `\begin{en}`, `\begin{sv}`, stamps
`% sync en=… sv=…`) stops both the build and `didactic-sync.py` (exit 2)
with a message naming the fix: rewrite it with `python3
"$(kpsewhich didactic-sync.py)" --migrate FILE…`. That rewrites the
blocks, the stamps' keys and `language=`/`\didacticlanguage` settings,
keeps every hash (so a source in step stays in step) and leaves blocks
shown in code or comments alone; `en` becomes `english` unless `--en
british` is given (both are one edition). Run it on every `.nw` and
`.tex` of the deck, then the check, and do not stamp anything for it.

Contents: [Layout and build](#layout-and-build) ·
[Converting a thick-driver deck](#converting-a-thick-driver-deck) ·
[Writing the pairs](#writing-the-pairs) ·
[In contents.nw](#in-contentsnw) ·
[Stamps](#stamps) ·
[Reference names](#reference-names) ·
[House styles](#house-styles) ·
[Limits](#limits)

## Layout and build

| Driver | Output | Output directory |
|---|---|---|
| `notes.tex`, `slides.tex` | `notes.pdf`, `slides.pdf`: the course's main language | `ltxobj` |
| `notes-sv.tex`, `slides-sv.tex` | `notes-sv.pdf`, `slides-sv.pdf`: Swedish | `ltxobj-sv` |

The layout assumes that **the second edition is Swedish**, which fits a
course whose main language is English. A course whose main language is
Swedish and wants an English second edition would have to change three
things: `OTHER_EDITIONS` in `scripts/build_deck.sh` (`-en`), the names of
the second pair of drivers (`notes-en.tex`, `slides-en.tex`, with the
English edition lines), and the `Makefile`'s `TEX_OUTDIR` line
(`notes-en.pdf slides-en.pdf: TEX_OUTDIR=ltxobj-en`, and the `PDFS` and
`clean` lines); then the unsuffixed drivers carry the Swedish lines.

- **The edition is babel's main language.** Each driver is four lines:
  `\PassOptionsToPackage{main=british}{babel}` (or `main=swedish`),
  cleveref's languages with the edition's **last**, then
  `\input{notes-body.tex}` or `\input{slides-body.tex}`. The preamble
  loads babel with both languages and cleveref with none. `british` or
  `english` gives the English edition, `swedish` the Swedish one.
- **One output directory per edition** (`notes-sv.pdf slides-sv.pdf:
  TEX_OUTDIR=ltxobj-sv` in the `Makefile`). PythonTeX's `.stdout` files
  do not say which job wrote them: in a shared directory a job that
  latexmk rebuilds without a PythonTeX run prints the other edition's
  transcripts, with exit 0 and no warning (`python3 hello-sv.py` in the
  English notes). The two jobs of one edition share their directory, as
  in a single-language deck.
- **A deck is bilingual when `notes-sv.tex` or `slides-sv.tex` exists.**
  `build_deck.sh` then builds four jobs, runs every check per edition,
  runs `didactic-sync.py` on the deck's own `.nw` and `.tex` sources
  (exit 1 or 2 fails, and so does a missing script), and fails when two
  editions' logs share a directory. `check_transcripts.py`, run for every
  deck, fails a job that printed transcripts from another job's PythonTeX
  run. So **ALL CHECKS PASSED means the two languages are in step**;
  `--draft` relaxes only the overfull-line check, never the sync check.
- **Single-language deck**: delete the `-sv` drivers (English only); for
  Swedish only, also set `main=swedish` and `english,swedish` (no
  `capitalise`) in the two remaining drivers. Nothing else changes.
- Never `\documentclass[swedish]{beamer}`: a class option reaches
  cleveref and turns its language order round. beamer's own block titles
  (translator's "Example", "Theorem") follow babel because didactic sets
  translator up for babel's Swedish itself: **the Swedish block titles
  need didactic v2.17.1 or later**. The slides body keeps only the
  `\deftranslation` house terms (Sats, Följdsats).
- From v2.17.1 a Swedish edition also gets translator's other words in
  Swedish (e.g. "Avsnitt" on a `\sectionpage`); the template's slides show
  no such page.

## Converting a thick-driver deck

A deck made before the current template has thick `slides.tex` and
`notes.tex`. To make it bilingual:

1. Move them to `slides-body.tex` and `notes-body.tex` (`git mv`, so the
   history follows), and copy the four drivers from
   `assets/deck-template/`.
2. In `slides-body.tex`, delete `\uselanguage{Swedish}` and
   `\languagepath{Swedish}` (didactic v2.17.1 sets translator up; the
   `\languagepath` would make the English edition Swedish), keep the
   `\deftranslation` lines, and delete the class option `swedish` if
   there is one.
3. In `preamble.tex`, load cleveref without a language
   (`\usepackage{cleveref}`: the drivers pass it), and take the
   `\crefname` block with its stamps from the template's preamble.
4. In the `Makefile`, take the template's `PDFS` lines, the body
   prerequisites, the `TEX_OUTDIR=ltxobj-sv` line and the `clean` lines;
   in `.gitignore`, add `notes-sv.pdf`, `slides-sv.pdf` and `ltxobj-sv/`.
5. Write the titles as `\ensv`, the prose in `onlyin` pairs, then build
   from clean and stamp each pair once both sides are written.

## Writing the pairs

- **Prose in block pairs**, one paragraph or list per block:
  `\begin{onlyin}{english}` … `\end{onlyin}` then
  `\begin{onlyin}{swedish}` … `\end{onlyin}`. The argument is babel's
  name (`english` and `british` are one language); a tag such as `sv` is
  an error. Blocks of different languages pair when only blank lines and
  comments lie between them.
- **Short strings with `\ensv{English}{Svenska}`**: titles of frames,
  sections, blocks and the deck, captions, list items, a word in a
  sentence. The decks use `\ensv`. `\sven{Svenska}{English}` is the same
  with the order swapped; `\didactictr[english,swedish,…]{…}{…}` takes
  any languages, one text each (one language named twice is an error),
  and plain `\didactictr{English}{Svenska}` is the form for a file or
  package that defines its own `\ensv`.
- **A term that is the same in both languages is written plainly**, not
  `\ensv{Term}{Term}`: every `\ensv` is a pair to stamp.
- **Keep lines short by wrapping inside the second argument**:
  `\ensv{...}%` then the Swedish half indented on the next line.
  Re-wrapping changes no stamp.
- **`\end{onlyin}` stands alone in column 1**, or the block never ends
  ("File ended while scanning use of \next"); the script reports it
  (exit 2). **Text after `\begin{onlyin}{english}` on the same line is
  dropped** by LaTeX; the script reports it (exit 2).
- **No block inside a block**: the inner `\end{onlyin}` ends the outer
  one (exit 2). A block may input a file that holds blocks.
- **`\ensv` takes its arguments as arguments**: they cannot hold verbatim
  material, `\verb` or a chunk; noweb's `[[code]]` quoting is fine. Use a
  block pair for anything verbatim.
- **A frame holding a block is `[fragile]`**; on the slides any other
  frame fails.
- **No block inside a macro argument** (`\ltnote{}`, `\mode<article>{}`,
  `\only<2>{}`, `\footnote{}`, a `restatable` learning objective): put the
  pair around the macro, or `\ensv` inside it. Both blocks of a pair may
  define the same `\label`; only one is read.
- **A block around a frame or a sectioning command** needs `\mode<all>`
  before the pair and `\mode*` after it, or the slides print both.
- **A block with no partner belongs to one edition.** If it sits directly
  before a pair, put a line with `\relax` between them, or the script
  pairs it with the wrong block.
- **A pair with an empty side cannot be stamped**: write the word one
  language lacks as `\ensv{the }{\relax}`.
- **`\ltnote`s are translated like the prose** (author, 2026-11-18: the
  Swedish edition goes into a Swedish teacher's book): a pair of blocks
  around two `\ltnote`s, or `\ltnote{\ensv{…}{…}}` for a short one. Each
  is stamped as a pair. The `sv` side follows `house-style-sv.md`.

## In contents.nw

- **`@` alone on its line before `\end{onlyin}`**: `@ \end{onlyin}`
  becomes one woven line that does not end the block (exit 2).
- **The file's last code chunk stands outside any block**, or the other
  edition loses noweb's chunk index (the script notes it on stderr).
- **A program per language tangles to its own file name**
  (`hello-en.py`, `hello-sv.py`): notangle ignores the blocks and tangles
  both, so both go on `EXAMPLES+=` lines. A chunk defined in a block is
  used only in that block.
- Shared chunks, runs and figures carry names both languages read alike
  (`house-style-en.md`, "Bilingual decks").

## Stamps

A pair is in step when each side still has the hash recorded in its
stamp, a trailing `% sync english=… swedish=…`: at the end of a block
pair's first `\begin` line, and at the end of the line where an `\ensv`
ends. The keys are the names the sides are written in (a block changed
from `{english}` to `{british}` keeps its stamp; a key that names no
side is an error). **Only the script writes stamps; never type or edit
one.** The line-length check ignores a trailing stamp.

```bash
SYNC=$(kpsewhich didactic-sync.py)
python3 "$SYNC" contents.nw abstract.tex       # report; exit 0, 1 or 2
python3 "$SYNC" --stamp contents.nw:42.2       # the name exactly as reported
python3 "$SYNC" origin/master...HEAD           # what a branch re-stamped
```

- **Stamp a pair only after reading both sides and judging that they say
  the same thing.** Never stamp in a loop, a whole file, or to make a
  check pass: a stamp is a judgement, and a stamp nobody judged hides
  exactly the drift the check exists to catch.
- After changing one side, either translate the other and stamp, or (a
  typo fix needing no translation) stamp alone; both are judgements.
- `--stamp FILE:LINE[.N]` takes the name exactly as the report gives it
  (`.N` numbers the pairs when several end on one line).
- `A...B` lists the pairs a branch re-stamped while only one side changed:
  put that listing in the pull request's body, so the reviewer can check
  those acceptances.

## Reference names

- **cleveref's `capitalise` is in the English drivers only**; the
  Swedish edition has none. English prints "Fig." unless the deck adds
  `noabbrev`; the house style has not decided that.
- **Names set with `\crefname` are never capitalised by cleveref**: the
  template's preamble writes them with `\ensv` and the English half
  capitalised by hand (`\ensv{Appendix}{bilaga}`), already stamped.
- **didactic's own names follow `capitalise` from didactic v2.17.2**: the
  English edition prints "Exercise 1" beside "Section 1.2", the Swedish
  one "övningsuppgift 1"; the names follow babel's current language.
  (Before v2.17.2 they stayed lowercase, didactic#107.)
- A deck's own `\crefname` for one of didactic's types goes in
  `\AtBeginDocument`, as the template's do: set in the preamble, it is
  replaced. `\lcnamecref` on didactic's types stops with an error
  (didactic#115).

## House styles

The `english` blocks and the English halves of `\ensv` follow
`house-style-en.md`; the `swedish` blocks and the Swedish halves follow
`house-style-sv.md`; `wording.md` holds for both. A pair says the same
thing at the same strength; it is not a word-for-word translation.

## Limits

The script reads the source without running TeX (didactic#106):

- a `%` inside a verbatim-like macro the script does not know (a
  package's own inline-code command) reads as a comment; `\verb`,
  `\mintinline`, `\url` and PythonTeX's `\py` and its kin are known;
- a lone block directly before a pair of other languages is paired with
  the wrong block, hence the `\relax` rule above;
- a block in the command form `\frame{…}` is not reported as needing
  `[fragile]`; the environment form is;
- an `\ensv` defined in another file or package is invisible to it: use
  `\didactictr` there;
- `\index{\ensv{…}{…}}` sorts under the macro, the same in both editions;
- the branch listing can show the diff against the wrong pair when both
  sides of two pairs are rewritten in one range.

PythonTeX: since didactic v2.18.1 the transcript files are written into
each job's output directory, so the two editions (`ltxobj`, `ltxobj-sv`)
no longer share or delete each other's (didactic#118; under v2.18 they
lay in the deck directory and could). Nothing in the checks depends on
that, so the skill works with v2.18, but use v2.18.1 or later. The two
jobs of one edition still share their directory; `build_deck.sh`'s rerun
of PythonTeX before each rebuilt job keeps a deck's own build right.

Not yet tested with this layout: Mentipy polls per edition, binding
bilingual decks into a book with `\deck` (`book-binding.md`), and
`\selectlanguage`/`otherlanguage` against cleveref's names.
`cutcheck.py` reads the `-sv` jobs in `ltxobj-sv/` (detector C needs
their log beside the PDF), so far tried on one deck only.
