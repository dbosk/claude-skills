# didactic footnotes & citations in dual beamer/article documents

This covers footnotes and citations when a single source builds **both** beamer
slides and a memoir article (the `beamerarticle` + memoir + didactic setup), and
the one real pitfall that wastes hours if you don't know it.

## What didactic does to footnotes

didactic auto-detects the document class:

- **beamer** (slides): footnotes render at the **bottom of the slide** (beamer's
  native handling). It never uses margin footnotes.
- **memoir** (article/book): didactic's memoir branch calls `\footnotesinmargin`
  — footnotes become **margin floats** (the Tufte look, alongside `\ltnote`
  margin notes and side-captions).

This split is automatic and is usually what you want: beamer never puts
footnotes in the margin, the article does.

## Citations inside *ordinary* frames are fine

A footnote, `\footnote`, `\autocite`, or csquotes `\textcquote`/`\blockcquote`
inside an **ordinary** `\begin{frame}` (one shown in both builds) works
correctly: it is a margin footnote in the article and a slide footnote in
beamer. Block titles, description items, and frame bodies are all fine. Do **not**
mode-split these or route them to the foot — they just work.

## The pitfall: a citation inside a `<presentation>`-only frame → "Float(s) lost"

A `\begin{frame}<presentation>` is a **slide-only** frame. In the article build,
`beamerarticle` suppresses the frame's visible content — but a citation/footnote
inside it **still executes** and emits a margin float (`\marginpar`) that has no
containing page context, so it is orphaned and lost. The result is a fatal,
location-less error at the end of the article build:

```
! LaTeX Error: Float(s) lost.
l.NNN \end{document}
```

The slides build is unaffected. The error names nothing and only appears after
all pages ship, so it is easy to misattribute to PythonTeX, page count, margin
overflow, or "footnotes in frames in general" — **none of which are the cause**.
Verify by minimal reproduction: an `\autocite` in an *ordinary* frame builds; the
same in a `\begin{frame}<presentation>` frame loses a float.

### Why `\begin{frame}<presentation>` leaks, and the fix

`\begin{frame}<presentation>` is **not a true exclusion** in article mode: it
drops the frame's typeset *output* but still *executes* the body, so an
`\autocite`/footnote inside runs and emits an orphaned margin float. `\mode<presentation>{...}`,
by contrast, is a genuine mode gate — the wrapped tokens are not executed at all
in the article.

**Preferred fix — make the whole frame a true mode gate.** Wrap the entire
slide-only frame in `\mode<presentation>{...}` instead of using
`\begin{frame}<presentation>`; then plain `\autocite` inside is fine (nothing
leaks):

```latex
\mode<presentation>{%
\begin{frame}
  \begin{block}{Variation theory~\autocite{VariationTheory}}
    ...
  \end{block}
\end{frame}%
}
```

`\mode`'s spurious-paragraph caveat only applies to *inline* use; wrapping a
whole block-level frame is exactly what `\mode<presentation>{...}` is for.

**Alternative — keep `\begin{frame}<presentation>` and filter each citation**
with `\only<presentation>{...}` (inline, overlay/mode-aware — and *not*
`\mode<presentation>{...}` inline, which inserts spurious paragraph breaks):

```latex
\begin{frame}<presentation>
  \begin{block}{Variation theory\only<presentation>{~\autocite{VariationTheory}}}
    ...
  \end{block}
\end{frame}
```

Prefer the whole-frame `\mode<presentation>` wrap: it fixes the root cause once
per frame rather than per citation.

### Do NOT "fix" it with a frame foot-hook

It is tempting to force footnotes to the foot inside frames:

```latex
\AtBeginEnvironment{frame}{\footnotesatfoot}   % AVOID
\AtEndEnvironment{frame}{\footnotesinmargin}
```

This compiles, but it is unnecessary (ordinary in-frame footnotes already work as
margin floats) and it drops the *article's* in-frame footnotes — the ones you
want in the margin — to the foot, since the frame material is shared. Filter only
the `<presentation>`-only citations with `\only<presentation>` instead.

## Citations: mode-adaptive commands and verbose margin references

For a shared beamer/article source, use citation commands that render
**differently per mode** rather than hard-coding one form. `\autocite` is the key
one: with didactic's memoir branch (`autocite=footnote`, `\SetCiteCommand{\autocite}`)
it is a footnote citation — hence a margin footnote in the article — and a
slide-appropriate citation in beamer. Avoid `\footcite` (hard-codes a footnote
everywhere).

For **verbose references in the margin** (full bibliographic data as a margin
footnote, à la the literate-programming book — full on first use, short on
repeats), configure biblatex with the verbose style:

```latex
\usepackage[
  natbib, backend=biber,
  style=verbose, citestyle=verbose,
  singletitle=false, maxbibnames=99,
]{biblatex}
```

Then drive citations with `\autocite`. Caveats:

- Under `verbose`, the *inline* forms print the full reference inline, so
  `\parencite` becomes a long inline citation — **convert parenthetical
  references to `\autocite`** to move them to the margin.
- **Keep `\textcite`** for sentence-integrated citations ("According to
  \textcite{X}, …"); don't convert those to `\autocite` (it breaks the
  sentence). `\textcite` stays textual in the running text.

## Loading didactic (recap)

Load didactic **last** (after `biblatex`, `csquotes`, `cleveref` — it adapts them
only if already loaded) with margin options as needed:

```latex
\usepackage[marginparmargin=right]{didactic}   % or =outer for a book
```

It requires `minted` and `pythontex` (so `-shell-escape`), and re-`\RequirePackage`s
`amsthm`, `thmtools`, `xparse`, `unique`, etc. — load those earlier if you need
specific options on them. didactic's memoir branch also sets `autocite=footnote`,
`\SetCiteCommand{\autocite}`, and `isbn/doi/url=false`.
