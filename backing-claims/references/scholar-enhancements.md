# `scholar` support for this skill: shipped + future ideas

The workflow ideas captured here have been implemented in `scholar` (repo
`dbosk/scholar`). This file records what shipped, so a missing command can
be traced to the change that brings it, and holds any future ideas.

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
The follow-ups queued then (DBLP zero-hit retry, atomic export writes,
venue normalisation at ingest) are delivered by the PRs below.

## Delivered October 2026 (PRs #115–#118, #124, #125; no version bump)

Opened 2026-10-11; until they are merged and the pipx install is rebuilt
from main, the installed scholar lacks these (`scholar --help` without
`--proxy` is the tell).

| PR | Capability | Where it shows |
|----|------------|----------------|
| [#116](https://github.com/dbosk/scholar/pull/116) | A failed search is recorded as failed, not 0: `failed (reason)`, `N, incomplete (reason)`, `N after k retries` | `sessions show`, `search -f csv` (`# Results:`, `# Retries:`), report |
| #116 | `providers check` fails on a JSON API answering with HTML (DBLP's anti-bot page) | exit 1, `http error` |
| #116 | DBLP repeats empty multi-term answers (2 s, 5 s), recorded as retries | session record |
| #116 | Scopus empty result sets are 0 papers (no placeholder record); list-valued venues normalised at ingest | — |
| [#117](https://github.com/dbosk/scholar/pull/117) | Session saves merge with the file on disk; atomic writes keep `<name>.json.bak`; an unreadable session (or notes file) is a hard error; `sessions list` flags sessions with records but no decisions and no context | `sessions list`, `.bak` |
| #117 | `sessions export` is all-or-nothing | exit 1, old outputs untouched |
| [#115](https://github.com/dbosk/scholar/pull/115) | `llm classify`: exactly one audit category per paper, note tags never assigned, failures left pending and listed | end of the run |
| #115 | Audit table: the status wins (discarded = "…, excluded"), "n/a" for a missing confidence, `sessions decide --confidence/-c` | `sessions export -f table` |
| #115 | One citation-key scheme for report, synthesis and `search -f bibtex` (`smith2024`, `smith2024a`, `nd`); synthesis cache invalidated once | `.bib` keys |
| #116 | The "Databases:" sentence names every provider that answered (zero hits included), notes partial failures, and names preprint servers properly | table caption |
| [#118](https://github.com/dbosk/scholar/pull/118) | `--proxy URL` / `SCHOLAR_PROXY` for every request; `providers check` prints the route, `--show-ip` the exit address; own User-Agent (`SCHOLAR_USER_AGENT` overrides); one rate limiter for every client | `providers check`, `fetch_pdf.py` |
| [#124](https://github.com/dbosk/scholar/pull/124) | `cache clear` keeps paid LLM caches (`--include-llm` removes them) and really clears the Crossref cache | `cache info` |
| [#125](https://github.com/dbosk/scholar/pull/125) | DBLP paced at 2 s per request and routed through the proxy; homonym numbers ("Wei Wang 0001") dropped, stored sessions reconciled | — |

Not delivered: DBLP itself. It blocks API clients with an anti-bot
page (dbosk/scholar#94); scholar does not try to get past it, so DBLP
coverage stays lost until DBLP lifts the block.

## Future ideas (not yet built)

When a new gap appears, offer to file it as a `gh issue`
on `dbosk/scholar` (per the `document-issues` convention) rather than building it
ad hoc:

```bash
gh issue create --repo dbosk/scholar --label enhancement \
  --title "<short title>" --body "<motivation + sketch>"
```
