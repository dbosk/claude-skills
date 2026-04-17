---
name: document-issues
description: "Captures unrelated follow-up issues discovered during repository work and records them for later. Use proactively when: (1) working inside a git repository, (2) an out-of-scope bug, cleanup item, missing test or documentation, or tech-debt task is discovered, (3) the user mentions filing an issue, follow-up, backlog item, or nytid import. Prefer gh issue, ask before creating anything unless autonomous issue capture is enabled, and optionally import created GitHub issues into nytid todo."
---

# Documenting follow-up issues

Use this skill while working in a git repository when an unrelated issue is
worth preserving for later follow-up.

## Default behavior

Prefer GitHub issues as the system of record.

Default to asking before creating anything unless the user explicitly enabled
autonomous issue capture for the current conversation.

Treat `nytid todo import` as an optional second step after creating a GitHub
issue, not as the default capture path.

## What to capture

Capture only issues that are:

- unrelated to the current task
- actionable enough to describe clearly
- valuable to revisit later

Typical examples:

- an unrelated bug
- missing tests discovered while fixing something else
- a cleanup/refactor item that should not be folded into the current change
- misleading docs or comments
- tooling or CI friction uncovered during the task

Do not create a follow-up issue when:

- the current task already includes fixing it
- the observation is too vague to be actionable
- there is no repository context
- the repository is not GitHub-backed or issue creation is unavailable

## Preferred workflow

### 1. Confirm that issue capture makes sense

When autonomous issue capture is not enabled, ask a short confirmation before
creating anything.

Recommended wording:

`I found an unrelated follow-up issue in this repo. Want me to file a GitHub issue for it?`

If the user has stated a session preference to also import created GitHub issues
into `nytid todo`, honor that after issue creation.

### 2. Verify repository and GitHub context

Check that the current directory is inside a git repository:

```bash
git rev-parse --is-inside-work-tree
```

Resolve the GitHub repository and ensure issues are enabled:

```bash
gh repo view --json nameWithOwner,url,hasIssuesEnabled
```

If this fails or `hasIssuesEnabled` is false, do not create a GitHub issue.
Offer `nytid todo` only if the user asked for it or GitHub issue creation is not
available and they still want the follow-up captured.

### 3. Check for likely duplicates

Search existing issues before creating a new one. Use a short query built from
the most specific keywords in the proposed issue title.

```bash
gh issue list --state all --search "<keywords>" --json number,title,url,body
```

If a likely duplicate exists, show it to the user instead of creating a new
issue unless they explicitly want another one.

### 4. Create the GitHub issue

Use noninteractive creation.

```bash
gh issue create --title "<title>" --body-file -
```

Prefer existing labels when clearly applicable. Do not create new labels
automatically.

Issue bodies should be concise but preserve the context that made the issue
worth filing.

Use this structure:

```markdown
## Context
What work was in progress when this came up?

## Observation
What problem, gap, or follow-up item was discovered?

## Why it matters
Why should this be addressed later?

## Evidence
Files, commands, error messages, or behavior that support the observation.

## Suggested follow-up
The most likely next step, without overcommitting to a solution.
```

When possible, include concrete file paths, function names, commands, and
behavior observed during the current task.

### 5. Optionally import into `nytid todo`

If the user enabled the session preference to also import created GitHub issues
into `nytid todo`, import the created issue after it is filed.

Always pass `--who dan-claude` for `nytid` operations.

Preferred import pattern:

```bash
nytid todo import <owner/repo> --number <issue-number> --who dan-claude --here --github-labels
```

Use `gh issue create` as the source of truth. If the returned output does not
reliably expose the issue number, resolve it by exact title with `gh issue list`
before importing.

Do not modify todo items assigned to other workers.

## Communication

When proposing or reporting a captured issue, include:

- the proposed or created title
- the target repository
- whether it was created in GitHub, imported into `nytid`, or both
- any duplicate issue found instead of creating a new one

If nothing was recorded, say why.
