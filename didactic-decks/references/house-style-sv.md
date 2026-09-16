# Swedish house style for decks

**Load when the deck is written in Swedish.** These are the author's
review rules, in the author's own words where the wording is load-bearing.
They hold for prose, `\ltnote`s, abstracts and appendices alike. The
project's own names, deck titles and example data stay in the project's
`CLAUDE.md`; this file carries the rules, not the course's data.

## The rules

**Swedish term first, English once.** Swedish throughout; the Swedish term
first, the English term once in parentheses at first use, then the Swedish
word: "spårutskrift (\foreignlanguage{english}{traceback})". With `acro`,
the Swedish word must be the `long` form and the English expansion rides
along inside it, because acro prints "long (short)" on first use. A
loanword with a Swedish equivalent is the Swedish word in the student
text: "sägen", not "folklore" (the author struck it, 2026-09-15).

**Never tie the text to weeks, lecture order or course events.** Not
"förra veckan", "vecka 38", "föreläsningens första halva", "på
laborationen", "veckans modul". Refer to topics, deck titles and
activities: "tidigare", "föreläsningen \emph{Funktioner}", "när du
programmerar". An `\ltnote` may still mention the lab; the student's text
may not.

**Address the student as "du".** Second person singular throughout the
student text — prose, exercises, learning objectives, appendices: "när du
programmerar", "din kod", "ditt program", "dina svar". Never "ni"/"er"
for the reader (the author, 2026-09-07: "use du"); a real plural — two
students in a pair — keeps "ni". Program strings and quoted sources keep
their own wording.

**Förkunskaper say "tagit del av".** "Studenten bör ha tagit del av
föreläsningen \emph{X}", never "ha sett".

**Exekverar, utför, köra.** "Ett program utför en uppgift;
processorn/datorn/tolken exekverar programmet." Whoever runs code
*exekverar* it (noun *exekvering*); a program or a person *utför* a task.
"Köra"/"körs" stays as the everyday word.

**Name the action, not the position.** "Något måste översätta det vi
skriver till det processorn exekverar", not "något måste stå emellan". A
title that names a literal reproduces it exactly ("Hello, World!"). And
never refer to physical position at all — "på nästa bild", "ovan" — use
`\cref`.

**No ambiguous sentence-initial pronouns in the appendices.** "Sökningen
gjordes ämnesdrivet ...", not "Den gjordes ...".

**The appendix pointer.** It reads "det vetenskapliga underlaget finns i
\cref{app:...}" and stands beside the claim it backs, **once**: in the
same sentence, as a parenthesis or a following clause. Never as a trailing
sentence a sentence or more away, and never twice for one appendix in a
paragraph. The pointer says what the appendix answers — "både var
principen kommer ifrån och om den håller, med sina förbehåll" — and the
claim is stated at the strength the appendix supports. For a claim backed
in another deck, `\cref` cannot cross documents, so name the deck: "det
vetenskapliga underlaget finns i föreläsningen \emph{Funktioner},
bilaga B". When the paragraph carries several principles, the pointer
names its own: "det vetenskapliga underlaget för DRY --- och de förbehåll
som hör till --- finns i …" (author, 2026-09-16, "för DRY").

**A measured claim is cited where it stands.** "erfarna utvecklare är
mätbart oense om den\autocite{Alkharabsheh2021Analysing,Hall2014Some}"
carries its sources in the sentence even though the bilaga pointer follows
a sentence later (author, 2026-09-15: "Ref!" beside the highlighted
clause). Never `\autocite` inside a float.

**The chapter precis.** Every appendix chapter opens with the verbatim
sentence

```latex
\chapterprecis{Författaren har ännu inte granskat resultaten i den här
  bilagan i sin helhet.}
```

*Project-overridable*: it states who has reviewed what, so a project with
a different review practice writes its own sentence — but writes the same
sentence in every chapter.

## Wording set elsewhere in the build

- **Block titles.** beamer's `translator` package ships no Swedish
  dictionary, so `slides.tex` must carry the `\deftranslation[to=Swedish]`
  block before `\usetheme`, or the blocks come out in English. See
  `deck-anatomy.md`.
- **cleveref names.** `\usepackage[swedish]{cleveref}` (cleveref reads its
  own package options, not babel's), no `[capitalize]` — Swedish
  typography wants lowercase mid-sentence references, and `\Cref` for a
  sentence-initial one. Then override `appendix` → "bilaga", `enumi` →
  "rad", `footnote` → "fotnot" in an `\AtBeginDocument` hook.
- **Section headings in the appendices**: Metod, Resultat, Diskussion och
  begränsningar, Slutsats, Fortsatt arbete, Träffar som rör påståendet.

## Example data: the pattern

The rule is a pattern; the names themselves belong to the project.

- **Never the author's own name** in example data.
- Pick a fixed cast and use it in a fixed order, so the same person
  reappears across decks rather than a new name each time.
- Hide a cultural fact in example data where it costs nothing — a year, a
  place (the author swapped an arbitrary town for the institution's own
  street, 2026-09-15: "Why Kungsängen?"). The fact stays **out** of the
  student's text and is recorded, with its source, in an `\ltnote`.
- Choose verbs that name the mental action: "värda att fundera på", not
  "värda att stanna vid".
- Every source has a real reference. No nicknames for sources
  ("missuppfattningsartikeln") in appendices or notes; the author's own
  manuscript gets an `@unpublished` entry with a provenance block.
