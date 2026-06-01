---
description: Create atomic git commits following best practices
user-invocable: true
license: MIT
---

## Current Context

- **Current branch:** !`git branch --show-current`
- **Git status:** !`git status --short`
- **Staged changes:** !`git diff --staged --stat`
- **Unstaged changes:** !`git diff --stat`
- **Recent commits:** !`git log --oneline -5`

## Git Commit Practices

**CRITICAL: Commit early, commit often, one concern per commit!**

### Branch Safety

**NEVER commit directly to main/master branches.**

If the current branch is `main` or `master`:
- Derive a descriptive feature branch name from the staged and unstaged changes
- If one clear name fits, create the branch immediately and continue
- If the branch name is ambiguous, use the available ask/question tool in the current environment to confirm or override it
- After choosing the name, create the branch yourself and proceed with the commit
- Do not ask the user to create the branch manually
- Example: `git switch -c fix-descriptive-name`

### Atomic Commits Principle

Each commit must represent **ONE logical change**:
- Easier code review - reviewers understand one change at a time
- Safer reverts - can undo specific changes without losing other work
- Clearer history - git log tells the story of the project
- Better debugging - git bisect works effectively

### Commit Granularity

**Good granularity:**
- Fix the first issue, commit, then fix the next
- One bug = one commit
- One feature component = one commit
- One refactoring aspect = one commit

**Red flags (split the commit):**
- If you need "and" to describe unrelated changes
- If `git diff` output is very long
- If changes touch 3+ files with different purposes

### Commit Message Format

```
Short summary (50 chars or less, imperative mood)

Detailed explanation if needed:
- What changed
- Why it changed
- Impact or implications
```

You can add attribution too, `Co-authored-by:`. Use Claude Code for Claude 
models and OpenCode for OpenAI models. Specify the model used.

**Rules:**
- Imperative mood: "Fix bug" not "Fixed bug"
- Capitalize first word
- No period at end
- Be specific: "Fix timestamp mismatch in terminal grading" not "Fix bug"
- Stay under 50 characters when possible

### Literate Programming Projects

**CRITICAL**: In projects with .nw files, NEVER commit generated files.

Before committing, check staged files:
- If a .py or .tex file has a corresponding .nw file, it's generated - DO NOT COMMIT
- Only commit the .nw source files
- Let .gitignore handle the rest

### Pre-Commit Checklist

Before committing, verify:
- [ ] On correct branch (not main/master unless approved)
- [ ] Represents ONE logical change
- [ ] Clear, descriptive commit message
- [ ] All related changes included
- [ ] No unrelated changes included
- [ ] No generated files staged (if literate programming project)

## Your Task

Based on the context above:

1. **Check the branch** - If on main/master, create a descriptive feature branch first. Use the available ask/question tool only if the branch name needs confirmation

2. **Review staged changes** - Determine if they represent one atomic commit or should be split

3. **If changes are atomic:**
   - Stage any relevant unstaged files if appropriate
   - Create the commit with a proper message following the format above
   - Use `git commit -m "$(cat <<'EOF' ... EOF)"` for multi-line messages

4. **If changes should be split:**
    - Explain why and what the logical divisions are
    - Use the available ask/question tool to ask which part to commit first, or guide through interactive staging

5. **For literate programming projects:**
   - Verify no generated .py/.tex files are staged that have corresponding .nw sources
   - If found, unstage them with `git reset HEAD <file>`

Execute the branch creation and commit using the available tools in the current environment. Stage and commit in a single response when appropriate.
