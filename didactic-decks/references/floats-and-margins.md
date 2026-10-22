# Floats, captions and the margin

The notes are a memoir document with a wide margin that didactic fills
with three things at once: instructor notes (`\ltnote`), citation
footnotes (every `\autocite` under the verbose style) and side captions.
They compete for the same space, and the failures are silent.

Contents: [Placement](#placement) · [Captions](#captions) ·
[The side-caption decision](#the-side-caption-decision) ·
[No manual page breaks](#no-manual-page-breaks) ·
[The float pool](#the-float-pool) · [Citations in floats](#citations-in-floats)

## Placement

Tables and figures sit close to where they are relevant and referenced:
`[htbp]` (or `[!htb]`) **right after the paragraph that references them**.
Never `[p]` — a float page moves the figure away from its discussion.

Every figure is referenced from the student-facing prose, not only from an
`\ltnote`, and the reference names the figure with `\cref`, never by
position ("på nästa bild", "ovan"). Check on the rendered pages that the
float landed on or facing the page of its reference.

**A figure that depicts code sits beside that code** (author, 2026-10-19,
beside a flowchart of `withdraw` placed on the slide after the program:
"On previous slide"): on the slides, in the frame that holds the code; in
the notes, next to the code's display, as a `marginfigure` when it is
small and the margin there is free. The student checks the picture
against the lines it draws, and a slide or page between them turns that
into a look back. Define the picture once as a macro and use it in both
places, as with tables below.

**Never scale a figure that holds text** (author, 2026-10-21, beside a
margin flowchart shrunk with `\resizebox`: "Font is too small" and
"Always keep the font size in relation to text, so typeset it with the
document, never scale as part of an image"). A figure's text is set at
the size of the text around it: the margin's size in a `marginfigure`,
the frame's size on a slide. No `\resizebox`, `\scalebox`, `scale=` or
`width=` on a TikZ picture or any other picture that carries text. If it
does not fit at that size, tighten it (node distances, labels wrapped
over two lines) or move it (from the margin to the text column, or split
the frame). Photos and screenshots are images and may be sized by width.

## Captions

A caption explains sufficiently and stands on its own. In order:

1. what the table or figure shows;
2. the abbreviations (OA, WoS, IEEE, ...);
3. the row codes (S1, M1, ...);
4. what the markers mean (`--`, `†`, superscript letters).

A caption made shorter is not a better caption. When a side caption has to
become a normal caption, it keeps the same full text.

## The side-caption decision

Priority order: **placement first**, then the caption style.

Use didactic's `sidecaption` environment when *both* hold:

- the margin beside the float is free, and
- the rendered caption is **not taller than the float itself**.

```latex
\begin{figure}[htbp]
  \begin{sidecaption}{The full caption text.}[fig:label]
    \includegraphics[width=0.7\textwidth]{figs/x.png}
  \end{sidecaption}
\end{figure}
```

No compatibility macros: the environment is didactic's own.

The float's contents sit against the margin that holds the caption.
didactic ≥ 2.9 does this by default (`sidecapalign=caption`), so write no
`\centering` (it never centred the contents anyway, which memoir boxes at
full width) and no `\flushscap`. A narrow figure flush left with its
caption far off on the right means an older didactic or
`sidecapalign=off`; see the latex-writing skill, \enquote{Push the content
towards its sidecaption}.

Otherwise use a normal `\caption` with the same full text. A side caption
that towers over a short table goes below it instead. A `longtable` cannot
take a side caption at all and always keeps a full `\caption`.

`preamble.tex` must carry `\ifdefined\setsidecappos\setsidecappos{b}\fi`.
memoir places a side caption with `\rlap`, so it takes part in no
collision avoidance and silently overprints an `\ltnote` at the same
height; anchoring the caption at the bottom of the float moves it below the
notes, which anchor where they stand in the body text.

## Tables in the notes

A table in the notes is a numbered `table` float with a caption that
stands on its own (what the rows, columns and cells are), referenced from
the prose with `\cref`, never a bare `tabular` carried over from a frame
(author, 2026-09-23, beside three truth tables: "Should be a proper table
with caption"). Define the tabular once as a macro and use it both on the
slide and in the float. A margin table is an option only where the margin
beside the reference is free; otherwise the float goes in the text.

A truth table is laid out like a multiplication table: the operator in
the corner, the left operand down the rows, the right operand along the
header row, a rule under the header row and a vertical rule after the
header column; a one-operand table (`not`) has the same shape, its
operand in the header row and the result below (author, 2026-09-23: "We
want the lines, just as in a multiplication table", "Then it can be read
the same way as the others"). With booktabs, a vertical rule needs
`\aboverulesep=0pt`, `\belowrulesep=0pt` and a little `\arraystretch`,
or it breaks at every rule.

## No manual page breaks

A deck carries **no manual page break for layout**: no `\needspace`,
`\pagebreak`, `\newpage`, `\enlargethispage`, `\nopagebreak`,
`\goodbreak`, `\filbreak`, and no `\clearpage` (bare or in
`\mode<article>{…}`) in `contents.nw` (author, 2026-10-22: "It was
introduced to deal with margin notes. But now that's resolved properly so
we should never need to do those hacks. Remove manual page breaks
everywhere."). The breaks were workarounds for margin notes and citation
footnotes landing on the page after their marker. didactic 2.6 resolved
that with marginfix 1.5: margin notes are deferrable and
`notepriority=split` (the default) lets a citation footnote go first and
splits a long `\ltnote` across pages, with a continuation cue. Earlier
rounds also showed the cost of the hacks: forced breaks left mostly blank
pages (author, 2026-09-22 and 2026-09-29: "Why new page here?", "Why new
page?") and a `\needspace` left a gap on a notes page (2026-10-22).

Structural breaks in the document skeleton are not layout hacks and stay:
`notes.tex`'s `\clearpage` after the abstract, the chapter and appendix
breaks memoir makes, and the book's `\deck` macro (`book-binding.md`).

When a page looks poor without a break, fix the content, not the break:

1. Shorten notes that merely restate the prose; state a deck-wide rule
   once, in one short note, instead of a paragraph in several.
2. Anchor a note just before the passage it discusses (the
   didactic-notes rule, "Placement"), never after it, so it starts
   printing beside the passage.
3. Split a long note and anchor the second half further on.
4. Move a citation a few lines earlier, or move or reword the prose
   around it.

When none of these gives an acceptable page, report the page to the
author instead of adding a break.

- Never anchor a note within a few lines of a `sidecaption` figure.

A margin already at capacity also pushes citation footnotes to the next
page. That is a defect, not a cosmetic issue: check it with the
per-page method in `review-checklist.md`, or with
`scripts/check_margin_notes.py`.

## The float pool

LaTeX allocates `\marginpar` boxes from the same pool of eighteen boxes as
floats, and didactic makes a margin note of every footnote and every
`\autocite`. A citation-heavy chapter empties the pool and dies with "Too
many unprocessed floats" pages after the cause, in a place that has
nothing to do with it. `preamble.tex` therefore carries:

```latex
\extrafloats{200}
```

## Citations in floats

Never `\textcite` or `\autocite` inside a `table` or `figure`: the citation
becomes a `\marginpar`, the float is lost ("Float(s) lost" in the log) and
its `\label` goes with it, so every `\cref` to it prints `??`. Use
`\parencite` inside the float, and put the footnoted first mention in the
prose outside it.
