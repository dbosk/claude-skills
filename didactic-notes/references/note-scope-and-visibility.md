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

The notes-off reading is not hypothetical: a student edition is made
exactly that way, by `\ltnoteoff` before the body (e.g. a book bound from
decks, `didactic-decks/references/book-binding.md`), so a note doing the
prose's work leaves a gap in a text students actually read.

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

Margin notes are floats. With didactic 2.6 and marginfix 1.5
(`notepriority=split`, the default) a note longer than the space left in
the margin splits and continues on the next page, giving way to citation
footnotes; it no longer queues whole beside a later section.

Never fix a crowded margin with a page break (`\clearpage`,
`\needspace`, `\pagebreak`, …): the didactic-decks rule "No manual page
breaks" (author, 2026-10-22: "Remove manual page breaks everywhere.").
Instead:

- Shorten notes that restate the prose. A note repeating the body text costs
  margin twice and buys nothing.
- Anchor a note just before the passage it discusses; split a long one and
  anchor the second half further on.
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
