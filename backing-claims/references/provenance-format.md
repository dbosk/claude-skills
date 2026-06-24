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
- [Migrating a `scholar rq` session into `FOUND-VIA`](#migrating-a-scholar-rq-session-into-found-via)
- [Validating](#validating)

## Schema

```bibtex
% === provenance: <bibkey> ===
% CLAIM: <the exact claim this reference backs>
% FOUND-VIA: <reproducible tool + provider + query>
% PICKED: <why this source among the results>
% QUOTE (<location>): "<verbatim passage that supports CLAIM>"
% VERIFIED: <abstract | full-text> ; applies because <one line>
% DATE: <YYYY-MM-DD>
@<type>{<bibkey>, ... }
```

Required: `CLAIM`, `FOUND-VIA`, `PICKED`, `QUOTE`, `VERIFIED`.
Recommended: `DATE` (warning if missing). The header line
`% === provenance: <bibkey> ===` is recommended and should match the entry key.

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
- **VERIFIED** — what you actually read (`abstract` or `full-text`) and a
  one-line reason it applies. This is the auditable record of the double-check;
  "title only" is never acceptable.
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
% DATE: 2026-06-24
@article{HattieTimperley2007, ... }
```

## Migrating a `scholar rq` session into `FOUND-VIA`

`scholar rq` records the provider-specific queries it generated for
reproducibility. Pull them into `FOUND-VIA` rather than paraphrasing:

```bash
scholar sessions list
scholar notes show "<paper title or id>"     # see recorded query/labels for a kept paper
```

Then write, e.g.:

```bibtex
% FOUND-VIA: scholar rq "How do LLMs support novice programming?" -p openalex -p dblp
%   (session "llm-novice-programming"; openalex query: "large language models" novice programming)
```

## Validating

```bash
scripts/check_provenance.py refs.bib          # full report, exit 1 on any error
scripts/check_provenance.py --quiet refs/*.bib  # print only files that fail
```

Run it before committing a `.bib`, and consider it in a pre-commit hook for
projects where every reference must be backed.
