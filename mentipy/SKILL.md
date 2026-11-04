---
name: mentipy
description: Author, build and run live classroom polls with Mentipy (self-hosted, QR codes on Beamer slides, PythonTeX helpers in mentipy.latex). Use proactively when (1) writing or editing a poll with mc, open_text, scale, ranking, word_cloud, pin_text or pin_image, or a deck or handout that imports mentipy, (2) giving a poll its program or data with context=, file_snippet or file_download, (3) a build fails on `import mentipy`, a stale venv, or QR codes or prefixes that changed, (4) running a poll in a lecture with mentipy present, serve, slides_command, --public, Skip, /active, or reading answers with mentipy list, view, watch or export, (5) the user mentions Mentipy, mentipy.json, mentipy-answers.jsonl, mentipy-obj, \mentipybasedir or live polls, or upgrades to 1.0. Load BEFORE writing the first poll. Owns the API, the build and the lecture; why and when to poll stays in try-first-tell-later and variation-theory, and the frame layout of a didactic deck is in references/beamer-decks.md here.
---

# Mentipy

Mentipy registers a question while the document compiles (a PythonTeX
block calls a helper), writes its QR code, and returns the LaTeX for
the slide or the handout. `mentipy present` (or `serve`) runs the poll
from the lecturer's machine, and the slides are built while it runs.
The questions live in the store, `mentipy.json`, and the answers beside
it in the log `mentipy-answers.jsonl`.

This describes Mentipy 1.0. Install the tool with
`uv tool install --python 3.11 'mentipy[public,wordcloud]'`, which
brings Python 3.11 along. If pipx has `mentipy`, run
`pipx uninstall mentipy` first, since uv refuses to replace the
executable. A deck's venv has no extras, so run `mentipy serve` outside
an activated `.venv` when `--public` UPnP or the word cloud needs them.
Upgrading a machine or a deck from an earlier version has an order: see
"Upgrading to 1.0".

## First: ask the installed Mentipy

Never write helper calls from memory. The API grows with each release,
and `mentipy latex` prints the installed version's reference: every
helper's signature, the per-question keywords (`next`, `results`,
`lock`, `context`), the context helpers, the inline-code rule, the
shared keywords and every config key. Read it first, plus
`mentipy <command> --help` for the CLI.

A deck compiles with the mentipy in **its own venv**, not with the
tool's. Check that venv's version
(`.venv/bin/python3 -m pip show mentipy`) before relying on a feature;
`mentipy latex` describes the tool's one.

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
- The same question asked twice in one deck (a poll before and after an
  explanation) is also one pool, so both rounds show together, and it
  has **one stop in the deck, at its last place**. In X, Y, A, B, C, A,
  Next goes from Y straight to B, and a student scanning A's QR code at
  its first place waits. Open that first ask from the admin index. It
  then stays open, so the second ask opens nothing new, and the toned
  row and `/active` stay on the question before it. A deck wanting two
  separate results should word the two asks differently.

## The build

PythonTeX's `python3` cannot import the tool's mentipy, so each deck (and a
bound book) has its own venv, which the Makefile makes. It is never a
manual step. A version stamp upgrades an existing venv once when the
deck needs a newer Mentipy. The snippet goes in a Makefile with `all:`
first, `TEX_PYTHONTEX=yes` and `include makefiles/tex.mk`, and the
preamble needs `\usepackage{pythontex}`, `\setpythontexoutputdir{.}` and
`\setpythontexworkingdir{..}`. **Without those two lines the build
succeeds with empty poll frames and no store:**

```make
MENTIPY_VENV=	$(CURDIR)/.venv
PYTHONTEXFLAGS=	--interpreter python:${MENTIPY_VENV}/bin/python3 --rerun=always

${MENTIPY_VENV}/bin/python3:
	mentipy init --venv ${MENTIPY_VENV}

MENTIPY_VERSION=	1.0
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
# Without this, make finds the PDF up to date and the old QR codes stay.
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
- Raise `MENTIPY_VERSION` when the deck starts using a newer feature
  or needs a fix: a new release never reaches an existing venv by
  itself. The version must be on PyPI, or every fresh build fails at
  the `pip install`.
- **To make the venv without the tool,** use
  `uv venv --seed --python 3.11 .venv`. `--seed` adds pip, which
  `mentipy init` and the recipe call.
- **Git and the answers.** Gitignore `.venv/`, `mentipy-obj/`,
  `mentipy-images/`, `mentipy.json` and `mentipy-answers.jsonl` (what
  students wrote). A project that deliberately tracks the store must
  also `git add mentipy-answers.jsonl`: otherwise `git commit -a` leaves
  the answers out and `git clean -fd` deletes the only copy. Then set
  `*-answers.jsonl merge=union` in `.gitattributes`. `serve` and
  `present` warn about both mistakes at the start.
- **The log and the images follow the store's name.** Rename all three
  together (`lecture1.json`, `lecture1-answers.jsonl`,
  `lecture1-images/`), and copy all three to move a store. To start a
  deck over, delete the store and the log.
- **Rebuilding an unchanged deck leaves the store byte-identical,** and
  questions dropped from the deck are not rewritten. Each PythonTeX run
  links its questions (`registered_after`).
- **Decks built with `mentipy render`** continue the store's latest run
  by default, so every rebuild changes the store and keeps questions
  dropped from the end. Pass `--new-run` on the deck's first question
  to replace the old run. Build such a deck serially, with
  `.NOTPARALLEL:` or one recipe, because `make -j` makes the order
  depend on timing. Do not mix the two paths in one deck: questions
  rendered before PythonTeX runs leave the navigation. A render-built
  deck that asks a question twice loses the questions before its first
  place from the navigation, with or without `--new-run`.
- **A Python upgrade kills the venv.** Its `python3` then fails with
  "No module named 'encodings'". Delete `.venv` and run `make`.
- In a book of decks, use `\usepackage{mentipy}` and
  `\mentipybasedir{auto}`. They resolve each deck's
  store and QR directory under `\subimport`. See
  `didactic-decks/references/book-binding.md`.

## Where the QR codes point

**Start the server first, then build.** While a server runs on the store,
builds use the address it serves, whichever mode it is in: `serve` or
`present` records it in `mentipy-obj/.served-base-url` (the configured
`qr_dir` beside the store; a deck's `qr_dir=` does not move it), and the
deck's helpers read that. So the same steps work on the LAN and with
`--public ssh`, with nothing to configure. `mentipy present` with
`slides_command` does this order by itself.

- **Never hard-code `base_url` in a deck.** It wins over the served
  address, so it pins every code to one address and serving in the
  other mode is then impossible.
- **Without a server,** a build uses the `base_url` setting, else the
  LAN address at compile time. Don't set `base_url` to follow a mode:
  it is for an address the phones can always reach. Back to LAN with
  `mentipy config base_url --set auto`.
- **Stopping the server removes the record,** on Ctrl-C, a plain `kill`
  or a closed terminal. The codes keep its address until the next
  build. After `kill -9`, Ctrl-\ or a power cut, builds keep using the
  dead address, without a warning, until a server starts again or
  `mentipy-obj/.served-base-url` is removed.
- **A build started by an older deck venv** writes the configured
  address whatever the server serves, so the deck venv must be 1.0.
- **Check:** `grep -ho 'http[^}]*' mentipy-obj/*.pdf_tex | sort -u`
  shows the address the PDF will carry.

## Upgrading to 1.0

1.0 keeps each setting as a top-level key (`base_url`, not
`mentipy.base_url`), and neither reads nor converts the old `mentipy`
section. The steps have an order:

1. `uv tool upgrade mentipy`, and check `uv tool list`. A tool on an
   older Python reports nothing to upgrade: use
   `uv tool upgrade --python 3.11 mentipy`.
2. `mentipy config mentipy` shows the old values; set the ones still
   wanted under their new names. `mentipy latex` lists the keys. Any
   unset key prints a harmless `KeyError` traceback.
3. In each deck, raise `MENTIPY_VERSION` to 1.0 and run `make`, or run
   `mentipy init`, then check `.venv/bin/python3 -m pip show mentipy`.
   On a `.venv` older than Python 3.11, **`mentipy init` reports success
   and stays on 0.17**, and `make` stops with a pip error about the
   Python version. Either way, delete that `.venv` and build again. A
   deck left at `0.17` splits: an existing venv stays on 0.17 while a
   fresh clone gets 1.0, with different QR addresses.
4. In each deck, add `mentipy-answers.jsonl` to `.gitignore`, or
   `git add` it if the store is tracked. Check that the Makefile has the
   `$(wildcard mentipy-obj/Q-*.pdf_tex)` line, or a rebuild after the
   server starts does nothing.
5. Once no deck needs the old section,
   `mentipy config mentipy --set ""`.

It is not a gradual change. A deck venv on 0.17 reads only the old
section, and its `view`, `watch` and `export` see none of the answers in
the log (`Responses: 0`; `export` writes an empty list, which overwrites
a good export if sent to the same file). No answer is harmed: answers
from before stay in `mentipy.json` and are read from there. Beware the
two silent mistakes: `mentipy config mentipy.base_url --set x` exits 0
and stores a value 1.0 never reads, and a value once stored under a
short name, which older versions ignored, now takes effect.

## In the lecture

1. Run `mentipy present` from the deck's directory (or `--store`). It
   is `mentipy serve` plus a bare `mentipy watch` in one terminal: it
   starts the server, then shows the tally of the question the
   lecturer has open. It takes serve's options and watch's
   `--interval`, `--window` and `--pin-heat`, and keeps serve's
   start-up lines and any server warnings in a banner, and opens the
   admin index in the browser (`--no-open` to skip; the command is
   `--open-with` or `open_command`, `none` turns it off, while an empty
   value only deletes the key). Use `mentipy serve` alone when the tally
   should not be on this screen. Off the LAN, add `--public ssh` (reads
   `ssh_tunnel`), when the banner holds the admin link, or `--public`
   (UPnP). Keep that terminal off the projector either way.
2. **Build and open the slides** with `slides_command` or
   `--slides-command`, for example
   `mentipy config slides_command --set "make slides.pdf && pdfpc -w both slides.pdf"`.
   It runs once the server is up, so the build gets the served address;
   the output goes to `slides-command.log` beside the served-address
   record. Join the steps
   with `&&`. Add `--no-slides` when restarting `present` during a
   lecture, or a second viewer opens. Without the command, build in
   another terminal after the server is up.
   - **A fatal LaTeX error deletes the PDF, even a good earlier one, so
     keep a copy.** It shows as `Slides FAILED`, and the viewer does not
     open.
   - **A `pycode` exception shows no failure:** the viewer opens a PDF
     whose poll frames are stale or empty. `present` adds
     `Slides may have failed` when the log has `Latexmk: Errors` or
     `Collected error summary`, but only for a build that ran, so a
     restart that `make` finds up to date opens that PDF silently. To
          make such a build fail, put
     `COMPILE.tex = ${PDFLATEX} ${LATEXFLAGS} -output-directory=${TEX_OUTDIR} $<`
     before the Makefile's `include`, and never `.DELETE_ON_ERROR:`. The
     failed build still rewrites the PDF, so a restart on the same port
     opens it until a source changes or is `touch`ed.
3. **Stopping.** Ctrl-C, a plain `kill` and closing the terminal all
   stop `serve` and `present` cleanly: the tunnel, the UPnP mapping and
   the address record go (a hung router can leave a mapping after a 30 s
   deadline; `nohup` keeps a server alive past the terminal). The slides
   command keeps running, so the viewer stays open. A build still running
   then writes the configured address: stop it with `kill -- -PID` (the
   banner has the pid) and start `present` again with the command.
4. **Answers are safe from builds.** They go to the log, which nothing
   rewrites, so a build during a lecture cannot lose one, and a student
   is thanked only after the answer was sent to the disk. A server that
   cannot write the log does not start. If a write fails during the
   lecture, the student is told it was not saved and to tell you.
5. **Pacing** (on by default, `--no-lock` turns it off):
   - A question opens for the students when the lecturer opens its
     results page on the server machine (admin). A `lock=False`
     question opens with the one before it.
   - The results page's floating nav row has Previous, Skip and Next.
     A skipped question stays closed until Reopen on its page.
      - Latecomers go to `/active`, or scan any QR code: one the lecturer
     has passed still shows its form, and its Next goes to the current
     question; a skipped one redirects to the current question; one not
     yet reached shows a waiting page.
   - The admin index (the server's root URL) lists `Current questions`,
     the deck as last built, and `Old questions` when a rebuild dropped
     or edited some. The toned row is the question the lecture is on. A
     question asked twice has one row, at its last place, so a deck
     A, B, C, A, D lists B first.
6. **Results:**
   - `--results` sends students to the live tally after answering;
     `results=` overrides that per question.
   - Watch the tally in `present` (or a bare `mentipy watch`, with
     `--server URL` when the server runs elsewhere), and refresh the
     projected results page only when most have answered, so the room
     does not see the results early. For one question, use
     `mentipy view PREFIX` or `mentipy watch PREFIX`
     (`--window session|hour|day|all`).
   - Afterwards, `mentipy export PREFIX`.
7. **Admin can steer the room** (opening, skipping). Admin is a request
   from the server machine. Under `--public ssh`, students arrive
   through the tunnel and would look local, so a token is required.
   `serve`/`present` then prints an `/?admin=<token>` link: open the lecturer's
   tab through it, and never show it on the projector. Any other tunnel
   that makes students look local hands them the room.

## Checks before the lecture

- `.venv/bin/python3 -m pip show mentipy` says 1.0 or newer.
- `grep -ho 'http[^}]*' mentipy-obj/*.pdf_tex | sort -u` shows the
  address being served.
- `mentipy list --store mentipy.json` lists the whole store in order of
  last registration: old questions stay, with no marking. Every prefix
  under a QR code must be there. For the deck as built, see
  `Current questions` on the admin index.
- Open every question's form on a phone-width window, with a server
  running. The options should sit right under the prompt, the context
  below them, and code spans should render as code. Opening a results
  page opens that question for the students, and a server restart locks
  it again.
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
  labels and the web pages.
  - A deck sets its language once, with `"locale": "sv"` in the
    shared keywords. The helper records it with the question, so the
    server shows that question's pages in it.
  - Otherwise set `locale`
    (`mentipy config locale --set sv`). `serve`/`present
    --locale` overrides both for one run, for every question.
  - A changed locale reaches the slides only when PythonTeX reruns,
    which is always with the deck Makefile's `--rerun=always`.
  - To reword one label, put `\providecommand{\mentipychooseone}{}`
    and then `\renewcommand{\mentipychooseone}{...}` in the preamble.
    `mentipy latex` lists the macro names.

## References

- `references/beamer-decks.md`: polls in a didactic Beamer deck. It
    covers the shared `pycode` block (`layout="auto"`, `environment=""`,
  no `base_url`) and placement with overlays. It also covers the notes' flat layout, the
  QR caption, and the deck checks.
