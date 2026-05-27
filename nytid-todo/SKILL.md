---
name: nytid-todo
description: |
  Manages work items via nytid todo subcommands as worker dan-claude. Relevant
  when the user asks to check, start, or complete tasks, view task details, add
  progress notes, create subtasks, reprioritize items, or import/sync GitHub
  issues. Also triggered by "what should I work on next?", "show my tasks",
  "mark that done", "what's in progress?", or mentions of nytid, todo, or work
  items.
---

# Managing work with `nytid todo`

## Identity: always use `--who dan-claude`

Every `nytid todo` command defaults to the current system user (`dbosk`). **Pass
`--who dan-claude` on every invocation** — listing, adding, starting,
completing, everything. Forgetting this flag means reading or modifying the
wrong person's tasks.

Omitting or widening `--who` is acceptable when *reading* tasks to get context
(see "Getting context from other assignees" below). **Never modify tasks that
are not assigned to `dan-claude`.**

### Exception: email-derived todos (user-owned work)

When the `inbox-info` skill is active and the user is converting flagged
emails into todos, **omit `--who`** entirely so the new todos default to the
current user (`dbosk`). `dan-claude` is a delegated worker for code/tooling
tasks, not a stand-in for the user in human communication — assigning email
replies to `dan-claude` mis-routes work the user must do themselves. See
`~/.claude/skills/inbox-info/references/todo-conversion-rules.md` for the
full rationale. This exception applies only to email-derived todos; all
other `nytid todo` work still uses `--who dan-claude`.

## Discovering options

Each subcommand has its own `--help` flag. Always consult it for exact syntax,
available flags, and defaults:

```
nytid todo <subcommand> --help
```

The rest of this document describes workflows, not exact command syntax.

## Core workflows

### See what to work on

Use `ls` to list your tasks sorted by effective priority. Key options control
depth (`--all` for subtasks), count limits, status filters, and output format —
check `ls --help`. The default shows only top-level items; use `--all` or
`--flat` to see the full hierarchy.

Use `status` to see the currently active task stack (what is already in
progress). Use `next` to let the system pick the highest-priority pending task.

### Work on a task

The task lifecycle follows a stack model:

1. **Start** a task with `start` (or let `next` pick one). This pushes it onto
   the active stack and optionally spawns a shell in the task's working
   directory.
2. **Stop** pauses the task and pops it from the stack without completing it.
3. **Done** marks the task complete and pops it from the stack.

Check `start --help` for options like tmux integration, timeouts, and working
directory handling.

If a task is already in progress, `next` will start its highest-priority pending
child rather than a new top-level task — this is how you drill into subtasks.

### Get context on a task

Use `view` to see full details of a task (title, description, labels, deadline,
estimate, notes, parent/child relationships). Without an ID it shows the
currently active task.

### Update tasks and leave notes

Use `edit` to change metadata (title, description, deadline, estimate, labels,
assignment, parent). Use `note` to append progress updates, blockers, or
decisions. Both support `--help` for available options.

Prefer `note` for incremental updates (progress, findings, blockers) and `edit`
for structural changes (reassignment, deadline shifts, re-parenting).

### Create subtasks

Use `add` to break a task into smaller pieces. **Auto-parenting**: if a task
is already in-progress (visible via `status`) and you omit both `--parent`
and `--top-level`, the new task auto-parents under the active todo. This is
the most ergonomic way to add subtasks while working on something — just
`nytid todo add ...` and the parent is inferred. Pass `--top-level` to opt
out and add at the root, or `--parent <id>` to target a specific parent.

**Priority assignment** defaults to interactive binary-search comparison
against existing siblings (you'll be prompted to compare priorities). For
non-interactive batch adds use one of:

- `--append` — places the new task just below the lowest-priority sibling.
  Safe even when the parent has no existing children (the first child gets
  a sensible default). When batch-adding in priority order (highest first),
  each `--append` slots one rung below the previous, encoding the order
  without prompts.
- `--skip-priority` — no numeric priority assigned; the task sorts by
  deadline only. Use for "do whenever" buckets.

**Default-command** (`-c`/`--command`): the value passed here becomes the
command `nytid todo start <id>` runs (replacing the worker's default, which
is `bash`). Useful for embedding a one-step action — opening a file in an
editor, launching a query in NeoMutt, running a script — so the user goes
from `start` to working with no copy-paste.

### Reprioritize

Use `reprioritize` (alias `reprio`) to rerun the binary-search priority
comparison for a task whose importance has changed.

## Getting context from other assignees

Your tasks often exist as children of broader items assigned to `dbosk` or
others. To understand the full picture:

- Use `ls` without `--who` (or with a wider filter) to see all assignees' tasks.
- Use `view` on a parent item to read its description and notes, even if it is
  not assigned to you.

This is read-only context gathering.

## GitHub integration

Use `import` to pull GitHub issues/PRs into the todo system and `sync` to keep
them updated. Both support `--help` for repository, type, and metadata options.
Always pass `--who dan-claude` when importing to ensure correct assignment.

## Quick reference

| Intent | Subcommand | Key flags to check |
|--------|------------|--------------------|
| List my top-level tasks | `ls` | `--all`, `--status`, `--flat`, `-n` (positional args = label filters, **not** parent IDs) |
| What am I working on? | `status` | — |
| Start next task | `next` | `--headless` |
| Start specific task | `start` | `--timeout`, tmux flags |
| Pause current task | `stop` | — |
| Complete current task | `done` | — |
| View task + its sub-items | `view <id>` | shows description, notes, children — use this instead of `ls <id>` |
| Edit task metadata | `edit` | `--edit` for editor, `-c` for default command |
| Add progress note | `note` | `--message`, `--edit` |
| Create subtask | `add` | `--parent`, `--top-level`, `--append`, `-c` (auto-parents to active todo by default) |
| Change priority | `reprioritize` | — |
| Import from GitHub | `import` | `--number`, `--type` |
| Sync with GitHub | `sync` | `--repo` |
| Remove a task | `rm` | `--force` |
