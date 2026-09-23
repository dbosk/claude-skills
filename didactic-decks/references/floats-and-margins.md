# Floats, captions and the margin

The notes are a memoir document with a wide margin that didactic fills
with three things at once: instructor notes (`\ltnote`), citation
footnotes (every `\autocite` under the verbose style) and side captions.
They compete for the same space, and the failures are silent.

Contents: [Placement](#placement) · [Captions](#captions) ·
[The side-caption decision](#the-side-caption-decision) ·
[The ltnote queue](#the-ltnote-queue) ·
[The float pool](#the-float-pool) · [Citations in floats](#citations-in-floats)

## Placement

Tables and figures sit close to where they are relevant and referenced:
`[htbp]` (or `[!htb]`) **right after the paragraph that references them**.
Never `[p]` — a float page moves the figure away from its discussion.

Every figure is referenced from the student-facing prose, not only from an
`\ltnote`, and the reference names the figure with `\cref`, never by
position ("på nästa bild", "ovan"). Check on the rendered pages that the
float landed on or facing the page of its reference.

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
  \centering
  \begin{sidecaption}{The full caption text.}[fig:label]
    \includegraphics[width=0.7\textwidth]{figs/x.png}
  \end{sidecaption}
\end{figure}
```

No compatibility macros: the environment is didactic's own.

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

## The ltnote queue

`\ltnote`s longer than the margin queue forward and print beside the next
section, or beside the appendix. `\clearpage` does **not** flush the queue.

What works, in this order of preference:

1. Shorten notes that merely restate the prose; state a deck-wide rule
   once, in one short note, instead of a paragraph in several.
2. Anchor a note where its decision is made, not at the end of the
   passage, so it starts printing earlier.
3. Split a long note and anchor the second half further on.
4. Move the citation that is being pushed to the next page a few lines
   earlier, or `\needspace{N\baselineskip}` with the smallest N that
   works.
5. Only then a forced break, `\mode<article>{\clearpage}` before the
   section the notes belong to (or before the **last** frame of a section
   whose notes overflow).

**A forced break must not leave a page mostly blank** (author,
2026-09-22, beside two such pages: "Why new page here?"). A reader sees an
empty half page as a defect, not as layout; `\clearpage` or `\needspace`
is acceptable only where the page it ends is already about two thirds
full. When no option above satisfies both this and the margin rule below,
report the conflict to the author instead of choosing silently. The same
holds for `\needspace` used to keep examples together: keep them together
only when the gap it leaves is small.

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
