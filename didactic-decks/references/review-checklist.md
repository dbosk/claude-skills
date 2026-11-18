# Checks before a deck is reviewed

Run every check. `scripts/build_deck.sh` automates all but the ones that
need a human eye (contact sheets, reading the pages, the pages the
margin-note check warns about).

Contents: [The numeric checks](#the-numeric-checks) ·
[Tangled examples](#tangled-examples) ·
[Bibliography](#bibliography) · [Reading the pages](#reading-the-pages) ·
[Margin notes](#margin-notes) ·
[Clipped and overflowing verbatim lines](#clipped-and-overflowing-verbatim-lines) ·
[Overfull lines in the notes](#overfull-lines-in-the-notes) ·
[Transcripts](#transcripts) ·
[Known harmless](#known-harmless)

## The numeric checks

The commands name the main edition's notes job and `ltxobj`. Run each for
every job: `slides`, and in a bilingual deck `notes-sv` and `slides-sv`,
whose files are in `ltxobj-sv/`.

| Check | Command | Threshold |
|---|---|---|
| LaTeX errors | `LC_ALL=C grep -a -c '^!' ltxobj/notes.log` | 0, both jobs |
| Unresolved references | `pdftotext notes.pdf - \| grep -c '??'` | 0, both jobs |
| Empty citations | `LC_ALL=C grep -a -c 'empty citation' ltxobj/notes.log` | 0, both jobs |
| Overfull vbox on slides | `LC_ALL=C grep -a -c 'Overfull .vbox' ltxobj/slides.log` | 0 |
| Overfull lines in the notes | `scripts/check_overfull.py --pdf notes.pdf ltxobj/notes.log` | none over 5pt |
| Minted placeholders | `pdftotext ltxobj/slides.pdf - \| grep -c MINTED` | 0 |
| PythonTeX instance skew | `wc -l ltxobj/notes.pytxcode ltxobj/slides.pytxcode` | nearly equal (per edition: `ltxobj-sv/*-sv.pytxcode`) |
| Transcripts in the PDF | `scripts/check_transcripts.py <deck dir> notes` (or `notes-sv`, read in `ltxobj-sv/`), right after building that job | every run has a non-empty transcript of its own program, and the job's last pass read its own PythonTeX run's output |
| Rerun messages | `LC_ALL=C grep -a -c 'Rerun to get\|undefined references\|run Biber' ltxobj/notes.log` | 0 after convergence |
| Line length | `awk '{ sub(/[ \t]*% sync [A-Za-z]+=[^%]*$/, "") } length > 79' contents.nw abstract.tex` (a trailing `% sync` stamp does not count) | no output |
| Languages in step (bilingual) | `python3 "$(kpsewhich didactic-sync.py)" contents.nw abstract.tex ...` (the deck's own `.nw` and `.tex`) | exit 0 |
| Manual page breaks | `grep -nw -e needspace -e pagebreak -e newpage -e clearpage -e enlargethispage -e nopagebreak -e goodbreak -e filbreak contents.nw` | no output |

Quote the grep pattern in **single** quotes, or use `grep -a -c "Overfull
\\\\vbox"`. In double quotes, `grep "Overfull \vbox"` matches nothing,
because the shell eats the backslash and `\v` never reaches grep.

`LC_ALL=C grep -a` is needed because the logs are not valid UTF-8 and grep
otherwise refuses to match in them.

An `Overfull \vbox` on a slide is content falling off the bottom of the
frame. On the notes it is ordinary typesetting and not a defect.

A manual page break in `contents.nw` is a defect whatever the page looks
like (`floats-and-margins.md`, "No manual page breaks"): remove it, and
if the page then looks poor, fix the content (move or reword prose,
shorten, split or re-anchor a note), not the break.

## Tangled examples

Every tangled program must run, and must be black-clean.

### Running them

**The build has already run every program that carries a `\runpython`**,
with the input the deck feeds it. For those, the check is not to run them
again but to read the transcripts in the notes against the tangled files
they claim to run. `runpython-and-output.md` has the recipe for forcing
PythonTeX to re-run when only a chunk changed.

To run one by hand, take its input from the `\runpython` call rather than
guessing. `python3 examples/x.py < /dev/null` reports a false failure for
every program that reads input, and in a deck about exception handling
that is typically all of them. Collect the values first:

```bash
grep -o 'stdin={[^}]*}' contents.nw
```

Then feed them in the order they appear, one per prompt:

```bash
printf '%s\n' Malvina 1927 | python3 examples/x.py
```

A program with no `\runpython` and no `stdin` is run bare. The loop for a
whole deck first collects the files the build already ran, then runs only
the rest. Flatten the source first: a `\runpython` call routinely wraps
over two lines, often with a `%` after the options, so a line-oriented grep
misses it and the pattern allows `%` and spaces before the file name.

```bash
ran=$(tr '\n' ' ' < contents.nw \
      | grep -o '\\runpython\(\[[^]]*\]\)\?%\? *{[^}]*}' \
      | sed 's/.*{//;s/}$//' | sort -u)
for f in examples/*.py; do
  grep -qxF "$f" <<< "$ran" && continue   # the build ran it: read its transcript
  python3 "$f" < /dev/null || echo "FAILED: $f"
done
```

Measured on a deck whose seven programs all read input, `$ran` holds all
seven and the loop runs nothing. That is the correct answer: the check
there is to read the transcripts.

### black

```bash
black --check examples/
```

**black honours the `.gitignore` at the git root, and a deck repository
ignores `examples/`**, so this command can answer "No Python files are
present to be formatted. Nothing to do" and exit 0 having checked
nothing. Read its count: it must match the number of tangled `.py` files.
If it does not, pass the files explicitly:

```bash
find examples -name '*.py' -type f | wc -l
black --check $(find examples -name '*.py' -type f)
```

`build_deck.sh` always passes the file list explicitly and prints the
count it checked, for this reason.

Hand-written activity inputs that a deck *reads* rather than presents are
exempt from `black --check`; exclude them by path (`build_deck.sh
--exempt GLOB`).

Confirm that `examples/` holds nothing but generated files:

```bash
git status --short --ignore-submodules=all .
```

Never edit `contents.tex` or anything in `examples/`; both are generated.

## Bibliography

Run the `backing-claims` checkers on `ltnotes.bib`:

```bash
python3 ~/.claude/skills/backing-claims/scripts/check_provenance.py ltnotes.bib
python3 ~/.claude/skills/backing-claims/scripts/check_metadata.py ltnotes.bib
```

Before calling the appendices done, run the **claim audit**: list every
imperative the deck makes ("follow the style guide", "use descriptive
names"), because each asserts a benefit and that benefit is an empirical
claim to back two-sidedly. An appendix sentence saying the deck "makes no
claims that required a search" is itself a claim, and must be tested the
same way.

## Reading the pages

Render and read **every** slide and **every** notes page. Contact sheets
first, then close reads of anything that looks wrong:

```bash
pdftoppm -r 40 -png ltxobj/slides.pdf /tmp/deck/slide
montage /tmp/deck/slide-*.png -tile 5x4 -geometry +2+2 /tmp/deck/sheet-%d.png
```

Also check for slides that came out nearly blank, which is what a broken
frame looks like from the outside:

```bash
n=$(pdfinfo slides.pdf | awk '/Pages/{print $2}')
for p in $(seq 1 "$n"); do
  w=$(pdftotext -f "$p" -l "$p" slides.pdf - \
      | grep -v "AUTHOR\|INSTITUTE\|TITLE" | tr -s ' \n' ' ' | wc -w)
  [ "$w" -lt 6 ] && echo "blank-ish: $p"
done
```

The `grep -v` strips the running head and foot, which appear on every
slide; pass the deck's own author, institute and title.

## Margin notes

Every margin footnote must print on the page that carries its marker:
beside its line or, if it doesn't fit there, at the foot of that page
(didactic v2.19 sets it there whole, in the text's width, and logs
nothing). A note didactic had to carry to a later page is named in the
log and passes the check, but is still worth fixing in the content: a
shorter note, the citation moved earlier, the prose moved or reworded;
never a page break (`floats-and-margins.md`, "No manual page breaks").

The mechanical check, per page, compares the superscript markers in the
body against the note numbers in the margin. `build_deck.sh` runs it on
the notes; by hand:

```bash
python3 ~/.claude/skills/didactic-decks/scripts/check_margin_notes.py \
        ltxobj/notes.pdf [--log ltxobj/notes.log | --margin-x BP]
```

It takes the margin column from the line `didactic-margin: odd=… even=…
width=…` that didactic writes to the notes log (found beside the PDF or in
`ltxobj/` by default; a log counts only when it shipped out as many pages
as the PDF has, so a stale `notes.log` left beside the PDF by an old build
is passed over with a NOTICE, and when no log matches the check refuses
with exit 2). Without that line it guesses the column from the
word positions and prints GUESSED; the guess has failed on code reaching
into the 4pt gutter and on notes with few margin words, so give a PDF
copied away from its build `--log` or `--margin-x`. Exit 1 is a note
printed away from its marker that nothing in the log names (DEFECT), or a
warning classed UNFORESEEN, LOST or INSTALL below; a note off its page
that a warning names (CARRIED) exits 0. Exit 2 means nothing was checked
(no column, no margin note found, or only another build's log) and is a
failure, not a pass. A deck
that really has no margin notes says so in a committed `.no-margin-check`
(first line: why), which makes `build_deck.sh` skip the check;
`--no-margin-ok` does the same for one manual run. WARNING lines (a
marker or note with no partner nearby) name pages to read by eye. A note
up to three pages after its marker that nothing names is a DEFECT; when a
marker in between has the same or a lower number (a new chapter, or
another note's number) the pairing is unsure and stays a WARNING, which
then says where the note with that number is. Deferrable notes
(`\ltnote`), which marginfix splits or moves on with its own warning
(`Package marginfix Warning: Deferrable margin note … moved from page P
to the next`), have no number: the check doesn't see them.

It also reads didactic's warnings about notes, joining the lines TeX
broke them over, and classes each:

| Line | Warning (`Package didactic Warning: …`) | Verdict | What the author does |
|---|---|---|---|
| CARRIED | `Margin note called out at F:L on page P is set on page Q: <why>` | passes; covers that one note off its page | shorten the note or move its callout so it fits beside its line or at the foot |
| PAST FOOT | `… runs <d>pt past the foot of the margin: …` | passes | nothing needed; shorten a note above it if the page looks crowded |
| LOOK | `Footnote called out at Y is set at the foot of page P before the one called out at X, which is still waiting in the margin`; `TeX ended page P before the line of the footnote … page P is <n> lines short`; a footnote in multicols set at the foot of another page; `Can't read the callouts of page P`; `With \nofiles …` | passes | read the page; reword or move the text near the callout |
| UNFORESEEN | `… is set on page Q (found from the last run): nothing said so in that run` | fails | two known causes give this wording: a foot that mixes didactic's footnotes with LaTeX's own (`\footnotesatfoot`, or multicols with memoir), taken on by a later line (didactic#104; move that footnote), and a note carried across `\mainmatter` from page i to page 1 (didactic#120; move its callout off the front matter's last page). Otherwise rebuild from clean, and if it stays, report it to didactic with the log |
| LOST | `… wasn't printed (found from the last run)`; `A footnote in … multicols … is lost`; `A margin note in multicols is lost` | fails | move the note out of the multicols, or out of the note it is nested in; under TeX Live's marginfix 1.2, shorten a note taller than the margin |
| INSTALL | `Can't place margin notes that don't fit: …`; `Couldn't patch \<name>, …` | fails | didactic and marginfix don't match: install the two together |
| NOTICE | `<n> footnote(s) wasn't/weren't plain: …`; `Can't patch memoir's side captions …` and `Can't patch noweb's code chunks …` (features other than the notes' placement); any other didactic warning that mentions a note | information | nothing, unless a note or that feature looks wrong |

A note found off its marker's page that no warning names is a DEFECT
(exit 1). A warning covers only a note of its kind: CARRIED one in the
margin of page Q, except a carried margin note without a number ("it
doesn't fit beside its line, and only a footnote can go to the foot"),
which covers none; the multicols footnote one at the foot of page Q. The
warnings' page numbers are as printed; the script matches them against
the PDF's page labels (with `pdftk`, so roman iv and arabic 4 stay apart)
or, without labels, through the log's shipout markers. The output ends
with a `to look at:` count of the CARRIED, PAST FOOT and LOOK lines.

A log from a didactic older than 2.19 (its `Package: didactic … v2.18.1`
line says which) was made under marginfix 1.6's rule and is judged by it,
as when it was built: a note on the next page passes when a
`marginfix-spill: page=P to=Q intended` or `… capped` line names it, an
`… unresolved` spill fails, and `marginfix-yield` lines are NOTICEs. The
first line of output after the column says which rule was applied.

By hand, for one page: `pdftotext -f N -l N notes.pdf -` and read the
superscript numbers in the text against the numbers in the margin block.

## Clipped and overflowing verbatim lines

minted (fvextra) sets every verbatim line as `\hbox to \linewidth{<line>\hss}`;
the `\hss` absorbs any excess, so a program or transcript line that runs
past a frame's edge or out of the notes' text block logs **no** Overfull
`\hbox`, and `check_overfull.py` cannot see it. Run

```bash
python3 ~/.claude/skills/didactic-decks/scripts/cutcheck.py <deck dir> slides notes
```

after the build. It reports

- `CUT`: a printed line that is a strict prefix of a tangled program or
  transcript line (clipped clean off a slide; found in six of eleven
  decks in one campaign, 2026-09-16);
- `OVER`: a word whose box passes the page width;
- `OVERPRINT` (notes): word boxes that overlap where one reaches into the
  margin column, i.e. a line printed over a margin note, or two notes
  over each other. The column comes from the log's `didactic-margin:`
  line;
- `MARGIN` (notes): a run of words on a body line ending more than 5pt
  past the text block (the column's edge less the 7pt `marginparsep`),
  with or without a note beside it. A program-output line of 102
  characters ran 50pt into the margin over a note (Variabler och
  utskrifter, 2026-11-16) and every other check passed; a notes line
  holds about 88 characters of the transcript font.

`MARGIN` skips lines it cannot judge: a line of a full-width block
(didactic's definitions, examples and wide code start about 20pt left of
the body and span the column on purpose; lines of the same display, at
most 19.5pt apart, count with it) and a line starting right of the text
block's middle (the right column of two programs side by side). An
overflow there, or one of 5pt or less, goes unreported: read those
pages. It also reports prose lines more than 5pt too wide, which
`check_overfull.py` reports from the log as well. On the eleven decks
built 2026-11-16 it reports nothing; on older builds the hits checked
were real (the `{"name": …}` literal below, a quotation running into a
note; bibliography lines and URLs that `check_overfull.py` also lists).

## Overfull lines in the notes

An inline code literal or a URL that cannot be broken runs out of the
text block, possibly over a margin note, and no other check sees it
(Praktiska v20, page 14: `{"name": …}` 67pt into the margin, every check
green). `build_deck.sh` runs `scripts/check_overfull.py` on the notes log
and fails on any `Overfull \hbox` more than `--overfull-pt` (default 5pt)
too wide; `--draft` prints the same list and passes, for a quick compile
for review. Each line reads

```
67.2pt too wide, page ~14, ./contents.tex:864 (paragraph)
    Jämförelse: upp-slags-lis-tor mot Item-klass Med upp-slags-lis-tor ( )
```

- The file is the one open when TeX logged the line, usually the woven
  `contents.tex`, whose line numbers are not `contents.nw`'s: grep the
  `.nw` for a word of the quoted text (the hyphens are TeX's break
  points; `( )` is a nested box, here the `\mintinline`). A range like
  `893--1, begun in another file` is a paragraph that started in
  `contents.tex` and ended in an `\input` transcript.
- The page is the one being built when TeX broke the paragraph; it can
  be the next one.
- Whether the line is in a margin note the log does not say.
- The threshold sits under memoir's 7pt `marginparsep` (the summary
  prints it): a body line more than that too wide runs into the margin
  column; at 5pt it ends within 2pt of it, visible as a nub on the edge.
- `not in the PDF (not counted)`: TeX set the box and threw it away (a
  `<presentation>` frame with a wide column gave 335pt). The check looks
  for the line's longest stretch of text on the page and its neighbours;
  a line with too little text to tell (a table, code) always counts.

Typical causes and fixes: a `\mintinline` or `[[...]]` literal at a line
end (reword so it falls mid-line, or break the literal), a URL or DOI in
a bibliography entry or provenance paragraph (biblatex does not break a
URL between letters by default; its counters `biburllcpenalty` and
`biburlucpenalty`, e.g. `\setcounter{biburllcpenalty}{7000}` in the
preamble, allow it), a wide table (narrow a column).

## Transcripts

Every `\runpython` must leave its transcript in the PDF.
`scripts/check_transcripts.py <deck dir> [notes|slides]` reads each run
instance from `ltxobj/<job>.pytxcode` (`ltxobj-sv/` for a bilingual
deck's `-sv` jobs), checks that the job's last pass read its
`py_*.stdout` (in `ltxobj/<job>.fls`), and that the transcript file it
names (`didactic_output_<hash>.txt`, `didactic_pair_…`) is not empty
and, for a `showcommand` run, names that program on its command line.
It also checks provenance: the job's last pass must not have read the
output of another job's PythonTeX run that runs other code at an
instance both have. `build_deck.sh` runs it on each job right after
building it.

Why: both jobs share `ltxobj/`, and the second job's PythonTeX run
deletes or rewrites the first job's `.stdout` files. An incremental
build that skips PythonTeX then typesets **nothing** where the
transcripts were, with no `??`, error or `MINTED` (Klasser och objekt,
2026-11-16: 16 of 27 transcripts gone, all checks green;
`build-and-gotchas.md`, "The shared PythonTeX cache"). Its WARNING lines
name files changed after the job's last pass: that PDF is right, but its
next incremental build will not be; rebuild clean before trusting one.

It cannot see a stale but plausible transcript (old output of the right
program): read the transcripts against the programs. Another program's
output in a run without `showcommand` it sees only through provenance,
which relies on file mtimes (a tree copied without them misleads it).

## Cross-deck premises

When a deck says what an earlier deck showed, or reuses its program, read
that deck's *current* `contents.nw`: the premise drifts when the earlier
deck is revised. The age program in *Variabler och utskrifter* came to
read its values with `input()`, and the input deck still opened on
"hittills stod värdena i koden" (author, 2026-09-16: "We updated this one
to include an input"). Grep the earlier deck for the program and the
claim; fix the premise, not the pointer's wording.

## Floats in the appendices

Bilaga A's question table is declared right after the paragraph whose
`\Cref` names it; declared at the chapter's end it prints two pages after
its reference (author: "Why is this table here at the end when it's
referenced at the first page?"). The same holds for every table and
figure in `sokprotokoll.tex`.

## Known harmless

- A permanent two-cycle of "Rerun to get cross-references right" caused by
  a margin citation at a page boundary, **as long as `??` is 0**.
- `Overfull \hbox` warnings in the notes up to 5pt: ordinary
  typesetting (wider ones fail, see "Overfull lines in the notes").

- **Side-by-side overflow** (didactic ≥ 2.7.1): `grep -c 'than its column' ltxobj/*.log` must be 0 for both jobs.
- **Margin check on a long book** that has no `didactic-margin` line in its log (the guess fails on long hit-list tables): split with `pdftk <pdf> cat A-B output part.pdf` into ~100-page ranges; never `pdfseparate` (one file per page fills the `/tmp` quota and killed two book builds, 2026-10-04).
