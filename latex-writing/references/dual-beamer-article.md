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

Put the full text of each question/hypothesis in a macro, and wrap the
macro in the environment where it is first stated:

```latex
% in preamble.tex
\newcommand{\rqpatterns}{Which patterns of variation, if any, ...?}
\newcommand{\hdeep}{Students with a stronger deep approach ...}

% at first statement (inside a frame, so it appears in both outputs)
\begin{question}\label{rq:patterns}
  \rqpatterns
\end{question}
\begin{hypothesis}\label{h:deep}
  \hdeep
\end{hypothesis}
```

Consequences:
- **Never write literal `RQ1`/`H2` in prose** — reference with
  `\cref{rq:patterns}`/`\cref{h:deep}` (cleveref renders "question 1",
  "Questions 1 and 4"; `\Cref` at sentence start). Numbers then survive
  reordering.
- Restate anywhere by using the macro, e.g.
  `For \cref{rq:experts} --- \enquote{\rqexperts} --- we expect ...`.
- In description lists of results per hypothesis, use
  `\item[\Cref{h:patterns}]` rather than `\item[H1]`.
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
