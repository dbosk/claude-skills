# English house style for decks

**Load when the deck is written in English, or for the English blocks of
a bilingual deck.** It is the counterpart of `house-style-sv.md`: the
same review rules, restated for English, with English examples. They
hold for prose, `\ltnote`s, abstracts and appendices alike. The
project's own names, deck titles and example data stay in the project's
`CLAUDE.md`; this file carries the rules, not the course's data.

Contents: [Spelling](#spelling) ·
[Terms and code in prose](#terms-and-code-in-prose) ·
[English rules](#english-rules) ·
[Rules shared with house-style-sv.md](#rules-shared-with-house-style-svmd) ·
[Wording set elsewhere in the build](#wording-set-elsewhere-in-the-build) ·
[Bilingual decks](#bilingual-decks)

## Spelling

**British spelling with -ize** (Oxford spelling), the majority in the
English course that adopted this file (introtools, 2026-10-31: -ize
against -ise 3 to 1 among the decks' words, 23 to 5 across its
pages, not counting GitHub's *organization*):

- *-ize*, *-ization*: organize, initialize, summarize, generalization;
- but *-yse*: analyse, paralyse;
- *-our*, *-re*, *-ce*: behaviour, colour, centre, licence (noun) and
  license (verb), practice (noun) and practise (verb), defence;
- doubled *l*: labelled, modelled, travelling;
- *program* for software, always; *programme* only for a course or
  degree programme.

Words that end in *-ise* in every spelling stay so: exercise, otherwise,
advise, revise, supervise, comprise, compromise, surprise.

Quotations, program strings, command output, option names and a
product's own terms keep their spelling: a dictionary entry quoted with
*organizations*, a GitHub *organization*, CSS `color`, `--color=auto`.

The preamble loads `babel` with `british` as the main language, which
babel takes from the last option: `[swedish,english,british]` (the
template's `[british,english,swedish]` is a Swedish deck's); the quotation
marks come from `\enquote` (csquotes; `latex-writing`), single on the
outside in British style. Never type quotation marks by hand.

## Terms and code in prose

**The English technical term, one term per concept.** Take the term the
tool's own documentation uses (the man page, POSIX, the Python
documentation): *directory*, *working directory*, *standard input*,
*pipe*, *redirection*, *exit status*, *option*, *argument*. The everyday
word (*folder*) may appear once, where the term is introduced, to
connect the two; then the term only, never alternating with synonyms for
variety. With `acro`, the English expansion is the `long` form and acro's
own "long (short)" at first use does the rest. A foreign word in an
English sentence goes in `\foreignlanguage{swedish}{…}` (hyphenation);
a proper name does not.

**Code in prose.** Everything the student types or the computer prints
is code markup: commands, options, file and directory names, paths,
variables, values. In the prose of `contents.nw` write noweb quoting,
`[[ls -l]]`; in block and frame titles `\texttt`, never `\mintinline`
(`chunk-authoring.md`). A snippet holding a `"` pair is a `\mintinline`
in any deck that loads Swedish babel (every bilingual deck): Swedish
shorthands break `[[...]]` (`chunk-authoring.md`, "Quoting traps").

- A command is written as the student types it on the course's system,
  suffix included (`python3`, `pydoc3`), with its options as one literal:
  `[[ls -la]]`.
- Name what the literal is the first time: "the command `[[cd]]`", "the
  option `[[-l]]`", "the file `[[notes.txt]]`". Never inflect a literal:
  "two calls to `[[print]]`", not "two `[[print]]`s".
- A key combination is code with a hyphen, `\texttt{Ctrl-C}` (as the
  existing decks write it); a single named key is a word with its
  keyboard capital: "press Enter", "the Tab key", "the arrow keys".
- A literal value a program reads or prints keeps its code markup
  whatever its size: `\texttt{13}`, not 13 set as running text.

The named parts of a sketched program are *pseudocode*, and their
definitions *refine* it ("later we refine the pseudocode into Python");
never "a name we decide on later" (`chunk-authoring.md`).

## English rules

The Swedish rules restated for English, where the language needs its own
wording.

**Address the student as "you".** Second person throughout the student
text — prose, exercises, learning objectives, appendices: "when you
work in the terminal", "your script". Not "the student", "students",
"one" or "the reader" in the student text. English "you" does not mark
number, so a real plural says so: "you and your partner", "the two of
you". Program strings and quoted sources keep their own wording.

**"We" does what we do.** When the text says what happens in the
material, the subject is "we", not the document: "We start with the
simplest case", not "It starts with" or "The lecture starts with". Do not
contort a sentence to avoid "we". And a part is not its whole: "The
exercise consists of seven tasks", not "is seven tasks".

**Prerequisites say "worked through".** "The student should have worked
through the lecture \emph{Functions}", never "seen" or "attended": the
notes can be read instead of the lecture. (The English counterpart of
"tagit del av", proposed 2026-10-31; not yet confirmed by the author.)

**Run, execute, perform.** A program performs (carries out) a task; the
processor, the computer, the interpreter or the shell executes the
program. Whoever runs code *executes* it (noun *execution*); a program or
a person *performs* a task. "Run" stays as the everyday word: "run the
script", "the command runs".

**Never tie the text to weeks, lecture order or course events.** Not
"last week", "week 38", "in the first half of the lecture", "in the lab",
"this week's module". Refer to topics, deck titles and activities:
"earlier", "the lecture \emph{Functions}", "when you work in
the terminal". An `\ltnote` may still mention the lab; the student's text
may not. Naming an earlier deck by its title in the first-person plural
is allowed and preferred: "as we discussed in the lecture
\emph{Functions}". The title points at a document the reader can open
in any week; "last week" does not, and that is the whole distinction.

**Numbers: one to nine in words, 10 and up in figures**, a common
British rule; English has no counterpart of Språkrådet (proposed
2026-10-31; not yet confirmed by the author). A round number (fifty, a
hundred, a thousand) may stay in words. A literal value keeps its code
markup (above).

**The appendix pointer** reads "the scientific basis is in
\cref{app:...}", across decks "the scientific basis is in the lecture
\emph{Functions}, Appendix B", and for one of several principles in a
paragraph "the scientific basis for DRY --- and the reservations that go
with it --- is in …". Placement (a footnote at the
claim, once), saying what the appendix answers, the qualification in the
same footnote ("… says.⁷,⁸") and citing a measured claim where it stands
are in `backing-claims/references/appendix-guide.md`, "Pointing at the
appendix from the text".

**The chapter precis.** Every appendix chapter opens with the verbatim
sentence

```latex
\chapterprecis{The author has not yet reviewed the results in this
  appendix in full.}
```

*Project-overridable*, as in Swedish: a project with another review
practice writes its own sentence, the same in every chapter.

## Rules shared with house-style-sv.md

These rules hold in every language. They stand here as well as in
`house-style-sv.md` so that each file serves a one-language deck alone;
**a change to one copy goes to the other in the same commit.**

- **Do not present as new what an earlier deck already taught.** Build
  on it and point back by title; cut a repeat rather than re-explaining
  it or re-running a near-verbatim exercise (author, 2026-09-29: "build
  on the earlier deck, cut repeats").
- **A heading names what the section builds**: "Our backup script", not
  "Our script" (author, 2026-09-23).
- **Name the action, not the position.** "Something has to translate
  what we write into what the processor executes", not "something has
  to stand in between". A title that names a literal reproduces it
  exactly ("Hello, World!"). Never refer to physical position ("on the
  next slide", "above", "below"): use `\cref`.
- **No ambiguous sentence-initial pronouns in the appendices.** "The
  search was topic-driven …", not "It was …".
- **State a backed claim; do not defend it.** The author struck "and we
  did not make that up" after "one of the most common novice mistakes"
  (2026-09-22): the citation and the pointer footnote carry the backing.
- **No count in front of a list unless the count is the point.** "The
  arithmetic operators are:", not "The five arithmetic operators are:"
  before a list of seven (2026-09-22). A count invites a check and goes
  stale.
- **The lead-in to a side-by-side example does not repeat its column
  labels.** "The counting in the two programs, side by side:" suffices
  before a `\codebycode`; the labels already name the files, and long
  file names in the lead-in pushed lines into the margin (2026-10-24).
- **Example data: the pattern** (the names belong to the project):
  never the author's own name; real places and real facts, matching the
  real world, with an `\ltnote` saying where they come from and what is
  approximated; a fixed cast in a fixed order across decks; a cultural
  fact hidden in the data where it costs nothing, kept out of the
  student's text and recorded with its source in an `\ltnote`.
- **Verbs name the mental action**: "worth thinking about", not "worth
  stopping at" (2026-09-20).
- **Every source has a real reference.** No nicknames for sources ("the
  misconceptions paper"); the author's own manuscript gets an
  `@unpublished` entry with a provenance block.
- **Boilerplate is not repeated deck after deck.** A paragraph restating
  a course convention appears once, where the convention is introduced;
  later decks refer to it in at most one short clause (2026-09-28: "Trim
  everywhere, not just in the book, if it's repetitive"). The same holds
  for repeated `\ltnote`s stating a deck-wide rule.

## Wording set elsewhere in the build

- **Block titles.** English is beamer's default: delete the
  `\deftranslation` block from `slides.tex` (`deck-anatomy.md`).
- **cleveref names.** `\usepackage[english,capitalise]{cleveref}`
  (cleveref reads its own options, not babel's; it has no `british`
  option). English decks capitalise mid-sentence ("Figure 3",
  "Appendix B"), as the existing English decks do; Swedish ones do not.
  cleveref's English names agree with memoir's "Appendix"; override only
  `enumi` → "line"/"lines" in the `\AtBeginDocument` hook, for
  references to numbered program lines.
- **The abstract's parts**: *Overview*, *Learning objectives*,
  *Prerequisites*, optionally *Reading*.
- **Section headings in the appendices**: Method, Results, Discussion and
  limitations, Conclusion, Further work, Hits bearing on the claim.
  `assets/deck-template/sokprotokoll.tex` is Swedish: translate its
  method chapter for an English deck.

## Bilingual decks

A bilingual deck has English and Swedish blocks side by side in one
`contents.nw`; the mechanism (the `en` and `sv` blocks, `\tr`, the sync
stamps) belongs to the didactic package. For the wording:

- **The en blocks follow this file, the sv blocks `house-style-sv.md`**,
  and each `\tr{English}{Svenska}` its two halves likewise. So the sv
  block gives the Swedish term with the English once in parentheses,
  the en block the English term alone; each block follows its own
  language's number rule.
- **A pair says the same thing; it is not a word-for-word translation.**
  The same claims at the same strength, the same steps, the same
  references and pointers, each written as a native writer would. If one
  side gains a sentence, so does the other, unless the block is meant
  for one edition only.
- **Shared material is written once for both editions.** Chunks,
  `\runpython` runs, figures and the section structure are unmarked, so
  every name in them is read in both languages: an example name is one
  both languages spell and pronounce alike, and identifiers and file
  names are ASCII. A chunk name is shared too; which language the shared
  names use is the project's decision, recorded in its `CLAUDE.md`.
- **Program output in a language** needs a chunk per language; a shell's
  messages are set per edition with `LC_ALL` instead.
- **Cross-references differ per edition**: cleveref is capitalised in
  English and not in Swedish, so its language and capitalisation follow
  the edition and cannot be fixed in the shared preamble.
