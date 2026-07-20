---
name: scientific-writing
description: Structure and workflow conventions for research papers. Use proactively when (1) writing or revising a paper draft, its introduction, method, results or conclusions, (2) adding research questions, hypotheses, contributions, questionnaires or analyses to a paper, (3) processing a review round on a draft, or (4) starting a new paper repository. Covers question-hypothesis-contribution traceability, substantive vs methodological research questions, literate-program appendices for instruments and analyses, method-section chronology, and the review-round loop.
---

# Scientific Writing

Conventions for structuring research papers and for the drafting workflow.
This skill owns the paper's *structure and process*; it delegates:

- citation finding/verification and the search-protocol appendix to
  **backing-claims**,
- LaTeX mechanics (semantic environments, restatable theorems, dual
  article/slides builds, noweb appendices) to **latex-writing**,
- reading and uploading annotated drafts to **remarkable**.

## Questions, hypotheses, contributions: full traceability

The skeleton of the paper is the mapping between contributions, research
questions and hypotheses. Enforce all of these:

1. **Two kinds of research questions, separately numbered.**
   *Substantive* questions ask about the world; *methodological* questions
   ask whether the study's own instruments work (do independent
   classifications agree? does coding from logs match coding from
   think-aloud?). Methodological questions get their own environment and
   counter, so they never renumber the substantive ones. See
   `references/question-structure.md` for the LaTeX pattern.
2. **Every contribution is held to account by a research question.**
   The introduction has a Contributions subsection; each listed
   contribution names the question that tests it. A methodological
   contribution (an instrument, a coding scheme, a triangulation) gets a
   methodological question. If a contribution has no question, either add
   the question or drop the claim.
3. **Hypotheses are predicted answers.** Each hypothesis answers exactly
   one question; descriptive/exploratory questions have no hypothesis and
   say so. If an overarching claim is not directly falsified but supported
   by inference to the best explanation, state that explicitly in the
   method overview.
4. **State once, restate twice.** Each question and hypothesis is stated
   once (introduction/theory) in a restatable environment, restated in
   the method overview together with *how* it will be answered, and
   restated in the conclusions together with its answer so far. Reference
   by `\cref`, never literal "RQ1"/"H2".

## Method section

- **Overview before details**: open by restating every question and
  hypothesis with its mode of answer (which data, which test, which
  section), then give the details in subsections.
- **Data collection in chronological order** of the study, and motivate
  each instrument *at the point in time it is used*: if an instrument is
  administered at start and end, the start section motivates only the
  start administration and a separate end-of-course section motivates the
  re-administration.
- **Do not duplicate a companion study's instrument.** When a companion
  paper collects data in the same setting (same course, same cohort),
  use its measurements instead of writing a parallel instrument, and
  let this study's own instruments test only what the companion's do
  not cover. State the division of labour in the method (which scores
  come from where), keep the instruments' platform titles
  distinguishable for participants and analysis alike, and discuss
  alternatives (e.g. established inventories) against the *combined*
  design.
- **Validated instruments stay verbatim.** Do not reword items of a
  validated questionnaire, even where wording fits the setting poorly;
  note the tension in prose instead. Search for and cite published
  criticisms of the instrument, and derive robustness checks from them
  (e.g. scoring a subscale separately).
- **Guard against circularity**: a classification must never be derived
  from the same data it is later correlated with; say explicitly which
  sources each classification uses.

## Literate-program appendices

Every questionnaire/quiz/survey the study administers, and every
quantitative analysis it runs, is a **literate program in the paper's
appendix**: one noweb source that weaves into the appendix chapter and
tangles into the runnable artifacts (e.g. the platform's quiz JSON, the
analysis script).

- The prose documents the data-file schemas; this doubles as the study's
  code book.
- Instrument definitions and their analysis share constants (e.g. item
  titles as result-file column keys) so they cannot drift apart —
  ideally in the same source file, side by side.
- **Uniform instruments are generated, not hand-written.** When the
  items share one form (a validated questionnaire: twenty items, the
  same five responses), do not tangle the platform's JSON directly:
  state the instrument once — titles, items, response anchors,
  instructions — in a constants chunk, tangle a small generator that
  unfolds it into the platform files, and have the analysis program
  include the *same* constants chunk (titles find the reports, anchor
  texts map answers back to scores). Reference: vt-debug's `rspq.nw`
  (`make_rspq.py` + `analyze_rspq.py`).
- Cross-reference both ways: the method section points to the appendix
  program, the appendix points back to the sections that motivate each
  piece.
- **End-to-end automation, both directions.** The programs reach into
  the platform themselves: they *create* the instruments (e.g.
  `canvaslms quizzes create`) and they *fetch* the results back (e.g.
  the student-analysis report via the platform CLI's own importable
  machinery) — course names and instrument titles are known constants,
  so nothing is clicked or downloaded by hand. Where a fetch cannot be
  automated yet, mark it XXX with a tracking issue rather than settling
  for a manual step silently.
- **LLM-assisted coding, human-verified.** For open-text answers that
  need qualitative coding, the analysis program pre-codes them with an
  LLM (the `llm` package; prompt states the coding scheme, answers in
  JSON) and writes the suggestions into columns *separate from* the
  human coder's verified codes — the sheet always shows which is which,
  and the human's codes are the data.
- Build mechanics (article-only noweb.sty, Makefile rules, tangle
  recipes, the syntax-highlighted weave): latex-writing's
  `references/dual-beamer-article.md` section "Literate-program
  appendices", and the literate-programming skill for the standard
  tominted recipe.
- Validate tangled artifacts in the round that creates them (JSON parses,
  Python compiles, quiz validators pass) — and test instrument creation
  end to end against a sandbox course before the real one.

## Review rounds

A draft iterates in review rounds; each round is one atomic unit and lives
on **its own branch with its own PR**. Name both after the draft version
the round *produces* — branch `review-round-vN`, PR to the default branch
titled `"Review round: draft vN (YYYY-MM-DD)"` — so branch, PR, commit
message and reMarkable name all carry one identifier (the round that
processes v48's comments and uploads v49 is `review-round-v49`; round
counts and draft versions diverge, so never number by round):

0. Open the round: branch `review-round-vN` off the default branch. The
   round's work happens here; the PR opens when the round's draft is
   uploaded.
1. Read all annotated pages of the previous draft (remarkable skill:
   `content_type=annotations` to list the pages, `render_merged` images to
   read the handwriting).
2. Interpret every comment; apply all edits of the round.
3. New literature needs discovered in a round go through backing-claims
   (find, verify, provenance block) and into the search-protocol appendix
   **in the same commit**.
4. Rebuild all outputs; verify: zero errors, no unresolved references,
   restatement counts unchanged where expected.
5. **One commit per round**, without asking; the commit message lists the
   round's changes and names the draft version it produces (`"This commit
   is the version uploaded to reMarkable as draft YYYY-MM-DD, vN"`), so
   every uploaded draft maps to exactly one commit. **Commit at upload
   time** — never upload a draft whose source is uncommitted. **Push after
   committing** — the paper repo and, when skills changed, the skills repo
   (mind that the first push of a fresh repo needs `git push -u origin
   <branch>`; a GitHub repo that only ever received issues counts as
   fresh).
6. Upload the new draft as `"<Title> (draft YYYY-MM-DD, vN)"` with N
   incremented.
7. Open the PR (`gh pr create`), listing the round's changes; use
   `closes #N` for issues the round resolved, so merging closes them.
   Merging the PR ends the round; the next round starts at step 0 with a
   new branch and PR.

## Open questions and pending decisions

- Mark open decisions with `% XXX` and deferred work with `% TODO` in the
  source, stating the alternatives and what resolves them; resolve or
  carry them forward consciously each round — never silently drop one.
- **Mirror them as GitHub issues** whenever the paper repository has a
  GitHub remote (`git remote -v`). This is standing authorisation: create
  the issues with `gh issue create` without asking. Conventions:
  - One issue per XXX/TODO item; the title states the decision or task,
    the body gives the file and section, the context, the alternatives,
    and what resolves it.
  - Annotate the source comment with the issue number — `% TODO(#12): ...`
    — so source and tracker stay linked.
  - Per round: new XXX/TODO items get new issues; items resolved in the
    round get their issues closed (`gh issue close N --comment ...`) in
    the same round, referencing the commit.
  - An item tracked elsewhere too (e.g. a `nytid todo` for work the
    author must do personally) still gets the issue; note the cross-link
    in both.
- Anonymise course/institution details before submission (keep a `% TODO`
  at the top of the method section until done).

## Checklist (per round)

- [ ] Every contribution names its research question
- [ ] Methodological questions separate from substantive ones
- [ ] Each question restated in method overview (with mode of answer) and
      in conclusions (with answer)
- [ ] Instruments motivated at their chronological place
- [ ] Questionnaires and analyses exist as literate appendix programs;
      tangled artifacts validated
- [ ] New citations verified and searches documented (backing-claims)
- [ ] XXX/TODO items mirrored as GitHub issues (new ones opened, resolved
      ones closed) when the repo is on GitHub
- [ ] Both outputs build clean; committed as one round; new draft uploaded
