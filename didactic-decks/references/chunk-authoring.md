# Authoring chunks and frames in contents.nw

Load the `literate-programming` skill before editing any `.nw` file. This
file covers only what is specific to a deck: chunks that also have to work
as slides.

Contents: [Chunks](#chunks) · [Frames](#frames) ·
[Environments](#theorem-style-environments) · [Recaps](#recaps) ·
[Code style](#code-style-in-chunks) · [Languages](#multi-language-decks) ·
[Quoting traps](#quoting-traps) · [Titles](#block-and-frame-titles) ·
[Mode splits](#mode-splits) · [cref traps](#cref-traps) ·
[Citations](#citations)

## Chunks

A code chunk replaces every `\inputminted[firstline=...,lastline=...]`.
Name the chunk after the file it tangles to and place it at its point of
presentation, inside the frame that shows it:

```latex
<<[[hello.py]]>>=
print("Hello, World!")
@
```

Chunk names read as **pseudocode** for the program, in the document's
language, so that the root chunk alone gives a useful overview (author,
2026-09-23: "Make these chunk names a bit more descriptive. Like
pseudocode"): `funktion för instruktionen att gå`, `fråga efter målet
tills vägvisaren känner det`, not `instruktionen att gå` or `vägvisarens
fråga`. Say what the part does and, for a definition, that it is one.

**Show the whole program once it is fully refined** (author, 2026-09-23:
"Always show the program as a whole when we've covered it fully and
refined all chunks"). After the last chunk of a literate program and its
explanation, a notes-only frame shows the tangled file whole ("Sätter vi
in varje del där dess namn står får vi hela programmet:" plus
`\inputminted{python}{examples/x.py}`), before the run. The slides
already show every chunk and need not repeat it.

**A literate solution unfolds top-down** (author, 2026-09-23), the way a
programmer works, not as a list of functions declared up front:

1. The root first: the file's layout — docstring, imports (once taught),
   a constants bucket, a helper-function bucket and the main program. The
   start call is not in the root: it stands right after `def main` in the
   main program's own chunk, so the definition and its call are read
   together (author, 2026-09-24, on two decks: "Keep the definition and
   call close to each other"). The tangled file is the same, since the
   main program is the root's last part. The layout is not explained to the
   student: a sentence like "Direkt efter definitionen av main står anropet,
   så att definitionen och anropet läses tillsammans" narrates the authoring
   rule and confuses (author, 2026-09-30, beside it: "I don't really
   understand that."); a reason belongs in an `\ltnote` if anywhere. Name the buckets for THIS program
   (`<<vägvisarens konstanter>>`, `<<vägvisarens hjälpfunktioner>>`,
   `<<vägvisarens huvudprogram>>`); a bucket named `<<hjälpfunktioner>>`
   in two programs would put every function in both files. Choose the
   shortest name that is sufficiently clear; look-alike programs in one
   deck may need the file name (author, 2026-09-24). A program that
   extends another may name the other's bucket and add its own.
2. Then sketch the main program, with chunk names as pseudocode.
3. Each helper is appended to the bucket (`=` again; noweb prints ≡, then
   +≡) where the discussion first needs it, after the reasoning that
   calls for it — never all at once before the problem's details are
   discussed ("The problem with the current programs is that it too
   early outlines what functions we need"). Say once in the prose what +≡
   means.
4. The whole program is shown once it is refined (above).

Classes are part of the layout: a program's classes get their own bucket
between the constants and the helper functions (they may use the
constants; the helpers and the main program use them). A class developed
method by method first shows its shell — `class X:`, docstring, a bucket
of X's methods named for the class — and each method is appended when
the reasoning reaches it. A class file's test program is called
`tests()`, not `main()` (the start call is `tests()` under the guard), and
it is not written last: sketch it as the class is designed, appending each
part's test functions, and their calls, right after that part, as in
ordinary literate programming, and show each test's output beside it
with PythonTeX, running just that test function (author, 2026-09-24,
2026-10-21). The mechanism is in `runpython-and-output.md`, "Output
beside test cases".

**No pass-through chunks.** Never append a new chunk name to a bucket (or
put one in a root) and then refine that chunk right after: the reader meets
a name that only forwards to the next display. Write the content in place
instead: the class shell `class X:` straight in the file's root when the
classes bucket would hold only that class, the method's code straight in
the `+≡` of the methods bucket instead of `<<metoden m>>` followed by its
definition (author, 2026-10-12, striking `<<book.py:s klasser>>` and
arrowing it to `class Book:`: "The rule is to not append a new chunk to the
bucket chunk and then refine that chunk immediately afterwards. Then skip
that indirection."). A name earns its place only when its definition comes
later, after reasoning the reader must meet first: that is the pseudocode
of rule 2.

Only programs the text *develops* — builds up from reasoning about the
problem — are restructured. A program the student predicts, runs or
compares stays whole (below), and in a contrast pair invariance between
the two programs wins over the blank-line rule: do not give one of them
spacing the other lacks (rollout, 2026-09-23). A file whose functions
move keeps the same lines; only the order of definitions may change,
which is allowed, and every run must give the same output.

The prose calls the sketch's named parts **pseudokod**, and their
definitions are where "senare preciserar vi pseudokoden med pythonkod";
never "ett namn" that "vi bestämmer sedan hur" (author, 2026-09-23,
striking both phrases).

**Blank lines serve the pseudocode, not the tangled file.** In the
literate source, group related chunk references on consecutive lines and
separate groups by a single blank line, never two: the tangle rule runs
black, which adds PEP 8's spacing (author, 2026-09-23: "use blank lines
for the readability of the 'pseudocode' (literate source), not the
underlying result"). The same holds for minted blocks, not only chunk
references (author, 2026-09-29: "Don't do double blanks."; asked about
black restoring PEP 8's two: "Single blank in the literate source. It's
fine that black makes it double blanks again in the tangled file."). Files
tangled raw, without black, keep their own spacing.

**A program the student reads or traces is not split into chunks**
(author, 2026-09-20 and again 2026-09-23: "Just do all of these inline,
not literate, since the student should practice reading code"). The
notes show it whole, as one chunk; when it is too long for one slide, the
slides show consecutive line ranges of the tangled file on several
presentation-only frames (`\inputminted[firstline=…,lastline=…]`), never
a shrunk frame. Literate splitting is for solution code, where the
decomposition is what the reader should learn.

## Frames

A frame containing a chunk — or any minted output — must be `[fragile]`.

**Avoid `\frametitle`: title a frame by its block** (author, 2026-10-21:
"I try to avoid \frametitle (eats so much space) in favour of
\begin{block}..\end{block} of different kinds. The subsection titles are
on the slides anyway for grouping and navigation."). Put the frame's
content in a block of the kind it is — `example`, `exercise`, `solution`,
`definition`, `remark`, `block`, … — and give the title as the block's
argument (`\begin{example}[Ett program som hälsar]`,
`\begin{block}{Titel}`). The headline already names the section and
subsection; a frame title repeats them at the cost of a line of the
slide. In the notes, didactic ≥ 2.13 sets a remaining `\frametitle` as a
run-in heading (bold title, the frame's text on the same line); older
versions put the text in a new paragraph under it, which reads as a
stray paragraph break.

Three examples belong on three adjacent frames, not on one overfull frame.

## Theorem-style environments

**Never start a theorem-style environment (`example`, `remark`,
`definition`, ...) directly with a chunk or a minted block.** The inline
label and the code display overprint each other in the notes job. Put a
short lead-in sentence first:

```latex
\begin{frame}[fragile]
  \begin{example}[Ett program som hälsar]
    Programmet skriver ut en rad:
<<[[hello.py]]>>=
print("Hej!")
@
  \end{example}
\end{frame}
```

One `example` or `exercise` environment per case, adjacent, never merged.

**A solution follows its exercise as one environment holding every run of
it.** Add a second `solution` only for a genuine alternative approach, and
say in the prose that it is one (author, 2026-09-29: "One solution per
assignment. Unless there are alternative solutions, in which case we point
that out."; beside two separate solutions to one exercise that
holds two programs: "Maybe one solution that keeps both. Just as for the exercise
itself.").

**An open exercise gets its model solution in the notes only** (author,
2026-10-19, on "sketch the algorithm for an automated warehouse": "We only
need it in the notes, the slides will review suggestions instead."). An
open exercise has no single right answer: a sketch, a design, a list of
advantages. At the lecture the slides go through the class's own answers
(the Mentipy `open_text` results), which a prepared answer on the next
slide would cut short; the notes' reader has no class to compare with, so
the notes give a worked model solution right after the exercise, outside
any frame. A reflective question ("Vad behöver du repetera mer?") needs no
solution.

A two-line display inside an `example` must not rely on `\\` inside a
`center`: the article job collapses it to one line. Use a one-column
`tabular`, or a `\par` between the lines.

```latex
\begin{center}
  \begin{tabular}{@{}c@{}}
    \texttt{first line} \\
    \texttt{second line}
  \end{tabular}
\end{center}
```

## Recaps

To show the same code again later, **do not redefine the chunk** — noweb
concatenates the definitions into the tangled file. Re-display the tangled
artifact instead, always the whole file, never a line range (the one
exception is the slide view of a program the student reads, under
"Chunks"):

```latex
\inputminted{python}{examples/foo.py}
```

Name the file in the example's title or lead-in, so the reader knows which
artifact is shown again: "En lista (\texttt{loop2.py})", not a bare
`\inputminted` with no title (author, 2026-09-29, beside an unnamed
re-display: "loop2.py?").

The Makefile's `EXAMPLES` dependency guarantees the file is current.

## Code style in chunks

The tangle rule pipes tangled `.py` files through `black`, and the tangled
file must match the slide byte for byte, so write Python chunks
black-clean from the start: four-space indent, double quotes, two blank
lines around top-level definitions.

Keep every source line ≤ 79 characters, in `contents.nw` and
`abstract.tex` alike. Rewrap what you touch.

## Multi-language decks

`autolang` infers each chunk's language from its filename-style name, so
`.py`, `.cpp`, `.sh`, `.s`, `.js`, `.lean` all just work. Declare the
suffix in the Makefile's `NOWEB_SUFFIXES` and add its tangle rule.

Pygments' GAS lexer marks `len = . - msg` as an error token, which minted
draws as a red box. Write it in the directive form instead:

```gas
.set len, . - msg
```

## Quoting traps

Noweb quoting `[[...]]` cannot hold a babel shorthand pair. `[[phone["adam"]]]`
prints `phone[ädam"]`, because the Swedish `"a` shorthand fires before
`\code` changes catcodes. Write such snippets with `\mintinline`:

```latex
\mintinline{python}|phone["adam"]|
```

## Block and frame titles

Block and frame titles use `\texttt`, never `\mintinline` — it vanishes on
slides.

When the Berlin theme's headline overflows, give the section a short form:

```latex
\section[short]{the long title}
```

## Mode splits

- Notes-only structure: `\mode<article>{\subsection{...}}`.
- Slide-only tweaks: `\mode<presentation>{...}` —
  `\setminted{fontsize=\scriptsize}`, `[shrink]` frames, poster frames
  `\centering\huge\texttt{...}`.
- **Verbatim does not survive inside `\mode<presentation>{}`.** A poster
  frame can hold `\texttt`, not a chunk.

Overlay staging that hides an answer on the slide (`\item<3->`,
`\onslide<2->` inside one example) collapses in the notes, where every
overlay prints at once. Stage structurally instead: material, exercise,
prose, then a second `example` environment carrying the answer.

## cref traps

didactic's `remark`, `summary` and `solution` are unnumbered, so `\cref` to
them prints `??`. `\cref` to an `example` prints "sats" in the beamer job.
Wrap such references so they exist only in the notes:

```latex
\only<article>{ (\cref{ex:foo})}
```

Prose between frames is article-only and may `\cref` freely.

## Citations

`\parencite` is used **only** inside `\ltnote`s; the student-facing prose
cites with `\autocite`, which didactic sets as a margin footnote. This
holds in the appendices too: a crowded margin is never fixed by turning
citations into `\parencite`. A repeat citation adds nothing to the margin,
because didactic reuses the existing footnote (option `footnotereuse`;
author, 2026-10-10: "Don't use inline citations, repeat citations
shouldn't add anything to the margin"). Remaining overflow is a layout
problem: fix it with paragraph order or a `\clearpage`.

Never put `\textcite` or `\autocite` inside a `table` or `figure` float:
the citation becomes a `\marginpar` and the float is lost ("Float(s)
lost"), taking its `\label` with it. Use `\parencite` in floats and put the
footnoted first mention in the prose outside the float.

## Two versions side by side: `\codebycode` (didactic 2.7)

A contrast between two versions of the same program or function is shown
side by side with `\codebycode[opts]{lang}{file}[opts]{lang}{file}`,
never by hand (no per-deck `pycode` helper, no `tabular` of
`\inputminted`). Per side: `name=` (a def, class or `Person.__eq__`),
`lines=3-10`, `from=`/`to=` (text delimiters; braces as `\{`/`\}`),
`nodocstring`, `label={\texttt{greet1.py}}` (always: the decks name
files on re-displays), `width=`. It reads the tangled file as text with
`ast` and never runs it, so bare-`main()` programs are safe. Notes: full
width by default with the margin blocked (inline is safe since the
marginfix fix of 2026-10-03; no float needed). Slides: the frame at
`\tiny`. The column widths are shares of each side's longest line; since
didactic 2.7.1 a side wider than its column logs `Package didactic
Warning: A line of code side by side is … wider than its column` (grep
the logs for `than its column`; sides with `breaklines` are not checked
since they wrap). Fix an overflow with per-side `breaklines` or
`nodocstring`/`lines=`; `shrink=10` widens the frame only by 11 %. The
`didactic_pair_*.txt` files it writes are build output (gitignored). The
runs of two programs go side by side with `\runbyrun` (a `shell` key for
a shell command side); stateful runs (a file after "w" vs after "a") are
written by hand with the documented environment (didactic 2.8):
`\begin{didacticpair}[runs]{2} \didacticpairlabel{…} & … \\ <left runs>
& <right runs> \end{didacticpair}` — runs execute left column first, top
to bottom, so the right column sees the left column's files. Since 2.8
transcripts no longer quote words with åäö (`$ python3 greet.py Åsa`), so a
rebuild under 2.8 changes such transcripts. `\textbytext` stays for prose. When the
second version may only appear after a try-first reveal and the first is
pages back, repeat the first beside the second (variation-theory skill).
