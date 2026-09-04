---
name: backing-claims
description: |
  Back factual and empirical claims with a small two-sided literature review — searches for literature that supports AND refutes/qualifies the claim (COUNTER) — verify sources in full text, and record provenance (how found, why picked, quote, counter-search outcome). Format-independent: papers, reports, memos, evidence logs, survey answers — any output resting on a factual claim, not just TeX. Use proactively when: (1) adding OR reusing a citation, page number, or attribution for a factual/empirical claim (inherited citations are NOT pre-verified), (2) attributing a claim to a source ("X found that…"), (3) the user asks to find a reference or check a citation — or wants an answer or decision backed by evidence, research, or literature, (4) writing related-work, background, or claims sections, (5) mentions of scholar, BibTeX, DOI, arXiv, OpenAlex, Crossref, or a literature search. (6) DELEGATING literature research to a subagent or teammate — the subagent prompt must tell it to load this skill, run every search under a named scholar session, and document alphaXiv/WebSearch complements in the appendix (see "Delegating research to subagents"). Trigger BEFORE citing; this skill owns finding/verifying/justifying the reference (markup: writing-crypto/latex-writing).
---

# Backing Claims with Verified References

Back every claim with scientific literature you have **read and verified**, and
**record how you got there**. A citation is a load-bearing claim: it asserts that
a specific source supports a specific statement. This skill makes that assertion
auditable.

The protocol is **format-independent**: it applies wherever a claim rests on a
source — a paper, a report or memo, an evidence log, a survey or questionnaire
answer, a recommendation given in conversation. The find → verify → record core
is always the same; only the *recording surface* differs (BibTeX provenance
blocks for papers, the deliverable's own evidence log or notes otherwise), and
the paper-appendix section at the end applies only when the output is a paper.

Backing a claim is a **small literature review, in both directions**: search
for literature that *supports* the claim **and** for literature that *refutes
or qualifies* it. One agreeable source is not backing — it is confirmation.
The claim earns its citation only after the counter-search: refuting work is
cited or the claim softened; qualifying work narrows the scope; an empty
counter-search is recorded as such.

## Core principle

**Never cite from memory, from a title, or from a search-result snippet.** Open
the source, find the passage that supports the claim, and record it. A reference
that is merely *about the same topic* is not support — the quote must entail the
specific claim, at the claim's scope and strength.

Corollary: **the search tool is free, the documentation is not.** Use any source
you like — `scholar`, Google Scholar, a publisher database, WebSearch, a
colleague's tip — but every reference must carry a reproducible `FOUND-VIA`.

Corollary: **an inherited citation is not a verified one.** A key that already
exists in the `.bib`, or one carried over from slides, notes, a draft, or an
earlier version, asserts support you have not personally checked. Verify it
against the source the first time you commit it to prose — and re-verify every
**page number** and every **"X reports/found/shows that…"** attribution you
write, since those are fresh claims even when the citation key is old. "The
cite was already there" is not evidence that it is correct. Trigger this skill
*while writing the sentence*, not only when a reviewer later asks.

This skill owns *find → verify → record*. It hands the citation **markup** off to
`writing-crypto` (biblatex `\autocite`/`\ac`) and `latex-writing` (`\cite`
family). Do not duplicate that guidance here.

## The find → verify → record protocol

### 1. State the claim precisely

Write the claim as one sentence and note its **scope** (population, domain),
**strength** (does it say *causes*, *correlates*, *can*, *always*?), and whether
it needs a **primary** source (an original finding/definition) or a **survey**
(an established consensus). The reference must match all three.

### 2. Find — a small review in both directions, not a single confirming hit

Backing a claim is a **miniature literature review**, not a hunt for one
agreeable source. That means two things:

**Search topic-driven, not author-anchored.** Query by *concept*, screen what
surfaces, and only then verify. Starting from a list of expected names (the
"usual suspects") is confirmation bias in search form: it finds what you
already believed and misses the systematic review or the competing strand
sitting one query away. Author-anchored *retrieval* is fine once discovery is
done (fetching a known paper's full text); author-anchored *discovery* is not.

**Search both directions.** For every load-bearing claim, run at least one
**counter-search** — a query phrased to surface literature that *refutes,
contradicts, or qualifies* the claim ("criticism of X", "X does not hold",
"limitations of X", the rival theory's terms). Three outcomes, all recorded:

- *Refuting work found* → do not bury it. Soften the claim to what survives,
  or cite both sides ("X reports…, though Y found…"). A claim stated over
  known counter-evidence is worse than an uncited claim.
- *Qualifying work found* (holds only in a subpopulation, era, or method) →
  narrow the claim's scope to match.
- *Nothing found* → record the counter-query and its emptiness. Absence of
  refutation after a real search is itself part of the claim's backing;
  an unrun counter-search is not.

`scholar` is preferred because it records the query for you and searches several
databases at once. See `references/scholar-cookbook.md` for the non-interactive
recipes (`search`, `rq`, `enrich`, `verify`, `prov`, `providers`, `syntax`,
`notes`, `pdf`). Run each claim's (or claim-cluster's) searches under a named
session (`search -n <claim-slug>`) so support- and counter-queries land in one
auditable record.

```bash
scholar search "authenticated encryption generic composition" -p s2 -p dblp -f bibtex
scholar search "authenticated encryption composition insecure attacks" -p s2 -p dblp -f bibtex   # counter-search
scholar rq "How do LLMs support novice programming?" -p openalex -p dblp --count 20
```

**Query several providers, and check they are actually alive.** `scholar`
exposes `s2`, `openalex`, `dblp`, `wos`, `ieee`, `scopus`, `arxiv`. Do not
settle for one or two — a claim "not found" under a narrow or *silently
degraded* provider set is not a real negative. Run **`scholar providers
check`** first and note any provider reporting `key rejected` / not `ok`: a
dead key (e.g. an expired `S2_API_KEY` returning HTTP 403) silently drops
that database's coverage with only a warning, so you can spend a whole
session blind to Semantic Scholar without realizing it. For a claim that
matters, query at least s2 + openalex + dblp, and add wos/scopus (strong for
older and non-CS/education literature) when keys are configured.

**Keyword search is for discovery; use field/DOI retrieval for a known
item.** Relevance-ranked keyword search buries older and grey-literature
works under recent hits — the same paper you *know* exists can sit off the
first page on every provider. When you already know the title or DOI, retrieve
it directly instead:

```bash
# by DOI (works even when keyword ranking buried it)
curl -s "https://api.openalex.org/works/doi:10.2190/689T-1R2A-X4W4-29J2"   # OpenAlex
curl -s "https://api.crossref.org/works/10.2190/689T-1R2A-X4W4-29J2"       # Crossref
# by exact title, via provider field-search syntax (see `scholar syntax`)
scholar search 'TI=(language-independent conceptual bugs)' -p wos            # WoS: TI= TS= AU=
scholar search 'TITLE("Language-Independent Conceptual Bugs")' -p scopus     # Scopus: TITLE() AUTH()
scholar search 'ti:"visual program simulation"' -p arxiv                     # arXiv: ti: au:
```

**The user's own library may hold it.** Before declaring a book or a
closed-access paper unobtainable, search the user's reMarkable library
(`remarkable_browse(query=…)`, then `remarkable_read(…, content_type="raw",
grep=…)` to locate the passage and its printed page). Books cited by chapter
or page (Gamma et al., Marton, Martin) and closed journal articles the user
has read are often there; delegate the page-by-page reading to a subagent.
Record such a retrieval as `FOUND-VIA: known item, read on the user's
reMarkable (<tablet path>)`.

**Grey literature may be in none of them.** Conference papers without a DOI
(e.g. AERA/education proceedings), dissertations, and tech reports are often
absent from OpenAlex, DBLP, WoS *and* Scopus — a `TI=`/`TITLE()` field search
returning empty on all of them means "not indexed here", not "does not
exist". Reach those via **Google Scholar** (WebSearch/`scholarly`), **citation
chaining** (find a paper you already have that cites the target and walk its
reference list — the most reliable route to a specific known work, but only
through a provider that indexes the target), or the **author's/publisher's
own copy**. Record such a retrieval honestly in `FOUND-VIA` (e.g. "not
returned by provider search; retrieved from author copy") — do not imply it
came from a database that does not hold it.

To get the BibTeX **already wrapped in provenance blocks** with `FOUND-VIA`
pre-filled from the query, use `-f bibtex+prov` (this is the easiest start —
you then fill in `CLAIM`/`PICKED`/`QUOTE`/`VERIFIED`):

```bash
scholar search "authenticated encryption generic composition" -p s2 -p dblp -f bibtex+prov
```

**Complementary sources are allowed — and every one of them is documented.**
Google Scholar, a publisher site, alphaXiv, WebSearch + WebFetch, Crossref/
OpenAlex/DataCite REST lookups, the `deep-research` skill for hard/contested
claims: use them whenever `scholar` is down, rate-limited, or does not index
the venue (grey literature, ACM proceedings when `s2` is dead). The rule is
not *which* tool but *what is recorded*: **capture the tool and the query/URL
verbatim** in `FOUND-VIA`/`COUNTER`, **and** list every non-`scholar` search
(tool, verbatim query, date, retained/dropped) in the search-protocol
appendix or the deliverable's evidence log. A complement that is not written
down did not happen; a complement that is written down is as good as a
`scholar` session. `references/scholar-cookbook.md` shows how to phrase each
source's `FOUND-VIA` line.

Two operational notes from real sessions: run **`scholar providers check`**
before searching and record its output (a rejected `s2` key or a 429-throttled
`openalex` silently drops coverage); and phrase **counter-searches with field
syntax** (WoS `TS=("cyclomatic complexity" AND (critique OR criticism))`,
Scopus `TITLE-ABS-KEY(...)`) — natural-language counter-queries such as
"maintainability index criticism limitations" returned only off-topic hits
on WoS/OpenAlex, so a "nothing found" from them is not a real negative.

Two rules that a reviewer had to add after a real appendix broke them:

- **Same queries, all providers.** Run *every* query — support and counter —
  on the *same* full set of live providers. When a provider needs field
  syntax, translate the *same* keywords into it; never one keyword set on
  WoS and a different one on Scopus. Record a query × provider × hits
  matrix; a cell may be empty only because a provider was down.
- **Vocabulary symmetry.** The counter-search uses every concept term the
  support search used, plus the field's indexed names for the concept (the
  practitioner name — "DRY" — is often unindexed; the academic name — "code
  clones", "code duplication" — is where the literature is). Never write
  "the concept is indexed as X and Y" unless both were searched in both
  directions.

**No `scholar` in the environment?** The protocol does not depend on it. Run the
same two-sided searches with WebSearch, and verify existence and content with
direct API/page retrieval — `api.crossref.org/works/<doi>`,
`api.openalex.org/works/doi:<doi>`, or WebFetch of the publisher's or issuing
organization's own page. A source whose existence cannot be verified this way is
**dropped and recorded as dropped**, never cited.

`scholar snowball`, `scholar tuxedo`, and `scholar search --review` are
interactive TUIs — **do not** drive them from an agent; use the non-interactive
subcommands instead.

### 3. Screen into supporting / refuting / qualifying, then pick

Sort the combined results of the support- and counter-searches into three
piles — **supports**, **refutes/contradicts**, **qualifies** — before picking
anything. This sorted screen *is* the small literature review; it decides
whether the claim survives as stated, gets narrowed, or gets a two-sided
citation. Only then pick which source(s) to cite, and record **why this one**:
primary source vs survey, canonical/most-cited, reputable venue, appropriate
year, closest match to the claim's scope. When the choice is non-obvious, note
the alternatives you rejected and why — that reasoning is the `PICKED` field.
When several independent strands (different subfields, different query
framings) converge on the same answer, say so — convergence across strands
backs a claim more strongly than any single source.

**Relevance is about bearing on the claim, not novelty.** A source that makes
the *same* point as one you already cite is **corroboration**: additional
support strengthens the claim, it does not weaken it. Never discard a source
from the "supports" pile because it is "redundant" or "already covered" —
that quietly biases the review toward under-citing agreement. Cite the
strongest/most-central source(s) for economy, and record the rest as
**supporting** (corroborating), not as excluded. This matters most when the
supporting pile is large and you are tempted to prune it: prune for *economy*
(cite the canonical one), and label the remainder honestly as corroboration in
the appendix — do not relabel corroboration as a reason for exclusion.
**Corroboration is cited, not exported**: each corroborating source gets a
verified bib entry (full text where obtainable, else abstract-level and
flagged in `VERIFIED`) and a citation with its one-clause finding in the
appendix. "Six further studies agree, see the export" is not a citation.

### 4. Verify applicability (the double-check)

Read the **actual source**, not just the title:

```bash
scholar enrich "<session>"            # fill in missing abstracts via DOI
scripts/fetch_pdf.py --text "<pdf-url-or-doi>"   # download into scholar's PDF cache, no viewer; prints cache + text paths
scholar pdf quote "<pdf-url>" --claim "<the claim>"   # surface candidate QUOTE passages
scholar verify "<session>"            # flag retracted/corrected/superseded papers
# or WebFetch the publisher/arXiv page to read the relevant section
```

**Fetch every full text through scholar's cache, never with a bare `curl` or
WebFetch into a scratch directory.** `scripts/fetch_pdf.py` calls scholar's
own downloader, so the file lands in the PDF cache (`scholar pdf path`,
keyed by the URL) and a later session asking for the same URL or DOI gets it
without fetching again; with `--text` it also leaves a `pdftotext -layout`
extraction beside the PDF for grepping. It accepts DOIs (resolved via
Unpaywall / Semantic Scholar) and direct URLs, and prints one TSV line per
source. Do not use `scholar pdf open` from an agent: it always launches the
system viewer. A source that only exists as plain text (an RFC `.txt`, an
HTML documentation page) is not a PDF and cannot be cached this way — record
its URL and access date in the provenance block instead.

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

The provenance fields — `CLAIM`, `FOUND-VIA`, `PICKED`, `QUOTE`, `VERIFIED`,
`COUNTER`, `DATE` — are format-independent; only where they live depends on the
deliverable. In a paper, write them as a comment block **immediately above** the
BibTeX entry, then write the citation in the project's style (defer to
`writing-crypto` / `latex-writing`). In any other deliverable (a report, memo,
evidence log, or answer), record the same fields per source in the deliverable's
own log or notes — a citation without them is unbacked regardless of format.
Full schema and worked examples: `references/provenance-format.md`.

```bibtex
% === provenance: BellareNamprempre2000 ===
% CLAIM: Authenticated encryption provides both confidentiality and integrity.
% FOUND-VIA: scholar search "authenticated encryption generic composition" -p s2 -p dblp
% PICKED: canonical, most-cited primary source that defines the notion (not a survey).
% QUOTE (§1): "an authenticated encryption scheme ... provides both privacy and authenticity"
% VERIFIED: full-text PDF read; applies because it defines AE as exactly C+I.
% COUNTER: scholar search "authenticated encryption composition insecure
%   attacks" -p s2 -p dblp -- surfaced attacks on *specific compositions*
%   (E&M with weak MACs), none refuting the definition itself; claim stands.
% DATE: 2026-06-24
@inproceedings{BellareNamprempre2000, ... }
```

Required fields: `CLAIM`, `FOUND-VIA`, `PICKED`, `QUOTE`, `VERIFIED`
(`DATE` recommended). For load-bearing claims also record `COUNTER`: the
counter-search query and its outcome — refuting/qualifying work found (and
how the claim was adjusted or the other side cited), or explicitly
"none found". You do not have to type the skeleton by hand:

```bash
scholar search "..." -f bibtex+prov     # entries pre-wrapped, FOUND-VIA + DATE filled
scholar prov found-via "<paper-id>"     # reproducible FOUND-VIA line for one paper
scholar prov export refs.bib --in-place # write notes' provenance blocks above entries
scholar prov import refs.bib            # pull .bib provenance blocks back into notes
```

Validate any `.bib` you touch:

```bash
scripts/check_provenance.py refs.bib        # exit 1 if any entry lacks provenance
scripts/check_metadata.py refs.bib [...]    # cross-check every DOI entry's
                                            # title/authors/year against Crossref
```

**Self- and companion-references are references too.** Author names and
metadata for the user's own or companion papers are copied from the source
repo's `\author{}` block, never written from memory — a fabricated
co-author name is the canonical failure here. After any bib work, run
`check_metadata.py` over the touched files; treat diacritic and subtitle
differences as benign, investigate everything else.

**Bib hygiene the reader sees.** A title containing quotes gets
`\mkbibquote{…}` around the inner quote (biblatex then nests it as single
quotes; raw `` `` `` inside a quoted title prints `""…"`). A source read
only in abstract, an edition other than the one cited, or a page number
*inferred* from a folio-less copy is said so in `VERIFIED` — and the
appendix's limitations paragraph repeats it.

## Mirror the searches into a paper appendix

When the citations belong to a paper, the searches must also surface as a
**backing appendix** in the paper itself — **one chapter per backed claim,
each a short, reproducible, self-contained paper** that a reader without the
repository can follow. `references/appendix-guide.md` is the authority
(skeleton, rules, LaTeX templates, checklist); the essentials:

- **By claim, not by search episode.** Each chapter opens with the *factual
  claim* as its research question ("Is X true? How well-established is X?"),
  never a question about a reference. Split mixed claims: *origin* ("from
  author A") is a known-item verification; *establishment* ("an established
  method") is an empirical claim about status in the field that the
  originator's paper cannot back — it needs evidence of adoption **and** a
  counter-search. "The belief is a known-item verification" written about
  anything containing "established/standard/proven" is the tell that you
  are backing the reference instead of the fact.
- **Mini-paper skeleton:** intro (claim cited at first mention, RQ,
  strength) → method (date, providers and their health, session name, a
  **query × provider × hits table**, how known items were retrieved and
  verified) → results per sub-question with every source cited → discussion
  and limitations → conclusion whose first sentence answers the RQ → the
  **full classified hit list as a table** at the end.
- **Self-contained.** Every source cited with a full reference; URLs as bib
  entries or footnotes, never inline; corroborating studies cited with a
  finding each. **No export paths, bib file names or CSV columns in the
  compiled text** — those are for the author and go in `%` comments next to
  the table's `\input` and in the bib provenance blocks.
- **Redo, don't narrate — and never do worse.** A search that was
  author-driven, partial, malformed or noisy is redone under the rules
  and only the redone search is documented; the appendix's limitations
  are facts about the data and tools, not the author's earlier attempts.
  A redo must recover every relevant result of the search it replaces —
  close gaps by improving the *concept* queries, never by searching for
  the missing paper by name. Session names are author-only — one `%`
  block per chapter with session, exports, date, providers and health,
  classification model and overrides, the exact table command and the
  bib keys; query-table captions introduce every abbreviation full name
  first ("OpenAlex (OA; not open access)") and sit in the margin
  (`sidecaption`).
- **The hit list is classified and included.** `scholar llm context` +
  `scholar llm classify --no-examples` over the whole session (two-sided
  tags: supports-claim / qualifies-claim / adjacent-subtopic /
  off-topic-false-hit; theme tags on the cited ones), read the
  low-confidence and every qualifying row yourself, then generate the table
  with `scholar sessions export <session> -f table --bearing-only --lang sv
  --label … --track … --theme TAG=NAME -o <base>` (fallback for older
  scholar: `scripts/session_table.py --csv <export.csv>`, same output).
  Model confidence shows per row; the caption counts both sides.

Run each round's searches under one named `scholar` session per paper and
commit the `sessions export` output to the repo — the export is the audit
record, the table in the appendix is what the reader gets. Update the
appendix in the same commit as the search.

## Delegating research to subagents

A literature search delegated to a subagent (Agent tool, Workflow script,
teammate) is still bound by this protocol, and the subagent does not inherit
it: it inherits only its prompt. Delegating without saying so produced, in one
session, three agents that cited from WebSearch snippets with no `scholar`
session to audit — and had to be redirected mid-run. So the **orchestrator
loads this skill first** and puts the protocol in the prompt. Start the
subagent prompt with this preamble (adapt the slug and paths):

```
Load the `backing-claims` skill (Skill tool: skill="backing-claims") and
follow it. Run `scholar providers check` first and record which providers
are alive. Run EVERY search under one named session:
  scholar search "<topic query>" -n <claim-slug> -p dblp -p wos -p ieee
    -p openalex -p scopus -f bibtex+prov
Run every query -- support AND counter -- on the SAME full set of live
providers (translate the same keywords into WoS TS=(...) / Scopus
TITLE-ABS-KEY(...) where needed; never different keyword sets per
provider) and record a query x provider x hits matrix. If an earlier
query in the session was author-driven, partial or malformed, rerun it
properly and mark the old one superseded; a redo must recover every
relevant result of the search it replaces -- close gaps by improving the
concept queries, never by searching for the missing paper by name. Search
topic-driven (by concept), not by author name; retrieve known items by
DOI (curl https://api.crossref.org/works/<doi>) or field search
(scholar search 'TI=(...)' -p wos). For every claim run COUNTER-searches
that reuse every concept term of the support searches plus the field's
indexed names for the concept. Verify each source by opening it (scholar
pdf quote / WebFetch of the publisher or an OA copy) and capture a
VERBATIM quote with locator. Corroborating sources get verified entries
too (abstract-level flagged as such), not a mention. alphaXiv, WebSearch
and WebFetch MAY complement scholar, but every such query must be
recorded verbatim (tool, query, outcome) in FOUND-VIA/COUNTER and in a
"Search protocol" section of your report. Classify the WHOLE session
(scholar llm context; scholar llm classify --no-examples; tags
supports-claim / qualifies-claim / adjacent-subtopic / off-topic-false-hit,
theme tags on cited papers; read low-confidence and qualifying rows
yourself) and export it (scholar sessions export) so the audit table can
be generated. Write a .bib with a provenance block (CLAIM / FOUND-VIA /
PICKED / QUOTE / VERIFIED / COUNTER / DATE) above every entry to
<scratchpad>/<slug>.bib and run <skill>/scripts/check_provenance.py on
it. Sources you cannot verify are listed as DROPPED, never cited. Write
the COMPLETE report to <scratchpad>/<slug>-report.md (agent replies are
truncated at ~4 KB) and reply with a one-paragraph summary plus the paths.
```

Then, when the reports arrive: read the `.bib` files rather than the
summaries, merge them into the deliverable's bibliography (deduplicating
keys — the same work often surfaces in two agents' sessions under different
keys), and build the appendix from the reports' search-protocol sections.
Papers the agents could not obtain are the user's to fetch: hand them over
as todos (the `nytid-todo` skill has the pattern), ordered load-bearing
first.

## Anti-patterns

| ✗ Wrong | ✓ Right |
|---------|---------|
| Cite a paper by its title or abstract snippet. | Read the source; paste the verbatim `QUOTE` that supports the claim. |
| Cite a survey for a specific primary finding. | Cite the primary source; use surveys only for "it is well established that…". |
| `QUOTE` is on-topic but doesn't entail the claim. | `QUOTE` matches the claim's scope **and** strength, or pick a better source. |
| No record of how the paper was found. | `FOUND-VIA` records the exact, reproducible query/source. |
| Over-claim beyond what the source shows. | Match the claim's strength to the evidence, or soften the prose. |
| Search only for confirmation (one agreeable source, then stop). | Small review both ways: support-search **and** counter-search; sort into supports/refutes/qualifies; record `COUNTER`. |
| Discover literature by querying expected author names. | Discover topic-driven (by concept); use names only to *retrieve* already-identified works. |
| Refuting/qualifying work found but not mentioned. | Soften or narrow the claim, or cite both sides — never state a claim over known counter-evidence. |
| Drop a source as "redundant" because it agrees with one already cited. | Keep it as corroboration — convergent support strengthens the claim; cite the strongest for economy and list the rest as "supports the claim". |
| Screen the full hit-list from titles alone. | Enrich abstracts, classify against a stated research context (`scholar llm classify`) with confidence, then override the model's weak/wrong calls by reading. |
| Bury several claims under one method-organized "search protocol" appendix. | One appendix chapter per claim, each stating the claim as its research question and standalone; depth scales (full sweep vs known-item verification). |
| Back "X is an *established* method" with a quote from X's originator. | The originator shows X was *proposed*, not *adopted*; investigate establishment (formalization, textbooks, adoption, descendants) AND counter-search for criticism — a two-sided review. |
| "Document" a counter-search by naming its session in passing. | A Method paragraph with the verbatim queries, providers, date, and export path — reproducible from the appendix text alone. |
| Chapter's answer buried mid-chapter; it ends on raw hit-list tables. | A Conclusion answers the research question explicitly; the tables follow it as audit data. |
| Search one or two providers; trust a "not found". | Query several (`s2 openalex dblp wos scopus`); run `scholar providers check` first — a dead key (S2 403) silently drops a database. |
| Delegate a literature search with "use WebSearch/alphaXiv" and no protocol. | Load this skill first; the subagent prompt carries the preamble above (named `scholar` session, counter-searches, provenance `.bib`, documented complements, report to a file). |
| Use alphaXiv/WebSearch and mention it in passing. | Record the tool and verbatim query in `FOUND-VIA`/`COUNTER` **and** in the search-protocol appendix — undocumented complements are unbacked. |
| Keyword-search for a paper whose title/DOI you already know. | Retrieve known items by DOI (OpenAlex `works/doi:`, Crossref) or field search (WoS `TI=`, Scopus `TITLE()`); Google Scholar / citation-chain / author copy for grey lit. |
| One counter-query on WoS, a different one on Scopus. | The same query on every live provider (same keywords, translated into each field syntax); a query × provider × hits matrix in the appendix. |
| "Six further studies agree — they are in the export." | Each corroborating study verified, in the bib, and cited with its one-clause finding. |
| "The export lies in `litteratursokning/x.csv`" in the compiled appendix; URLs inline in prose. | Hit-list table `\input` at the end of the chapter; sources cited with bib entries/footnotes; paths only in `%` comments. |

## Reference files

| File | Content | Search patterns |
|------|---------|-----------------|
| `references/provenance-format.md` | Full provenance schema, field semantics, worked examples, migrating a `scholar rq` session into `FOUND-VIA` | `FOUND-VIA`, `QUOTE`, `VERIFIED`, `multi-line` |
| `references/verification-checklist.md` | Applicability tests for deciding whether a source really supports a claim | `scope`, `primary vs secondary`, `over-claim`, `retraction`, `venue` |
| `references/scholar-cookbook.md` | Non-interactive `scholar` recipes (incl. `bibtex+prov`, `prov`, `verify`, `pdf quote`) + how to phrase `FOUND-VIA` for non-`scholar` sources | `bibtex+prov`, `prov found-via`, `pdf quote`, `verify`, `WebFetch`, `Crossref` |
| `references/scholar-enhancements.md` | Record of shipped provenance support (#49–#53) and a place for future ideas | `shipped`, `gh issue`, `future ideas` |
| `references/appendix-guide.md` | The backing appendix as a short reproducible paper: skeleton, self-containment rules, query-table template, hit-list table generation, checklist | `Self-contained`, `Same queries`, `Vocabulary symmetry`, `Query table`, `session_table` |
| `scripts/session_table.py` | Fallback for `scholar sessions export -f table`: classified session CSV → the same auditable `longtable` (`--bearing-only`, `--lang sv|en`, `--theme`) | `--csv`, `--label`, `--theme` |

## Workflow checklist

- [ ] Claim stated with scope and strength
- [ ] Found via recorded, reproducible, **topic-driven** queries (names only for retrieval)
- [ ] Several providers queried and their **health checked** (`scholar providers check`); known items retrieved by DOI/field search, not buried keyword ranking
- [ ] **Counter-search run** and its outcome recorded (`COUNTER`): refuting/qualifying work handled, or "none found"
- [ ] Results screened into supports / refutes / qualifies; claim adjusted if needed
- [ ] Picked with a written rationale among alternatives
- [ ] Source actually read (abstract or full text), not just the title
- [ ] Verbatim supporting quote captured, entails the claim
- [ ] Provenance block written above the entry; `check_provenance.py` passes
- [ ] Citation emitted in the project's markup style (writing-crypto / latex-writing)
- [ ] Every query run on every live provider; counter vocabulary mirrors support (matrix recorded)
- [ ] Appendix self-contained: claim cited at first mention, corroborations cited, classified hit-list table included, no export paths/URLs in the compiled text (`references/appendix-guide.md` checklist)
