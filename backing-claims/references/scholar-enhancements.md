# `scholar` provenance support: shipped + future ideas

The provenance workflow ideas originally captured here were implemented in
`scholar` (issues #49–#53, repo `dbosk/scholar`). This file now records what
shipped and holds any future ideas.

## Shipped (use these; see `scholar-cookbook.md` for recipes)

| Issue | Capability | Command |
|-------|------------|---------|
| [#49](https://github.com/dbosk/scholar/issues/49) | Provenance-stub BibTeX export | `scholar search ... -f bibtex+prov` |
| [#50](https://github.com/dbosk/scholar/issues/50) | Reproducible `FOUND-VIA` for a paper | `scholar prov found-via <id>` |
| [#51](https://github.com/dbosk/scholar/issues/51) | Candidate `QUOTE` passages from a PDF | `scholar pdf quote <url> --claim "..."` |
| [#52](https://github.com/dbosk/scholar/issues/52) | Retraction / currency check (Crossref) | `scholar verify <session>` |
| [#53](https://github.com/dbosk/scholar/issues/53) | Provenance ⇄ notes round-trip | `scholar prov import/export <bib>` |

`-f bibtex+prov`, `pdf quote`, and `verify` ship in `scholar` ≥ 1.20; the `prov`
group landed shortly after. If `scholar prov` is unknown, run
`pipx upgrade scholarcli` (or reinstall from `~/devel/scholar`).

`scholar` uses noweb literate programming (`src/scholar/*.nw` are the source of
truth; activate the `literate-programming` skill before editing). Relevant
files: `src/scholar/cli.nw` (commands), `src/scholar/crossref.nw` (verify),
`src/scholar/pdf.nw` (quote), `src/scholar/notes.nw` (prov round-trip).

## Requested (in progress)

| Capability | Status | Interim |
|------------|--------|---------|
| `scholar sessions export --format table` — a classified session as an auditable LaTeX `longtable` (cited / supports / qualifies / adjacent / off-topic / pending, provider-duplicate merging, confidence per row, `--lang sv\|en`, `--label`, `--track`) for `\input` in a backing appendix | Spec sent to the scholar development session 2026-09-02 (from the intropy computational-thinking deck); add the issue/PR number here when known | `scripts/session_table.py` in this skill, same interface |

## Future ideas (not yet built)

When a new gap appears, offer to file it as a `gh issue`
on `dbosk/scholar` (per the `document-issues` convention) rather than building it
ad hoc:

```bash
gh issue create --repo dbosk/scholar --label enhancement \
  --title "<short title>" --body "<motivation + sketch>"
```
