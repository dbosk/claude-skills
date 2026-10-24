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
may not. Naming an earlier deck by its title in natural first-person
plural is allowed and preferred: "som vi pratade om i föreläsningen
\emph{Funktioner}", "vi mötte den i föreläsningen \emph{Algoritmiskt
tänkande}" (author, 2026-09-20). Do not contort the sentence to avoid
"vi": "som föreläsningen \emph{Funktioner} namnger / kallade /
kontrasterade / tanglar" reads as contrived and is the wrong fix. The
title points at a document the reader can open in any week; "förra
veckan" does not, and that is the whole distinction.

**Do not present as new what an earlier deck already taught.** Build on
it and point back by title, cutting a repeat rather than re-explaining it
or re-running a near-verbatim exercise (author, 2026-09-29, beside
"Hittills har våra program gjort varje sak en gång": "Not entirely true,
we've done 'while True' for inputs, until the user gets it right."; asked
about an exercise that nearly repeated an earlier deck's: "build on the
earlier deck, cut repeats").

**Address the student as "du".** Second person singular throughout the
student text — prose, exercises, learning objectives, appendices: "när du
programmerar", "din kod", "ditt program", "dina svar". Never "ni"/"er"
for the reader (the author, 2026-09-07: "use du"); a real plural — two
students in a pair — keeps "ni". Program strings and quoted sources keep
their own wording.

**Förkunskaper say "tagit del av".** "Studenten bör ha tagit del av
föreläsningen \emph{X}", never "ha sett".

**"Vi" does what we do.** When the text says what happens in the
material, the subject is "vi", not the document: "Vi börjar i det
enklaste", not "Den börjar i det enklaste" (author, 2026-09-23, "Vi"
written over "Den"). And a part is not its whole: "Övningen består av
sju uppgifter", not "är sju uppgifter".

**"Och till sist", not "och sist"**, at the end of an enumeration of
answers or steps (author, 2026-09-23).

**A heading names what the section builds.** "Vårt sängväljarprogram",
not "Vårt program" (author, 2026-09-23).

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
\cref{app:...}" and is a **footnote anchored at the claim** it backs,
**once** (author, 2026-09-20: "Make it a rule to put those statements in
a footnote"; before that date it stood in the body as a parenthesis or
clause, and older decks are converted when next revised). The claim stays
in the running text; the footnote never becomes a body sentence, never a
trailing sentence further away, and never appears twice for one appendix
in a paragraph. The pointer says what the appendix answers — "både var
principen kommer ifrån och om den håller, med sina förbehåll" — and the
claim is stated at the strength the appendix supports. For a claim backed
in another deck, `\cref` cannot cross documents, so name the deck: "det
vetenskapliga underlaget finns i föreläsningen \emph{Funktioner},
bilaga B". When the paragraph carries several principles, the pointer
names its own: "det vetenskapliga underlaget för DRY --- och de förbehåll
som hör till --- finns i …" (author, 2026-09-16, "för DRY").

**State a backed claim; do not defend it.** "ett av de vanligaste
misstagen bland nybörjare, och det är inte något vi hittat på" — the
author struck the second clause (2026-09-22). The citation and the
appendix footnote carry the backing; a sentence assuring the reader that
the claim is real reads as defensive and adds nothing.

**No count in front of a list unless the count is the point.** "De
aritmetiska operatorerna är fem:" before a list of seven (author struck
*fem*, 2026-09-22). A count invites a check and goes stale when the list
changes; write "De aritmetiska operatorerna är:".

**The lead-in to a side-by-side example does not repeat its column
labels.** Before a `\codebycode` (or any two columns of code), "Räkningen
i de två programmen, sida vid sida:" suffices; not "… i `letters.py` till
vänster och i `counter.py` till höger". The column labels already name
the files, and file names are long unbreakable words: the repetition gave
six lines 14–35pt into the margin in one sweep (author, 2026-10-24).

**Numbers: ett till tolv i ord, 13 och uppåt i siffror** (Språkrådet's
rule; author, 2026-09-29, beside "åttioen": "Skrivregler: ett till tolv,
13 till oändligheten."). A round number (femtio, hundra, tusen) may stay
in words past twelve — the author's choice when asked. A literal value a
program reads or prints keeps its code markup regardless of magnitude:
`\texttt{13}`, not "13" or "tretton" set as running text.

**"En range", not "ett range".** Common gender (author, 2026-09-29).

**A qualification lives in the pointer footnote**: the rule is in
`backing-claims/references/appendix-guide.md`; in Swedish it reads
"… säger.⁷,⁸" with footnote 8 holding "guiden som helhet har det inte …"
and the pointer.

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
- **Real places, real facts.** Example data taken from the real world
  must match it, not only borrow its names: a route across campus follows
  the real walk (author, 2026-09-23, beside a hand-drawn map: "This is what
  it looks like in reality. Adapt to it."). Say in an `\ltnote` where the
  facts come from and what is approximated.
- Pick a fixed cast and use it in a fixed order, so the same person
  reappears across decks rather than a new name each time.
- Hide a cultural fact in example data where it costs nothing — a year, a
  place (the author swapped an arbitrary town for the institution's own
  street, 2026-09-15: "Why Kungsängen?"). The fact stays **out** of the
  student's text and is recorded, with its source, in an `\ltnote`.
- Choose verbs that name the mental action: "värda att fundera på", not
  "värda att stanna vid" (author, 2026-09-20: "värt att reflektera över" is the other accepted replacement).
- Every source has a real reference. No nicknames for sources
  ("missuppfattningsartikeln") in appendices or notes; the author's own
  manuscript gets an `@unpublished` entry with a provenance block.

**Boilerplate is not repeated deck after deck.** A student-facing
paragraph that restates a course convention (e.g. "Alla program här är
skrivna i den form du känner från föreläsningen *Funktioner* …") appears
once, where the convention is introduced or first applied; later decks
refer to it in at most one short clause, if at all (author, 2026-09-28:
"Trim everywhere, not just in the book, if it's repetitive"). The same
holds for repeated `\ltnote`s stating a deck-wide rule.
