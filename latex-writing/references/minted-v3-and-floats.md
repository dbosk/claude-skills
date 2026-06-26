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

The most common cause in didactic/memoir educational documents is a **footnote
(or `\footcite`/`\autocite`) inside a beamer `frame`** while memoir is in
`\footnotesinmargin` mode: a margin footnote is a float and cannot be emitted
from inside the frame box, so it is lost. See the **didactic-notes** skill's
`references/footnotes-and-citations.md` for the full diagnosis and fixes (keep
footnotes in prose, or `\AtBeginEnvironment{frame}{\footnotesatfoot}`). It is
not a footnote-text problem, not a PythonTeX problem, and not page-count
related — don't chase those.

Other classic triggers of "Float(s) lost": a `figure`/`table` nested inside
another box (minipage, `\parbox`, another float), or a margin float emitted from
any restricted-mode context.
