# `scholar` cookbook (non-interactive) + other sources

`scholar` (PyPI `scholarcli`, on `PATH` as `scholar`; source at
`~/devel/scholar`) is the preferred way to find literature because it searches
several databases at once and records the query. Use only its **non-interactive**
subcommands from an agent.

> **Out of scope (interactive TUIs):** `scholar snowball`, `scholar tuxedo`,
> and `scholar search --review`. Do not drive these from an agent.

> **Version note:** `-f bibtex+prov`, `pdf quote`, and `verify` ship in
> `scholar` ≥ 1.20; the `prov` command group (`found-via`, `import`, `export`)
> landed shortly after. If `scholar prov` reports "No such command", upgrade:
> `pipx upgrade scholarcli` (or reinstall from `~/devel/scholar`).

## Table of contents

- [Providers and keys](#providers-and-keys)
- [Searching](#searching)
- [Research-question search](#research-question-search)
- [Reading the source (verification)](#reading-the-source-verification)
- [Provenance commands](#provenance-commands)
- [Notes and sessions](#notes-and-sessions)
- [Writing `FOUND-VIA` for each source](#writing-found-via-for-each-source)

## Providers and keys

```bash
scholar providers       # which providers are available (key-configured)
scholar syntax          # per-provider query operators (AND/OR/NOT, phrases, fields)
```

| Provider | `-p` name | Key needed |
|----------|-----------|------------|
| Semantic Scholar | `s2` | optional (`S2_API_KEY`) |
| OpenAlex | `openalex` | optional (`OPENALEX_EMAIL`) |
| DBLP (CS) | `dblp` | none |
| arXiv (preprints) | `arxiv` | none |
| Web of Science | `wos` | required |
| IEEE Xplore | `ieee` | required |
| Scopus | `scopus` | required |

Query syntax differs per provider (run `scholar syntax`): e.g. OpenAlex/WoS need
UPPERCASE boolean operators; DBLP treats space as implicit AND and disables NOT;
arXiv uses `ANDNOT`. s2/openalex support `"phrase"` search; dblp supports
`author:` and prefix `*` wildcards.

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
```

`bibtex+prov` is the fastest honest start: it fills the reproducible `FOUND-VIA`
line (including `--limit`) and `DATE`, and leaves the fields that require human
judgement (`CLAIM`, `PICKED`, `QUOTE`, `VERIFIED`) as `TODO`. Results are
deduplicated, keeping the richest copy of each paper.

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
scholar pdf open "<pdf-url>"           # download (cache) and open full text
scholar pdf info                       # PDF cache stats

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

```bash
scholar sessions list                  # saved review sessions
scholar notes list                     # papers that have notes (and their IDs)
scholar notes show "<doi-or-hash>"     # notes for one paper
scholar notes search "scope mismatch" -f json   # search note text/titles
scholar notes export notes.json        # dump all notes (machine-readable)
```

Notes are an optional secondary store; the **authoritative** provenance lives in
the `.bib` comment block (see `provenance-format.md`).

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
