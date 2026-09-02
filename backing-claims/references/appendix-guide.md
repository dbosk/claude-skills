# The backing appendix as a short, reproducible paper

The appendix is read by people who do not have the repository: students,
reviewers, colleagues, the author in five years. Everything they need to
judge the claim and to redo the search must be **in the compiled text**.
Everything only the author needs — file paths, session exports, bib
provenance fields — goes into **source comments**, never into the PDF.

## One chapter per backed claim, each a mini-paper

1. **Intro** — point (`\cref`) to the main-text passage that makes the
   claim; state the claim **with its attribution cited at first mention**
   ("… principen DRY, efter Hunt och Thomas\autocite{HuntThomas1999}");
   pose the research question as a question about the *fact*, not about a
   reference; say what strength is being tested ("en risk, inte alltid
   fel"). Split mixed claims: origin (known-item) vs establishment
   (two-sided review).
2. **Method** — reproducible from the text alone: search date, tool,
   databases and their health that day, and a **query × database × hits
   table** (template below). Say which items were retrieved as known
   documents, why that is the right method for them (a pre-DOI journal,
   DOI-less proceedings, a book) and how each was verified (full text;
   OCR of a scan; abstract only). Session names, export paths and bib
   details are for the author: `%` comments, never the compiled text.
3. **Results**, one paragraph per sub-question — origin, establishment,
   criticism — every source cited with a full reference (footnote
   citation in verbose styles) and a verbatim quote with locator for the
   load-bearing ones. **Corroborating sources are cited here with a
   one-clause finding each**, not summarised as "six further studies
   agree, see the export".
4. **Discussion and limitations** — facts about the data and the tools: a
   dead provider, hit caps, a database's implicit AND, a phrase that is
   unindexed, a source available only in abstract, an inferred page
   number, an edition that could not be obtained. Not the author's earlier
   attempts (see "Redo, don't narrate"). Written plainly; a limitation
   stated is not a weakness of the appendix.
5. **Conclusion** — first sentence answers the research question ("Ja på
   båda frågorna, med ett förbehåll: …"); then the caveats and what they
   mean for how the claim is used in the main text.
6. **Hit list** — the classified session as a `longtable` at the end of
   the chapter (`\input{…-full}`), so the reader can audit the screening,
   not only the winners. When a topic-driven search returns thousands of
   records, list the rows that *bear on the claim* — cited, supporting,
   qualifying/contradicting — and give the adjacent and off-topic
   records as counts in the caption (`session_table.py --bearing-only`);
   the per-query totals are in the query table and the full record is in
   the session export named in the author block. The chapter's argument
   ends at the conclusion; the table is audit data after it.

A short chapter (known-item verification plus a light counter-search)
keeps the same skeleton as `\paragraph`s; a long one uses `\section`s.

## Rules the appendix must satisfy

### Self-contained

- Every work the text relies on is cited; a name in the prose ("efter Hunt
  och Thomas") carries a citation the first time it appears.
- URLs of sources go into bib entries or footnotes, never inline in prose
  as `\texttt{…}`. A publisher excerpt or an author's copy that was
  actually read gets a bib entry (edition, URL, urldate) and is cited.
- **No export paths, no bib file names, no CSV column names, no session
  names in the text.** Everything the *author* needs to verify and
  reproduce the chapter goes in one `%` block per chapter, placed above
  the query table (and repeated in short above the `\input` of the
  hit-list table) and in the bib provenance blocks. The block is
  complete when a future author can redo the search and rebuild the
  tables from it alone:

  ```latex
  % Author's note (verification and reproduction):
  %   scholar session : dry-principle
  %   exports         : litteratursokning/dry-principle.{csv,bib,tex}
  %   searched        : 2026-09-02; providers openalex dblp wos scopus ieee
  %                     (s2: key rejected, HTTP 403 -- absent)
  %   classification  : scholar llm context + llm classify --no-examples,
  %                     model github_copilot/gpt-5.4; 53 human overrides via
  %                     scholar sessions decide (read: every qualifies row,
  %                     every row < 0.7)
  %   hit-list table  : session_table.py --csv litteratursokning/dry-principle.csv
  %                     --label sok-dry --track "DRY-principen" --lang sv
  %                     --theme clones-faults="..." ...
  %   provenance      : ltnotes.bib, keys HuntThomas1999 ThomasHunt2019
  %                     Juergens2009Clones ... (CLAIM/FOUND-VIA/QUOTE/VERIFIED)
  \input{litteratursokning/dry-principle-full}
  ```

  The compiled text may say, once, in the general method chapter, that
  each source's provenance is recorded in the bibliography's source file
  with fixed fields — and explain the fields there.

### Same queries, all providers

Run **every** query — support and counter — on the **same full set of
live providers** (`scholar providers check` first). When a provider needs
field syntax (WoS `TS=`, Scopus `TITLE-ABS-KEY`), translate the *same*
keywords into it; never one keyword set on WoS and a different one on
Scopus. The query table makes this auditable: a row is a query, the
columns are providers, the cells are hit counts (or "—" when the query was
not run there, which the text must justify).

### Vocabulary symmetry

The counter-search uses every concept term the support search used, plus
the field's indexed names for the concept (the practitioner name — "DRY"
— is often unindexed; the academic name — "code clones", "code
duplication" — is where the literature is). Never write "the concept is
indexed as X and Y" unless both X and Y were searched in both directions.

### Redo, don't narrate

The appendix documents the method that produced the evidence, not the
history of attempts. A search that was author-driven, ran on a subset of
the providers, was malformed by shell quoting, or drowned in noise is
**redone under the rules and the redone search is documented**; the
earlier attempt is not chronicled ("track 1 was author-driven and that is
a weakness"; "the first round read six studies on their titles"). What
stays in the limitations are facts about the world: a provider was down,
counts are capped, a database applies an implicit AND, the practitioner
name of a concept is unindexed, a venue is not indexed so the item was
retrieved as a known document. Known-item retrieval of a primary source
is a method, stated as such — never "topic search failed, so…".

### A redo must not do worse

Before superseding a search, record its **baseline**: every source the
chapter cites and every row the old session marked supports/qualifies.
After the redone, topic-driven search, check by DOI or normalised title
that every baseline item is in the new session. Close a gap by
**improving the concept query** — synonyms, the field's own vocabulary
(the terms the literature uses for the concept, not the missing paper's
title), a broader or narrower phrasing, a second formulation of the same
concept — and iterate until coverage is at least the baseline. **Never**
by searching for the missing paper by author or title: "I'm missing X,
I'll search for X" is author-anchored discovery in disguise. Only an item
provably outside topic search on these providers (a pre-DOI journal,
DOI-less proceedings, a book) is retrieved as a known item, stated as
such. Report before/after coverage in the working notes; the appendix
shows only the final search.

### Corroboration is cited, not exported

A source that agrees with the cited one is *corroboration*: it gets a
verified bib entry (full text where obtainable, otherwise abstract-level
and flagged as such in `VERIFIED`) and a citation with its one-clause
finding in the results. Pruning for economy means citing the canonical
source *first*, not leaving the rest in a CSV.

### The hit-list table

Classify the whole session before writing the appendix:

```bash
scholar llm context <session> "<research question>; a paper is relevant
  if …; category tags: supports-claim = bears on the claim and supports it,
  qualifies-claim = bears on it and contradicts or narrows it,
  adjacent-subtopic = same field, different question,
  off-topic-false-hit = another field, keyword overlap only"
scholar llm classify <session> --no-examples -n <all pending>
scholar sessions export <session>          # csv with tags, confidence, source
```

Read the low-confidence rows and every `qualifies-claim` row yourself and
override with `scholar sessions decide` where the model is wrong; tag the
sources you cite with a theme tag (e.g. `dry-origin`) so they show as
*cited* with a reason. Then generate the table — with
`scholar sessions export --format table` once it exists, until then with
the skill's `scripts/session_table.py`:

```bash
~/.claude/skills/backing-claims/scripts/session_table.py \
  --csv litteratursokning/dry-principle.csv --label sok-dry \
  --track "DRY-principen" --lang sv \
  --theme dry-origin="principens ursprung" --theme clones-faults="klonfel" \
  -o litteratursokning/dry-principle-full.tex
```

Rows are grouped cited → supports → qualifies/contradicts → adjacent →
off-topic → still pending, with the model's confidence per machine-decided
row. Two-sided category names must appear in the caption counts so the
reader sees at a glance how much refuting/qualifying work there was.

## Query table template

The caption goes in the margin (memoir's `sidecaption`; the didactic
package provides a fallback environment for other classes), names the
date and the tool, and **introduces every abbreviation the sensible way
round — full name first, abbreviation in parentheses**: "OpenAlex (OA;
not open access)", "Web of Science (WoS)". No session name.

```latex
% Author's note (verification and reproduction): see the block above the
% hit-list \input at the end of the chapter.
\begin{table}[htbp]
  \begin{sidecaption}{Sökfrågor och antal träffar per databas,
    2026-09-02, verktyget \texttt{scholar}.  S = stödfråga, M = motfråga,
    K = känt dokument.  Databaser: OpenAlex (OA; inte
    \foreignlanguage{english}{open access}), DBLP, IEEE Xplore (IEEE),
    Web of Science (WoS), Scopus.  Högst 40 träffar per databas och fråga,
    så 40 betyder \enquote{minst 40}.  DBLP kräver att varje ord matchar.
    Web of Science fick nyckelorden som \texttt{TS=(\dots)}, Scopus som
    \texttt{TITLE-ABS-KEY(\dots)}, OpenAlex och IEEE som boolesk fritext,
    DBLP som ordlista.}[tab:dry-queries]
    \centering\footnotesize
    \begin{tabular}{@{}lp{0.5\linewidth}rrrrr@{}}
      \toprule
      & Nyckelord & OA & DBLP & IEEE & WoS & Scopus \\
      \midrule
      S1 & \enquote{code clones} inconsistent changes faults & 40 & 0 & 14 & 2 & 4 \\
      … \\
      M1 & \enquote{code clones} (beneficial, harmless eller \enquote{considered harmful}) & 40 & 0 & 40 & 19 & 31 \\
      \bottomrule
    \end{tabular}
  \end{sidecaption}
\end{table}
```

Prefix support queries S, counter queries M (motsökning) or C, known-item
retrievals K, and refer to them by label in the prose.

## Checklist for the appendix

- [ ] Claim cited at first mention; RQ about the fact; strength stated
- [ ] Method: date, tool, databases + health, side-captioned query ×
      database × hits table with the abbreviations defined; known-item
      retrievals justified and their verification mode stated
- [ ] Every query on every live provider; counter vocabulary mirrors support
- [ ] Redone searches recover every baseline item (coverage checked);
      no narration of earlier attempts; no session names in the text
- [ ] Results cite every source (load-bearing ones with verbatim quote and
      locator); corroborations cited with a finding each
- [ ] Limitations paragraph present and honest
- [ ] Conclusion's first sentence answers the RQ
- [ ] Session classified; hit-list table `\input` at the end, with
      two-sided counts in the caption
- [ ] No export paths, bib file names or CSV columns in the compiled text —
      all in `%` comments
- [ ] Bib: titles containing quotes use `\mkbibquote{…}`; inferred page
      numbers and abstract-only verification are marked in `VERIFIED`
