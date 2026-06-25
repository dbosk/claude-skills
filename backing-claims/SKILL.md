---
name: backing-claims
description: |
  Back factual and empirical claims with scientific literature that has been verified to actually support the claim, and record the provenance of each citation (how it was found, why it was picked, and the verbatim quote that supports the claim). Use proactively when: (1) adding a citation to a factual, empirical, or theoretical claim in prose, .tex, .nw, or notes, (2) the user asks to "find a reference for", "back this up", "cite this", "is this citation correct", or to verify that a citation actually applies, (3) writing a related-work, background, or claims section, (4) the user mentions scholar/scholarcli, BibTeX, DOI, Semantic Scholar, arXiv, OpenAlex, Crossref, or a literature search, (5) reviewing a .bib file for unsupported or undocumented references. Complements (does not replace) the writing-crypto and latex-writing skills, which own the citation markup; this skill owns finding, verifying, and justifying the reference.
---

# Backing Claims with Verified References

Back every claim with scientific literature you have **read and verified**, and
**record how you got there**. A citation is a load-bearing claim: it asserts that
a specific source supports a specific statement. This skill makes that assertion
auditable.

## Core principle

**Never cite from memory, from a title, or from a search-result snippet.** Open
the source, find the passage that supports the claim, and record it. A reference
that is merely *about the same topic* is not support — the quote must entail the
specific claim, at the claim's scope and strength.

Corollary: **the search tool is free, the documentation is not.** Use any source
you like — `scholar`, Google Scholar, a publisher database, WebSearch, a
colleague's tip — but every reference must carry a reproducible `FOUND-VIA`.

This skill owns *find → verify → record*. It hands the citation **markup** off to
`writing-crypto` (biblatex `\autocite`/`\ac`) and `latex-writing` (`\cite`
family). Do not duplicate that guidance here.

## The find → verify → record protocol

### 1. State the claim precisely

Write the claim as one sentence and note its **scope** (population, domain),
**strength** (does it say *causes*, *correlates*, *can*, *always*?), and whether
it needs a **primary** source (an original finding/definition) or a **survey**
(an established consensus). The reference must match all three.

### 2. Find — prefer `scholar`, but any source counts

`scholar` is preferred because it records the query for you and searches several
databases at once. See `references/scholar-cookbook.md` for the non-interactive
recipes (`search`, `rq`, `enrich`, `verify`, `prov`, `providers`, `syntax`,
`notes`, `pdf`).

```bash
scholar search "authenticated encryption generic composition" -p s2 -p dblp -f bibtex
scholar rq "How do LLMs support novice programming?" -p openalex -p dblp --count 20
```

To get the BibTeX **already wrapped in provenance blocks** with `FOUND-VIA`
pre-filled from the query, use `-f bibtex+prov` (this is the easiest start —
you then fill in `CLAIM`/`PICKED`/`QUOTE`/`VERIFIED`):

```bash
scholar search "authenticated encryption generic composition" -p s2 -p dblp -f bibtex+prov
```

Any complementary source is allowed (Google Scholar, a publisher site, WebSearch
+ WebFetch, Crossref/DOI lookup, the `deep-research` skill for hard/contested
claims). Whatever you use, **capture the query/source verbatim** so `FOUND-VIA`
can be reproduced. `references/scholar-cookbook.md` shows how to phrase each
source's `FOUND-VIA` line.

`scholar snowball`, `scholar tuxedo`, and `scholar search --review` are
interactive TUIs — **do not** drive them from an agent; use the non-interactive
subcommands instead.

### 3. Screen and pick

Compare the top results and record **why this one**: primary source vs survey,
canonical/most-cited, reputable venue, appropriate year, closest match to the
claim's scope. When the choice is non-obvious, note the alternatives you
rejected and why — that reasoning is the `PICKED` field.

### 4. Verify applicability (the double-check)

Read the **actual source**, not just the title:

```bash
scholar enrich "<session>"            # fill in missing abstracts via DOI
scholar pdf open "<pdf-url>"          # download + open full text
scholar pdf quote "<pdf-url>" --claim "<the claim>"   # surface candidate QUOTE passages
scholar verify "<session>"            # flag retracted/corrected/superseded papers
# or WebFetch the publisher/arXiv page to read the relevant section
```

`scholar pdf quote` proposes candidate supporting passages (with location) — the
**judgement stays yours**; read the passage and confirm it entails the claim.
`scholar verify` runs the currency/retraction test for you via Crossref.

Extract a **verbatim** passage that supports the claim, and apply the tests in
`references/verification-checklist.md` (scope/strength match, primary vs
secondary "citation of a citation", over-claiming, contested/retracted work,
predatory venue, quote actually *entails* the claim). If the source does not
genuinely support the claim, discard it and return to step 2 — do not weaken the
quote to fit. Escalate hard or contested claims to the `deep-research` skill.

### 5. Record provenance, then emit the citation

Write the provenance comment block **immediately above** the BibTeX entry, then
write the citation in the project's style (defer to `writing-crypto` /
`latex-writing`). Full schema and worked examples:
`references/provenance-format.md`.

```bibtex
% === provenance: BellareNamprempre2000 ===
% CLAIM: Authenticated encryption provides both confidentiality and integrity.
% FOUND-VIA: scholar search "authenticated encryption generic composition" -p s2 -p dblp
% PICKED: canonical, most-cited primary source that defines the notion (not a survey).
% QUOTE (§1): "an authenticated encryption scheme ... provides both privacy and authenticity"
% VERIFIED: full-text PDF read; applies because it defines AE as exactly C+I.
% DATE: 2026-06-24
@inproceedings{BellareNamprempre2000, ... }
```

Required fields: `CLAIM`, `FOUND-VIA`, `PICKED`, `QUOTE`, `VERIFIED`
(`DATE` recommended). You do not have to type the skeleton by hand:

```bash
scholar search "..." -f bibtex+prov     # entries pre-wrapped, FOUND-VIA + DATE filled
scholar prov found-via "<paper-id>"     # reproducible FOUND-VIA line for one paper
scholar prov export refs.bib --in-place # write notes' provenance blocks above entries
scholar prov import refs.bib            # pull .bib provenance blocks back into notes
```

Validate any `.bib` you touch:

```bash
scripts/check_provenance.py refs.bib        # exit 1 if any entry lacks provenance
```

## Anti-patterns

| ✗ Wrong | ✓ Right |
|---------|---------|
| Cite a paper by its title or abstract snippet. | Read the source; paste the verbatim `QUOTE` that supports the claim. |
| Cite a survey for a specific primary finding. | Cite the primary source; use surveys only for "it is well established that…". |
| `QUOTE` is on-topic but doesn't entail the claim. | `QUOTE` matches the claim's scope **and** strength, or pick a better source. |
| No record of how the paper was found. | `FOUND-VIA` records the exact, reproducible query/source. |
| Over-claim beyond what the source shows. | Match the claim's strength to the evidence, or soften the prose. |

## Reference files

| File | Content | Search patterns |
|------|---------|-----------------|
| `references/provenance-format.md` | Full provenance schema, field semantics, worked examples, migrating a `scholar rq` session into `FOUND-VIA` | `FOUND-VIA`, `QUOTE`, `VERIFIED`, `multi-line` |
| `references/verification-checklist.md` | Applicability tests for deciding whether a source really supports a claim | `scope`, `primary vs secondary`, `over-claim`, `retraction`, `venue` |
| `references/scholar-cookbook.md` | Non-interactive `scholar` recipes (incl. `bibtex+prov`, `prov`, `verify`, `pdf quote`) + how to phrase `FOUND-VIA` for non-`scholar` sources | `bibtex+prov`, `prov found-via`, `pdf quote`, `verify`, `WebFetch`, `Crossref` |
| `references/scholar-enhancements.md` | Record of shipped provenance support (#49–#53) and a place for future ideas | `shipped`, `gh issue`, `future ideas` |

## Workflow checklist

- [ ] Claim stated with scope and strength
- [ ] Found via a recorded, reproducible query/source
- [ ] Picked with a written rationale among alternatives
- [ ] Source actually read (abstract or full text), not just the title
- [ ] Verbatim supporting quote captured, entails the claim
- [ ] Provenance block written above the entry; `check_provenance.py` passes
- [ ] Citation emitted in the project's markup style (writing-crypto / latex-writing)
