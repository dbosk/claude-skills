---
allowed-tools: Bash(*), Read, Glob, Grep, Edit, Skill, AskUserQuestion
description: Review recent changes for correctness, regressions, and relevant domain-specific quality criteria
user-invocable: true
license: MIT
---

## Current Context

- **Current branch:** !`git branch --show-current`
- **Default remote branch:** !`git rev-parse --abbrev-ref origin/HEAD 2>/dev/null || echo "unknown"`
- **Staged files:** !`git diff --staged --name-only`
- **Unstaged changed files:** !`git diff --name-only`
- **Files changed vs base branch:** *(determined in Step 1)*
- **Recent commits:** !`git log --oneline -5`

## Step 1: Determine Files to Review

1. First, get files changed vs the base branch:
   ```bash
   git diff --name-only $(git merge-base HEAD $(git rev-parse --abbrev-ref origin/HEAD 2>/dev/null || echo main)) HEAD
   ```

2. Combine with staged and unstaged files from the context above (deduplicate the list).

3. If no changed files are found, use the available ask/question tool in the current environment to ask which files to review.
   - In Claude Code, use `AskUserQuestion`.
   - In OpenCode, use `question`.
   - Allow a custom answer so the user can type file paths.

## Step 2: Detect and Activate Relevant Skills

All reviews must include a general correctness pass, even when no specialized skill applies.

Based on the changed files, determine which skills to activate in addition to the general correctness review using this table:

| File pattern | Skills to activate |
|---|---|
| Educational `.md` files such as student guides, tutorials, READMEs, or conceptual docs that teach ideas, compare approaches, or rely on example ordering | `variation-theory` |
| Any `.nw` file | `literate-programming`, `variation-theory`, `latex-writing` |
| Any `.tex` file | `latex-writing` |
| `.tex`/`.nw` with `\ltnote`, `\begin{exercise}`, `\begin{frame}`, `\begin{example}` | `didactic-notes`, `variation-theory`, `try-first-tell-later` |
| `.tex`/`.nw` with `\ac{IND-CPA}`, `\ac{AE}`, `\ac{MAC}`, `\ac{PRF}`, `bibsp`, `\prf`, `\mac`, `\enc`, `\dec`, `\secpar` | `writing-crypto` |

**Content detection**: For `.md`, `.tex`, and `.nw` files, read them to check for educational/tutorial structure, comparisons between alternative approaches, example ordering, pedagogical sequencing, and crypto content before deciding which additional skills to activate.

If a Markdown guide, tutorial, README, or conceptual doc asks the reader to discern differences between workflows, approaches, examples, or sequences, activate `variation-theory` even when there is no LaTeX markup or code block.

### CRITICAL: You MUST use the Skill tool to activate each relevant skill BEFORE starting the domain-specific review.

For each skill identified above, call:
```
Skill(skill: "skill-name")
```

This loads the full skill criteria into your context. Without this step, you will miss important review criteria. Do NOT skip this step. Do NOT rely on memory of what the skills contain.

Example — if reviewing `.nw` files with educational content:
1. `Skill(skill: "literate-programming")`
2. `Skill(skill: "variation-theory")`
3. `Skill(skill: "latex-writing")`
4. `Skill(skill: "didactic-notes")`
5. `Skill(skill: "try-first-tell-later")`

## Review Principles

- **Consistency is not correctness.** If an issue appears repeatedly throughout the codebase, flag it anyway. The fact that something is done consistently — even in existing, untouched code — does not make it right. Review against the criteria, not against existing patterns.
- **Correctness comes first.** Review every changed file for correctness, regressions, contradictions, and broken references, even when no specialized skill applies. Skills supplement, not replace, general review.

## General Correctness Criteria

Apply these criteria to every changed file, regardless of file type:

1. **Correctness and accuracy**
   - Is the content correct for its purpose?
   - Are claims, equations, examples, instructions, and references accurate?
   - Does code appear logically correct for the surrounding context?

2. **Regressions and broken connections**
   - Do the changes break existing behavior, document flow, references, links, labels, imports, or cross-file assumptions?
   - Are renamed concepts or files updated consistently everywhere they matter?

3. **Contradictions and inconsistencies**
   - Does the file contradict nearby code, prose, notation, tests, or prior definitions?
   - Are terms, variables, symbols, and instructions used consistently?

4. **Missing cases and assumptions**
   - Are edge cases, prerequisites, caveats, or failure modes omitted where they matter?
   - Does the work rely on unstated assumptions that could mislead the reader or break execution?

5. **Clarity where correctness depends on wording**
   - Is wording precise enough to avoid misleading interpretation?
   - Are steps, examples, and requirements unambiguous?
   - When prose explains "why", does it also explain why the chosen
     approach works in this context, rather than only stating why it was
     selected?

## Step 3: Review Each File

For each changed file:

1. **Read the file** in full
2. **Apply the general correctness criteria**
3. **Apply all criteria** from the activated skills
4. **Note each issue** with:
    - Which general criterion or skill/criterion is violated
    - File location (`file:line`)
    - The problematic text (quoted)
    - Why it is an issue
    - A specific fix proposal

When `variation-theory` is active for prose, not just code examples, check whether the comparison keeps the task or problem invariant and varies only the intended method, aspect, or sequencing. For example, if a guide contrasts browser chat with a terminal agent, keep the repository task fixed and review whether the workflow difference is the main thing that changes.

When reviewing explanatory prose, flag passages that justify a design choice
without explaining why the approach works. Look for missing mechanisms,
invariants, constraints, or failure modes that make the claimed approach
credible.

## Step 4: Present Issues Interactively

Use the available ask/question tool in the current environment for all interactive review choices.
- In Claude Code, use `AskUserQuestion`.
- In OpenCode, use `question`.

Batch issues by file. For each file:

```
## File: path/to/file.ext

### Issue 1: [General correctness or Skill — Criterion] at line X
**Problem:** [description]
**Current:**
> [quoted problematic text]
**Proposed fix:**
> [replacement text]

### Issue 2: [Skill — Criterion] at line Y
...

Use the ask/question tool to ask:
- header: `Review action`
- question: `What would you like me to do for path/to/file.ext?`
- options:
  - `Apply all fixes`
  - `Apply fixes one by one`
  - `Skip this file`
  - `Stop review`
```

If the user chooses `Apply fixes one by one`, use the same ask/question tool for each proposed fix in that file.

## Step 5: Apply Fixes

When the user approves, apply fixes using the Edit tool. After all files are reviewed, provide a summary:

- Skills activated
- Number of issues found (general + per skill)
- Number of fixes applied
- Any remaining issues the user chose not to fix

## Review Priority

Focus on issues in this order (highest impact first):

1. **Correctness and regressions** — bugs, factual errors, broken references, contradictions
2. **Missing cases and risky assumptions** — omitted edge cases, caveats, prerequisites
3. **Narrative/pedagogical flow** — wrong ordering, compiler-dictated structure
4. **Variation theory violations** — principles before examples, missing contrasts
5. **Literate programming quality** — chunk names, test placement, explanation quality
6. **LaTeX conventions** — semantic environments, csquotes, cleveref
7. **Didactic notes** — pedagogical reasoning in student-facing text
8. **Crypto notation** — inconsistent notation, missing acro usage
