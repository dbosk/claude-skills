# didactic footnotes & citations in dual beamer/article documents

This covers how footnotes and citations behave when a single source builds
**both** beamer slides and a memoir article (the `beamerarticle` + memoir +
didactic setup), and the fatal pitfall that wastes hours if you don't know it.

## What didactic does to footnotes

didactic auto-detects the document class:

- **beamer** (slides): footnotes render at the **bottom of the slide** (beamer's
  native handling). It never uses margin footnotes.
- **memoir** (article/book): didactic's memoir branch calls
  `\footnotesinmargin` — footnotes become **margin floats** (the Tufte look,
  alongside `\ltnote` margin notes and side-captions).

This split is automatic and is usually what you want: *beamer never puts
footnotes in the margin, the article does.*

## The pitfall: a footnote inside a frame → fatal "Float(s) lost"

A margin footnote is emitted as a `\marginpar` (a float). **A float cannot be
emitted from inside a box** — and a beamer `frame` (and beamer `block`) is a box
in the memoir/`beamerarticle` build too. So a footnote, `\footnote`, `\footcite`
or `\autocite` placed **inside a `frame`** in the article build is deferred and
ultimately lost, producing a fatal error at `\end{document}`:

```
! LaTeX Error: Float(s) lost.
l.NNN \end{document}
```

The error names no location and appears only at the very end after all pages
ship, so it is easy to misattribute. It is **not** caused by a specific
footnote's text, nor by PythonTeX, nor by the page count — it is any
margin-footnote-producing command inside a frame. The slides build is fine
(beamer footnotes aren't margin floats); only the **article** build dies.

### The fix: put footnotes and citations in prose, not inside frames

This is the idiomatic pattern (see the literate-programming lecture notes). In a
`\mode`-based beamer/article source, the frames are slide content and the prose
between them is article material. Put footnotes and `\autocite` in that prose:
they become margin footnotes in the article, and the slides carry their own
citations/footnotes via the frame content. No footnote inside a frame ⇒ no lost
floats, and the article keeps margin footnotes everywhere.

When a frame *summarises* something the prose already discusses (e.g. a
"Misconception" block whose source is cited in the surrounding prose), let the
**prose** carry the `\autocite` and drop the in-frame citation — don't duplicate
it inside the frame.

### Do NOT route in-frame footnotes to the foot via a frame hook

It is tempting to "fix" the lost float by forcing footnotes to the foot inside
frames:

```latex
\AtBeginEnvironment{frame}{\footnotesatfoot}   % AVOID
\AtEndEnvironment{frame}{\footnotesinmargin}
```

This compiles, but because the frame material is **shared** between the slides
and the article, it forces the *article's* in-frame footnotes to the page foot
too — so the article ends up with a mix of margin and foot footnotes instead of
the consistent margin (Tufte) style you wanted. Restructure to keep footnotes in
prose instead.

## Citations: prefer mode-adaptive commands; verbose references in the margin

**The guiding principle for a shared beamer/article source: use citation and
footnote commands that *do different things in beamer vs. article mode*, rather
than hard-coding one rendering.** `\autocite` is the key one — it follows the
document's `autocite` setting, so it is a footnote citation in the memoir
article (hence a *margin* footnote there) and a slide-appropriate citation in
beamer. `\footcite` hard-codes a footnote everywhere, removing that adaptivity
and triggering the in-frame "Float(s) lost" above; replace it with `\autocite`.

To get **verbose references in the margin** (full bibliographic data as a margin
footnote in the article, à la the literate-programming book), configure
biblatex with the verbose style and let `\autocite` produce the footnote:

```latex
\usepackage[
  natbib,
  backend=biber,
  style=verbose,
  citestyle=verbose,
  singletitle=false,
  maxbibnames=99,
]{biblatex}
```

With `citestyle=verbose`, `\autocite` is a footnote citation (full reference,
short form on repeats) → a margin footnote in the memoir article, a slide
footnote in beamer. **Caveat:** under `verbose`, the *inline* forms render the
full citation inline too — so `\parencite` becomes a long inline reference
(usually undesirable; convert parenthetical references to `\autocite` to move
them to the margin), while `\textcite` stays a sentence-integrated textual
citation (keep it only where the sentence names the author). Don't blindly
convert `\textcite` to `\autocite` — that breaks "According to X, …" sentences.

For a citation that should appear **on the slide but in the article's prose
margin** (not inside the article's frame), use mode splitting: put the slide
citation inside the frame under `\mode<presentation>{\autocite{...}}`, and let
the surrounding article prose carry its own `\autocite{...}`. This keeps the
slide self-citing while the article gets a clean margin footnote outside the
frame box.

## Toggling footnote placement: do NOT wrap the switch in a group

`\footnotesatfoot` and `\footnotesinmargin` are memoir **declarations** (state
switches). Wrapping one in a group scopes (and instantly reverts) it, so it does
nothing:

```latex
\mode<article>{\footnotesatfoot}   % WRONG: \mode{...} groups it -> no-op
```

In a file shared between the beamer and memoir builds, guard with `\ifdefined`
instead (the commands exist only under memoir), which does not introduce a
group:

```latex
\ifdefined\footnotesatfoot\footnotesatfoot\fi      % takes effect; skipped in beamer
... frame ...
\ifdefined\footnotesinmargin\footnotesinmargin\fi
```

A bare `\footnotesatfoot` in a memoir-only file (e.g. the article root, or
around `\maketitle` to keep a `\thanks` footnote off the title-page margin)
needs no guard.

## Loading didactic (recap)

Load didactic **last** (after `biblatex`, `csquotes`, `cleveref` — it adapts
them only if already loaded) and pass margin options as needed:

```latex
\usepackage[marginparmargin=right]{didactic}   % or =outer for a book
```

It requires `minted` and `pythontex` (so `-shell-escape`), and re-`\RequirePackage`s
`amsthm`, `thmtools`, `xparse`, `unique`, etc. — load those earlier if you need
specific options on them.
