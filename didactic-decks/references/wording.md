# Wording rules for decks in every language

**Load together with the deck's house style** (`house-style-sv.md`,
`house-style-en.md`). These rules hold whatever language a deck is written
in, so they stand here once. A rule that needs its own wording per language
stays in the house style, even when the two say much the same thing. They
hold for prose, `\ltnote`s, abstracts and appendices alike.

The Swedish examples come from the author's reviews and are kept as struck;
the English ones are their counterparts. Follow the example in the deck's
language.

Contents: [Building on earlier decks](#building-on-earlier-decks) ·
[Headings and naming](#headings-and-naming) ·
[Claims and lists](#claims-and-lists) ·
[Example data: the pattern](#example-data-the-pattern) ·
[Sources](#sources)

## Building on earlier decks

**Do not present as new what an earlier deck already taught.** Build on
it and point back by title, cutting a repeat rather than re-explaining it
or re-running a near-verbatim exercise (author, 2026-09-29, beside
"Hittills har våra program gjort varje sak en gång": "Not entirely true,
we've done 'while True' for inputs, until the user gets it right."; asked
about an exercise that nearly repeated an earlier deck's: "build on the
earlier deck, cut repeats").

**Boilerplate is not repeated deck after deck.** A student-facing
paragraph that restates a course convention (e.g. "Alla program här är
skrivna i den form du känner från föreläsningen *Funktioner* …") appears
once, where the convention is introduced or first applied; later decks
refer to it in at most one short clause, if at all (author, 2026-09-28:
"Trim everywhere, not just in the book, if it's repetitive"). The same
holds for repeated `\ltnote`s stating a deck-wide rule.

## Headings and naming

**A heading names what the section builds.** "Vårt sängväljarprogram", not
"Vårt program"; "Our backup script", not "Our script" (author, 2026-09-23).

**Name the action, not the position.** "Något måste översätta det vi
skriver till det processorn exekverar", not "något måste stå emellan";
"Something has to translate what we write into what the processor
executes", not "something has to stand in between". A title that names a
literal reproduces it exactly ("Hello, World!"). And never refer to
physical position at all ("på nästa bild", "ovan"; "on the next slide",
"above", "below"): use `\cref`.

**No ambiguous sentence-initial pronouns in the appendices.** "Sökningen
gjordes ämnesdrivet ...", not "Den gjordes ..."; "The search was
topic-driven …", not "It was …".

**Verbs name the mental action.** "värda att fundera på", not "värda att
stanna vid" (author, 2026-09-20: "värt att reflektera över" is the other
accepted replacement); "worth thinking about", not "worth stopping at".

## Claims and lists

**State a backed claim; do not defend it.** "ett av de vanligaste
misstagen bland nybörjare, och det är inte något vi hittat på": the
author struck the second clause (2026-09-22); in English, no "and we did
not make that up" after "one of the most common novice mistakes". The
citation and the
appendix footnote carry the backing; a sentence assuring the reader that
the claim is real reads as defensive and adds nothing.

**No count in front of a list unless the count is the point.** "De
aritmetiska operatorerna är fem:" before a list of seven (author struck
*fem*, 2026-09-22). A count invites a check and goes stale when the list
changes; write "De aritmetiska operatorerna är:", "The arithmetic
operators are:".

**The lead-in to a side-by-side example does not repeat its column
labels.** Before a `\codebycode` (or any two columns of code), "Räkningen
i de två programmen, sida vid sida:" or "The counting in the two programs,
side by side:" suffices; not "… i `letters.py` till vänster och i
`counter.py` till höger". The column labels already name the files, and
file names are long unbreakable words: the repetition gave six lines
14–35pt into the margin in one sweep (author, 2026-10-24).

## Example data: the pattern

The rule is a pattern; the names themselves belong to the project.

- **Never the author's own name** in example data.
- **Real places, real facts.** Example data taken from the real world
  must match it, not only borrow its names: a route across campus follows
  the real walk (author, 2026-09-23, beside a hand-drawn map: "This is what
  it looks like in reality. Adapt to it."). Say in an `\ltnote` where the
  facts come from and what is approximated.
- Pick a fixed cast and use it in a fixed order, so the same person
  reappears across decks rather than a new name each time.
- Hide a cultural fact in example data where it costs nothing: a year, a
  place (the author swapped an arbitrary town for the institution's own
  street, 2026-09-15: "Why Kungsängen?"). The fact stays **out** of the
  student's text and is recorded, with its source, in an `\ltnote`.

## Sources

**Every source has a real reference.** No nicknames for sources
("missuppfattningsartikeln", "the misconceptions paper") in appendices or
notes; the author's own manuscript gets an `@unpublished` entry with a
provenance block.
