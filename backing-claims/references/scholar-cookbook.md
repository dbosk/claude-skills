# `scholar` cookbook (non-interactive) + other sources

`scholar` (PyPI `scholarcli`, on `PATH` as `scholar`; source at
`~/devel/scholar`) is the preferred way to find literature because it searches
several databases at once and records the query. Use only its **non-interactive**
subcommands from an agent.

> **Out of scope (interactive TUIs):** `scholar snowball`, `scholar tuxedo`,
> and `scholar search --review`. Do not drive these from an agent.

> **Version note:** `-f bibtex+prov`, `pdf quote`, and `verify` ship in
> `scholar` ≥ 1.20; the `prov` command group (`found-via`, `import`, `export`)
> landed shortly after. Non-interactive **named sessions** (`search -n`
> persisting without `--review`) and headless decisions (`sessions decide`)
> ship in ≥ 1.25 (dbosk/scholar#66). The failure records, session
> integrity, `--proxy`, `cache clear --include-llm` and `sessions decide
> --confidence` described below come from dbosk/scholar PRs #115–#118,
> #124 and #125 (October 2026, no version bump): if `scholar --help` has
> no `--proxy`, the installed scholar predates them. If a command is
> missing, upgrade: `pipx upgrade scholarcli` (or reinstall from
> `~/devel/scholar`).

## Table of contents

- [Providers and keys](#providers-and-keys)
- [Searching](#searching)
- [Known items](#known-items)
- [Research-question search](#research-question-search)
- [Reading the source (verification)](#reading-the-source-verification)
- [Provenance commands](#provenance-commands)
- [Notes and sessions](#notes-and-sessions)
- [Network route and identity](#network-route-and-identity)
- [Cache](#cache)
- [Writing `FOUND-VIA` for each source](#writing-found-via-for-each-source)

## Providers and keys

```bash
scholar providers       # which providers are available (key-configured)
scholar syntax          # per-provider query operators (AND/OR/NOT, phrases, fields)
```

| Provider | `-p` name | Key needed |
|----------|-----------|------------|
| Semantic Scholar | `s2` | optional (`S2_API_KEY`) |
| OpenAlex | `openalex` | optional (`OPENALEX_API_KEY`; `SCHOLAR_EMAIL`) |
| DBLP (CS) | `dblp` | none (blocked for API clients since Sep 2026) |
| arXiv (preprints) | `arxiv` | none |
| HAL (French open archive) | `hal` | none |
| Preprint servers via OpenAlex | `ssrn`, `biorxiv`, `medrxiv`, … or the group `-p preprints` | none |
| Web of Science | `wos` | required |
| IEEE Xplore | `ieee` | required |
| Scopus | `scopus` | required |

**Use all configured providers, not just the keyless ones.** On this
machine the WoS, Scopus, IEEE and S2 keys are set (check with
`env | grep -E '^(WOS|SCOPUS|IEEE|S2)'`) — "key required" in the table
means *a key*, not *no access*. Gap/negative-result claims are only as
strong as the databases searched: WoS and Scopus index the education
venues the CS-specific indexes miss. Their relevance ranking is poor for
natural-language queries — prefer their field-tagged syntax (see
`scholar syntax`). The S2 key may be expired; S2 still works keyless at
a lower rate limit.

**Check provider health before *and* during a long session.**

```bash
scholar providers check     # route, then each provider: ok / key rejected /
                            # http error / network error / rate limited /
                            # quota exhausted / not configured
scholar providers limits    # quota usage and reset times per provider
```

The exit status is 1 exactly when a *configured* provider is unusable: `key
rejected`, `network error`, or `http error` — which now includes a JSON API
that answers HTTP 200 with an HTML page. That is DBLP's state since
September 2026: dblp.org and both mirrors serve an Anubis anti-bot page to
every API request, with no client-side fix, and scholar does not try to get
past it. So in the pre-flight gate a failing `dblp` is **expected**: proceed
with the other providers, record DBLP as unavailable (with the date) in the
appendix, and never count its cells as zero. `rate limited` and `quota
exhausted` exit 0 (the configuration is fine); an unkeyed `s2` often shows
`rate limited` because it shares a public pool. The gate passes, but its
searches may still fail — read the per-cell outcomes below before trusting
its coverage, and rerun its failed cells later.

Run the check again partway through a long session: keys get rejected and
daily quotas run out mid-run.

**Failed searches are recorded as failed.** Scholar records each search's
outcome per query × provider, and every view uses the same words:

| Outcome | Meaning | In the matrix |
|---------|---------|---------------|
| `12` | answered with 12 hits | 12 |
| `0` | answered, nothing found | 0 |
| `failed (reason)` | no answer (e.g. `failed (non-JSON response (HTTP 200, text/html))`, a 429, a rejected key) | *failed*/*unavailable*, never 0 |
| `7, incomplete (reason)` | broke off part-way; 7 is a lower bound | "≥7, incomplete" |
| `3 after 2 retries` | answered only on a repeat (DBLP's empty answers, see below) | 3 |

Read them from `scholar sessions show <session>` (under "Queries by
provider:", failures highlighted), from `search -f csv` (the `# Results:`
header line, plus `# Retries: N` when there were any) or from the report.
A script that parses `# Results:` must treat anything that is not a plain
number as a failure, not as 0. A failed re-run never overwrites an earlier
record that had an answer, and a failed result is never cached, so rerunning
a failed cell later is safe. See `appendix-guide.md`, "Provider quirks that
fake a negative", for the per-provider failure modes.

Query syntax differs per provider (run `scholar syntax`): e.g. OpenAlex/WoS need
UPPERCASE boolean operators; DBLP treats space as implicit AND and disables NOT;
arXiv uses `ANDNOT`. s2/openalex support `"phrase"` search; dblp supports
`author:` and prefix `*` wildcards.

**DBLP, when it answers.** Scholar paces it at one request per 2 s (DBLP's
FAQ asks for one or two seconds between requests) and repeats an empty
answer to a query of two or more terms after 2 s and then 5 s, with the
identical query, since a throttled DBLP returns zero hits without an error.
The repeats are recorded (`N after k retries`); a zero that survives them is
recorded as 0, and a repeat that fails makes the search fail. Do not re-query
DBLP zeros by hand. Homonym numbers in author names ("Wei Wang 0001") are
dropped at ingest.

## Searching

```bash
# BibTeX straight out (default providers = all available)
scholar search "authenticated encryption generic composition" -f bibtex

# BibTeX already wrapped in provenance blocks (FOUND-VIA + DATE pre-filled;
# CLAIM/PICKED/QUOTE/VERIFIED left as TODO for you to complete)
scholar search "authenticated encryption generic composition" -p s2 -p dblp -f bibtex+prov

# Pick providers; cap results per provider
scholar search "cognitive load theory" -p s2 -p openalex -l 50 -f bibtex

# JSON/CSV for programmatic screening
scholar search "federated learning privacy" -p s2 -f json

# Named session: -n persists every search (query, provider, filters, limit,
# results) to the session, interactive or not; repeat the same -n across
# searches to build one session per review/paper
scholar search 'TS=("command line" AND novice*)' -p wos -n vt-terminal-systematic -f json
```

For a systematic round, run **every** query of the round under one `-n`
session per paper: the session becomes the reproducible record that
`sessions export` turns into the protocol-appendix artifacts.

`bibtex+prov` is the fastest honest start: it fills the reproducible `FOUND-VIA`
line (including `--limit`) and `DATE`, and leaves the fields that require human
judgement (`CLAIM`, `PICKED`, `QUOTE`, `VERIFIED`) as `TODO`. Results are
deduplicated, keeping the richest copy of each paper. Citation keys follow
one scheme across scholar's outputs (`smith2024`, `smith2024a`, `nd` for no
year); keys in a `.bib` from an older scholar may differ — see
`provenance-format.md`, "Bib hygiene the reader sees".

## Known items

Relevance-ranked keyword search buries older and grey-literature works under
recent hits, so a paper you already know can sit off the first page on every
provider. Retrieve it directly:

```bash
# by DOI (works even when keyword ranking buried it)
curl -s "https://api.openalex.org/works/doi:10.2190/689T-1R2A-X4W4-29J2"   # OpenAlex
curl -s "https://api.crossref.org/works/10.2190/689T-1R2A-X4W4-29J2"       # Crossref
# by exact title, via provider field-search syntax (see `scholar syntax`)
scholar search 'TI=(language-independent conceptual bugs)' -p wos            # WoS: TI= TS= AU=
scholar search 'TITLE("Language-Independent Conceptual Bugs")' -p scopus     # Scopus: TITLE() AUTH()
scholar search 'ti:"visual program simulation"' -p arxiv                     # arXiv: ti: au:
```

## Research-question search

`scholar rq` turns a research question into provider-specific queries with an
LLM and records them for reproducibility — ideal when you want the `FOUND-VIA`
trail captured for you.

```bash
scholar rq "How do LLMs support novice programming?" -p openalex -p dblp --count 20
scholar rq "..." -y 2020- -oa          # year range, open-access only
```

Then pull the recorded query into `FOUND-VIA` (see `provenance-format.md`).

## Reading the source (verification)

```bash
scholar enrich "<session>"             # fill missing abstracts via DOI lookup
scholar search "..." --enrich -f bibtex  # enrich inline during a search
scripts/fetch_pdf.py --text "<url-or-doi>"  # download into the cache, no viewer;
                                       # prints <source>\t<cache pdf>\tOK\t<text file>
scholar pdf path                       # the cache directory (~/.cache/scholar/pdfs,
                                       # files named by SHA-256 of the URL)
scholar pdf info                       # PDF cache stats
scholar pdf open "<pdf-url>"           # interactive only: caches AND opens a viewer

# Surface candidate supporting passages for a claim (the QUOTE step).
# Ranks lexically, then optionally reranks with an LLM. Judgement stays human.
scholar pdf quote "<pdf-url>" --claim "AE provides confidentiality and integrity"
scholar pdf quote "<pdf-url>" --claim "<claim>" -n 8 --no-llm --json

# Currency / retraction check for a whole session (the VERIFIED currency test).
# Looks up each DOI in Crossref; reports retracted/corrected/superseded and
# saves the status back to the session.
scholar verify "<session>"
scholar verify "<session>" --json
```

`scholar pdf quote` options: `--claim` (required), `--limit/-n` (passages, default
5), `--model/-m` (rerank model), `--lexical/--no-lexical`, `--llm/--no-llm`,
`--json`. It only proposes passages — always read the passage and confirm it
*entails* the claim before using it as the `QUOTE`.

For sources `scholar` can't fetch, `WebFetch` the publisher/arXiv page and read
the relevant section. Always read at least the abstract; read the results
section in full text for precise quantitative or causal claims.

## Provenance commands

The `prov` group moves provenance between the `.bib` comment blocks (the
authoritative store) and `scholar notes`.

```bash
# Print a reproducible FOUND-VIA line for one paper, rebuilt from the saved
# session(s) that surfaced it. Reports every matching session.
scholar prov found-via "<doi-or-hash>"
scholar prov found-via "<doi-or-hash>" -f json

# Round-trip with notes. Import merges blocks into each paper's note keyed by
# CLAIM (re-import never duplicates; personal note text is kept). Export writes
# stored blocks above each entry and never emits personal prose.
scholar prov import refs.bib
scholar prov export refs.bib            # to stdout
scholar prov export refs.bib --in-place # overwrite the file
```

Find a paper's ID with `scholar notes list` or `scholar sessions`. The `.bib`
comment block remains the source of truth (see `provenance-format.md`); notes
are a synced secondary copy.

## Notes and sessions

The full review loop runs headlessly: search with `-n`, decide with
`sessions decide`, export with `sessions export` — no TUI needed.

```bash
# Record screening decisions non-interactively; discarding REQUIRES a --tag
# stating the motivation; a selector matching nothing saves no changes.
scholar sessions decide vt-terminal-systematic --keep \
    --doi 10.1145/3502718.3524753 -t shell-teaching-intervention
scholar sessions decide vt-terminal-systematic --discard \
    --doi 10.1109/ISED67359.2025.11405208 -t "LLM tutoring tool, no learner findings"
# An agent's own screening is recorded as an LLM decision, with the
# model's confidence (0-1; ignored, with a note, for human decisions):
scholar sessions decide vt-terminal-systematic --source llm -c 0.7 \
    --keep --paper-id hash:115f4c4a5e6a6b32 -t supports-claim

# Export a session's audit trail (bib + csv + latex report) into the paper
# repo, e.g. literature-review/ (the vt-* papers' layout)
scholar sessions export vt-terminal-systematic -f all \
    -o literature-review/vt-terminal-systematic

scholar sessions show vt-terminal-systematic   # papers with ids; per query x
                                               # provider: hits or "failed (...)"
scholar sessions list                  # saved review sessions
scholar notes list                     # papers that have notes (and their IDs)
scholar notes show "<doi-or-hash>"     # notes for one paper
scholar notes search "scope mismatch" -f json   # search note text/titles
scholar notes export notes.json        # dump all notes (machine-readable)
```

Notes are an optional secondary store; the **authoritative** provenance lives in
the `.bib` comment block (see `provenance-format.md`).

**Sessions are safe to work on in parallel.** A save merges with the file on
disk, so a long `scholar enrich` no longer wipes an `llm context`/`llm
classify` run that saved in the meantime; if two processes decide the same
paper differently, the later save wins and a warning names both decisions.
Every save is atomic and keeps the previous version as `<name>.json.bak` in
the sessions directory (`$SCHOLAR_DATA_DIR/review_sessions/`, by default
`~/.local/share/scholar/review_sessions/`); notes files get a `.bak` too.

- An unreadable session file is a hard error ("Cannot read session file …
  Nothing was saved"): `search -n`, `--review` and `rq` exit 1 instead of
  starting a fresh session over it. Restore `<name>.json.bak` (or rebuild
  from a committed `sessions export`); never delete the file to get going.
- `sessions list` warns about sessions that have search records but no
  decisions and no research context (`needs_check` in `-f json`): either not
  screened yet, or screened and lost by an older scholar — check the `.bak`
  and the committed export before rescreening.
- `sessions export` is all-or-nothing: it writes every requested format or,
  on any failure, prints one line, exits 1 and leaves earlier outputs
  byte-identical, so a failed export never leaves a half-updated audit
  record in the repo.

**Classifying with audit categories.** When the session's vocabulary holds
the categories (supports-claim, qualifies-claim, adjacent-subtopic,
off-topic-false-hit), `llm classify` gives every paper exactly one of them.
Note tags such as `duplicate-record-of-cited-source` are for humans: the
model is never offered them and its attempts are dropped. A paper still
without exactly one category after the one retry is left pending and
listed at the end of the run under "Left pending, not exactly one category
tag (N):" with its paper id — decide each with `sessions decide`.

## Network route and identity

Every request scholar makes — searches, enrichment, PDF downloads — leaves
by one route: `--proxy URL` (a global option, before the command:
`scholar --proxy socks5h://127.0.0.1:1081 search …`), else `SCHOLAR_PROXY`,
else requests' own `HTTPS_PROXY`/`HTTP_PROXY`. Prefer `socks5h://` (the
tunnel resolves host names too); SOCKS needs PySocks in scholar's venv
(`pipx inject scholarcli PySocks`). A proxy URL that cannot work stops the
command with exit 2 instead of making every search fail quietly. `providers
check` prints the route first (`Route: proxy socks5h://127.0.0.1:1081
(--proxy)`, credentials redacted); `--show-ip` adds the exit address, asked
of a third party (ipify), so only on request. The university tunnel and
the full-text recipe: `closed-access.md`.

Scholar identifies itself as `scholar/<version>
(+https://github.com/dbosk/scholar)`, without an e-mail address
(`SCHOLAR_EMAIL` still goes to OpenAlex, Crossref and Unpaywall through
their own parameters); `SCHOLAR_USER_AGENT` overrides it. Never set it to a
browser's user agent: a bot check (Cloudflare, a login page, DBLP's anti-bot
page) is a stopping point, not an obstacle to get around.

## Cache

```bash
scholar cache info                 # sizes, incl. an "LLM caches" row
scholar cache clear                # search/enrichment caches; keeps paid LLM output
scholar cache clear --include-llm  # also the LLM synthesis caches
```

`cache clear` keeps the synthesis caches, which hold paid model output, and
says how many it kept. The citation-key change (#115) invalidated cached
synthesis prose once, so the first `llm synthesize` after upgrading calls
the model again.

## Writing `FOUND-VIA` for each source

The rule: the line must let someone **repeat the search**. For a paper that came
from a `scholar` session, do not hand-write it — generate it:

```bash
scholar prov found-via "<doi-or-hash>"   # prints the exact FOUND-VIA line(s)
scholar search "..." -f bibtex+prov      # bakes it into each entry's block
```

Patterns by source:

```text
# scholar (preferred — records the query; or use `prov found-via`)
FOUND-VIA: scholar search "authenticated encryption" -p s2 -p dblp
FOUND-VIA: scholar rq "How do LLMs support novice programming?" -p openalex
             (session "llm-novice-programming")
FOUND-VIA: scholar search 'TS=("command line" AND novice*)' -p wos
             (session "vt-terminal-systematic")   # prefer naming the session

# Google Scholar (manual)
FOUND-VIA: Google Scholar "power of feedback meta-analysis", picked result #1

# General web search + fetch
FOUND-VIA: WebSearch "cognitive load theory original paper" -> WebFetch <url>

# Crossref / DOI metadata lookup
FOUND-VIA: Crossref DOI 10.1023/A:1022193728205 (metadata + verification)

# deep-research skill (hard/contested claims)
FOUND-VIA: deep-research "<question>" (report cited <source>)
```

Use Crossref to turn a known DOI into clean BibTeX metadata, e.g.
`WebFetch https://api.crossref.org/works/<DOI>` or
`https://doi.org/<DOI>` with a BibTeX `Accept` header — but still read the
source itself before writing the `QUOTE`.
