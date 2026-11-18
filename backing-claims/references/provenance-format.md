# Provenance format

Every reference that backs a claim carries a **provenance comment block** placed
immediately above its BibTeX entry. The block travels with the `.bib`, survives
reordering, and is invisible in the compiled document. The validator
`scripts/check_provenance.py` keys on the field names below.

## Table of contents

- [Schema](#schema)
- [Field semantics](#field-semantics)
- [Multi-line values](#multi-line-values)
- [Worked examples](#worked-examples)
- [Reusing a source across documents](#reusing-a-source-across-documents)
- [Every source gets an entry — no nicknames](#every-source-gets-an-entry--no-nicknames)
- [Generating the block instead of typing it](#generating-the-block-instead-of-typing-it)
- [Bib hygiene the reader sees](#bib-hygiene-the-reader-sees)
- [Validating](#validating)

## Schema

```bibtex
% === provenance: <bibkey> ===
% CLAIM: <the exact claim this reference backs>
% FOUND-VIA: <reproducible tool + provider + query>
% PICKED: <why this source among the results>
% QUOTE (<location>): "<verbatim passage that supports CLAIM>"
% VERIFIED: <full-text | abstract> ; applies because <one line>
% COUNTER: <counter-search query> -- <refuting/qualifying work found and how
%   the claim was adjusted or the other side cited | none found>
% DATE: <YYYY-MM-DD>
@<type>{<bibkey>, ... }
```

Required: `CLAIM`, `FOUND-VIA`, `PICKED`, `QUOTE`, `VERIFIED`, `COUNTER`.
Recommended: `DATE` (warning if missing). The header line
`% === provenance: <bibkey> ===` is recommended and should match the entry key.
A field still holding a placeholder (an unquoted `TODO`, a `<template>`, the
location `(<loc>)`) counts as missing.

## Field semantics

- **CLAIM** — the single statement this reference supports, at the scope and
  strength it is used in the text. If one entry backs two distinct claims, prefer
  two `CLAIM` lines or two entries; a quote rarely supports two claims equally.
- **FOUND-VIA** — enough to *reproduce the search*: the tool, the provider(s),
  and the exact query string. Not "Semantic Scholar" but
  `scholar search "..." -p s2`. For non-`scholar` sources see
  `scholar-cookbook.md`.
- **PICKED** — why this result over the others: primary source vs survey,
  most-cited/canonical, venue, year, closest scope match. Name rejected
  alternatives when the choice was not obvious.
- **QUOTE** — a **verbatim** passage, in quotation marks, with a location in
  parentheses on the field header: a page `(p.7)`, section `(§3.2)`, or
  `(abstract)`. The quote must *entail* the claim, not merely share its topic.
- **VERIFIED** — what you actually read, as the **first word**: `full-text`
  (or `full text`) or `abstract`; then a one-line reason it applies. This is
  the auditable record of the double-check. A title, a search-result snippet,
  a machine summary (`tldr`) or memory is never acceptable (the levels of
  `verification-checklist.md`, "What verified requires"). A precise
  causal or quantitative claim ("improves", "reduces … by 15 %") needs
  `full-text`; a corroborating source that could only be read in abstract
  says so: `VERIFIED: abstract only, corroboration (closed access)`. Write
  "full text not obtainable" after the level, not before it.
- **COUNTER** — the counter-search behind the claim (SKILL.md step 2), in one
  of three forms: `<counter-search query> -- <outcome>`; `none found,
  searched: <query>` (an empty counter-search still names its query: an
  unrun one is not backing); or `see <bibkey>` when another entry of the same
  `.bib` backs the same claim and records the search. Required for every
  entry: a bare "none found" fails.
- **DATE** — when the reference was verified (sources get retracted, superseded).

## Multi-line values

A value may continue onto following comment lines until the next `% FIELD:`
header. Use this for long quotes or rationales:

```bibtex
% QUOTE (§1): "an authenticated encryption scheme ... provides both
%   privacy and authenticity, that is, it is both a secure encryption
%   scheme and a secure message authentication scheme"
% VERIFIED: full-text PDF read; applies because it defines AE as exactly C+I.
```

The validator concatenates continuation lines, so the quote is checked as one
value.

## Worked examples

### Primary source, full text read

```bibtex
% === provenance: Sweller1988 ===
% CLAIM: Excessive intrinsic + extraneous load impairs learning during problem solving.
% FOUND-VIA: scholar search "cognitive load theory problem solving" -p s2 -p openalex
% PICKED: original primary source introducing the construct, not a later review.
% QUOTE (p.262): "the cognitive load imposed by ... means-ends analysis ...
%   interferes with schema acquisition"
% VERIFIED: full-text PDF read; the quoted mechanism is exactly the claimed impairment.
% COUNTER: scholar search "cognitive load theory criticism measurement" -p s2
%   -p openalex -- <what the counter-search found, and how the claim was adjusted>
% DATE: 2026-06-24
@article{Sweller1988, ... }
```

### Survey, used for an established-consensus claim

```bibtex
% === provenance: HattieTimperley2007 ===
% CLAIM: Feedback is among the strongest influences on achievement (well established).
% FOUND-VIA: Google Scholar "power of feedback meta-analysis", picked result #1 (most cited)
% PICKED: high-citation synthesis; appropriate because the claim asserts consensus, not a new finding.
% QUOTE (p.81): "feedback is among the most powerful influences on achievement"
% VERIFIED: abstract + p.81 read via WebFetch of the publisher page.
% COUNTER: none found, searched: Google Scholar "feedback effects negative
%   meta-analysis"
% DATE: 2026-06-24
@article{HattieTimperley2007, ... }
```

## Reusing a source across documents

A claim already backed in another document is **not searched again**. Copy the
entry together with its provenance block into the new bibliography, unchanged —
the original `FOUND-VIA` is still the reproducible record of how the source was
found — and add one line saying how it reached *this* document:

```bibtex
% === provenance: HuntThomas1999 ===
% CLAIM: Duplicated knowledge becomes inconsistent when the copies change apart.
% FOUND-VIA: scholar search "code clones inconsistent changes faults" -p openalex -p ieee
% FOUND-VIA (here): backed in Algoritmiskt tänkande, bilaga E
% PICKED: ...
```

The `(here)` line is what tells a later reader that no new search stands behind
this copy, and where the search that does stand behind it is written up. Point
at that appendix from the prose as well (see `appendix-guide.md`, "Pointing at
the appendix from the text"); the claim may only be stated at the strength that
appendix supports.

## Every source gets an entry — no nicknames

A source referred to in an appendix, a note, or any prose is cited, never
called by a nickname ("the misconceptions article", "Knuth's paper"). A
nickname cannot be verified, and it hides whether the source was read.

This includes unpublished material. The author's own manuscript gets a real
entry, with the repository path as author-only information in the comment
block:

```bibtex
% === provenance: BoskMisconceptions ===
% CLAIM: Novices hold specific, recurring misconceptions about assignment.
% FOUND-VIA: known item, the author's manuscript
%   (repository: ~/devel/edu/vt-prog-misconceptions)
% PICKED: the study this text summarises; no published version exists yet.
% QUOTE (§4): "..."
% VERIFIED: full-text; the manuscript's results section states the claim.
% COUNTER: scholar search "..." -p openalex -p wos -- ...
% DATE: 2026-09-07
@unpublished{BoskMisconceptions,
  author = {Bosk, Daniel},
  title  = {...},
  year   = {2026},
  note   = {Manuskript},
}
```

`note = {Manuskript}` (or "Manuscript") is what the reader sees; the repository
path never reaches the compiled text.

## Generating the block instead of typing it

`scholar` builds the provenance skeleton for you, so `FOUND-VIA` and `DATE` are
never hand-transcribed (the judgement fields stay yours):

```bash
# Whole search, each entry pre-wrapped with FOUND-VIA + DATE filled in:
scholar search "..." -p s2 -p dblp -f bibtex+prov

# One paper's reproducible FOUND-VIA line, rebuilt from the saved session(s):
scholar prov found-via "<doi-or-hash>"        # -f json for tooling
# "Not reproducible:" instead? See scholar-cookbook.md, "Not reproducible"

# Sync blocks to/from scholar notes (authoritative store stays the .bib):
scholar prov export refs.bib --in-place
scholar prov import refs.bib
```

`found-via` always prints `scholar search` commands, one per search that
returned the paper, never a `scholar rq` line. That holds for an `rq`
session too, and is what makes it reproducible: `rq` has a language model
write one query per provider, so running the `rq` line again would ask the
model again (the queries are not cached), and nothing makes it write the
same ones; the session records the queries it
did run, and each `FOUND-VIA` re-runs one of them. A paper that an `rq`
session found on two providers gets two lines (`found-via` output, long
lines broken here):

```bibtex
% FOUND-VIA: scholar search '("large language model" OR LLM) AND novice
%   programming' -p openalex --limit 0
%   (session "rq-demo"; research question: "How do LLMs support novice programming?")
% FOUND-VIA: scholar search 'TS=("large language model*" AND novice* AND
%   programming)' -p wos --limit 0
%   (session "rq-demo"; research question: "How do LLMs support novice programming?")
```

See `scholar-cookbook.md` for the full `prov`, `verify`, and `pdf quote`
recipes.

## Bib hygiene the reader sees

- A title containing quotes gets `\mkbibquote{…}` around the inner quote
  (biblatex then nests it as single quotes; raw `` `` `` inside a quoted
  title prints `""…"`).
- A source read only in abstract, an edition other than the one cited, or
  a page number *inferred* from a folio-less copy is said so in
  `VERIFIED` — and the appendix's limitations paragraph repeats it.
- **Citation keys.** Every `.bib` scholar writes (`search -f bibtex` and
  `bibtex+prov`, `sessions export`, `llm synthesize`) uses one scheme
  (dbosk/scholar#115): the first author's surname reduced to letters and
  digits — the part before the comma in "Smith, John" — then the year or
  `nd`, with `a`, `b`, … on a clash: `smith2024`, `smith2024a`,
  `obrien2024` for O'Brien. DBLP's homonym numbers ("Wei Wang 0001") are
  stripped at ingest (#125), so keys like `00012024` no longer appear.
  A `.bib` from an older scholar may carry other keys for the same works
  (`john2024_0`, `smith2024b` for the first clash). Do not merge the two
  blindly: keep the keys the prose already cites, or rename them in the
  prose and the `% === provenance: <key> ===` header together
  (`check_provenance.py` warns on a header that no longer matches).
  `scholar prov import/export` match a block to its entry by paper id
  (DOI, else a title+author hash), not by key, so provenance follows the
  paper through a rename.

## Validating

```bash
scripts/check_provenance.py refs.bib          # full report, exit 1 on any error
scripts/check_provenance.py --quiet refs/*.bib  # print only files that fail
scripts/check_provenance.py --quotes refs.bib   # + each QUOTE in the full text
scripts/check_provenance.py --fetch refs.bib    # + download missing full texts
```

Run it before committing a `.bib`, and consider it in a pre-commit hook for
projects where every reference must be backed.

**Errors (exit 1):** a missing block; a missing or empty required field
(`COUNTER` included); a placeholder (an unquoted `TODO`, a `<template>`, the
location `(<loc>)`); a `VERIFIED` that does not begin with `full-text` or
`abstract`, or names a title, snippet, `tldr`, summary or memory; an
`abstract` `VERIFIED` on a claim with a causal verb (causes, improves,
reduces, increases, decreases, prevents, leads to) or a quantity (`15%`,
`3-fold`, `by 2`), unless marked as corroboration; a `COUNTER` that does
not name its search, or a `see <key>` to an entry that does not. A fresh
`-f bibtex+prov` stub therefore **fails** until its judgement fields and a
`COUNTER` line are written: the stub is a start, not a record. A word "TODO"
that belongs to a claim (a study of TODO comments) is written in quotes,
`"TODO"`, and is then not taken for a placeholder. **Warnings:** no `DATE`,
no or a mismatched header, a `QUOTE` without a quoted passage or a location.

**`--quotes`** looks every `QUOTE` up in the paper's text. The quoted
passage is split at ellipses (`...`, `…`, `[...]`) and bracketed insertions,
and each fragment must occur, in order; both sides are compared as
case-folded letters and digits only, so line breaks, hyphenation at line
ends, punctuation, quote marks, ligatures and accents do not count. The
text is looked for in `--text KEY=PATH`, `--fulltext-dir DIR`
(`DIR/<key>.pdf` or `.txt`, e.g. the curl downloads of `closed-access.md`),
the entry's `file` field, scholar's PDF cache (the file `fetch_pdf.py` or
`scholar pdf quote` left for the entry's `url`, `pdf` or
`https://doi.org/<doi>`; `SCHOLAR_CACHE_DIR` is honoured) and the entry's
`abstract` field. The cache is keyed by the PDF's URL, and a PDF fetched by
DOI is cached under the URL it was found at, so an entry with only a DOI
needs `--fetch` (network: `fetch_pdf.py --text`, through scholar's route,
into the cache) or `--text`. A PDF is read with `pdftotext` in reading
order and in content-stream order (`-raw`); either may split a sentence the
other keeps whole. A quote found in none of the texts is an error; an entry
with no text, or a non-abstract quote with only the abstract field to look
in, is a warning ("not checked"). The check confirms the words, not the
locator, and not that the passage entails the claim.
