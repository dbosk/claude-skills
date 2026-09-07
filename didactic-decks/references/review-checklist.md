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

Every tangled program must run, and must be black-clean:

```bash
black --check examples/
for f in examples/*.py; do python3 "$f" < /dev/null || echo "FAILED: $f"; done
```

Hand-written activity inputs that a deck *reads* rather than presents are
exempt from `black --check`; exclude them by path.

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

## Known harmless

- A permanent two-cycle of "Rerun to get cross-references right" caused by
  a margin citation at a page boundary, **as long as `??` is 0**.
- `Overfull \hbox` warnings in the notes: ordinary typesetting.
