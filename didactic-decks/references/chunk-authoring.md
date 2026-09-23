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
   a constants bucket, a helper-function bucket, the main program, and
   the start call. Name the buckets for THIS program
   (`<<vägvisarens konstanter>>`, `<<vägvisarens hjälpfunktioner>>`,
   `<<vägvisarens huvudprogram>>`); a bucket named `<<hjälpfunktioner>>`
   in two programs would put every function in both files. A program that
   extends another may name the other's bucket and add its own.
2. Then sketch the main program, with chunk names as pseudocode.
3. Each helper is appended to the bucket (`=` again; noweb prints ≡, then
   +≡) where the discussion first needs it, after the reasoning that
   calls for it — never all at once before the problem's details are
   discussed ("The problem with the current programs is that it too
   early outlines what functions we need"). Say once in the prose what +≡
   means.
4. The whole program is shown once it is refined (above).

**Blank lines serve the pseudocode, not the tangled file.** In the
literate source, group related chunk references on consecutive lines and
separate groups by a single blank line, never two: the tangle rule runs
black, which adds PEP 8's spacing (author, 2026-09-23: "use blank lines
for the readability of the 'pseudocode' (literate source), not the
underlying result"). Files tangled raw, without black, keep their own
spacing.

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
cites with `\autocite`, which didactic sets as a margin footnote.

Never put `\textcite` or `\autocite` inside a `table` or `figure` float:
the citation becomes a `\marginpar` and the float is lost ("Float(s)
lost"), taking its `\label` with it. Use `\parencite` in floats and put the
footnoted first mention in the prose outside the float.
