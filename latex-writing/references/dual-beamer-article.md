# Dual beamer/article builds (one source, two outputs)

Conventions for papers built twice from the same content files: once as a
prose article (`article.tex`: memoir + `beamerarticle` +
`\setjobnamebeamerversion{slides}`) and once as slides (`slides.tex`:
`\documentclass{beamer}`). Content files start with `\mode*`; the drivers
`\input` the same files. Reference layout: the vt-debug and
vt-prog-misconceptions repositories.

Search patterns: `pyblock frame`, `ProvideSemanticEnv`, `restatable`,
`biber root`, `mode presentation`.

## PythonTeX: every pyblock goes inside a frame

**Rule: every `pyblock` (and `\printpythontex`) MUST sit inside a
`\begin{frame}[fragile] ... \end{frame}` that renders in BOTH modes.**

Why: `\mode*` makes the slides job skip everything outside frames —
including `pyblock` bodies, which then never reach the slides'
`.pytxcode`. Both jobs share one PythonTeX output directory
(`\setpythontexoutputdir{.}`), so if the two jobs disagree about a
session's block sequence, whichever job's `pythontex` ran last poisons
the other's data.

Symptoms of a violation:
- An output block shows **another block's output** (session numbering
  shifted — e.g. a later example's numbers where lists were expected).
- An output block shows **`?? PythonTeX ??`** (the shorter sequence has no
  block at that index).
- A "clean rebuild" seems to fix it, then it comes back after building the
  other target.

Fix: wrap the offending `pyblock`s in `\begin{frame}[fragile]`, then do a
full clean rebuild (`make clean` plus removing `py_*.stdout`,
`pythontex_data.pkl`, `pythontex-files-*`, `*.pytx*` from the output
directory) so both jobs regenerate consistent session data.

Frames render inline in the article via `beamerarticle`, so wrapping
changes little visually. In the article, give output blocks a title:
`\begin{block}{Output}\printpythontex[verbatim]\end{block}` — an empty
`\begin{block}{}` looks broken in print.

## Restatable semantic environments for RQs and hypotheses

State research questions and hypotheses in **semantic environments with
their text in preamble macros**, so they are numbered like theorems in the
article, rendered as blocks in the slides, cross-referenced with `\cref`,
and restatable verbatim anywhere.

The didactic package provides `question` (and `exercise`, `remark`, `idea`,
…). Declare missing ones (e.g. `hypothesis`) with didactic's own builder —
**the translations must be declared first**, since `\ProvideSemanticEnv`
fetches them at declaration time in article mode:

```latex
% in preamble.tex, AFTER \usepackage{didactic}
\DeclareTranslation{English}{Hypothesis}{Hypothesis}
\DeclareTranslation{English}{hypothesis}{hypothesis}
\DeclareTranslation{English}{hypotheses}{hypotheses}
\DeclareTranslation{English}{Hypotheses}{Hypotheses}
\ProvideSemanticEnv{hypothesis}[block]{Hypothesis}
  {hypothesis}{hypotheses}{Hypothesis}{Hypotheses}
```

Use thmtools' `restatable` (load `\usepackage{thmtools,thm-restate}` in the
document preamble — do NOT add it to didactic; the package itself uses
nothing from it). State once, restate with the starred tag command, which
repeats the original number:

```latex
% at first statement (inside a frame, so it appears in both outputs)
\begin{restatable}{question}{rqpatterns}\label{rq:patterns}
  Which patterns of variation, if any, ...?
\end{restatable}

% restated later (e.g. the method overview), same number, labels gobbled
\rqpatterns*
```

thm-restate assumes theorem environments with counters, which the semantic
environments only are in the *article* build; in the slides they are
counterless beamer blocks. Add this shim to the shared preamble (it is a
no-op for the article job):

```latex
% AFTER \usepackage{didactic}
\makeatletter
\@ifclassloaded{beamer}{%
  \DeclareDocumentEnvironment{restatable}{o m m}{%
    \expandafter\ProvideDocumentCommand\csname #3\endcsname{s}{\relax}%
    \IfValueTF{#1}{\begin{#2}[#1]}{\begin{#2}}%
  }{%
    \end{#2}%
  }%
}{\relax}
\makeatother
```

The wrapper typesets the wrapped environment transparently and defines the
tag command as a star-tolerant no-op, so restatements are simply dropped in
the slides (they belong in article-mode prose, which `\mode*` skips
anyway). Reference implementations: vt-debug's `preamble.tex`,
literate-programming's `src/abstract.tex` (learning objectives).

Consequences:
- **Never write literal `RQ1`/`H2` in prose** — reference with
  `\cref{rq:patterns}`/`\cref{h:deep}` (cleveref renders "question 1",
  "Questions 1 and 4"; `\Cref` at sentence start). Numbers then survive
  reordering.
- A restatement is a full theorem block, not inline text; for an inline
  mention use `\cref`, don't try to quote the statement mid-sentence.
- Verify after building: each statement should appear exactly twice with
  the same number, and later theorems' numbers must be undisturbed
  (`pdftotext file.pdf - | grep -oE "(Question|Hypothesis) [0-9]+\." |
  sort | uniq -c`).
- In beamer the environments render as (unnumbered) coloured blocks —
  that is fine; the numbering matters in the article.

## Slide-only and article-only material

- Slide-only frame: wrap in `\mode<presentation>{ \begin{frame} ... }` —
  NOT `\begin{frame}<presentation>`, which still executes the body in the
  article and orphans citations' margin footnotes ("Float(s) lost", see
  SKILL.md). Fragile caveat: a `[fragile]` frame cannot be `\mode`-wrapped;
  see SKILL.md.
- Article-only prose simply sits outside frames (skipped in slides by
  `\mode*`).
- Bullet lists that duplicate adjacent article prose (summary blocks,
  "Tested"-style remarks, itemised example labels) belong slides-only;
  give the article real prose instead. A reviewer reading the article
  should never see slide bullets restating the previous paragraph.

## Biber for the second job

When one job's citations stay undefined ("Please (re)run Biber"), run
biber manually **from the project root**: `biber ltxobj/<jobname>`.
Never `cd ltxobj && biber <jobname>` — the `.bib` paths in the `.bcf` are
relative to the project root, so biber errors with "Cannot find X.bib"
(and a stray latexmk failure can then leave the aux tree half-cleaned).

## Literate-program appendices (noweb) in a dual-output paper

To include appendix chapters that are literate programs (woven prose +
tangled runnable files) in the article but not the slides:

- Write each appendix as a `.nw` file whose top level matches the paper's
  content files (`\section` when the article remaps `\section`→`\chapter`).
  No `\mode*` needed — only the article inputs the woven `.tex`.
- Load noweb support in **article.tex only** (`\usepackage[minted]{noweb}`
  + `\noweboptions{breakcode,longchunks}`), never in the shared preamble:
  the slides never see woven output and beamer doesn't need the package.
- **Weave highlighted** (the literate-programming skill's standard
  tominted recipe — see it for the one-time lexer whitelist setup):
  override the flags before the include,
  `NOWEAVEFLAGS.tex = -n -delay -autolang -autodefs python3 -index
  -filter 'tominted -lexer noweb_lexer.py'`, add a rule copying
  `noweb_lexer.py` from noweb's lib dir into the project root (where
  LaTeX runs; gitignore it) and make `article.pdf` depend on it. With
  `\setminted{...,breaklines}` overlong code lines *wrap in the PDF* —
  the fix for unbreakable long strings (JSON!) whose format forbids
  literal line breaks: break at the presentation layer, not in the file.
- Build with the makefiles submodule: `include makefiles/noweb.mk`
  (replaces the `tex.mk` include — noweb.mk includes it itself). The
  `%.tex: %.nw` weave rule is automatic; add any non-default suffix
  (`NOWEB_SUFFIXES += .json`) **before** the include, or its
  `NOTANGLE.<suffix>` never gets defined.
- Root chunks are named `<<[[filename]]>>=` (matches noweb.mk's
  `-R"[[$(notdir $@)]]"`). When the tangled filename differs from the
  `.nw` stem (several files from one source), the pattern rules do NOT
  apply — write explicit recipes, as in learnlog:
  `analyze_quiz.py: quiz.nw` + tab + `${NOTANGLE.py}`.
- `NOTANGLE.py` pipes through `black`; gitignore the woven `.tex`, the
  tangled outputs, and `__pycache__/` (a `py_compile` syntax check
  creates it — easy to commit by accident).
- JSON as a tangled artifact works well for optional parts: make the
  optional chunk empty and have the preceding items end without a
  trailing comma, documenting that added items must start with one.
- Cross-reference freely between the woven appendix and the paper's
  sections (`\cref` both ways) — they are one document, and this is the
  main payoff over a separate tool repo.
