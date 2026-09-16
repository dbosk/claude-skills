# Checks before a deck is reviewed

Run every check. `scripts/build_deck.sh` automates all but the ones that
need a human eye (contact sheets, reading the pages, margin-note pairing —
for which `scripts/check_margin_notes.py` does the mechanical part).

Contents: [The numeric checks](#the-numeric-checks) ·
[Tangled examples](#tangled-examples) ·
[Bibliography](#bibliography) · [Reading the pages](#reading-the-pages) ·
[Margin notes](#margin-notes) · [Known harmless](#known-harmless)

## The numeric checks

| Check | Command | Threshold |
|---|---|---|
| LaTeX errors | `LC_ALL=C grep -a -c '^!' ltxobj/notes.log` | 0, both jobs |
| Unresolved references | `pdftotext notes.pdf - \| grep -c '??'` | 0, both jobs |
| Empty citations | `LC_ALL=C grep -a -c 'empty citation' ltxobj/notes.log` | 0, both jobs |
| Overfull vbox on slides | `LC_ALL=C grep -a -c 'Overfull .vbox' ltxobj/slides.log` | 0 |
| Minted placeholders | `pdftotext ltxobj/slides.pdf - \| grep -c MINTED` | 0 |
| PythonTeX instance skew | `wc -l ltxobj/notes.pytxcode ltxobj/slides.pytxcode` | nearly equal |
| Rerun messages | `LC_ALL=C grep -a -c 'Rerun to get\|undefined references\|run Biber' ltxobj/notes.log` | 0 after convergence |
| Line length | `awk 'length > 79' contents.nw abstract.tex` | no output |

Quote the grep pattern in **single** quotes, or use `grep -a -c "Overfull
\\\\vbox"`. In double quotes, `grep "Overfull \vbox"` matches nothing,
because the shell eats the backslash and `\v` never reaches grep.

`LC_ALL=C grep -a` is needed because the logs are not valid UTF-8 and grep
otherwise refuses to match in them.

An `Overfull \vbox` on a slide is content falling off the bottom of the
frame. On the notes it is ordinary typesetting and not a defect.

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
over two lines, so a line-oriented grep misses it.

```bash
ran=$(tr '\n' ' ' < contents.nw \
      | grep -o '\\runpython\(\[[^]]*\]\)\?{[^}]*}' \
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

Every margin footnote must print on the page that carries its marker. A
note pushed to the next page is a defect, fixed by layout: a shorter note,
the citation moved earlier, or `\needspace`.

The mechanical check, per page, compares the superscript markers in the
body against the note numbers in the margin:

```bash
python3 ~/.claude/skills/didactic-decks/scripts/check_margin_notes.py \
        ltxobj/notes.pdf
```

By hand, for one page: `pdftotext -f N -l N notes.pdf -` and read the
superscript numbers in the text against the numbers in the margin block.

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
- `Overfull \hbox` warnings in the notes: ordinary typesetting.
