# Provenance of this template

The five build files (`Makefile`, `slides.tex`, `notes.tex`,
`preamble.tex`, `.gitignore`) were copied from the build template deck and
genericised: title, author and institute replaced by placeholders,
`NOWEB_SUFFIXES` and `NOTANGLEFLAGS` reduced to the Python case, and the
language-specific blocks marked `% PROJECT:`.

| Field | Value |
|---|---|
| Source | `~/devel/edu/intropy/modules/helloworld/slides` |
| Branch | `worktree-literate-deck-pattern` |
| Commit | `280ee14` (last commit touching that directory) |
| Copied | 2026-09-07 |

`abstract.tex`, `contents.nw`, `sokprotokoll.tex` and `README.md` are
written for this template; they are skeletons, not copies.

## Re-syncing after the source deck's build wiring changes

```bash
diff -ru ~/.claude/skills/didactic-decks/assets/deck-template \
         ~/devel/edu/intropy/modules/helloworld/slides \
  | grep -v '^Only in'
```

Read the diff and carry over changes to the build wiring only. Content
differences (title, learning objectives, chunks, appendix chapters) are
expected and must not be copied back. After re-syncing, update the Commit
and Copied rows above.
