---
name: mentipy
description: Author, build and run live classroom polls with Mentipy (self-hosted, QR codes on Beamer slides, PythonTeX helpers in mentipy.latex). Use proactively when (1) writing or editing a poll with mc, open_text, scale, ranking, word_cloud, pin_text or pin_image, or a deck or handout that imports mentipy, (2) giving a poll its program or data with context=, file_snippet or file_download, (3) a build fails on `import mentipy`, a stale venv, or QR codes or prefixes that changed, (4) running a poll in a lecture with mentipy serve, --public, Skip, /active, or reading answers with mentipy list, view, watch or export, (5) the user mentions Mentipy, mentipy.json, mentipy-obj, \mentipybasedir or live polls. Load BEFORE writing the first poll. Owns the API, the build and the lecture; why and when to poll stays in try-first-tell-later and variation-theory, and the frame layout of a didactic deck is in references/beamer-decks.md here.
---

# Mentipy

Mentipy registers a question while the document compiles (a PythonTeX
block calls a helper), writes its QR code, and returns the LaTeX for
the slide or the handout. `mentipy serve` then runs the poll from the
lecturer's machine. The answers live in the store, `mentipy.json`.

## First: ask the installed Mentipy

Never write helper calls from memory. The API grows with each release,
and `mentipy latex` prints the installed version's reference: every
helper's signature, the per-question keywords (`next`, `results`,
`lock`, `context`), the context helpers, the inline-code rule, the
shared keywords and every config key. Read it first, plus
`mentipy <command> --help` for the CLI.

A deck compiles with the mentipy in **its own venv**, not with pipx's.
Check that venv's version
(`.venv/bin/python3 -m pip show mentipy`) before relying on a feature;
`mentipy latex` describes the pipx one.

## Choosing the question type

| Helper | Use it for |
|---|---|
| `mc` (`multi=True` for several) | a prediction with a few plausible answers; distractors are real misconceptions |
| `open_text` | an explanation in the student's own words; the answers are listed one by one |
| `scale` | confidence or self-assessment, before and after |
| `ranking` | ordering steps or priorities; the result is an average rank |
| `word_cloud` | activating prior knowledge, many short answers |
| `pin_text` | "point at the bug" in code or text; `allow_comment=True` asks why |
| `pin_image` | the same on a figure |

Why to ask, and when in the sequence: `try-first-tell-later` (an `mc`
poll's stem and options follow "Writing a poll" in its
`references/patterns.md`) and `variation-theory`. The intent of each
poll goes in an `\ltnote` (`didactic-notes`).

## Writing the prompt and options

- **Plain text.** Mentipy escapes everything for LaTeX and HTML: no
  macros, no `\cref`, no math. Quotes are safe. LaTeX prompts are not
  supported yet (dbosk/mentipy#54).
- **Code in backticks**, as in Markdown: ``"What does `len(xs)`
  return?"``, options ``["`2`", "`3`"]``. The slide sets it as
  `\texttt`; the phone shows it as code. Backticks pair left to right,
  so a stray one steals the next span: write apostrophes as `'`.
- **The program goes in `context=`, not in the prompt.** For example,
  `file_snippet("examples/x.py")`, or `name="f"` or `name="Cls.meth"`
  for one function or class. Use `file_download(path)` for data too
  large to read on a phone, and a plain string for prose. The phone
  shows the context after the options and the Submit button, and the
  results page shows it under the aggregate. It is never on the slide,
  so the slide's frame still shows the code itself.
- **Context holds the premises, never the answer.** No output, no
  solution: the student reads it before answering.
- A file read by `file_snippet` must exist before PythonTeX runs. In a
  literate deck that is a tangled example, so the PDFs must depend on
  it in the Makefile.

## Identity: what a change does to the QR code

The question's hash, and so its URL prefix and QR code, comes from the
**premises**: the prompt, the options or other input set, and the
context's text or bytes.

- Editing any of those makes a **new question**. You get a new prefix
  and a new QR code, and the answers start over (the old ones stay under
  the old prefix). Recompile, and never project an old PDF or printout.
- Labels, `lock`, `next`, `results`, `layout`, a snippet's label or
  language, and a word cloud's rendering are presentation. They keep
  the prefix, and a recompile updates the stored question in place.
- The same question asked in two decks, or two years running, is one
  question with one answer pool. Its results page opens on the current
  server session (since the last `mentipy serve` start), so an earlier
  run does not show; `?window=all` or `mentipy view --window all` does.

## The build

PythonTeX's `python3` cannot import pipx's mentipy, so each deck (and a
bound book) has its own venv, which the Makefile makes. It is never a
manual step. A version stamp upgrades an existing venv once when the
deck needs a newer Mentipy:

```make
MENTIPY_VENV=	$(CURDIR)/.venv
PYTHONTEXFLAGS=	--interpreter python:${MENTIPY_VENV}/bin/python3 --rerun=always

${MENTIPY_VENV}/bin/python3:
	mentipy init --venv ${MENTIPY_VENV}

MENTIPY_VERSION=	0.14
MENTIPY_STAMP=	${MENTIPY_VENV}/mentipy-${MENTIPY_VERSION}

# Order-only: the venv must exist, but its timestamp must not trigger
# an upgrade.  The PythonTeX output goes with the upgrade, since latexmk
# reruns PythonTeX only when the code changed.
${MENTIPY_STAMP}: | ${MENTIPY_VENV}/bin/python3
	${MENTIPY_VENV}/bin/python3 -m pip install 'mentipy>=${MENTIPY_VERSION}'
	${RM} ${TEX_OUTDIR}/*.pytxmcr
	touch $@

notes.pdf slides.pdf: ${MENTIPY_STAMP}
# mentipy serve rewrites the QR sidecars; the PDFs must follow them.
notes.pdf slides.pdf: $(wildcard mentipy-obj/Q-*.pdf_tex)
```

- The recipe relies on the shared `makefiles/tex.mk` running PythonTeX
  inside latexmk (`TEX_PYTHONTEX=yes`, makefiles ≥ 1571556 "Make
  TEX_PYTHONTEX actually run PythonTeX"). An older checkout only has
  `%.pdf: pythontex-files-%/%.pytxmcr`, which nothing builds when the
  output goes to `ltxobj/`. Make then skips the rule silently, and the
  PDF builds with **empty poll frames and no error**. The fix is to
  update the submodule
  (`git -C makefiles pull origin master` and commit the bump), not to
  write a custom rule. The check is `grep -n latexmkrc makefiles/tex.mk`.
- PythonTeX runs the code in the `python3` on PATH unless
  `--interpreter python:<venv>/bin/python3` is given. Running pythontex
  itself with the venv's python is not enough.
- Raise `MENTIPY_VERSION` when the deck starts using a newer feature.
  The version must be on PyPI, or every fresh build fails at the
  `pip install`.
- Gitignore `.venv/`, `mentipy-obj/` and `mentipy.json` (the students'
  answers), unless the project deliberately tracks the store.
- **A Python upgrade kills the venv.** Its `python3` then fails with
  "No module named 'encodings'". Delete `.venv` and run `make`.
- In a book of decks, use `\usepackage{mentipy}` and
  `\mentipybasedir{auto}` (mentipy ≥ 0.13). They resolve each deck's
  store and QR directory under `\subimport`. See
  `didactic-decks/references/book-binding.md`.

## Where the QR codes point

Two things write the QR images and their address captions. The deck
build writes them with the helper's address: `base_url=` if given,
else `mentipy.base_url`, else the LAN address at compile time.
`mentipy serve` rewrites them with the address it serves. **Whichever
ran last wins**, and decks rerun PythonTeX on every build, so a rebuild
after `serve` reverts the codes (dbosk/mentipy#67).

- **Never hard-code `base_url` in a deck.** It pins every code to one
  address, and serving in the other mode is then impossible.
- **LAN lecture:** build, then run `mentipy serve`. A rebuild on the
  same machine resolves the same LAN address, so it stays consistent.
- **Public lecture:** `serve --public` takes the tunnel's address (or
  `mentipy.public_base_url`), but the build reads only
  `mentipy.base_url`. So set the public address there too, with
  `mentipy config mentipy.base_url --set http://host:port`, then build
  and run `mentipy serve --public ssh`. Back to LAN:
  `mentipy config mentipy.base_url --set auto`, then rebuild.
- **Check:** `grep -ho 'http[^}]*' mentipy-obj/*.pdf_tex | sort -u`
  shows the address the PDF will carry.

## In the lecture

1. Run `mentipy present` from the deck's directory (or `--store`). It
   is `mentipy serve` plus a bare `mentipy watch` in one terminal: it
   starts the server, then shows the tally of the question the
   lecturer has open. It takes serve's options and watch's
   `--interval`, `--window` and `--pin-heat`, and keeps serve's
   start-up lines and any server warnings in a banner, and opens the
   admin index in the browser (`--no-open` to skip; the command is
   `--open-with` or `mentipy.open_command`, `none` turns it off).
   Ctrl-C stops both. Use `mentipy serve` alone when the tally should not be on this
   screen. Off the LAN, add `--public ssh` (reads
   `mentipy.ssh_tunnel`) or `--public` (UPnP). The banner then holds
   the admin link, so keep that terminal off the projector. The QR
   codes must carry the address the students reach (see "Where the QR
   codes point").
2. **Recompile after the first `serve`** if the address changed: it
   rewrites the QR images and their sidecars.
3. **Pacing** (on by default, `--no-lock` turns it off):
   - A question opens for the students when the lecturer opens its
     results page on the server machine (admin). A `lock=False`
     question opens with the one before it.
   - The results page's floating nav row has Previous, Skip and Next.
     A skipped question stays closed until Reopen on its page.
   - Latecomers go to `/active`, or scan any QR code: one the lecturer
     has passed redirects them to the current question, and one not yet
     reached shows a waiting page.
4. **Results:**
   - `--results` sends students to the live tally after answering;
     `results=` overrides that per question.
   - Watch the tally in `present` (or a bare `mentipy watch`, with
     `--server URL` when the server runs elsewhere), and refresh the
     projected results page only when most have answered, so the room
     does not see the results early. For one question, use
     `mentipy view PREFIX` or `mentipy watch PREFIX`
     (`--window session|hour|day|all`).
   - Afterwards, `mentipy export PREFIX`.
5. **Admin can steer the room** (opening, skipping). Admin is a request
   from the server machine. Under `--public ssh`, students arrive
   through the tunnel and would look local, so a token is required.
   `serve`/`present` then prints an `/?admin=<token>` link: open the lecturer's
   tab through it, and never show it on the projector. Any other tunnel
   that makes students look local hands them the room.

## Checks before the lecture

- `mentipy list --store mentipy.json` lists the questions in slide
  order. Their prefixes must match the ones printed under the QR codes.
- Open every question's form on a phone-width window. The options
  should sit right under the prompt, the context below them, and code
  spans should render as code.
- The notes PDF contains no poll URL:
  `pdftotext notes.pdf - | grep -c <host>` gives 0.

## Pitfalls

- Never combine `\pause` with PythonTeX content in one frame. In a frame
  with overlays, register the question at top level with
  `write_snippet(name, latex)` and `\mentipyinput{name}` it in the
  frame. See `references/beamer-decks.md`.
- Never copy the QR sidecar's URL into literal text: the copy freezes
  while the QR image keeps following the server. Restyle the caption
  through `\mentipyqrcaption` instead.
- **Language.** Mentipy ships English and Swedish for the slide
  labels and the web pages. Check `mentipy latex` for the installed
  version: older releases print English only, and a deck then needs
  the string-replacing wrapper in `references/beamer-decks.md`.
  - A deck sets its language once, with `"locale": "sv"` in the
    shared keywords (every helper takes `locale=`, newer than 0.14:
    check that the deck venv's `mentipy latex` lists it). The helper
    records it with the question, so the server shows that question's
    pages in it.
  - Otherwise set `mentipy.locale`
    (`mentipy config mentipy.locale --set sv`). `serve`/`present
    --locale` overrides both for one run, for every question.
  - A changed locale reaches the slides only when PythonTeX reruns,
    which is always with the deck Makefile's `--rerun=always`.
  - To reword one label, put `\providecommand{\mentipychooseone}{}`
    and then `\renewcommand{\mentipychooseone}{...}` in the preamble.
    `mentipy latex` lists the macro names.

## References

- `references/beamer-decks.md`: polls in a didactic Beamer deck. It
  covers the shared `pycode` block (`layout="auto"`, `environment=""`,
  no `base_url`), the label wrapper for older releases, and
  placement with overlays. It also covers the notes' flat layout, the
  QR caption, and the deck checks.
