# minted v3, and debugging "Float(s) lost"

## minted v3 (TeX Live 2024+) — breaking changes

A document that compiled on older TeX Live can fail after a TeX Live upgrade
because **minted 3.x changed its interface**. Two failures recur:

### 1. The `outputdir` package option is gone

```
! Package minted Error: Package option "outputdir" is no longer needed with
minted v3+; the output directory is automatically detected for TeX Live 2024+...
```

Fix: load minted **without** `outputdir`:

```latex
\usepackage{minted}          % NOT \usepackage[outputdir=ltxobj]{minted}
\setminted{autogobble}
```

The output directory is auto-detected for TeX Live 2024+; otherwise set the
environment variable `TEXMF_OUTPUT_DIRECTORY`. (The shipped reference
`preamble.tex` already loads minted without `outputdir`.)

### 2. The language/lexer argument must not contain a line break

minted v3 is strict about the lexer name. A `minted` environment or
`\mintinline` whose **argument is split across a line break** passes a name with
a stray leading space and fails:

```
! Package minted Error: Pygments lexer " python" is unknown.
```

This is a latent bug that older minted tolerated. It comes from hand-wrapping
source at 80 columns *inside* the macro arguments. Keep each minted invocation's
arguments intact on their own lines:

```latex
% BAD — language split across the newline -> lexer " python"
\begin{minted}[highlightlines={2,7}]{
python}
% GOOD
\begin{minted}[highlightlines={2,7}]{python}

% BAD — \mintinline argument split
output of \mintinline{python}{
x == y}
% GOOD
output of \mintinline{python}{x == y}
```

When wrapping prose, break *between* `\mintinline{...}{...}` calls (at word
boundaries), never inside one.

## Debugging `! LaTeX Error: Float(s) lost.`

This fatal error is reported at `\end{document}` and **names no location**, so
latexmk/biber/PythonTeX noise easily masks the real cause. To see the genuine
first error, run one bare pass with halt-on-error instead of trusting the
latexmk summary:

```bash
pdflatex -shell-escape -halt-on-error -interaction=nonstopmode \
    -output-directory=<outdir> <doc>.tex
grep -n -A3 '^!' <outdir>/<doc>.log | head
```

A common cause in didactic/memoir educational documents (which build both
beamer slides and a memoir article from one source) is a citation/footnote
inside a **slide-only `\begin{frame}<presentation>` frame** while memoir is in
`\footnotesinmargin` mode: `\begin{frame}<presentation>` suppresses the frame's
*output* in the article but still *executes* the body, so the citation emits an
orphaned margin float that is lost. Note: citations inside *ordinary* frames are
fine — don't assume "footnote in any frame" is the problem. Preferred fix: wrap
the whole slide-only frame in `\mode<presentation>{\begin{frame}...\end{frame}}`
(a true mode gate; plain `\autocite` inside is then fine). Alternatively filter
each citation with `\only<presentation>{\autocite{...}}` (inline; not inline
`\mode<presentation>{...}`). See the **didactic-notes** skill's
`references/footnotes-and-citations.md` for the full diagnosis. It is not a footnote-text problem, not a PythonTeX problem,
and not page-count related — don't chase those.

### Caveat: the `\mode<presentation>{...}` wrap breaks `[fragile]` frames

The preferred fix above conflicts with `[fragile]`. A `fragile` frame writes its
body verbatim to an external `.vrb` file and scans for `\end{frame}`; wrapping it
in `\mode<presentation>{\begin{frame}[fragile]...\end{frame}%\n}` leaves the
group's closing `}` *outside* that scan, so the **slides** build dies with:

```
! Extra }, or forgotten \endgroup.
\endframe ->\egroup ...
```

So for a slide-only frame you cannot have both `\mode<presentation>{...}` and
`[fragile]`. Resolve by checking whether `fragile` is actually needed:

- **`fragile` is not needed** (the frame has no `verbatim`/`minted`/`listings`;
  inline math `\(...\)`, `\alert<>`, `\pause`, `block`/`itemize` are all fine):
  drop `[fragile]` and use `\mode<presentation>{\begin{frame}...\end{frame}}`.
  This satisfies both outputs — the article never executes the body, the slides
  wrap cleanly. This is the common case.
- **`fragile` is genuinely needed** (verbatim-like content inside): keep
  `\begin{frame}<presentation>[fragile]` (note: spec `<presentation>` goes
  *before* the `[fragile]` option) and guard every citation/footnote in the body
  with `\only<presentation>{\autocite{...}}` so it does not execute in the
  article and orphan a margin float.

Other classic triggers of "Float(s) lost": a `figure`/`table` nested inside
another box (minipage, `\parbox`, another float), or a margin float emitted from
any restricted-mode context. Diagnose by minimal reproduction (does the
construct alone lose a float?) and by bisecting the document file-by-file.
