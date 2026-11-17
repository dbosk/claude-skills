# Provenance of this template

The build files (`Makefile`, `slides-body.tex`, `notes-body.tex`,
`preamble.tex`, `.gitignore`) were copied from the build template deck and
genericised: title, author and institute replaced by placeholders,
`NOWEB_SUFFIXES` and `NOTANGLEFLAGS` reduced to the Python case, and the
language-specific blocks marked `% PROJECT:`. `slides-body.tex` and
`notes-body.tex` are that deck's `slides.tex` and `notes.tex`.

| Field | Value |
|---|---|
| Source | `~/devel/edu/intropy/modules/helloworld/slides` |
| Branch | `worktree-literate-deck-pattern` |
| Commit | `280ee14` (last commit touching that directory) |
| Copied | 2026-09-07 |

The bilingual wiring is not from that deck, which is Swedish only: the
four thin edition drivers (`notes.tex`, `slides.tex`, `notes-sv.tex`,
`slides-sv.tex`), the per-edition output directory in the `Makefile`, the
languages of babel and cleveref, the stamped `\ensv` reference names in
`preamble.tex` come from a spike deck built with didactic v2.17
(2026-11-13) and were added on 2026-11-15. The translator set-up
(`\uselanguage`, `\languagepath`) was removed then too: didactic v2.17.1
does it; only the `\deftranslation` house terms stay. On 2026-11-16 the
stamps were rewritten for didactic v2.18 with `didactic-sync.py
--migrate` (keys `english=`/`swedish=`, hashes unchanged).

`abstract.tex`, `contents.nw`, `sokprotokoll.tex` and `README.md` are
written for this template; they are skeletons, not copies, and so are the
placeholders `ltnotes.bib`, `figs/example.png` and
`litteratursokning/claim-full.tex`.

## Re-syncing after the source deck's build wiring changes

```bash
cd ~/.claude/skills/didactic-decks/assets/deck-template
src=~/devel/edu/intropy/modules/helloworld/slides
diff -u slides-body.tex $src/slides.tex
diff -u notes-body.tex $src/notes.tex
for f in Makefile preamble.tex .gitignore; do diff -u $f $src/$f; done
```

Read the diff and carry over changes to the build wiring only. Content
differences (title, learning objectives, chunks, appendix chapters) are
expected and must not be copied back, and neither are the differences of
the bilingual wiring above (the source deck has one edition). After
re-syncing, update the Commit and Copied rows above.
