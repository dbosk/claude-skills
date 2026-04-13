---
name: nytid-todo
description: >-
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

Use `add` with `--parent` to break a task into smaller pieces. The priority
system uses interactive binary-search comparison, so when adding tasks you will
be asked to compare priorities. Use `--top-level` to override automatic
parenting if needed.

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
| List my tasks | `ls` | `--all`, `--status`, `--flat`, `-n` |
| What am I working on? | `status` | — |
| Start next task | `next` | `--headless` |
| Start specific task | `start` | `--timeout`, tmux flags |
| Pause current task | `stop` | — |
| Complete current task | `done` | — |
| View task details | `view` | — |
| Edit task metadata | `edit` | `--edit` for editor |
| Add progress note | `note` | `--message`, `--edit` |
| Create subtask | `add` | `--parent`, `--here` |
| Change priority | `reprioritize` | — |
| Import from GitHub | `import` | `--number`, `--type` |
| Sync with GitHub | `sync` | `--repo` |
| Remove a task | `rm` | `--force` |
