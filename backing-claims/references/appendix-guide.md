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
   table** (template below), its cells copied from `scholar sessions
   show`, where a failed search reads `failed (reason)`: such a cell is
   *failed*, never 0. Say which items were retrieved as known
   documents, why that is the right method for them (a pre-DOI journal,
   DOI-less proceedings, a book) and how each was verified (full text;
   OCR of a scan; abstract only). Session names, export paths and bib
   details are for the author: `%` comments, never the compiled text.
   The method also states, each in a sentence or two:
   - **when** each database answered: the search dates from `sessions
     show` (a cache hit carries its original fetch date), as the caption's
     "Searched A to B." gives them. PRISMA-S item 13: "For each search
     strategy, provide the date when the last search occurred."
   - **which search** a database ran when it has several: Semantic
     Scholar's bulk search (title and abstract, stemmed) or its relevance
     search (`s2 (via bulk)` in `sessions show`; cookbook, "Providers and
     keys").
   - **deduplication** (PRISMA-S item 16: "Describe the processes and any
     software used to deduplicate records from multiple database
     searches and other information sources."): scholar deduplicates a
     search's results (`search --dedup`, the default): copies with one
     id (DOI, else a title-and-author hash) merge, the richest copy as
     base, DOI-less copies only when their years are at most one apart;
     a DOI-less copy folds into the DOI copy of the same work; a
     preprint and its published version collapse onto the published
     one when the match is unambiguous. Copies that reach a session from different searches are listed
     by `sessions show` and folded by `sessions reconcile`; copies
     decided differently are settled by hand (say how many). Cite
     PRISMA-S (Rethlefsen et al., *Systematic Reviews* 10:39, 2021,
     doi:10.1186/s13643-020-01542-z) where the method follows it.
   - **who screened** (see "Who screened" below).
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
6. **Future work** (Swedish decks: `\section{Fortsatt arbete}`) — two
   halves, one to three short paragraphs, no new searches: (a) what *this*
   search left undone — providers that were down or quota-limited, sources
   read only at abstract level (cite them), sources found but not obtained
   (name them, DOI in a footnote), queries that could not be run; and (b)
   what the *field* lacks for a surer answer — the population never
   studied (e.g. Python novices), the sub-claim nobody tested, the kind of
   study that would settle it (controlled experiment, replication,
   longitudinal), and one sentence on how the main text would change if
   that study came out either way. This is the chapter's to-do list; it
   turns "with reservations" into work someone can pick up.
7. **Hit list** — the classified session as a `longtable` at the end of
   the chapter (`\input{…-full}`), so the reader can audit the screening,
   not only the winners. When a topic-driven search returns thousands of
   records, list the rows that *bear on the claim* — cited, supporting,
   qualifying/contradicting — and give the adjacent and off-topic
   records as counts in the caption (`scholar sessions export … -f table
   --bearing-only`);
   the per-query totals are in the query table and the full record is in
   the session export named in the author block. The chapter's argument
   ends at the conclusion; the table is audit data after it.

A short chapter (known-item verification plus a light counter-search)
keeps the same skeleton as `\paragraph`s; a long one uses `\section`s.

## Pointing at the appendix from the text

The appendix is only reachable if the main text points at it, and the pointer
is part of the claim, not an afterthought.

- **At the claim, once, as a footnote** (author, 2026-09-20: "Make it a
  rule to put those statements in a footnote"). The claim itself stays in
  the running text, stated at the strength the appendix supports; the
  sentence saying where the backing lives and what it answers ("Det
  vetenskapliga underlaget finns i \cref{app:dry} …" or, across decks,
  "… i föreläsningen \emph{Funktioner}, bilaga B") is a `\footnote`
  anchored right after the claim — never a sentence of the body, and never
  a trailing sentence further down, which reads as a note about the
  document rather than a warrant. One footnote per appendix per
  paragraph. (Before 2026-09-20 the pointer stood in the body as a
  parenthesis or clause; decks written that way are converted when next
  revised.)

- **A qualification goes in the pointer footnote.** When a backed claim
  comes with a qualification (the guide as a whole is not backed, the
  attribution cannot be verified), the running text keeps the claim at
  the strength the appendix supports, and the qualification moves into
  the appendix-pointer footnote, which follows the citation directly
  (author, 2026-09-23, first for PEP 8 — "Move to footnote 8, let
  footnote 8 follow immediately on 7" — then for KISS: "should follow the
  same pattern").

- **Say what the appendix answers.** "Se \cref{app:dry}" tells the reader
  nothing about whether to go there. Name the question the chapter settles:

  ```latex
  % vague
  Följ DRY-principen.\autocite{HuntThomas1999}  Underlaget finns i \cref{app:dry}.
  % says what is there
  Principen kommer från Hunt och Thomas\autocite{HuntThomas1999}, och risken
  den varnar för är verklig när kopior ändras olika --- \cref{app:dry} redovisar
  både var principen kommer ifrån och om den håller, med sina förbehåll.
  ```

- **Name the claim the pointer serves** when a paragraph carries several
  ("det vetenskapliga underlaget för DRY … finns i …"), and **cite a
  measured claim where it stands** — "erfarna utvecklare är mätbart oense
  om den\autocite{…}" keeps its sources in the sentence even though the
  appendix pointer follows a sentence later (the author's "Ref!" beside
  the clause, 2026-09-15).

- **State the claim at the strength the appendix supports.** The pointer makes
  the two checkable against each other: if the conclusion was "a risk, not an
  absolute rule", the sentence carrying the pointer may not say "always".
  Weakening the prose is the fix, not weakening the appendix.

- **`\cref` cannot cross documents.** When the backing lives in a *different*
  document (the claim was backed there and is reused here — see
  `provenance-format.md`), name the document and the appendix letter in words:
  "det vetenskapliga underlaget finns i föreläsningen \emph{Funktioner},
  bilaga~B". A dangling `\cref` to another document's label prints `??`.

- **A reused pointer states the finding, not the reuse.** When the
  backing lives in another document, the footnote says what that
  appendix found, same as "Say what the appendix answers" above — never
  that this material chose not to repeat the search: the author struck
  "Vi återanvänder svaret här i stället för att pröva det på nytt."
  (2026-09-29).

- **Point only backwards** (author, 2026-09-22: "We should only refer to
  appendices in previous notes or the current one"). In a series read in
  order (a course's lecture and tutorial notes), a pointer may name the
  current document or one the reader has already met, never one that
  comes later. When a later document holds the backing, **move the
  chapter to the first document that makes the claim** (with its
  provenance blocks, bibliography entries and hit-list tables), and let
  the document it came from point back to it. The order is the reading
  order the course's `CLAUDE.md` defines; check it for every cross-document
  pointer, including those in tables of Bilaga A.

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
  %                     (s2: key rejected, HTTP 403 -- absent; dblp:
  %                     failed, anti-bot page, every query)
  %   classification  : scholar llm context + llm classify --no-examples,
  %                     model github_copilot/gpt-5.4; 53 human overrides via
  %                     scholar sessions decide --source human (read: every
  %                     qualifies row, every row < 0.7)
  %   sample          : scholar llm sample dry-principle --discarded -n 50
  %                     --seed 20260902; --report: 3 of 50 changed
  %   hit-list table  : scholar sessions export dry-principle -f table
  %                     --bearing-only --lang sv --label sok-dry
  %                     --track "DRY-principen" --theme clones-faults="..." ...
  %                     -o litteratursokning/dry-principle-full
  %   provenance      : ltnotes.bib, keys HuntThomas1999 ThomasHunt2019
  %                     Juergens2009Clones ... (CLAIM/FOUND-VIA/QUOTE/VERIFIED)
  \input{litteratursokning/dry-principle-full}
  ```

  The compiled text may say, once, in the general method chapter, that
  each source's provenance is recorded in the bibliography's source file
  with fixed fields — and explain the fields there.

### One method chapter across a collection

In a collection of decks (a course, a book), Chapter A's generic
description — turning the claim into a question, choosing the right kind
of source, searching so you can be wrong, reading in full text, drawing
the hedged conclusion — is written in full once, in the first deck in
reading order. Every later deck's Chapter A keeps its opening, its
summary of that deck's claims as questions with answers and where each is
answered, and anything specific to the deck, and replaces the generic
sections with one paragraph pointing at the first deck's Chapter A and
saying what it describes (author, 2026-09-28: "shorten appendix A: I like
that it summarizes the questions and answers for that chapter (the other
appendices), so we can keep that part").

### The method names its sources

A Metod section that says the sources come from an earlier review ("hämtade
ur en systematisk genomgång … som kursens lärare gjort") cites that review
(`\parencite{<key>}` with its own provenance block), or the appendix's whole
method rests on a work the reader cannot reach (the author's "Ref to that
study.", 2026-09-16).

### Same queries, all providers

Run **every** query — support and counter — on the **same full set of
live providers** (`scholar providers check` first). When a provider needs
field syntax (WoS `TS=`, Scopus `TITLE-ABS-KEY`), translate the *same*
keywords into it; never one keyword set on WoS and a different one on
Scopus. The query table makes this auditable: a row is a query, the
columns are providers, the cells are hit counts — or a mark for a search
that failed or was not run there, which the caption explains. A failed
search is never written as 0: scholar records it as `failed (reason)`
(`sessions show`, the CSV's `# Results:` line), and that is what the cell
reports.

### Provider quirks that fake a negative

- **Test a zero before recording it.** A cell of 0 is only a negative if
  the provider can answer that kind of query at all: send that same
  provider one query known to match (a known study's title words in the
  same syntax and filters) and record its count beside the zero. A provider
  that returns nothing for the known query too has failed, whatever it
  reported; the cell is *failed*, not 0. Practice in the MFA review
  (2026-11-18); the quirks below are the reasons a zero can lie.
- **DBLP** has answered every API request with an anti-bot (Anubis)
  page since September 2026; scholar records each such search as
  `failed (non-JSON response (HTTP 200, text/html))` and `providers check`
  fails on it. Record DBLP as unavailable — in the method, the query
  table's DBLP column and the limitations — never as a column of zeros.
  When it answers, it indexes titles only and applies an implicit AND
  (keep queries to two or three terms), and a throttled DBLP answers *zero
  with no error*: scholar paces it and repeats empty multi-term answers
  itself, recording `N after k retries`, so a recorded DBLP 0 is one that
  survived the repeats.
- **OpenAlex** is metered ($0.001 per request against a daily free
  budget shared by everything run that day, reset at midnight UTC) and
  answers HTTP 429 with a JSON body (`dailyRemainingUsd`, `retryAfter`)
  when the budget is spent; a cell left unanswered is provider-limited,
  not zero. `SCHOLAR_EMAIL` (the polite pool) raises the *rate* limit but
  draws on the same budget — verified by sending the same request with
  and without `mailto` while the budget was spent — so the lever against
  a budget outage is an API key, not the address: a free OpenAlex key
  raises the daily budget tenfold
  (https://help.openalex.org/api/authentication/; set it as
  `OPENALEX_API_KEY` in `~/.credentials`, never in a prompt or a report).
  Without one, plan a thorough chapter (a hundred-odd queries) against
  the free budget, or run it across two days. `scholar providers check`
  shows the daily budget left and any prepaid or one-time credit; a spent
  daily allowance does not block searches while such credit remains.
- **OpenAlex's abstracts are incomplete.** It held one sentence of a CCS
  paper's abstract (2026-11-13), so a query whose word came later in the
  abstract matched in Web of Science, Scopus and arXiv and not in OpenAlex;
  of 44 records compared, 9 had no abstract there and 5 a shortened one
  (a small, selected sample). A title-and-abstract search in OpenAlex
  (`scholar search … -p openalex --in title-abstract`) is therefore not the
  same search as in Web of Science: say so in the limitations, and do not count on
  OpenAlex alone for a negative.
- **Semantic Scholar's paper search is a keyword search** with a trained
  ranking (its API tutorial says so); only its snippet search matches by
  meaning. A plain-language question sent to `-p s2` is not a search by
  meaning. Its relevance search takes no operators and stops at 1 000; a
  Boolean query sent there answered 0 with HTTP 200 in the MFA review
  (2026-11-18), where the bulk search matched 780. Scholar now sends
  Boolean queries and `-l 0` to the bulk search and records which one
  answered; a record from before that (no `via bulk`) with an operator
  query and 0 hits is not a negative: rerun it.
- **IEEE Xplore** has a daily quota; **Scopus** may reject every query
  (HTTP 400) on a bad day; an unkeyed **Semantic Scholar** shares a public
  pool and answers 429 when it is busy. Scholar records these searches as
  `failed (reason)`; report them as failed with the reason and rerun them
  when the provider is back — never as 0. (An empty Scopus answer is now
  0 papers; no placeholder record appears in the session.)
- **Relevance ranking buries old papers.** For a bare-concept query whose
  subject *is* the classic paper ("stepwise refinement", "literate
  programming"), take the full result set rather than the top 40, and say
  so in the query table.

### No caps on searches

Every query is run without a limit (`-l 0`), so a cell of the query table
is the number of records the database holds for the query, not "at least
40". If the user then decides to screen or read only part of what came
back, the method says so in three numbers per question: retrieved,
screened, read in full. A search that was run with a limit is redone
without one (see "Redo, don't narrate").

### Exclusion criteria

The criteria for leaving a record out are a **labelled list** in the
method, and the labels are the reasons recorded in the session.

**The labels are mnemonic** (author, 2026-11-13: "they should be mnemonic,
even two-three short, representative words should work as a label"): two or
three short words that say what the criterion is, and the same words as the
tag. A count then reads without a key ("212 new scheme, 31 usability
only"), which "212 under X1" does not. Numbered labels are for a document
that already has them.

```latex
A record is excluded if it is one of the following.
\begin{description}
  \item[New scheme] It proposes a new scheme and offers only its own
    security argument for it.
  \item[Machines only] It concerns authentication between machines, with
    no human user.
  \item[Usability only] It studies usability or adoption and reports
    nothing about security.
  \item[No evidence] It gives an opinion or an overview without evidence
    of its own or a stated method.
\end{description}
```

```bash
scholar llm classify <session> --no-examples \
  -t supports-claim -t qualifies-claim -t adjacent-subtopic -t off-topic-false-hit \
  -t new-scheme -t machines-only -t usability-only -t no-evidence
scholar sessions decide <session> --source agent --discard --doi <doi> -t new-scheme
```

**One criterion is always on the list: No abstract.** A title and an
author list cannot be screened against the claim. Before classifying, run
`scholar enrich <session> --pending-only --fields abstract
--enrich-providers openalex,s2,arxiv,ieee,wos,scopus` (OpenAlex first:
batched lookups; through the tunnel, for Scopus; recipe in
`scholar-cookbook.md`, "Reading the source") so every record with a DOI or
another identifier gets its abstract where a provider has one; a record that gains
one stays in. A DOI or URL saves a record only if it leads to an abstract
or the full text: a landing page with nothing more than the title adds
nothing to screen (author, 2026-11-18: "if the link adds nothing, we
discard it"). The rest are discarded with the tag `no-abstract` before the
classification, not left to the model (an agent: `sessions decide
--source agent --discard -t no-abstract`). The audit caption counts
discards by criterion, apart from duplicates of cited sources: "…, 31
excluded for lack of an abstract", "…, 12 excluded by the criterion
new-scheme". A discard is counted by its criterion only when it carries no
category tag and no note tag (the criterion is its last other tag); one
with a category tag counts under the category. The flow counts give the records
without an abstract, the ones enrichment rescued and the ones removed, and
the limitations paragraph says that older or grey-literature work indexed
without an abstract can be missed this way. A known item that comes back
without an abstract is not discarded: it is read in full instead.

```latex
  \item[No abstract] The record has no abstract, and none could be added
    from its DOI or other identifier.
```

The research context given to `llm context` states each criterion with its
tag, and asks for the criterion tag on every record that is not kept. The
flow counts in the results are then given per criterion, the session
export carries the reason for every discard, and a reader who doubts a
decision can see which rule made it. A record discarded for a reason
outside the list means the list is incomplete: add the criterion, do not
invent a tag. Check the tags after a classification run: the model may
invent one or reuse a theme tag, and those are removed.

### Vocabulary symmetry

The counter-search uses every concept term the support search used, plus
the field's indexed names for the concept (the practitioner name — "DRY"
— is often unindexed; the academic name — "code clones", "code
duplication" — is where the literature is). Never write "the concept is
indexed as X and Y" unless both X and Y were searched in both directions.

### A concept is several wordings

A keyword search returns what shares its words. List the concepts the
claim rests on (each threat of a threat model, each sub-claim, each
population) and give **every one** the words an author might use for it:
synonyms, the noun and the verb, singular and plural, and the bare word
beside the phrase. One exact phrase per concept is the fault to look for,
and a query that strings several concepts together as one phrase each
(`"SIM swap" OR "push fatigue" OR "account recovery"`) has it for all of
them at once.

Observed 2026-11-13: a review searched the threat "account recovery or a
weaker fallback login" with the phrase `"account recovery"`. The largest
study of that threat says "recovery procedures" and "recover from losing
access" in its abstract and was returned by none of 20 queries on five
databases; Web of Science held the whole abstract, so the wording was the
cause and not a database. `recovery OR recover OR fallback OR reset OR
lockout OR "backup codes"` returned it, with three further sources.

**Fix the wordings before the queries.** Before writing a concept's query,
put the concept as a plain question to a search that returns passages
(the cookbook's "Search by meaning" table lists the tools and their
limits) and read the first passages for the words authors use for it.
Those words, read by a person, go into the query. Observed in the MFA
review (2026-11-18): the passages held the bare word "recovery" in 84 of
677 papers and "reset" in 48, while the query had only the phrase
"account recovery"; the phrase "prompt bombing" occurred in none of them.
Counting words by program, without a reader, found nothing usable there.

Before running, tick each concept off against the queries. A concept
with no term at all is named in the limitations; a concept with one
phrase is reworded now.

### Studies that the queries must return

Write into the method, before the search is relied on, a few studies
known to bear on the claim: the ones the user names, the claim's own
citations, what a first run found. After the search, look each one up in
the session by DOI or title. A query for a concept that returns none of
the known studies on that concept is reworded (by concept, as in "A redo
must not do worse") and run again on every provider. The list and the
outcome go in the method, one sentence. Without such a list a gap cannot
show: the query table and the counts of a search that missed a study look
exactly like those of one that did not.

### Check the keyword search with a search by meaning

The record of a search shows what was found, never what was missed. So
when the keyword searches are done, and always before a conclusion leans
on "the search found none", ask a search by meaning one question in plain
words **per concept** and look each returned work up in the sessions:

```bash
scholar sessions check <session> [<session> ...] -o <dir> \
  -s "an attacker uses account recovery or a weaker fallback login to get
      around multi-factor authentication"
```

(OpenAlex `search.semantic`; its buckets, tally line and the other tools
and their limits: `scholar-cookbook.md`, "Search by meaning".) Write the questions down
before running. Then:

- A work that bears on the claim and is **not in any session** is a gap
  in the queries. Find why (which word of its title or abstract no query
  has), add the wording to the *concept* query, and rerun on every
  provider. The work then enters through our own search.
- Works that name the concept and not the claim's subject (studies of
  fallback authentication that never say "two-factor") cannot be returned
  by a query built on the subject's term block. Say so in the
  limitations, or search the concept alone.
- Be as precise as for keywords: a general question ("is MFA necessary or
  sufficient") returned mostly surveys and overviews (all 29 works already
  screened were excluded ones); one concept as a sentence returned 7
  bearing works among 27 already screened.

It is a documented complement, never the search: record the tool, the
questions verbatim, the date and the list returned. It gives at most 50
works and no count of what matched, because nothing matches or fails to
match, so it cannot fill a flow table and "the search found none" cannot
rest on it; its order also depends on citation counts and on a model the
provider can replace.

**A ranked list has no honest stopping point.** Wherever it is cut, relevant
work lies below the cut. Observed in the MFA review (2026-11-18): for one
question, 13 of 37 known relevant papers were in the first 100 places of
the ranked list, and their median place was 171. So a list from a search
by meaning informs the queries and checks them; it is never the source of
a count, of a flow-table number, or of "none found". A report by another tool (Asta, Elicit, a
deep-research run) on the same question is the same kind of check: list
its sources and look each one up in the sessions.

### When a study turns out to have been missed

A reviewer, another tool's report or a search by meaning names a study
that bears on the claim and is not cited. In order:

1. **Look, do not answer from memory.** Is it in a session, and how was
   it classified? In the full-text matches that were kept and not
   screened (which queries, which place)? Does a database that searches
   whole abstracts (Web of Science) hold it, and did it return it?
2. **Name the cause**: the wording of a query, a database that lacks the
   record or its abstract, a cap, a wrong exclusion by the classifier.
   They have different repairs.
3. **Repair by concept** (see "A redo must not do worse"): reword the
   concept's query from the claim's own statement of the concept, not from
   the study. A word taken from the missed study may be added, as a query
   of its own, and is reported as **fitted to that study**.
4. **Look for the same fault elsewhere.** The repair shows that the
   queries now return this study and nothing about what else is missing:
   check every other concept that was searched in the same way.
5. **Report it**: a deviation, dated, with what prompted it. If the
   prompt was another tool's report that the paper compares itself with,
   the comparison keeps describing the review as it stood before the
   repair, and the repair is told separately.

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

Seed the four category tags (`llm classify -t supports-claim -t
qualifies-claim …`) if the session has none yet: with categories in the
vocabulary the model must give each paper exactly one, and a paper it
fails on after one retry is left pending and listed at the end of the
run — decide those with `scholar sessions decide`. Read the low-confidence
rows and every `qualifies-claim` row yourself and override with `scholar
sessions decide` where the model is wrong; tag the sources you cite with a
theme tag (`decide … -t dry-origin`) so they show as *cited* with a
reason. **An agent passes `--source agent`** on every `decide` (required
off a terminal). Its decisions, like the classifier's, stay unreviewed and
are never *cited* until the author confirms them (TUI, or `decide --source
human`), and it never uses `--force` to replace a decision the author made
or reviewed (cookbook, "Notes and sessions"). Then generate the table with
scholar:

```bash
scholar sessions export dry-principle -f table --bearing-only --lang sv \
  --label sok-dry --track "DRY-principen" \
  --theme dry-origin="principens ursprung" --theme clones-faults="klonfel" \
  -o litteratursokning/dry-principle-full        # writes …-full.tex
```

Cited = a kept row decided or confirmed by a human (source `human`,
`llm_reviewed` or `agent_reviewed`) whose first non-category tag is in the
`--theme` allowlist; an unreviewed agent or LLM keep, and a decision of
unknown source, is a candidate and never cited. Other non-category tags are audit notes shown in
parentheses; machine-labelled rows show their category and the model's
confidence, or "n/a" ("saknas") when none was recorded. The status wins:
a discarded row never counts as supporting or qualifying, whatever its
category; it reads "supports the claim, excluded" ("…, utesluten"), is
not listed under `--bearing-only`, and the caption counts it separately.
Omit `--bearing-only` for the full list. If the installed scholar
predates `-f table`, `scripts/session_table.py --csv <export.csv> …`
gives the same rows from the CSV export; its database sentence cannot
know zero-hit or failed providers, so fix that sentence by hand.

Rows are grouped cited → supports → qualifies/contradicts → adjacent →
off-topic → still pending → other (duplicates, excluded), with the model's
confidence per machine-labelled row. Two-sided category names must appear
in the caption counts so the reader sees at a glance how much
refuting/qualifying work there was.

The caption's "Databases:" sentence is the coverage statement: it names,
full name first, every database that answered at least one query (one
that answered with zero hits included), and notes partial failures —
"DBLP (failed for 4 of 5 queries)". A database that failed *every* query
is not named at all, since it was not searched; say so in the method and
the limitations ("DBLP could not be searched: …"). A database whose
searches hit a limit reads "capped at the limit for 2 of 5 queries" (redo
them with `-l 0`); one known only from a merged record of several
providers (saved before #164) reads "failed or incomplete for k of n
queries, in a merged record" (rerun per provider). The caption then gives
the dates the databases answered, "Searched 2026-11-13 to 2026-11-18."
(cache hits count from their fetch date), or says for how many searches
the date is unknown.

## Who screened

Scholar records who made each decision (cookbook, "Notes and sessions"),
and the report counts them by source. The method says it in plain words:
which decisions a person made, which a classifier or an agent proposed,
and how many of those the author reviewed. A machine's screening is part
of the method only together with a measure of its error, so the method
includes a **review of a random sample** as a step:

1. After `llm classify` (and any agent decisions), draw a seeded sample of
   the unreviewed discards (and, if kept rows matter, of the keeps):
   `scholar llm sample <session> --discarded -n <N> --seed <K>`. The size
   is the author's call; record the seed.
2. The author reviews every sampled paper, in the drawn order (TUI filter
   `s`, or `sessions decide --source human`). An agent does not review
   the sample.
3. `scholar llm sample <session> --report` gives the reviewed count, the
   number changed, the disagreement rate and its 95% modified Wilson
   interval.
4. The method or the appendix states the sample and the rate, e.g. "Of a
   random sample of 50 of the 412 discards made by the model (seed
   20261118), the author changed 3 (6.0 %; 95 % modified Wilson interval
   …)", citing the interval's source, Brown, Cai and DasGupta (2001,
   doi:10.1214/ss/1009213286), verified per this skill before it is
   cited. The report's "LLM screening" section gives the same sentence
   together with the model, prompt version and dates of the decisions.

A high rate is a finding, not a reason to redraw: say what it means for
the discards that were not reviewed, or have them all reviewed.

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
    Web of Science (WoS), Scopus.  Sökningarna har ingen övre gräns:
    talen är alla träffar.  \enquote{--} betyder att sökningen
    misslyckades: DBLP svarade på varje fråga med en sida som stoppar
    automatiserade klienter i stället för med data, så DBLP kunde inte
    genomsökas.  Web of Science fick nyckelorden som
    \texttt{TS=(\dots)}, Scopus som \texttt{TITLE-ABS-KEY(\dots)},
    OpenAlex och IEEE som boolesk fritext.}[tab:dry-queries]
    \centering\footnotesize
    \begin{tabular}{@{}lp{0.5\linewidth}rrrrr@{}}
      \toprule
      & Nyckelord & OA & DBLP & IEEE & WoS & Scopus \\
      \midrule
      S1 & \enquote{code clones} inconsistent changes faults & 212 & -- & 14 & 2 & 4 \\
      … \\
      M1 & \enquote{code clones} (beneficial, harmless eller \enquote{considered harmful}) & 388 & -- & 61 & 19 & 31 \\
      \bottomrule
    \end{tabular}
  \end{sidecaption}
\end{table}
```

Prefix support queries S, counter queries M (motsökning) or C, known-item
retrievals K, and refer to them by label in the prose. A failed cell gets a
mark the caption explains ("--" above), never 0; a cell answered only
in part gets its lower bound and the same kind of explanation.

## Checklist for the appendix

- [ ] Claim cited at first mention; RQ about the fact; strength stated
- [ ] Method: date, tool, databases + health, side-captioned query ×
      database × hits table with the abbreviations defined; known-item
      retrievals justified and their verification mode stated
- [ ] Every query on every live provider, without a limit; counter vocabulary mirrors support
- [ ] Every concept of the claim has several wordings in the queries (none
      searched by one phrase), taken from passages read before the queries
      were written; the studies that the queries must return are named in
      the method and were returned
- [ ] A search by meaning (or another tool's report) was held against the
      sessions, one question per concept; what it returned that the records
      lack is screened or named in the limitations; a repair after a missed
      study is reported as a deviation, fitted queries marked
- [ ] Exclusion criteria labelled in the method and used as discard tags; flow counts given per criterion; any cap on screening or reading decided by the user and stated
- [ ] Method states the search dates, which S2 search answered, the
      deduplication (PRISMA-S item 16; `sessions reconcile`) and who
      screened: decisions by source, a seeded sample of the machine's
      decisions reviewed by the author, its disagreement rate with interval
- [ ] Every agent decision recorded `--source agent`; nothing cited that
      the author has not decided or confirmed; no `--force`
- [ ] Failed searches reported as failed (query table, method,
      limitations), never as 0; every 0 tested with a query known to
      match on that provider; a database that failed every query is
      named as not searched
- [ ] Redone searches recover every baseline item (coverage checked);
      no narration of earlier attempts; no session names in the text
- [ ] Results cite every source (load-bearing ones with verbatim quote and
      locator); corroborations cited with a finding each
- [ ] Limitations paragraph present and honest
- [ ] Conclusion's first sentence answers the RQ
- [ ] Future work: what this search left undone (named sources, dead
      providers) and what the field must study for a surer answer
- [ ] Session classified; hit-list table `\input` at the end, with
      two-sided counts in the caption
- [ ] No export paths, bib file names or CSV columns in the compiled text —
      all in `%` comments
- [ ] Bib: titles containing quotes use `\mkbibquote{…}`; inferred page
      numbers and abstract-only verification are marked in `VERIFIED`
