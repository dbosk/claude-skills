# Deck anatomy: files, drivers, preamble, abstract, appendices

Contents: [Files](#files) · [slides.tex](#slidestex) · [notes.tex](#notestex) ·
[preamble.tex](#preambletex) · [abstract.tex](#abstracttex) ·
[sokprotokoll.tex](#sokprotokolltex-the-search-appendices) ·
[ltnotes.bib](#ltnotesbib)

## Files

One deck directory builds two PDFs from one source.

| File | Committed | Purpose |
|---|---|---|
| `contents.nw` | yes | the single source: prose, frames, chunks, `\ltnote`s |
| `contents.tex` | **no** | woven from `contents.nw`; never edit it |
| `examples/` | **no** | tangled from `contents.nw`; entirely generated |
| `slides.tex` | yes | beamer driver |
| `notes.tex` | yes | memoir + beamerarticle driver |
| `preamble.tex` | yes | shared by both drivers |
| `abstract.tex` | yes | overview, learning objectives, prerequisites |
| `sokprotokoll.tex` | yes | the appendices: method + one chapter per backed claim |
| `ltnotes.bib` | yes | sources, each with a provenance block |
| `litteratursokning/*.tex` | yes | generated hit-list tables, `\input` by the appendices |
| `figs/` | yes | figures the deck includes |
| `Makefile` | yes | see `build-and-gotchas.md` |
| `notes.pdf`, `slides.pdf` | **no** | symlinks into `ltxobj/` |
| `latexmkrc` | **no** | tangled from the makefiles submodule's `tex.mk.nw` |
| `ltxobj/` | **no** | build directory, ignored repo-wide |

`.gitignore` must list the PDFs, `contents.tex`, `examples/`, `latexmkrc`
and PythonTeX's `didactic_output_*.txt`, `*.pytxcode`,
`pythontex-files-*`. Data files a deck *reads* (a directory of CSV files
under `examples/`, say) are tracked inputs and must be excluded from the
`examples/` ignore rule.

## slides.tex

After `\input{preamble.tex}`:

```latex
\usepackage[minted]{noweb}
\noweboptions{breakcode,nomargintag,noxref}
```

Then neuter the chunk cross-referencing apparatus. Sub-page labels break
under beamer overlays, because `\pause` re-executes the frame body and the
labels come out multiply defined; the defines/uses lists are noise on a
slide.

```latex
\def\sublabel#1{}
\def\subpageref#1{}
\def\nwindexdefn#1#2#3{}
\def\nwindexuse#1#2#3{}
\def\nwidentdefs#1{}
\def\nwidentuses#1{}
\def\nwused#1{}
\def\nwnotused#1{}
\def\nwalsodefined#1{}
\def\nwusesondefline#1{}
\def\nwprevnextdefs#1#2{}
```

`\nwusesondefline` must go too: the "(used in ...)" tag resolves a
`\subpageref`, which is gutted above, so leaving it in produces undefined
references.

**Block titles in the document's language.** beamer names its
example/definition/theorem blocks through the `translator` package, which
ships no Swedish dictionary, so without this block the titles come out in
English. Put it **before** `\usetheme`:

```latex
\uselanguage{Swedish}
\languagepath{Swedish}
\deftranslation[to=Swedish]{Example}{Exempel}
\deftranslation[to=Swedish]{Definition}{Definition}
\deftranslation[to=Swedish]{Theorem}{Sats}
\deftranslation[to=Swedish]{Lemma}{Lemma}
\deftranslation[to=Swedish]{Corollary}{Följdsats}
\deftranslation[to=Swedish]{Proof}{Bevis}
```

Add `\deftranslation[to=Swedish]{Summary}{Sammanfattning}` if didactic's
`summary` block still shows "Summary" on the rendered slides.

didactic's theorem-style environments (`remark`, `idea`, `question`,
`exercise`, ...) have no beamer counterpart; `slides.tex` maps each onto a
block with `\ProvideDocumentEnvironment`. Keep only the ones the deck uses.

The bibliography frame stays commented out: the sources belong to the
notes, since the `\ltnote`s are instructor-facing and the search protocol
is an appendix of the notes.

## notes.tex

`memoir` with `[a4paper,10pt,oneside,openright,oldfontcommands]`, then
`\input{preamble.tex}`, then `\usepackage[noamsthm,notheorems]{beamerarticle}`,
then:

```latex
\usepackage[minted]{noweb}
\noweboptions{breakcode}
\def\nwidentdefs#1{}
\def\nwidentuses#1{}
```

The notes keep the full noweb apparatus — margin sub-page tags,
`⟨chunk 2a⟩≡` headers, "used in" cross-references — because that is the
point of literate notes. Only the identifier index is hidden: it
recognises ASCII identifiers only and indexes every language with the same
machinery, so the lists come out inconsistent and read as errors
(dbosk/noweb#13).

Body order: `\maketitle`, the `abstract` environment wrapping
`\input{abstract.tex}`, `\clearpage`, `\tableofcontents*`, `\chapter{...}`,
`\input{contents.tex}`, then

```latex
\appendix
\crefalias{chapter}{appendix}
\input{sokprotokoll.tex}
\printbibliography
```

## preamble.tex

Requirements beyond the ordinary packages:

- `\usepackage{minted}` plain. **Never** `\usepackage[outputdir=...]{minted}`:
  minted v3 (TeX Live 2024+) errors on that option. noweb's `[minted]`
  option tolerates minted being loaded already.
- `\usepackage[makestderr]{pythontex}`, `\setpythontexoutputdir{.}`,
  `\setpythontexworkingdir{..}`. PythonTeX runs from `ltxobj` (the output
  directory), and `workingdir=..` moves it up to the deck directory so
  `examples/...` resolves.
- `\usepackage[marginparmargin=outer]{didactic}` followed immediately by:

  ```latex
  \extrafloats{200}
  \ifdefined\setsidecappos\setsidecappos{b}\fi
  ```

  didactic sets footnotes — and, under the verbose citation style, every
  `\autocite` — as margin notes, and LaTeX allocates `\marginpar` boxes
  from the same pool of eighteen boxes as floats. A citation-heavy chapter
  empties the pool and dies with "Too many unprocessed floats" pages after
  the cause. memoir places a side caption with `\rlap`, so it takes part in
  no collision avoidance and silently overprints an `\ltnote` at the same
  height; anchoring the caption at the bottom moves it below the notes.
  `\setsidecappos` is memoir's, so guard it with `\ifdefined` — beamer does
  not define it.
- cleveref's language comes from **its own** package options, not babel's:
  `\usepackage[swedish]{cleveref}`. Fix the names memoir and babel disagree
  about in an `\AtBeginDocument` hook registered after cleveref's own, so
  yours wins (`appendix` → bilaga, `enumi` → rad, `footnote` → fotnot).
- The `lo` environment for learning objectives:

  ```latex
  \ProvideSemanticEnv{lo}{Learning Objective}
    [style=definition,numbered=yes]
    {LO}{LO}
    {Learning objective}{Learning objectives}
  ```

  plus `\ProvideTranslation` lines per language.
- `\usepackage{thmtools,thm-restate}` for the `restatable` objectives.
- `\DeclareUnicodeCharacter` mappings for Greek letters that appear in
  generated hit-list tables.

## abstract.tex

Three parts, marked with `\emph`, not `\section`:

1. **Översikt** — one paragraph: what question the deck opens with, what
   it takes the student through, where it stops.
2. **Lärandemål** — one `restatable` `lo` environment per objective,
   labelled `<Module>LO<Aspect>` so the notes can restate the objective
   where the prose meets it (`\ModuleLOFirst`). Objectives say what the
   student can do, in plain words, without restating the mechanism. Keep
   the course's own outcome codes in a LaTeX comment, not in the text.
3. **Förkunskaper** — what the student should have met first, named by
   deck title, never by week or lecture number.

An optional **Läsning** part points at supporting material.

## sokprotokoll.tex: the search appendices

Bilaga A is the method, written for the students: turn the claim into a
question, choose the right kind of source, search so you can be wrong, read
in full text and record how, draw the conclusion with its reservations.
It opens by listing the deck's claims that cannot be checked at the
keyboard, each `\cref`ed to the section that makes it.

Then **one chapter per backed claim**, in this shape:

1. Title = the question the chapter answers.
2. `\chapterprecis{...}` — a verbatim project sentence saying the author
   has not yet reviewed the results in full.
3. An opening paragraph: where the claim is made, what exactly is claimed
   (often two claims, establishment and origin), the question, and a road
   map of the sections.
4. `\section{Metod}` — date, which databases answered and which refused,
   what the supporting and counter queries look for, then the query table
   (S-rows and M-rows, hits per database), then screening counts and how
   many sources were read in full text.
5. `\section{Resultat}` — what the sources say, supporting and qualifying
   alike, with quotes.
6. `\section{Diskussion och begränsningar}`.
7. `\section{Slutsats}` — the **first sentence** answers the chapter's
   question.
8. `\section{Fortsatt arbete}` — what this search left undone and what the
   field would have to study for a surer answer.
9. `\section{Träffar som rör påståendet}` with `\input` of the generated
   hit list from `litteratursokning/`.

A claim already backed in another deck is not searched again: cite the same
source, copy its provenance block, add `% FOUND-VIA (here): backed in
<deck>, bilaga <X>`, and point at it in prose. `\cref` cannot cross
documents, so the pointer names the other deck by title.

## ltnotes.bib

Every entry carries a provenance block (`CLAIM`, `FOUND-VIA`, `PICKED`,
`QUOTE`, `VERIFIED`, `COUNTER`, `DATE`). Load the `backing-claims` skill
before adding or reusing any entry; it owns the format and ships
`check_provenance.py` and `check_metadata.py`.
