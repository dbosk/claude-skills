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
   providers and their health that day, session name (as a name, not a
   path), and a **query × provider × hits table** (template below). Say
   which items were retrieved as known documents and how (DOI, title
   search, author copy) and how each was verified (full text; OCR of a
   scan; abstract only). Failed and malformed queries stay in the table,
   labelled.
3. **Results**, one paragraph per sub-question — origin, establishment,
   criticism — every source cited with a full reference (footnote
   citation in verbose styles) and a verbatim quote with locator for the
   load-bearing ones. **Corroborating sources are cited here with a
   one-clause finding each**, not summarised as "six further studies
   agree, see the export".
4. **Discussion and limitations** — dead providers, queries that returned
   noise, a provider that only holds the abstract, inferred page numbers,
   a phrase that is unsearchable in the databases, an edition that could
   not be obtained. Written plainly; a limitation stated is not a weakness
   of the appendix.
5. **Conclusion** — first sentence answers the research question ("Ja på
   båda frågorna, med ett förbehåll: …"); then the caveats and what they
   mean for how the claim is used in the main text.
6. **Full hit list** — the classified session as a `longtable` at the end
   of the chapter (`\input{…-full}`), so the reader can audit the
   screening, not only the winners. The chapter's argument ends at the
   conclusion; the table is audit data after it.

A short chapter (known-item verification plus a light counter-search)
keeps the same skeleton as `\paragraph`s; a long one uses `\section`s.

## Rules the appendix must satisfy

### Self-contained

- Every work the text relies on is cited; a name in the prose ("efter Hunt
  och Thomas") carries a citation the first time it appears.
- URLs of sources go into bib entries or footnotes, never inline in prose
  as `\texttt{…}`. A publisher excerpt or an author's copy that was
  actually read gets a bib entry (edition, URL, urldate) and is cited.
- **No export paths, no bib file names, no CSV column names in the text.**
  Put them in `%` comments next to the `\input` of the hit-list table and
  in the bib provenance blocks:

  ```latex
  % Session export: litteratursokning/dry-principle.{csv,bib}; table
  % regenerated with: scholar sessions export --format table … (or, until
  % that ships, session_table.py --csv … --label sok-dry --lang sv)
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

```latex
\begin{table}[htbp]
  \centering\footnotesize
  \caption{Sökfrågor och antal träffar per databas, session
    \texttt{dry-principle}, 2026-09-02.  Semantic Scholar var otillgängligt
    (nyckeln nekades).  Fältsyntax: WoS \texttt{TS=(...)}, Scopus
    \texttt{TITLE-ABS-KEY(...)}; övriga databaser fick samma nyckelord som
    fritext.}
  \label{tab:dry-queries}
  \begin{tabular}{@{}lp{0.45\linewidth}rrrrr@{}}
    \toprule
    & Fråga & OA & DBLP & WoS & Scopus & IEEE \\
    \midrule
    S1 & code clones inconsistent changes faults & 31 & 0 & 22 & 25 & 13 \\
    … \\
    M1 & code clones beneficial harmless "considered harmful" & … \\
    \bottomrule
  \end{tabular}
\end{table}
```

Prefix support queries S and counter queries M (motsökning) or C, and
refer to them by label in the prose.

## Checklist for the appendix

- [ ] Claim cited at first mention; RQ about the fact; strength stated
- [ ] Method: date, providers + health, session name, query × provider ×
      hits table; known-item retrievals and verification mode stated
- [ ] Every query on every live provider; counter vocabulary mirrors support
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
