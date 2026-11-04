# Polls in a didactic Beamer deck

An `exercise` can be a live poll, with a QR code on the slide and a
plain exercise in the notes. This pattern is verified in the intropy
decks *Algoritmiskt tänkande*, *Hello, World!* and *Repetition: kursens
grunder* (with context, mentipy 0.14, 2026-10). The build (venv and
version stamp) is in `SKILL.md`. Composition and the rest of the build
are in the `didactic-decks` skill.

## The shared block

One `pycode` block at the top of `contents.nw`, inside `\mode<all>` …
`\mode*`, holds what every question shares:

```latex
\mode<all>
\begin{pycode}
from mentipy.latex import file_snippet, mc, open_text, scale
from mentipy.store import Store
mentipy_common = {
    "store": Store("mentipy.json"),   # the deck dir is PythonTeX's cwd
    "qr_dir": "mentipy-obj",
    "qr_format": "png",
    "environment": "",                # the exercise is written by hand
    "show_url": False,                # no URL in the notes
    "layout": "auto",                 # QR columns on slides, flat in notes
    "locale": "sv",                   # labels and web pages
}
def fraga(helper, *args, **kwargs):
    return helper(*args, **{**mentipy_common, **kwargs})
\end{pycode}
\mode*
```

- **No `base_url` in the deck.** While a server runs, a build uses the
  address it serves; otherwise the `base_url` setting, or else the LAN
  address at compile time. A deck-level `base_url` wins over all of
  those and pins every QR code to one address, so serving in the other
  mode (LAN instead of public, or the reverse) becomes impossible. See
  "Where the QR codes point" in `SKILL.md`.
- **`environment=""`:** the deck writes the `exercise` environment
  around the call, so titles and `\label`s survive.
- **`locale`:** the deck's language, for the slide labels and for
  the question's web pages. A deck that still wraps its helpers in a
  string-replacing `translate` can drop the wrapper (see "Language" in
  `SKILL.md`).

## A question

```latex
\begin{frame}[fragile]
  \begin{exercise}[What is printed?]
    \label{ex:hello-run}
    <<the program, shown on the slide>>
    \begin{pycode}
print(fraga(
    mc,
    "What does hello.py print?",
    ["Only an error", "The first line, then an error", "All three lines"],
    context=file_snippet("examples/hello.py"),
))
    \end{pycode}
  \end{exercise}
\end{frame}
```

- **Two surfaces:** the slide shows the program from the frame's chunk.
  The phone gets it from `context=`, because the slide's program is not
  on the phone.
- **Phrasing:** the prompt names the file, and code inside the prompt
  or the options goes in backticks.
- **The flat article layout** (the `\mode<article>` branch of `auto`)
  is transparent. The notes show the prompt alone, in the running
  text's weight: no options, no "Choose exactly one", no type, limit or
  range, no bold. So a prompt that only works with its options
  ("which one is right?") must be rephrased for both surfaces.
- **Pacing flags:**
  - `lock=True` (the default) paces a question with the slides.
  - `lock=False` is for a second question on the same slide.
  - `next=False` goes on the deck's last question.

## Placement with overlays

A `pycode` inside a frame is safe only if the frame has no overlays.
To keep the overlays, register the question at top level, right before
the frame and in `\mode<all>`, with
`write_snippet("hello-run", fraga(mc, ...), directory="mentipy-obj")`.
The `directory` defaults to the config's `qr_dir`, not to the deck's
`qr_dir=`, so pass it. Then put `\mentipyinput{hello-run}` inside the
exercise.

- **The macro:** `\mentipyinput` is in `mentipy.sty`
  (`\usepackage{mentipy}`, installed by `mentipy sty --install`). It
  reads `mentipy-obj/` unless `\mentipysnippetdir{...}` says otherwise,
  and warns until PythonTeX has written the file.
- **Without the package,** use `\input{mentipy-obj/hello-run.tex}` with
  an `\IfFileExists` guard for the first pass.
- **`\pause`:** never combine it with PythonTeX content in one frame.

## The QR caption

The address under the QR code lives in the sidecar
`mentipy-obj/Q-*.pdf_tex`, which `mentipy serve` rewrites together with
the image.

- **Never post-process the sidecar `\input` into literal text.** The
  copy freezes at compile time, so the caption stops following the
  server while the QR image keeps updating.
- **To make the URL fit the narrow QR column,** redefine the hook in
  `\mode<all>` before the first question:
  `\newcommand{\mentipyqrcaption}[1]{{\tiny\url{#1}}}`. `\url` breaks
  after `:`, `.` and `/`.
- **Make the PDFs depend on the sidecars**
  (`$(wildcard mentipy-obj/Q-*.pdf_tex)`, as in `SKILL.md`), or `make`
  after `mentipy serve` says there is nothing to do.

## Checks

- Before the final build, run the deck's clean recipe, and check that
  the `pytxcode` counts are equal.
- `mentipy list --store mentipy.json` lists the questions in slide
  order, and the prefixes match the ones under the QR codes.
- `pdftotext notes.pdf - | grep -c <base host>` gives 0.
- Render and read every question slide. Open every form at phone width
  to check the options and the context.
