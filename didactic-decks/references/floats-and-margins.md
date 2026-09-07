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

## The ltnote queue

`\ltnote`s longer than the margin queue forward and print beside the next
section, or beside the appendix. `\clearpage` does **not** flush the queue.

What works:

- Put `\mode<article>{\clearpage}` before the section the notes belong to.
- Put one before the **last** frame of a section whose notes overflow, so
  the queue drains on a page still inside the chapter.
- Shorten notes that merely restate the prose.
- Anchor a note where its decision is made, not at the end of the passage.
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
