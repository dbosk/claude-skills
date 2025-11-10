---
name: git-commit-practices
description: Guide proper git commit practices including commit granularity, frequency, and message quality. Use proactively when: (1) making multiple related code changes, (2) completing any logical unit of work, (3) before refactoring or starting new features, (4) after fixing bugs or issues. Always commit early and often with focused, single-purpose commits rather than large combined commits.
---

# Git Commit Practices

**CRITICAL: Commit early, commit often, one concern per commit!**

This skill ensures you follow proper git commit practices to maintain clean, reviewable git history.

## Core Principle: Atomic Commits

Each commit should represent **one logical change** - a single fix, feature, or refactoring that can be understood, reviewed, and reverted independently.

### Benefits of Atomic Commits
- **Easier code review** - Reviewers can understand one change at a time
- **Safer reverts** - Can undo specific changes without losing other work
- **Clearer history** - Git log tells the story of the project
- **Better debugging** - Git bisect works effectively
- **Professional workflow** - Industry standard practice

## When to Commit

### ✅ Commit Immediately After

1. **Fixing a single bug** - One bug, one commit
2. **Completing a logical unit** - Function works, tests pass
3. **Refactoring one aspect** - Before and after are both working states
4. **Adding one feature component** - Each independent piece
5. **Updating documentation** - Separate from code changes
6. **Making configuration changes** - Isolated from feature work
7. **Quoted all variables in one file** - Before moving to next file
8. **Fixed one specific issue** - Don't bundle unrelated fixes

### ❌ Don't Wait Until

- You've fixed "everything"
- The entire feature is complete
- You've made changes to many files
- End of the day/session
- You remember to commit

## Commit Granularity Guide

### Perfect Granularity Examples

**Scenario: Fixing critical bugs in grading scripts**

Bad (what you did):
```
✗ One commit: "Fix critical bugs in grading scripts"
  - Fixed timestamp bug
  - Fixed undefined variable
  - Fixed SSH injection
  - Quoted all variables everywhere
  (5 files, 90 insertions, 88 deletions)
```

Good (what you should have done):
```
✓ Commit 1: "Fix terminal grading timestamp format mismatch"
  modules/terminal/grading/grade.sh.nw | 2 +-

✓ Commit 2: "Fix LaTeX grading undefined variable reference"
  modules/latex/grading/grade.sh.nw | 8 ++++----

✓ Commit 3: "Fix SSH command injection in common.sh"
  adm/grading/common.sh.nw | 3 ++-

✓ Commit 4: "Quote variables in common.sh for safety"
  adm/grading/common.sh.nw | 12 ++++++------

✓ Commit 5: "Quote variables in git grading script"
  modules/git/grading/grade.sh.nw | 8 ++++----

✓ Commit 6: "Quote variables in latex grading script"
  modules/latex/grading/grade.sh.nw | 12 ++++++------

✓ Commit 7: "Quote variables in ssh grading script"
  modules/ssh/grading/grade.sh.nw | 6 +++---

✓ Commit 8: "Quote variables in terminal grading script"
  modules/terminal/grading/grade.sh.nw | 10 +++++-----
```

### More Examples

**Scenario: Adding a new feature**
```
✓ Commit 1: "Add user authentication data model"
✓ Commit 2: "Add user authentication API endpoint"
✓ Commit 3: "Add user authentication UI component"
✓ Commit 4: "Add user authentication tests"
✓ Commit 5: "Add user authentication documentation"
```

**Scenario: Refactoring**
```
✓ Commit 1: "Extract validation logic to separate function"
✓ Commit 2: "Rename ambiguous variable names for clarity"
✓ Commit 3: "Remove unused imports and dead code"
```

## Workflow for Multiple Changes

### Step-by-Step Process

When you have multiple fixes to make:

1. **Fix the first issue**
   ```bash
   # Make the change
   vim file1.nw

   # Verify it works (if applicable)
   make

   # Commit immediately
   git add file1.nw
   git commit -m "Fix specific issue in file1"
   ```

2. **Fix the second issue**
   ```bash
   # Make the change
   vim file2.nw

   # Commit immediately
   git add file2.nw
   git commit -m "Fix specific issue in file2"
   ```

3. **Continue for each issue**
   - Never batch multiple fixes
   - Each commit should be independently reviewable

### Interactive Staging for Mixed Changes

If you've already made multiple changes (not ideal but happens):

```bash
# Stage changes selectively
git add -p file.nw

# Review what's staged
git diff --staged

# Commit the staged portion
git commit -m "First logical change"

# Repeat for remaining changes
git add -p file.nw
git commit -m "Second logical change"
```

## Commit Message Guidelines

### Format

```
Short summary (50 chars or less)

Detailed explanation if needed:
- What changed
- Why it changed
- Impact or implications

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Summary Line Rules

- **Imperative mood**: "Fix bug" not "Fixed bug" or "Fixes bug"
- **Capitalize first word**: "Add feature" not "add feature"
- **No period at end**: "Update docs" not "Update docs."
- **Be specific**: "Fix timestamp mismatch in terminal grading" not "Fix bug"
- **Stay under 50 characters** when possible

### Good vs Bad Messages

**Bad:**
```
✗ "Fix stuff"
✗ "Updates"
✗ "WIP"
✗ "Fixed various issues"
✗ "Changes to multiple files"
```

**Good:**
```
✓ "Fix timestamp format mismatch in terminal grading"
✓ "Remove undefined variable from check_student"
✓ "Quote variables in common.sh for space safety"
✓ "Add error handling for missing config file"
```

## Proactive Reminders

### After Reading Multiple Files

If you read multiple files to understand an issue:
- **Don't fix them all at once**
- Fix the first one and commit
- Then move to the next

### After Making a Plan

If you create a todo list with multiple items:
- **Commit after completing each todo item**
- Don't wait until all items are complete
- Each item should ideally be one commit

### When User Says "Fix all..."

If user requests fixing multiple issues:
- **Clarify**: "I'll fix these one at a time and commit each separately"
- **Proceed sequentially**: Fix, commit, next
- **Update user**: "Fixed X (committed), now working on Y"

## Red Flags (Stop and Commit)

Watch for these signs you should commit NOW:

1. **Multiple file changes** - If you've modified 3+ files, you've probably done multiple things
2. **Large diffs** - If `git diff` output is long, break it up
3. **Mixed concerns** - If commit message needs "and", split it
4. **Time passing** - If 15+ minutes since last commit, commit something
5. **Before switching tasks** - Always commit current work before starting new work
6. **After "done"** - When you think "that works", commit it

## Exception: When to Combine

Very rarely, commits can be combined IF:

1. **Mechanical changes** - Same operation applied everywhere (e.g., "Rename function X to Y across codebase")
2. **Tiny fixes** - Fixing typos in multiple places
3. **Broken state** - Change #1 breaks build and change #2 fixes it (but avoid this situation)

**Default rule**: When in doubt, commit separately.

## Integration with TodoWrite

When using TodoWrite tool:

```
Todo item completed → Commit immediately → Mark todo as completed
```

**Not:**
```
Complete all todos → One big commit → Mark all completed
```

## Checklist for Each Commit

Before committing, verify:

- [ ] This commit represents ONE logical change
- [ ] The commit message clearly describes what changed
- [ ] All related changes are included (nothing missing)
- [ ] No unrelated changes are included (nothing extra)
- [ ] The code works/builds at this commit (if applicable)
- [ ] The commit can be understood independently

## Recovery from Large Commits

If you've already made a large commit with multiple concerns:

### Option 1: Accept and Move Forward
- Learn from it for future commits
- Don't amend/rewrite if already pushed

### Option 2: Split with Interactive Rebase (if not pushed)
```bash
# Reset to before the commit
git reset HEAD~1

# Stage and commit each logical piece
git add -p
git commit -m "First logical change"

git add -p
git commit -m "Second logical change"
```

## Summary

**Remember:**
1. **Commit early and often** - After each logical unit of work
2. **One concern per commit** - Each commit is independently reviewable
3. **Good messages** - Future you (and reviewers) will thank you
4. **Before refactoring** - Save working state first
5. **Stop and commit** - When any red flag appears

**The mantra:** "Working state reached → Commit now → Continue working"
