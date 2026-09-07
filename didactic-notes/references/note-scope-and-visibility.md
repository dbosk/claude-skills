# Note Scope and Visibility

What belongs in an `\ltnote` rather than in the student's prose, where the
note goes on the page, and what the margin does when notes and citations
compete for it.

## Table of Contents

1. [What exists only in a note does not exist for the student](#what-exists-only-in-an-ltnote-does-not-exist-for-the-student)
2. [Anchor the note where the decision is made](#anchor-the-note-where-the-decision-is-made)
3. [The margin queue](#the-margin-queue)
4. [Do not pre-announce a summary](#do-not-pre-announce-a-summary)

---

## What exists only in an `\ltnote` does not exist for the student

`\ltnote` is instructor-facing. Students never see it, so anything they are
meant to *notice* must be in the prose. Two failure modes, both common when
the notes are written before the narrative:

- **A reason the student should hold.** "Vi visar assembler först för att
  göra översättningssteget synligt" belongs in the body, as a sentence
  before the example. In a note it is a design record only.
- **A development the student should follow.** If the sequence of examples
  builds an argument — each language further from the machine, each version
  handling one more failure — say so in the running text. A note that traces
  the argument leaves the student with an unexplained list.

The test: read the material with notes off (`\ltnoteoff`). If a reader
cannot tell why an example is there, or what changed since the previous one,
the note is doing the prose's work. Move the *what* and the *why for the
student* into the body; keep the *why for the teacher* — which learning
objective, which critical aspect, which misconception, which variation
pattern — in the note.

---

## Anchor the note where the decision is made

Attach a note to the element it explains, not to the end of the passage. A
note about why an exercise precedes the definition sits at the exercise; a
note about the choice of example data sits at the example that uses it.
Notes collected at the end of a section explain decisions the reader walked
past pages ago, and they arrive as a block the margin cannot hold.

Never place an `\ltnote` within a few lines of a `sidecaption` figure: both
claim the same margin, and memoir `\rlap`s the side caption straight over
the note.

---

## The margin queue

Margin notes are floats. A note longer than the space left in the margin
does not shrink — it queues, and prints beside the *next* section or, at
worst, beside the appendix. `\clearpage` does not flush that queue.

Design around it:

- Put `\mode<article>{\clearpage}` before the section the notes belong to,
  and before the **last frame** of a section whose notes overflow, so the
  queue drains on a page still inside the chapter.
- Shorten notes that restate the prose. A note repeating the body text costs
  margin twice and buys nothing.
- A margin at capacity also pushes **citation footnotes** to the next page.
  A footnote marker on one page with its note on the next is a defect, not a
  cosmetic detail: check every page where notes are dense, comparing the
  superscript numbers in the text against the note numbers in the margin.

---

## Do not pre-announce a `summary`

A one-line paragraph saying what the following `summary` block is about to
say ("Låt oss sammanfatta vad vi sett om undantag.") spends the reader's
attention twice and removes the block's function as a closer. Let the block
open the summary itself. If the transition genuinely needs prose, it must
add something the block does not contain.
