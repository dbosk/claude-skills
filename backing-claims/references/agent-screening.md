# Agent screening of search records

How AI agents screen the records of a `scholar` session, and how their
work is checked before it counts. The validator
`scripts/validate_screen.py` does the batch checks; this file is the
procedure around it.

## Contents

1. When
2. Before screening
3. Batches
4. The brief (template)
5. Validate every batch
6. Write the decisions
7. Look-ups for bearing records without an abstract
8. Check the screen
9. Change a decided record
10. Say who did what
11. Tool support

## 1. When

Agents screen when `scholar llm classify` is not available, or as a second
screener beside it. They record through the CLI only:

```bash
scholar sessions decide S --source agent --discard -t off-topic-false-hit \
    --by <screener-name> --reasons-file group.tsv   # lines: ID<TAB>REASON[<TAB>CONFIDENCE]
```

- Never edit a session's JSON and never call scholar's Python API.
- One writer per session: screeners only read a batch and write a sheet;
  one agent (the writer) runs every `sessions decide`.
- Name every screener with `--by`, so each decision says which agent
  made it.

## 2. Before screening

- Run `scholar enrich S --fields abstract` first (`--pending-only` to
  leave decided records alone).
- An abstract that is only disclosure, funding or keyword text (scholar
  #287) counts as no abstract: blank it in the batch.
- Build the batches from `scholar sessions export S -f csv -o <base>`
  (it has `paper_id`, `status`, `title`, `year`, `venue`, `abstract`):
  JSON Lines with `id` (the session paper id), `title`, `year`, `venue`,
  `abstract`. Keep every batch file: the validator needs it.

## 3. Batches

- **At most 100 records per screener.** Observed in this skill's runs
  (2026-11): in one run, three of four batches of about 365 rows came back
  with defaulted rows (one verdict, one shared reason, a flat
  confidence), and none of about 125 batches of 100 or fewer did; in
  another run, eight consecutive batches of 100, out of 194, still came
  back with one generic reason on 53 to 93 rows each. Smaller batches
  helped there; only the validator tells.
- The screener writes its sheet to a named file and replies in one line:
  agent replies are cut at about 4 KB.
- Give the batch file, the output path and the brief; nothing else to
  read.

## 4. The brief (template)

Fill the angle brackets; quote the session's research context verbatim
(`scholar llm context S` prints it). Keep the rules as written.

```
You screen literature-search records for one claim. You only read and
judge: never run `scholar`, never touch a session file, never search the
web. Read the batch file, write exactly one output file.

Research context (verbatim from the session):
> <research context>

Category -> verdict: supports-claim, qualifies-claim -> keep;
adjacent-subtopic, off-topic-false-hit -> discard.
Exclusion tags (every discard gets exactly one): <tags>, no-abstract.
Themes (keeps only): <theme = meaning, ...>.

Rules
1. Judge only from the record's title, year, venue and abstract. Nothing
   from memory: if the abstract does not say it, the paper does not.
2. Read every record yourself. No title rules, no keyword filters, no
   script that sorts or decides records; a script may only read the batch
   and check your file.
3. A record without an abstract: decide from the title only where the
   title settles the case (another field). Otherwise discard it with
   exclusion no-abstract, keeping the bearing category the title
   suggests (supports-claim or qualifies-claim) when it may bear on the
   claim; such records go on a look-up list. Never keep a record without
   an abstract. Its reason starts "no abstract; title: ..." and then
   says why the title settles or suggests the category; the title
   alone is not a reason.
4. A record that bears on the claim but meets an exclusion criterion is
   discarded and keeps its bearing category.
5. Every row gets its own reason: one sentence, at most about 300
   characters, naming what decides it and quoting the deciding words.
   A quote is copied verbatim in double quotes; anything not verbatim
   carries no quote marks. No tabs or newlines.
6. Every row gets its own confidence (0-1, steps of 0.05) for verdict and
   category together: 0.5-0.7 when the abstract is thin or the call
   close, 0.9 or more only when it leaves no doubt.
7. No defaults and no shared reasons: never give unread rows one verdict,
   one reason or one confidence. Return fewer rows rather than defaulted
   ones; say which ids you left out.

Output: <output path>, a TSV with the header
id  verdict  category  exclusion  theme  confidence  reason
and one line per record in batch order (exclusion "-" for a keep, theme
"-" for a discard). Check that every id appears once.
Batch: <batch path> (JSON Lines: id, title, year, venue, abstract).
Reply with one line: the output path, the row count, the counts per
verdict and category, and any id you left out or found hard to call.
```

## 5. Validate every batch

Before anything is written to the session:

```bash
python3 -I ~/.claude/skills/backing-claims/scripts/validate_screen.py \
    <sheet> <batch> --exclusions <tags>,no-abstract --themes <themes>
```

It checks ids (each once, in order), vocabulary and keep/discard
consistency, confidence range, empty or placeholder reasons, duplicate
reasons, flat confidence, long runs of near-identical rows, and every
quote of three or more words against that row's own title and abstract
(`--help` lists the thresholds; `--json` for scripts; exit 0 clean, 1
failures, 2 usage). Reasons are compared word by word, after the row's
own id and any run of 75% or more of its title's words are replaced, so
a template such as "subject is <title>." or "no abstract; title:
<title>" counts as one shared reason, while a subject named in a few of
the title's words ("About blockchain consensus protocols, not
programming education") stays the screener's own. A flat confidence at 0.9 or above is not counted (a batch of
plainly off-topic records sits there). A sheet is read as written; a TSV
written by `csv.writer` (doubled quotes) needs `--csv-quoting`, one
without a header `--columns`. Then:

- **Duplicates, flat confidence, runs, missing rows:** re-screen the
  batch (or the rows named) with a fresh screener. Never patch the
  defaulted rows by hand.
- **Quote `paraphrase`:** drop the quote marks (the reason stays,
  unquoted); never keep an inexact quote.
- **Quote `mixup`** (the words are another row's): re-screen those rows.
- **Quote `unsupported`:** re-screen the row.
- Validate the repaired sheet again; log every repair (row, what, why).

**Which check runs where.** The validator runs on each screener batch
of about 100 rows, before the writer, with a low threshold (more than 3
rows sharing a reason). Scholar (from commit e7dc5f5, #291, #293) runs
its batch check at 10 records on what the writer loads (`sessions
decide --reasons-file`, `sessions screen --verdicts-file`) and on what a
session stores (`scholar sessions check-batches S`, read-only), where
batches are already merged. There it lists findings and saves unless
`--strict` refuses (exit 2); `sessions decide --dry-run` runs every check
and writes nothing. Scholar compares reasons only after collapsing white
space and case, so a trailing full stop or a templated id or title
defeats it, and its flat check has no exception for high values: it
fires only when every row of a file of 20 or more has the same
confidence. Run both. With scholar e7dc5f5 or later installed,
`validate_screen.py … --scholar S --by <screener>` also sends the sheet
through `sessions decide S --source agent --dry-run --strict
--reasons-file …`, one file per verdict and tags (an id
`other-session|paper-id` goes to that session), and fails on any
nonzero exit.

## 6. Write the decisions

`decide` applies status, tags and `-c` to a whole reasons file, so split
each validated sheet into one file per verdict + category + exclusion
(or theme), with the per-line confidence as third column:

```bash
scholar sessions decide S --source agent --keep -t supports-claim -t <theme> \
    --by <screener-name> --reasons-file keep-supports-<theme>.tsv
scholar sessions decide S --source agent --discard -t qualifies-claim -t no-abstract \
    --by <screener-name> --reasons-file discard-qualifies-noabs.tsv
```

A bad line, an id not in the session, or one id with two reasons aborts
the whole file unsaved; reasons hold 1 to 2000 characters and are stored
as written. An agent decision never replaces a human one: never pass
`--force` over the author.

## 7. Look-ups for bearing records without an abstract

For each record on the look-up list (discarded as no-abstract with a
bearing category):

- Do a known-item lookup by DOI or exact title: Crossref, OpenAlex,
  PubMed or Europe PMC, the publisher's page.
- Stop at a bot challenge or a served login form.
- Read the full text only when the record would be cited or the call
  stays open on the abstract.
- An abstract found this way is screened like any other, and the reason
  names where it was found. Once scholar #258 is installed,
  `scholar sessions set-abstract` records it in the session.

## 8. Check the screen

- **Blind second screen.** A second screener gets the same brief and the
  same records, without the first verdicts. Say only that: a sample drawn
  from the discards tells the screener the likely verdict by
  construction, so the second screen is blind to the first verdicts, not
  to the selection.
- **Coverage:** every keep and every discard below confidence 0.7.
- **Disagreements** go to a reading agent (reads the abstract or full
  text) or to adjudicators (given both categories and reasons, decide
  from the abstract). A seeded 10% of the resolutions is spot-checked by
  another agent.
- **Report** the agreement and Cohen's κ between the two screens
  (category, and bearing vs not bearing), with the strata.
- **Report the bearing counts in two parts:** firm, and borderline (a
  ruling below 0.6 that nobody re-read).
- **Model decisions** (`llm classify`): draw stratified seeded samples of
  keeps and discards, `scholar llm sample S --kept -n N --seed X` and
  `--discarded`, and report them with `scholar llm sample S --report`.

## 9. Change a decided record

- Reset, then decide again, so the old decision stays in the record's
  reset history:
  `scholar sessions reset S --paper-id <id> --note "<why>" --by <who>`
  (`--dry-run` first), then `sessions decide` as in section 6. Reset
  clears the classifier's trace into that history.
- To correct a classifier decision in place instead, `sessions decide
  --source agent -c <conf> --keep-trace` keeps the trace of the call it
  corrects.
- Only unreviewed decisions (agent, llm) can be reset or replaced.
- Rehearse a bulk change on a copy (the session file in
  `<scratch>/review_sessions/`, commands run with
  `SCHOLAR_DATA_DIR=<scratch>`), then run it for real and verify record
  by record: export (`sessions export S -f csv` or `sessions show S -f
  json`) and compare status, tags, source, confidence and reason with the
  sheet.

## 10. Say who did what

The appendix's Method states exactly who read what: which screener agents
read which records (batch size, how many screeners), who wrote the
decisions, who did the second screen, the adjudication and the spot
check, which model classified, and that the author has not reviewed the
screen (until the author has, and then what the author reviewed).

## 11. Tool support

On scholar's main branch (2026-11-20; installed copies may be older):
#256 (quote check in `sessions decide`), #258 (`sessions set-abstract`),
#287 (doubtful abstracts flagged by enrich), and, from commit e7dc5f5,
#291 (batch checks; section 5 says how they divide the work with the
validator) and #293 (records decided without an abstract). #292 (screen
sheets in batches, batch ids in the trace) is open. Check the installed
scholar's `--help` before relying on any of them; until a check is
installed, `validate_screen.py` does it.
