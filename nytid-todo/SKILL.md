---
name: nytid-todo
description: |
  Manages work items via nytid todo subcommands as worker dan-claude. Relevant
  when the user asks to check, start, or complete tasks, view task details, add
  progress notes, create subtasks, reprioritize items, or import/sync GitHub
  issues. Also triggered by "what should I work on next?", "show my tasks",
  "mark that done", "what's in progress?", or mentions of nytid, todo, or work
  items. Also use when handing the user a batch of follow-ups from a session
  ("add todos to my nytid", papers to download, things only the user can do)
  and when a todo should resume the current Claude session (`claude --resume`)
  in a given working directory.
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

### Exception: user-owned work (omit `--who`)

`dan-claude` is a delegated worker for code/tooling tasks, not a stand-in
for the user. When the todo is something **only the user can do**, **omit
`--who`** entirely so it defaults to the current user (`dbosk`):

- **Email-derived todos** — when the `inbox-info` skill is active and the
  user is converting flagged emails into todos. Assigning email replies to
  `dan-claude` mis-routes human communication. See
  `~/.claude/skills/inbox-info/references/todo-conversion-rules.md`.
- **Batches of follow-ups the user asked to have "in my nytid"** — e.g.
  papers to fetch through the library proxy, credentials to obtain, people
  to contact. See "Handing the user follow-ups from a session" below.

All other `nytid todo` work still uses `--who dan-claude`.

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
`--flat` to see the full hierarchy. The listing is **capped** (`-n`, 10 by
default): pass `-n 0` to see everything, in particular when checking that an
`add` landed. On a terminal a cut listing ends with "… N more (use -n 0 to
show all)"; piped output is headerless tab-separated rows, `-f csv` adds a
header and commas, `-f json` gives structure.

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
currently active task. `view N --notes` prints every sub-item's description and
notes in full instead of a one-line preview; `--all` includes done sub-items,
so `view N --all --notes` reads a whole group's history.

### Update tasks and leave notes

Use `edit` to change metadata (title, description, deadline, estimate, labels,
assignment, parent). Use `note` to append progress updates, blockers, or
decisions. Both support `--help` for available options.

Prefer `note` for incremental updates (progress, findings, blockers) and `edit`
for structural changes (reassignment, deadline shifts, re-parenting).

**Description versus notes.** The description is **one line**: what the task
is and why (or empty). Everything else goes in the notes: context, artefact
paths, what to check, progress, findings, review history. At creation pass
`--note "…"` (repeatable; each value is one paragraph); afterwards use `note`,
which appends. `edit --description` **replaces** the whole line and an empty
string clears it; never turn the description into a status log ("reviewed v1
and v2; since v2: …" belongs in `note`). `edit -E` shows the description as a
`description: |` block and the notes as the body, so the user can reformat
either by hand.

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

- `--bottom` (old name `--append`) — places the new task just below the
  lowest-priority sibling. Safe even when the parent has no existing children
  (the first child starts in the middle of the parent's range). When
  batch-adding in priority order (highest first), each `--bottom` slots one
  rung below the previous, encoding the order without prompts.
- `--top` — places the new task above the highest-priority sibling.
- `--prio N` — stores exactly `N`; write negatives as `--prio=-10`.
- `--skip-priority` — no numeric priority assigned; the task sorts by
  deadline only. Use for "do whenever" buckets.

See "Priority and ranking" below for what the number means.

**Default-command** (`-c`/`--command`): the value passed here becomes the
command `nytid todo start <id>` runs (replacing the worker's default, which
is `bash`). Useful for embedding a one-step action — opening a file in an
editor, launching a query in NeoMutt, running a script — so the user goes
from `start` to working with no copy-paste.

### Priority and ranking

A priority is a float; **higher means more urgent**, and any value is allowed,
negatives included (spell them `--prio=-10`; a bare `--prio -10` is read as
another option). Listings (`ls -p`) show the *effective* priority: the stored
number plus a boost that grows as a deadline approaches, so the number `ls`
shows is not the number you set. Placement flags always work on stored
numbers among the item's active, ranked siblings for the same worker; done
items and other workers' items are ignored. Children of an unranked parent
stay unranked.

Non-interactive controls (each command refuses two of these together):

- `add --top | --bottom | --prio N | --skip-priority`.
- `edit ID --prio N | --top | --bottom` re-ranks among the current siblings.
- `edit ID --parent P` **re-ranks interactively** among the new siblings by
  default; in a session without a terminal always add `--top`, `--bottom`,
  `--prio N` or `--keep-prio` (keeps the old number), or the prompt aborts.
- `reprioritize ID --top | --bottom | --above ID2 | --below ID2` (alias
  `reprio`); `--above`/`--below` place the item strictly between `ID2` and its
  neighbour, and `ID2` must be a ranked sibling in the comparison set. Without
  a flag, `reprioritize` reruns the interactive binary search; without an ID
  it ranks every unranked item and takes no placement flag.

## Handing the user follow-ups from a session

When a session produces a batch of items the user must do personally (e.g.
"the papers that couldn't be downloaded: add todos so I try to fetch them"),
build **one parent todo that resumes the session, with one subtask per
item**, all assigned to the user (omit `--who`):

1. **Parent** — top-level, `--bottom` (no interactive priority prompt), a
   one-line description, notes saying where the session's artefacts live
   (scratchpad paths, scholar sessions, plan file) and the ordering rule for
   the subtasks, and a default command that lands the user back in *this*
   session in the right directory:

   ```
   nytid todo add <labels> --top-level --bottom -t "<what and why>" \
     --description "<one line: what and why>" \
     --note "<artefact locations>" --note "<ordering rule for subtasks>" \
     -C <working directory of the session> \
     -c "claude --resume <session-id>"
   ```

   The session id is the UUID in the session's scratchpad path
   (`…/<project>/<session-id>/scratchpad`); the working directory is the
   session's primary working directory (a worktree path when working in
   one). `-C` and `-c` can also be set afterwards with `edit`.
2. **Subtasks** — `--parent <parent-id> --bottom`, added in priority order
   (most load-bearing first, so `--bottom` encodes the order), each with a
   one-step default command (`-c "xdg-open https://doi.org/<doi>"` for a
   paper, an editor or URL otherwise) and a `--note` stating **what to
   check once the item is obtained** (e.g. "verify the 13/3/÷16 parameters
   attributed to it"), so the user does not have to reconstruct the context.
3. Report the parent id and the few subtasks that matter most; the rest
   are visible via `view <parent-id> --notes`.

Batch the subtask adds in one shell loop; each `add` prints `Added todo
#<id>`, so capture the parent's id from its own output before the loop.

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
| List my top-level tasks | `ls` | `--all`, `--status`, `--flat`, `-n 0` for everything (positional args = label filters, **not** parent IDs) |
| What am I working on? | `status` | — |
| Start next task | `next` | `--headless` |
| Start specific task | `start` | `--timeout`, tmux flags |
| Pause current task | `stop` | — |
| Complete current task | `done` | — |
| View task + its sub-items | `view <id>` | `--notes` for sub-items' notes, `--all` for done ones — use this instead of `ls <id>` |
| Edit task metadata | `edit` | `--edit` for editor, `-c` for default command, `--description` replaces the one-line statement (details go in `note`), `--parent` with `--top`/`--bottom`/`--keep-prio` |
| Add progress note | `note` | `--message`, `--edit` (replaces the whole notes on local items) |
| Create subtask | `add` | `--parent`, `--top-level`, `--top`/`--bottom`, `--note` (repeatable), `-c` (auto-parents to active todo by default) |
| Change priority | `reprioritize` | `--top`, `--bottom`, `--above ID`, `--below ID` |
| Import from GitHub | `import` | `--number`, `--type` |
| Sync with GitHub | `sync` | `--repo` |
| Remove a task | `rm` | `--force` |
