# Brief skeleton for a fix or implementation agent

One file per agent, on disk. Copy this, fill every `{{placeholder}}`, and put
nothing in the launch message except the target, the branch, the base SHA, the
scratch directory and this file's path. Distilled from the briefs of a
47-branch campaign; §0 is the part that must not be edited away, because every
step in it cost an agent real time at least once.

---

# Brief: {{one-line task}} for {{unit}}

You are {{doing what}} in the repository `{{owner/repo}}`. Your launch message
names the unit `{{unit}}`, its directories, the branch `{{branch}}`, the base
commit `{{base-sha}}` and your scratch directory `/tmp/claude-1000/{{branch}}/`.
Read this file completely before touching anything.

## 0. Setup in your worktree (do these first, in this order)

0a. `pwd`; `git rev-parse --show-toplevel`; `git remote get-url origin` must
    name `{{owner/repo}}`. If not, STOP and report; do not improvise.
0b. `git log --oneline -1`. The worktree is often created at an OLD
    default-branch commit whose working tree already matches the base, so a
    plain `git checkout -B` may abort. Base your branch regardless:
    `git -c submodule.recurse=false checkout -f -B {{branch}} {{base-sha}}`
    (the worktree is fresh, so `-f` discards nothing of value). Verify with
    `git log --oneline -1` that HEAD is {{base-sha}} before anything else.
0c. `git submodule update --init --checkout {{submodule}}`. `--checkout` is
    required: with `submodule.{{submodule}}.update=none` in the repo config the
    plain form prints nothing and checks out nothing. If it fails because the
    submodule is half-initialised (a gitfile pointing at a
    `.git/worktrees/…/modules/{{submodule}}` holding only `config`), never
    touch `.git/` — clone instead:
    `git clone {{submodule-url}} /tmp/claude-1000/{{branch}}/{{submodule}}`,
    check out the pinned commit {{submodule-sha}} there, and pass
    `{{VAR}}=/tmp/claude-1000/{{branch}}/{{submodule}}` on every build command
    line. Never "fix" a submodule by deleting `.git` files or copying
    directories from another worktree.
0d. Never `git stash` — the stash stack is shared across all worktrees and
    parallel agents pop each other's entries — and never `git reset --hard`,
    which corrupts a worktree that has submodules. Revert a file with
    `git checkout <sha> -- <path>`.
0e. Generated artifacts are gitignored ({{list}}): build them, never commit
    them, and never hand-edit a generated file — edit its source.
0f. Scratch, logs, clones and renders only under `/tmp/claude-1000/{{branch}}/`
    (create it). Nothing in a shared scratch directory: parallel agents
    overwrite each other's `probe.py` and `build.log`. Nothing in the
    repository outside {{your area}}.
0g. Credentials: `set -a; source ~/.credentials; set +a` in every shell that
    needs them. Never print a key or the file's contents anywhere — not in a
    report, a log, a commit message or a generated file.
0h. Do not push, do not merge, do not open PRs, do not upload or publish
    anything, do not run `git pull`. Other agents' branches and worktrees are
    frozen: never check them out, merge them or edit them. Touch only
    {{your area}}.
0i. Disk is tight ({{free}} free). If a command reports "No space left on
    device", STOP and report; do not delete anything to make room.

## 1. Read before editing

Load the skills {{skills}} and follow them; where they conflict with this
brief, this brief wins. Read {{project standard file}} completely, and
{{the model or worked example}} as a second example. Read every file you will
change, in full, before changing anything.

## 2. Task and decisions

{{The task, item by item, each with the source it comes from.}}

Decisions already taken — do not re-litigate and do not guess:

- {{ambiguous item}} → {{the decision}}.
- {{item a rule seems to demand but which must not change}} → leave it, and
  say so in the report.

Out of scope: {{…}}. Report bugs you notice outside your area; do not fix them.

## 3. Build and check

    {{build command — one job or target at a time}}

Run every check and report each result verbatim, as numbers, never as "clean":
{{check list — 0 errors in the log, 0 unresolved references, formatter
`--check`, every generated program runs, renders read}}. A check that reports
zero from a pattern you have not seen match is unproven: prove it against a
known-positive first.

## 4. Commit and report

Commit on `{{branch}}` ({{which files}}; one commit per {{unit}} is fine), the
message naming what changed and why, with the trailers:

    Co-Authored-By: {{model}} <noreply@anthropic.com>
    Claude-Session: {{session url}}

Final report — raw data for the orchestrator, not prose:

- branch, commit SHAs, `git log --oneline {{base-sha}}..HEAD`
- per {{unit}}: a table of every change (which item, `file:line` before, what
  it became), and which items changed nothing
- the check results verbatim; paths of the built artifacts
- anything an item seemed to demand but you left undone, with the reason
- deviations from this brief; open questions for the orchestrator
- bugs or problems you noticed and did NOT fix

Keep the worktree: a round-2 message may follow.
