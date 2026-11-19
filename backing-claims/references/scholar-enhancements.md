# `scholar` support for this skill: shipped + future ideas

The workflow ideas captured here have been implemented in `scholar` (repo
`dbosk/scholarcli`, formerly `dbosk/scholar`). This file records what shipped, so a missing command can
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
| Record who decided | `scholar sessions decide … --source human\|llm` (a human decision on an LLM row marks it `llm_reviewed`; `agent` added by #162, below) |
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

## Delivered November 2026 (PRs #141–#147, merged 2026-11-18)

The repository is now `dbosk/scholarcli`. Until the pipx install is rebuilt
from main, the installed scholar lacks these (`scholar sessions check
--help` failing is the tell).

| Issue | Capability | Command |
|-------|------------|---------|
| [#135](https://github.com/dbosk/scholarcli/issues/135) | Match title and abstract only: OpenAlex and its preprint servers (`search.title_and_abstract`), Scopus (`TITLE-ABS-KEY()` unless the query names fields), WoS `TS=` already; s2, dblp, ieee, arxiv, hal warn and do not record it; `scholar syntax` lists each provider's default fields | `scholar search … --in title-abstract` (also `rq`) |
| [#140](https://github.com/dbosk/scholarcli/issues/140) | A search record is identified by query, provider and filters: full-text and `--in title-abstract` runs (or different `--year`) are separate records; `sessions show` and the report print the flags | `sessions show` |
| [#136](https://github.com/dbosk/scholarcli/issues/136) | OpenAlex search by meaning held against sessions: per question each work's place and bucket (bearing, adjacent, unclassified, other topic, excluded, not in any session), a tally, known studies' places; read-only. Replaces `scripts/semantic_check.py` | `scholar sessions check S [S…] -s "Q" [-k DOI-or-title] [-o DIR]` |
| #136 | The ranked list itself, labelled `top N, ranked (not a count)`; only provider of a run, no filters | `scholar search "Q" -p openalex-semantic` |
| [#137](https://github.com/dbosk/scholarcli/issues/137) | Enrich only pending papers and only the named fields; batched OpenAlex DOI lookups (name `openalex` first); saved every 50 papers; Ctrl-C/SIGTERM keeps the progress (exit 130) | `scholar enrich S --pending-only --fields abstract --enrich-providers openalex,…` |
| [#138](https://github.com/dbosk/scholarcli/issues/138) | OpenAlex prepaid and one-time credit shown; a spent daily allowance no longer blocks while credit remains | `scholar providers check` |
| [#139](https://github.com/dbosk/scholarcli/issues/139) | Clear one provider's cache; a WARNING when cached standard-view (abstract-less) Scopus results are served because COMPLETE could not be confirmed | `scholar cache clear --provider scopus` |
| [#130](https://github.com/dbosk/scholarcli/issues/130) | Start-up about 2.3 s faster (snowball and tuxedo imported lazily) | — |
| [#148](https://github.com/dbosk/scholarcli/issues/148) | Semantic Scholar kept at one request a second (0.9/s) across endpoints, retries, threads and processes; retries reported, a lost connection pauses S2 for 60 s | `scholar providers limits` |

`scripts/openalex_title_abstract.py` is replaced by `--in title-abstract`;
both scripts were removed from this skill.

Merged the same day, from the MFA review's follow-ups (PRs #149, #155–#158,
#178–#184; installed via pipx from main at 51c296e; `scholar llm sample
--help` failing is the tell of an older install):

| Issue | Capability | Command |
|-------|------------|---------|
| [#150](https://github.com/dbosk/scholarcli/issues/150) | An OpenAlex search cut short by a rate-limit block is recorded `N, incomplete (…)` (pages kept), never 0 | `sessions show` |
| [#151](https://github.com/dbosk/scholarcli/issues/151) | OpenAlex refusals carry OpenAlex's own message, plus a key hint when a key would help | `failed (HTTP 503: …; no API key: set OPENALEX_API_KEY)` |
| [#152](https://github.com/dbosk/scholarcli/issues/152) | Spent-budget warning of the semantic search has the key hint; an authorless match is not labelled title+author | `sessions check` |
| [#153](https://github.com/dbosk/scholarcli/issues/153) | `enrich` keeps a copy from before the run | `<name>.json.pre-enrich-<time>.bak` |
| [#154](https://github.com/dbosk/scholarcli/issues/154) | Dependencies updated (Dependabot alerts closed) | — |
| PR #155 | User-Agent and help name `dbosk/scholarcli` | — |
| [#159](https://github.com/dbosk/scholarcli/issues/159), [#160](https://github.com/dbosk/scholarcli/issues/160) | API keys and `mailto` addresses redacted from error text; the contact email kept out of test runs | `providers check` |
| [#161](https://github.com/dbosk/scholarcli/issues/161) | S2: Boolean queries and `-l 0` go to the bulk search (title+abstract, stemmed, most cited first when capped, 100 000 cap); plain words with a limit to relevance (stops at 1 000, marked incomplete); endpoint recorded as `via`; other databases' field syntax refused as failed | `-p s2`; `sessions show` `s2 (via bulk)` |
| #161 | Semantic Scholar snippet search as a backend of the check by meaning | `sessions check -b s2-snippets` |
| [#162](https://github.com/dbosk/scholarcli/issues/162) | `--source agent` (and `agent_reviewed`); `--source` required off a terminal (exit 2); a machine decision cannot replace a human or reviewed one without `--force`; unknown sources read as unknown, unreviewed, uncited | `sessions decide --source human\|agent\|llm` |
| [#163](https://github.com/dbosk/scholarcli/issues/163) | The LaTeX report counts decisions by source, shows unreviewed machine decisions and names every search | `sessions export -f latex` |
| [#164](https://github.com/dbosk/scholarcli/issues/164) | One search record per provider; old merged records labelled as such, naming each failing provider | `sessions show` |
| [#165](https://github.com/dbosk/scholarcli/issues/165) | A provider skipped for a cooldown or spent quota is recorded as `failed (skipped: …; resets …)` | `sessions show` |
| [#166](https://github.com/dbosk/scholarcli/issues/166) | Totals and caps: `100 of 2,130 (capped at 100)`; the record kept is the latest answered run of the widest scope; caption "capped at the limit for k of n queries" | `sessions show`, caption |
| [#167](https://github.com/dbosk/scholarcli/issues/167) | `searched_at`/`fetched_at` per record; caption "Searched A to B."; `bibtex+prov` `DATE` is the fetch date, never today for a cache hit | `sessions show`, `-f bibtex+prov` |
| [#168](https://github.com/dbosk/scholarcli/issues/168) | Each LLM decision stores model, time, prompt version, reason, truncated-abstract flag; an unusable answer leaves the paper pending; only reviewed examples by default; report section "LLM screening" | `llm classify`, report |
| [#173](https://github.com/dbosk/scholarcli/issues/173) | Seeded random sample of unreviewed LLM/agent decisions for the author's review; disagreement rate with a 95% modified Wilson interval | `scholar llm sample S --discarded\|--kept -n N --seed K [--report]` |
| [#169](https://github.com/dbosk/scholarcli/issues/169) | Audit caption counts exclusion-criterion discards per criterion ("excluded for lack of an abstract"), not as duplicates of cited sources | `sessions export -f table` |
| [#170](https://github.com/dbosk/scholarcli/issues/170) | A DOI-less copy folds into the DOI copy of the same work within a search; copies across searches listed by `sessions show` and folded on request; DOI-less works no longer merge across years | `scholar sessions reconcile S [--dry-run]` |
| [#174](https://github.com/dbosk/scholarcli/issues/174) | Tests clear provider key attributes set at import | — |
| [#175](https://github.com/dbosk/scholarcli/issues/175) | Concurrent scholar processes no longer empty the cache (locked, atomic, merged saves; unreadable files never overwritten) | — |
| [#176](https://github.com/dbosk/scholarcli/issues/176) | `bibtex+prov` stubs carry `% COUNTER: TODO`; `prov import/export` keep `COUNTER` and read wrapped (indented continuation) field lines as one value | `scholar search ... -f bibtex+prov`, `scholar prov` |
| [#177](https://github.com/dbosk/scholarcli/issues/177) | Re-deciding with a new status replaces the old category tags | `sessions decide` |

`scholar llm sample --help` now names the modified Wilson interval the
report computes (dbosk/scholarcli PR #187).

Merged 2026-11-19 (PRs #189, #193, #197–#202, #205; installed via pipx
from main at f8b9ca2; `scholar sessions decide --help` without `--untag`
is the tell of an older install):

| Issue | Capability | Command |
|-------|------------|---------|
| [#188](https://github.com/dbosk/scholarcli/issues/188) | A provider known only from records without an outcome is listed "Also queried, with no recorded outcome", not as searched | caption, report |
| [#192](https://github.com/dbosk/scholarcli/issues/192) | A re-run with `-n` keeps the stored paper (abstract, sources) and unites providers | `search -n` |
| [#195](https://github.com/dbosk/scholarcli/issues/195) | Remove a tag (`--untag`, before `--tag`); a category `--tag` replaces the old category whatever the status; two categories in one decide are refused. `--untag` is part of a decision: a machine untag needs `-c` again, a human untag reviews an agent/LLM decision | `sessions decide S --keep --untag no-abstract --source agent -c 0.9 --doi …` |
| [#196](https://github.com/dbosk/scholarcli/issues/196) | An audit row shows the note tags of every copy of the work (pending copies too); themes stay with their copy | `sessions export -f table` |
| [#191](https://github.com/dbosk/scholarcli/issues/191) | Papers from pre-#164 merged searches are credited only to providers their `sources` (or a per-provider link) confirm, in the audit rows, the caption and the report | `sessions export` |
| [#190](https://github.com/dbosk/scholarcli/issues/190) | A failed or skipped re-run replaces a record without an outcome unless a link or a paper naming that provider shows it answered | `sessions show`, report |
| [#185](https://github.com/dbosk/scholarcli/issues/185) | S2 bulk: whole hyphenated tokens quoted (`"don't-care"`), `~N` kept outside the quotes and routed to bulk, a wildcard after a hyphenated word refused | `-p s2` |
| [#194](https://github.com/dbosk/scholarcli/issues/194) | Concurrent saves fill gaps in a paper from the other process's copy (a field both hold keeps this process's value, #206) | — |
| [#181](https://github.com/dbosk/scholarcli/issues/181) | A session saves into the file it was loaded from; a file whose stored name differs is warned about and flagged by `sessions list` (`name_mismatch`) | `sessions list` |

Merged 2026-11-19, third round (PRs #208–#242; installed via pipx from
main at bc8ec8c; `scholar sessions relabel --help` failing is the tell of
an older install):

| Issue | Capability | Command |
|-------|------------|---------|
| [#216](https://github.com/dbosk/scholarcli/issues/216) | Correct who decided without touching the decision: only unreviewed targets (`agent`, `llm`); LLM trace and confidence kept; `pre-relabel` backup; each decision records `relabelled` (from, to, at, note, by) | `sessions relabel S --from human --to agent --all --dry-run --note … --by …` |
| [#218](https://github.com/dbosk/scholarcli/issues/218) | Audit table: a row is cited when the text's bibliography cites the work, whoever decided; cited exclusions and works the session lacks are listed on stderr; uncited keeps counted apart | `sessions export S -f table --cited-from refs.bib` |
| [#220](https://github.com/dbosk/scholarcli/issues/220) | Non-Latin text (and Latin letters T1 lacks) wrapped in `\scholarnonlatin{…}` instead of dropped; defined only where used (text under XeLaTeX/LuaLaTeX, a marker under pdfLaTeX); standalone reports load T1; rows starting with `[` compile | `sessions export`, `llm synthesize` |
| [#230](https://github.com/dbosk/scholarcli/issues/230) | `search -f bibtex`/`bibtex+prov` escape their fields; provenance blocks record `% ID: <paper id>`; an `@preamble` defines `\scholarnonlatin` when needed | `search -f bibtex+prov`, `prov import/export` |
| [#204](https://github.com/dbosk/scholarcli/issues/204) | A work's audit row comes from its confirmed copy (a human or reviewed verdict on the work), not from an unreviewed classifier copy; `no-abstract`/version-note discards judge only the record | `sessions export -f table` |
| [#224](https://github.com/dbosk/scholarcli/issues/224) | Classifier and relayed `--source llm` answers must have a category that fits the status; all four categories are offered once a session uses any | `llm classify`, `sessions decide --source llm` |
| [#237](https://github.com/dbosk/scholarcli/issues/237) | Session arguments: a label fitting two files exits 2; `foo.json` / `<hash>.json` pick a file; paths outside the sessions dir refused | every command taking a session |
| [#245](https://github.com/dbosk/scholarcli/issues/245) | An agent's correction can keep the classifier's trace (model, prompt, reason); `sessions show` marks a trace under someone else's decision | `sessions decide S --discard --tag off-topic-false-hit -c 0.8 --source agent --keep-trace --doi …` |
| [#228](https://github.com/dbosk/scholarcli/issues/228) | Two decisions under one id survive appends and concurrent saves; `decide` refuses copies decided apart unless `--all-copies` | `sessions decide … --all-copies` |
| [#206](https://github.com/dbosk/scholarcli/issues/206), [#219](https://github.com/dbosk/scholarcli/issues/219) | Concurrent saves merge paper fields three ways (a retraction found by `verify` survives a stale save); Crossref notices are united | — |
| [#203](https://github.com/dbosk/scholarcli/issues/203), [#207](https://github.com/dbosk/scholarcli/issues/207), [#213](https://github.com/dbosk/scholarcli/issues/213), [#214](https://github.com/dbosk/scholarcli/issues/214) | Appends load only their own session file and keep the right merge baseline; a namesake never inherits another work's decision | `search -n` |
| [#215](https://github.com/dbosk/scholarcli/issues/215), [#221](https://github.com/dbosk/scholarcli/issues/221), [#231](https://github.com/dbosk/scholarcli/issues/231), [#233](https://github.com/dbosk/scholarcli/issues/233), [#241](https://github.com/dbosk/scholarcli/issues/241) | Copy lists show same-id pairs; listings and pooled samples read sessions by file; DBLP homonym numbers no longer split audit rows; the Crossref contact address is read per request | `sessions show`, `llm sample --report` |

## Future ideas (not yet built)

When a new gap appears, offer to file it as a `gh issue`
on `dbosk/scholar` (per the `document-issues` convention) rather than building it
ad hoc:

```bash
gh issue create --repo dbosk/scholarcli --label enhancement \
  --title "<short title>" --body "<motivation + sketch>"
```


Gaps seen on 2026-11-13 (MFA review), filed 2026-11-15 as #135, #136
and #137: delivered, see "Delivered November 2026".
