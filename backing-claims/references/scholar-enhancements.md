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

## Shipped 2026-09-02 (installed via pipx from the stacked tip of dbosk/scholar PRs #80 and #81)

| Capability | Command |
|------------|---------|
| Audit table of a classified session as an `\input` fragment; cited = kept by a human decision (source `human` or `llm_reviewed`) with a non-category tag or none, theme = first non-category tag; LLM keeps show category + confidence | `scholar sessions export SESSION -f table --lang sv --label sok-A --track "sökspår 1" --theme TAG=NAME -o base` → `base.tex` |
| Record who decided | `scholar sessions decide … --source human\|llm` (a human decision on an LLM row marks it `llm_reviewed`) |
| OpenAlex API key (bearer token; a free key raises the metered daily budget tenfold) | `OPENALEX_API_KEY` in the environment; `scholar providers check` shows remaining budget and reset time; a 429 with the budget spent blocks the group until the reset |
| `\input`-able report / synthesis | `scholar sessions export -f latex --no-standalone`; `scholar llm synthesize -f latex --no-standalone --output …` |
| List-valued venues no longer crash the export | — |

`-f table --bearing-only` shipped the same day (PR #80 commit f814c33):
bearing rows only, excluded counts in the caption, no session name in the
compiled text (a `% Session:` comment at the top of the fragment),
databases listed full-name-first, bookkeeping tags shown as notes,
`--theme` as the allowlist for cited rows. Verified against
`scripts/session_table.py` on a 715-record session: identical rows,
cited counts and reasons. The script stays as the CSV-based fallback.
Queued follow-ups pending the user's OK: DBLP zero-hit backoff/retry,
atomic export writes, venue normalisation at ingest.

## Future ideas (not yet built)

When a new gap appears, offer to file it as a `gh issue`
on `dbosk/scholar` (per the `document-issues` convention) rather than building it
ad hoc:

```bash
gh issue create --repo dbosk/scholar --label enhancement \
  --title "<short title>" --body "<motivation + sketch>"
```
