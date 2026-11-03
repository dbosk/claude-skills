---
name: nytid-todo
description: |
  Manages work items with nytid todo, a list shared by the user and their
  agents: mostly todos for the user, plus items an agent can do on its own
  (worker dan-claude). Relevant
  when the user asks to check, start, or complete tasks, view task details, add
  progress notes, create subtasks, reprioritize items, link items (several
  parents, blocking dependencies, discovered-from), or import/sync GitHub
  issues. Also triggered by "what should I work on next?", "what's ready?",
  "show my tasks", "mark that done", "what's in progress?", "what blocks
  this?", or mentions of nytid, todo, or work items. Also use when handing
  the user a batch of follow-ups from a session ("add todos to my nytid",
  papers to download, things only the user can do) and when a todo should
  resume the current Claude session (`claude --resume`) in a given working
  directory.
---

# Managing work with `nytid todo`

`nytid todo` is shared by the user and their agents. Most of the time an agent
adds todos **for the user**.

## Who an item is for

**By default, omit `--who`.** Items then go to the current user (`dbosk`), and
listings show theirs. This covers anything that needs the user: replying to
email (see `~/.claude/skills/inbox-info/references/todo-conversion-rules.md`),
fetching papers through the library proxy, getting credentials, contacting
people, making decisions, and batches of follow-ups (see "Handing the user
follow-ups from a session").

Change, complete or remove the user's existing items only when asked to.

### Items an agent can do on its own

File an item with `--who dan-claude` when an agent can do it on its own, without
intervention. To work on such items, pass `--who dan-claude` to the listing and
lifecycle commands as well.

### What `--who` means per command

- **Assigns:** `add`, `import` and `edit`. **`edit --who` reassigns the item**, so
  never pass it just to say who is acting.
- **Filters by regex:** `ls`, `ready`, `next`. The default is the current user, and
  `--who ''` means everyone.
- **Acts as that worker:** `start`, `stop`, `done`, `note`, `view`, `rm`, `adopt`.
  Without an ID they use that worker's active item. `done <id>` refuses another
  worker's item, so a `dan-claude` item needs `--who dan-claude`.
- **Not accepted:** `status` (shows every worker's active items), `reprioritize`
  (without an ID, it ranks the current user's items), `export`, `sync`.

## Discovering options

Each subcommand has its own `--help` flag. Always consult it for exact syntax,
available flags, and defaults:

```
nytid todo <subcommand> --help
```

This document describes workflows and the flags they rely on; `--help` is the
authority on exact syntax.

To try a command out, never use the real lists: set `NYTID_HOME` to a
scratch directory (`NYTID_HOME=$(mktemp -d) nytid todo …`), and the
configuration and all data live there instead. **This does not isolate tmux.**
Inside tmux, `start` and `adopt` still adopt the real window and install hooks on
the real session, and those hooks run without `NYTID_HOME`. Unset the variables
too: `env -u TMUX -u TMUX_PANE NYTID_HOME=… nytid todo start …`.

## Core workflows

### See what to work on

Use `ls` to list tasks sorted by effective priority. Key options control
depth, count limits, status filters, and output format — check `ls --help`.
The default shows only top-level items: `--all` adds their direct sub-items,
`-r N` shows N levels and a bare `-r` every level; `--flat` only drops the
tree layout. The listing is **capped** (`-n`, from `todo.ls.count`): pass `-n
0` to see everything, in particular when checking that an `add` landed. On a
terminal a cut listing ends with "… N more (use -n 0 to show all)"; piped
output is headerless tab-separated rows, `-f csv` adds a header and commas,
`-f json` gives structure.

Use `status` to see the currently active task stack (what is already in
progress, for every worker). Use `next` to start the highest-priority pending
task: it walks the tree one level per call, and takes label filters.

**To decide what to work on, prefer `ready`**: a flat list, in priority
order, of the items that can be started now — pending, nothing open blocks
them, and no open sub-items (`--all` also lists ready parents). It takes the
same label filters, `-n` and `-f` as `ls`; read it as `nytid todo ready -f json`,
adding `--who dan-claude` for an agent's own items. To start the first one,
use `next --ready` (`--tree` walks the tree for one call when `todo.next.ready`
makes `--ready` the default). With a todo active, `next --ready` only considers
items below it, and fails rather than starting something elsewhere. `next` and
`ready` skip blocked items; `ls --blocked` lists the blocked and stuck ones with
the reason.

### Work on a task

The task lifecycle follows a stack model:

1. **Start** a task with `start` (or let `next` pick one). This pushes it onto
   the active stack and runs the task's command, or else opens a shell in its
   working directory. `--no-command --no-shell` starts it without launching
   anything. Inside tmux that still adopts the current window and installs hooks
   on the session; `todo adopt` does this on purpose for an existing window.
2. **Stop** pauses the task and pops it from the stack without completing it.
3. **Done** marks the task complete and pops it from the stack.

Check `start --help` for options like tmux integration, timeouts, and git
worktrees.

If a task is already in progress, `next` will start its highest-priority pending
child rather than a new top-level task — this is how you drill into subtasks.

**Claims.** Starting an item claims it for the worker (`claimed_by`). `start`
refuses an item that another worker has active; do **not** pass `--force`
(which takes it over and stops the other worker's tracking) unless the user
asked for it. Starting a blocked item warns but still starts it; prefer an
item from `ready`.

### Get context on a task

Use `view` to see full details of a task (title, description, labels, deadline,
estimate, notes, parent/child relationships). Write `view`: `show` is only an
alias in recent versions, and older installs reject it. Without an ID it shows
the currently active task. It lists direct children, at most `-n` per parent
(`todo.view.subitems`, 5 by default). `--notes` prints their descriptions and
notes in full instead of a one-line preview, `--all` includes done ones, and `-r`
goes deeper, so `view N --all --notes -n 0 -r` reads a whole group's history.
`view` also prints `Parents:` (for an item with several), `Blocked by:` /
`Blocks:`, `Discovered from:` / `Led to:`, `Needed by` / `Raised to` (see
"Priority and ranking") and, for done items, when they were closed.
Notes are signed: each appended note starts with a
`[YYYY-MM-DD HH:MM who]` header. `ls -f json` carries the same data in the
fields `parents`, `blocked_by`, `discovered_from`, `closed`, `claimed_by`.

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
either by hand. In that buffer every sub-item heading ends with its id,
`## Title {#7}`; a shared item's second appearance is a reference
`## Title {also #7}`. Keep the markers when editing: deleting a heading
removes the item only from *that* parent (a shared item is detached, not
deleted), and moving a section re-parents the item.

### Create subtasks

Use `add` to break a task into smaller pieces. **Auto-parenting**: if a task
is already in-progress (visible via `status`) and you omit both `--parent`
and `--top-level`, the new task auto-parents under the active todo. This is
the most ergonomic way to add subtasks while working on something — just
`nytid todo add ...` and the parent is inferred. Pass `--top-level` to opt
out and add at the root, or `--parent <id>` to target a specific parent.

**Part of vs found while doing.** Auto-parenting means "this is part of the
active task". For work you *discovered* while doing it but that is not part
of it (an unrelated bug, a follow-up), add it with `--top-level` or another
`--parent`: the active task's id is then recorded automatically as
`discovered_from` (shown as `Discovered from:` / `Led to:` in `view`). Use
`--discovered-from N` to name another source, `--no-discovered-from` to skip.

**Several parents.** An item can sit under several parents and at the top
level at once: repeat `--parent` on `add` (`--top-level --parent 12` = top
level and under #12), or use `edit --add-parent P` / `--remove-parent P`
(`0` = top level; `--parent P` replaces all). Labels are the union of the
parents', the deadline the earliest. It keeps **one** priority, the highest
any of its places gives it; under the other parents it shows "(ranked via
#12)" and sorts first.

**Dependencies.** `add --blocked-by B` / `--blocks Y` (repeatable) and
`edit --add-blocker B` / `--remove-blocker B` / `--blocks Y` link any two
items. An item is blocked while one of its blockers, or a blocker of an
ancestor on every one of its paths, is open. A link that would leave work
that can never be done is refused with the circle explained; `rm` warns
instead. A blocker below the item it blocks has no effect.

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

**Where it runs.** `--here` captures the current directory and environment,
`-C` sets the directory only, `--env` captures the environment only, and
`--worktree NAME` runs in a git worktree that is removed on exit if left
unchanged. All of them also work on `edit` and `import`.

**Default-command** (`-c`/`--command`): the value passed here becomes the
command `nytid todo start <id>` runs, instead of the worker's default
(`todo.worker.<worker>.command`); with neither, `start` opens a shell in the
item's directory as `--shell` and `todo.shell` allow. Useful for embedding a
one-step action — opening a file in an editor, launching a query in NeoMutt,
running a script — so the user goes from `start` to working with no
copy-paste.

### Priority and ranking

A priority is a float; **higher means more urgent**, and any value is allowed,
negatives included (spell them `--prio=-10`; a bare `--prio -10` is read as
another option). Listings (`ls -p`) show the *effective* priority, so the number
`ls` shows is not the number you set. It is the stored number plus a boost that
grows as the item's *latest finish* approaches: the latest it can be done for
everything after it to meet its own deadline (`ls` shows "Oct 16 for #12", `view`
says `Needed by`). A blocker is also raised to at least the priority of what it
holds up (`view` says `Raised to`). Placement flags always work on stored
numbers among the item's active, ranked siblings for the same worker; done
items and other workers' items are ignored. Children of an unranked parent
stay unranked. Ranges nest: a sub-item's number lies between its parent and
the parent's next-lower sibling, and re-ranking a parent moves its sub-items
along. Files with older numbers are renumbered once on the first write
("Renumbered N priorities…" on stderr); that is expected.

Non-interactive controls (each command refuses two of these together):

- `add --top | --bottom | --prio N | --skip-priority`.
- `edit ID --prio N | --top | --bottom` re-ranks among the current siblings.
- `edit ID --parent P` **re-ranks interactively** among the new siblings by
  default; in a session without a terminal always add `--top`, `--bottom`,
  `--prio N` or `--keep-prio` (keeps the old number), or the prompt aborts.
- `reprioritize ID --top | --bottom | --above ID2 | --below ID2` (alias
  `reprio`); `--above`/`--below` place the item strictly between `ID2` and its
  neighbour, and `ID2` must be ranked in one of the item's places. Without
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

## Seeing everyone's items

`ls` and `ready` show only the current user's items by default. Pass `--who ''`
to include every assignee, or a regex to pick some. `view` works on any item,
whoever it is assigned to.

## GitHub integration

Use `import` to pull GitHub issues/PRs into the todo system and `sync` to keep
them updated. Both support `--help` for repository, type, and metadata options.
`--who` works as for `add`: omit it for the user, and pass `--who dan-claude`
when an agent can do the issue on its own.

**A GitHub-linked item writes to GitHub at once** (the `github` field in
`ls -f json`): `note` posts the text as a comment on the issue, and `done`
closes the issue, both immediately and under the user's account, not at the
next `sync`. Before a batch of notes or closes, list which items are linked,
word their notes for the issue's readers (or skip the note), and tell the user
which issues the batch will comment on or close.

**Batch adds while the user has a task active.** Auto-parenting also applies
to the user's own active stack: a batch `add` without `--parent`/`--top-level`
lands under their in-progress item and copies its labels. Always pass
`--parent` or `--top-level` (and `--no-discovered-from`) in scripts, and parse
the new id from the `Added todo #N` line, not the first `#N` in the output (a
"Discovered from: #M" line comes first).

## Quick reference

| Intent | Subcommand | Key flags to check |
|--------|------------|--------------------|
| List top-level tasks | `ls` | `--all`, `-r` for depth, `--status`, `--flat`, `--blocked`, `--who ''` for everyone, `-n 0` for everything (positional args = label filters, **not** parent IDs) |
| What can I start now? | `ready` | `-f json`, label filters, `--all` for ready parents |
| What is in progress? | `status` | no `--who` |
| Start next task | `next` | `--ready`, label filters, `--headless` |
| Start specific task | `start` | `--no-command`, `--no-shell`, `--timeout`, tmux flags |
| Track an existing tmux window | `adopt` | `--rename` |
| Pause current task | `stop` | — |
| Complete current task | `done` | — |
| View task + its sub-items | `view <id>` | `--notes` for sub-items' notes, `--all` for done ones, `-r` for depth, `-n 0` for no cap — use this instead of `ls <id>` |
| Edit task metadata | `edit` | `--who` **reassigns**, `--edit` for editor, `-c` for default command, `--description` replaces the one-line statement (details go in `note`), `--parent` with `--top`/`--bottom`/`--keep-prio`, `--add-parent`/`--remove-parent`, `--add-blocker`/`--remove-blocker`/`--blocks` |
| Add progress note | `note` | `--message`, `--edit` (replaces the whole notes on local items) |
| Create a task or subtask | `add` | `--parent` (repeatable), `--top-level`, `--top`/`--bottom`, `--note` (repeatable), `-c`, `--here`, `--worktree`, `--blocked-by`/`--blocks`, `--discovered-from` (auto-parents to active todo by default) |
| Change priority | `reprioritize` | `--top`, `--bottom`, `--above ID`, `--below ID` |
| Import from GitHub | `import` | `--number`, `--type`, `--here`, `--github-labels` |
| Sync with GitHub | `sync` | `--repo` |
| Export as ICS | `export` | `--output`, `--all` |
| Remove a task | `rm` | `--force` |
