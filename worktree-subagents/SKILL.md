---
name: worktree-subagents
description: Orchestrate parallel fix/implementation subagents in isolated git
  worktrees without them testing the wrong code or colliding. Use proactively
  when (1) spawning Agent tasks with worktree isolation, (2) running a batch
  bug-fix or migration campaign where several agents edit the same repo in
  parallel, (3) a worktree agent reports import/venv/submodule build failures,
  (4) resuming subagents after a session limit or crash (HTTP 429 vs 529,
  agents unreachable after a restart), (5) writing prompts or a brief for
  agents that must build a generated-artifact project (e.g. noweb/literate
  programs) before testing, or (6) running reader agents over the finished
  artifacts or scripting long orchestrated builds. Documents obstacles
  observed in a real 47-branch campaign and the prompt preamble that avoids
  them.
---

# Running parallel subagents in git worktrees

Lessons from a real campaign: 7 review agents + dozens of fix agents, each in
its own worktree of a literate-programming (noweb) repo, one branch and PR per
fix. Every item below cost an agent real time at least once.

## The ten worktree traps (put these in every agent prompt)

0. **The auto-created worktree may be based on the DEFAULT branch, not the
   branch you are on.** Agent-tool worktree isolation has been observed to
   check out the repo's main/default branch even when the orchestrator's
   session is on a feature branch — and agents then implement fixes against
   the wrong code state while *reporting* the base they were told to expect
   (in one campaign, three of four agents were mis-based and only one
   noticed; another agent asserted "branched from <feature-tip>" in its
   report while its merge-base said otherwise). Prompt every agent to run
   `git log --oneline -1` FIRST, compare against the intended base SHA
   (name the SHA explicitly in the prompt), and `git reset --hard <sha>` /
   fast-forward before doing anything. As orchestrator, verify each
   returned branch with `git merge-base <intended-base> <branch>` before
   evaluating the diff — a diff against the wrong base shows phantom
   changes (reverts of the feature branch's own commits) and hides real
   conflicts until merge time.

1. **Submodules are not initialized in a fresh worktree.** Any `make` that
   needs them fails cryptically. Prompt the agent to run
   `git submodule update --init <name>` first. Do not let agents "fix" this by
   deleting `.git` gitlinks or copying directories from the main checkout.

2. **Generated artifacts do not exist in a fresh worktree.** If build products
   (tangled `.py`, compiled assets) are gitignored, the worktree contains only
   sources — the agent must build *everything* the tests import, not just the
   file it edited.

3. **The package import may silently resolve to the MAIN repo.** A Poetry/pip
   editable install points a `.pth` at the main checkout; `poetry run` inside
   the worktree instead mints a fresh *empty* venv. Either way the agent tests
   the wrong code. Required recipe:
   - use the MAIN repo's venv interpreter directly (find via `poetry env info -p`
     in the main repo),
   - prepend `PYTHONPATH="$PWD/src"` (PYTHONPATH precedes site-packages),
   - build the whole source tree first — Python does NOT merge package
     directories across sys.path entries; a partially built worktree falls
     back to main-repo modules per-package, silently,
   - **verify**: `python -c "import pkg.mod; print(pkg.mod.__file__)"` must
     print a worktree path. Make agents report this check.

4. **The stash stack is SHARED across all worktrees.** `git stash` writes to
   the repo-level `refs/stash`, so concurrent agents pop *each other's*
   stashes — in the campaign one agent's `stash pop` applied another agent's
   changes into its worktree and dropped that agent's stash entry (recovered
   from the dangling stash commit, but only barely). Forbid `git stash` in
   agent prompts; for temporarily reverting a fix (e.g. to prove a test is
   load-bearing) use `git checkout <commit> -- <file>`, edit the generated
   artifact directly, or keep a scratch copy in /tmp.

5. **`git reset --hard` breaks worktrees that have submodules.** Observed:
   it half-initializes a not-yet-inited submodule — creating
   `<submodule>/.git` plus an empty
   `.git/worktrees/<wt>/modules/<submodule>/` holding only `config` — after
   which *every* `git status` fails with `fatal: not a git repository:
   <submodule>/../../../.git/worktrees/.../modules/<submodule>` (HEAD does
   not move). Recovery, verified:
   `rm -f <submodule>/.git && rm -rf .git/worktrees/<wt>/modules/<submodule-parent-dir>`.
   Tell agents to avoid `git reset --hard` in worktrees; to revert files use
   `git checkout <sha> -- <path>`.

6. **Partial builds of a namespace-package tree test the WRONG repo.** The
   specific Python variant of trap 3 that cost four agents in one campaign:
   building only a subpackage (`make -C src/pkg/sub all`) leaves the
   worktree's top-level `src/pkg/` without `__init__.py`, making it a
   PEP 420 namespace-package *portion* — which loses to the main repo's
   regular package on `sys.path`, so `PYTHONPATH=$PWD/src` + pytest silently
   runs the MAIN repo's code with green results. Build the package ROOT and
   every subpackage before testing, and require the `__file__`/`__path__`
   verification of trap 3 (it is the only thing that catches this).

7. **Worktree creation follows the ORCHESTRATOR's cwd repo — a shell parked
   inside a submodule spawns submodule worktrees.** Observed: the
   orchestrator ran a check with `cd <repo>/makefiles && ...`, the cwd
   persisted, and all three agents launched in the next tool call received
   worktrees of the *submodule* repo (no project sources, wrong history,
   base SHA unresolvable). The agents' isolation guard then blocks them
   from reaching the real repo, so they cannot self-repair — only a
   relaunch helps (agents whose task IS the submodule can be told to
   continue with adjusted gates). Prevention: immediately before any
   worktree-isolated Agent call, verify `pwd` and
   `git rev-parse --show-toplevel` name the intended repo root; and give
   every agent a step-0a check that `git rev-parse --show-toplevel` /
   `git remote get-url origin` name the expected repo, with orders to STOP
   and report rather than improvise if not.

8. **The auto-created worktree may sit at a STALE default-branch commit
   whose working tree already equals your base — so `git checkout -B` aborts
   or refuses.** Observed (nine agents, one campaign): worktrees were
   created at an old `master` commit while the files matched the feature
   tip, and with a submodule in the tree the plain checkout also tried to
   recurse into it. The command that works in every case:
   `git -c submodule.recurse=false checkout -f -B <branch> <base-sha>`
   (the worktree is fresh, so `-f` discards nothing of value). As
   orchestrator, run `git worktree list` right after launching: a new
   worktree still showing the stale commit a minute later means the agent
   skipped the step.

9. **`git submodule update --init <name>` can be a silent no-op.** If the
   repo config carries `submodule.<name>.update=none` (set by someone who
   never wanted that submodule checked out), the plain form prints nothing
   and checks out nothing; pass `--checkout` explicitly:
   `git submodule update --init --checkout <name>`. When the submodule is
   half-initialised (a gitfile `<name>/.git` pointing at a
   `.git/worktrees/<wt>/modules/<name>` that holds only `config`) and the
   agent must not touch `.git/`, give it a fallback that needs no repair:
   clone the submodule's repository into the agent's own scratch directory
   at the pinned commit and pass its path on the make command line
   (`make … INCLUDE_MAKEFILES=<clone>`), so the repository is never
   modified and merge time sees nothing unusual.

## Prompt-engineering the fix agents

- Include a SETUP preamble with the ten traps above. Agents without it each
  lose ~15 minutes rediscovering the venv trap; agents with it don't.
- When several agents edit the same file on different branches, assign each an
  explicit region ("keep your diff to function X; branches A/B own areas Y/Z")
  and say which other branches exist. Conflicts still possible — note expected
  ones in the orchestrator's plan for integration time.
- Slow doc-weaving/`all` targets exceed the 120 s Bash timeout; tell agents to
  build narrow targets (`make module.py`) when iterating.
- Shared scratchpad directories collide between parallel agents — require
  scratch and log filenames prefixed with the agent's branch name, kept out
  of the repo and cleaned up. Observed twice in one campaign: `/tmp/b1.log`
  and `scratchpad/probe.py` overwritten by siblings mid-task, making one
  agent's build look further along than it was.
- Include the ten traps' SETUP preamble verbatim; in one round the
  preamble said "build the dirs you touch" instead of "build ALL" and four
  agents independently lost ~20 minutes to trap 6 before their import-path
  check caught it.
- Demand a structured final report: branch, commit, files, chunks/areas
  touched, what/why, full-suite result, deviations. The report is raw data for
  the orchestrator, not prose.
- Add "report bugs you notice but do NOT fix them" — in the campaign this
  surfaced ~15 pre-existing bugs as follow-up issues instead of scope creep.
- Require the agent to prove any new regression test is load-bearing:
  temporarily revert the *generated/tangled* file (never the source), rerun
  the test, watch it fail, restore. Cheap and catches vacuous tests.

## Orchestration mechanics

- Agents sometimes go idle without delivering their final report. Poke them
  with SendMessage ("send me your findings/report now"); a queued message
  ("delivered at next tool round") means the agent is still running — wait.
- A session limit kills all background agents mid-task. Within the same
  session they resume from their transcript with SendMessage — committed work
  and worktrees survive, and resume is near-free while relaunching re-does
  everything. Which agents are still reachable, and whether by name or by id,
  depends on what killed them: see "Session limits, resume and unreachable
  agents" below.
- Branches created in worktrees are visible in the main repo — review diffs,
  push, and open PRs from the main repo; never merge or push from inside an
  agent worktree.
- Review every agent branch yourself before pushing: `git diff master..branch`
  plus the agent's test evidence. Treat security-classifier warnings on a
  subagent as "read the whole diff line by line", not as a verdict.
- Persist orchestration state (plan file with per-branch status, follow-up
  issue list) outside the conversation after every batch — sessions die.

## Session limits, resume and unreachable agents

- **Read the HTTP code before retrying — 529 and 429 need opposite
  responses.** `529 Overloaded` is API-wide: the launch never produced a
  working agent, its unchanged worktree is auto-removed, so resuming it is
  useless and changing model does not help (observed on `claude-opus-5` and on
  the session model within one half hour). Relaunch after a pause of ~15
  minutes; do not hammer. `429` "session limit · resets <time>" is the
  account's usage limit: running agents die mid-task but a worktree with
  changes survives, so they are resumable and relaunching throws work away.
- **Resume by agent id when the name has been reused.** SendMessage to
  `deck-packages` reaches the *latest* launch under that name, not the crashed
  one you mean. Record each spawn's agent id in the plan file at launch, and
  resume by id — three agents came back that way hours later, worktrees intact.
- **After a session restart or compaction every in-process subagent of the
  earlier session is unreachable** ("No agent named … is reachable"), while
  their worktrees remain — locked — and their branch names stay taken. A
  follow-up round then needs a *fresh* agent on a *new* branch (`fix-<x>-rN`)
  from the current tip with the brief re-pointed; that costs one brief plus one
  read of the target, but only because the brief is a file on disk.
- **Data shared across branches gets a `% TODO(orchestrator)` placeholder, not
  an invention per agent.** When several agents need the same bibliography
  entry or shared config line, which so far exists only on a sibling branch,
  have each write a placeholder key carrying the marker; resolve them once at
  merge time, and grep for the marker before every merge.
- **Check disk before a batch, and tell the user instead of freeing space
  yourself.** A worktree costs ~45–50 MB plus build output; 28 of them reached
  1.5 GB on a disk with 500 MB free. Report what is large (`/usr/bin/du -sh`),
  delete nothing, and give every agent "No space left on device → STOP and
  report".
- **Clean up at the end of a round.** Merged worktrees are not free and the
  auto-created branches accumulate silently. Confirm first that
  `git branch --no-merged <base>` lists none of the agent branches. Then
  `git worktree unlock <path>` the locked ones, `git worktree remove --force
  <path>` each, `git branch -d` both the agent branches *and* the auto-created
  `worktree-agent-*` branches, and `git worktree prune`. Verify with
  `git worktree list` and `/usr/bin/du -sh <worktree dir>` — 1.5 GB became
  95 MB in the campaign.

## Reader and fix agents from a brief on disk

- **One brief file per agent, on disk — never a task typed into the launch
  message.** The launch names only the target, the branch, the base SHA, the
  scratch directory and the brief's path; everything else lives in the file:
  §0 setup preamble (the traps above as numbered steps), §1 what to read before
  editing, §2 the task with an explicit decision on every ambiguous item,
  §3 build and checks, §4 commit trailers and the report format. Skeleton to
  copy: `references/brief-skeleton.md`. The file makes a relaunch cheap when an
  agent becomes unreachable, and keeps ten agents' instructions identical.
- **Decide the ambiguous items in the brief, not in the agent.** Anything the
  source material leaves open — which of two readings of a review comment, what
  wins when a rule and a local convention collide — is answered in §2 by name;
  agents that must guess guess differently.
- **Run an independent reader agent per 2–3 finished artifacts.** It never saw
  the diff; it reads the *product*: text extraction per page, 45-dpi contact
  sheets (`pdftoppm -r 40` + `montage`), 110-dpi close reads of the pages that
  look wrong, and a re-run of every generated program against the output
  embedded in the document. It reports by severity — blockers, should-fix,
  nits — each with `file:line`. Template: `references/reader-agent-brief.md`.
- **The reader exists because a fix agent's report inherits its own
  assumptions.** Readers caught a 19.5 pt overrun the build log never warned
  about, a caption contradicting the transcript beside it, and a count in the
  prose disagreeing with its table — none visible in a diff.
- **The orchestrator reads the diff itself**, spot-checks renders, applies
  small merge-time fixes directly (a flag in a Makefile, a name, a caption) and
  routes redesigns back to the agent by name with the reader's list; the agent
  keeps its worktree for round 2.
- **A round is: brief → fix agent → reader → fix list → merge → the
  orchestrator's own build → deliver → generalise.** The last step pays: every
  defect the round found becomes a rule in the project's standard file and in
  the brief, so the next unit cannot reproduce it.

## Shell traps when orchestrating builds

- **`pkill -f <pattern>` kills the tool's own shell** when the pattern also
  occurs in the command line running it (twice, exit 144, mid-round). Use the
  bracket trick in a command with no other literal copy: `pkill -f '[p]dflatex'`.
- **A backslash pattern in `grep` can silently match nothing.**
  `grep -c "Overfull \vbox"` reports 0 against a log full of them — and single
  quotes fail identically: the shell passes `\v` through and the regex engine
  leaves it undefined. Write `grep -c 'Overfull .vbox'`; a zero count from a
  pattern with a backslash is unproven until it matches a line you know exists.
- **A trailing `&` backgrounds the WHOLE `&&` chain, not the last command.**
  `git merge … && git push && nohup build.sh &` backgrounds the merge and the
  push too, and you then review a merge that has not happened. Wrap only the
  detached part: `git merge … && git push && ( nohup build.sh > log 2>&1 & )`.
- **The Bash tool caps a command at ten minutes**, so longer work runs detached
  (`nohup script.sh > log 2>&1 &`), printing one summary line per unit and a
  final `ALL DONE` marker; watch it with the Monitor tool polling that log.
- **Never build two jobs of one document concurrently**: they share the build
  directory and its caches, so one job reads the other's intermediates.
- **`du` may be an alias in the user's shell** — call `/usr/bin/du` wherever a
  script or a measurement must not depend on it.

## After the PRs: review rounds and live verification

- **Unit tests inherit the author's assumptions.** An agent (and the
  orchestrator's diff review) approved a branch whose regression test
  asserted the *absence* of an API field — because the agent believed
  omission selected a sensible default. The live API rejected the call.
  A test asserting the implementation's own assumption is no protection
  when the assumption is wrong; for code that talks to an external
  system, smoke-test each fixed path against the real system (a sandbox)
  before declaring the fix verified.
- **Verify writes past the tool's own cache.** If the tool updates a
  local cache on write, a read-back can show the cache, not the server —
  a server-side no-op looks fixed. Use the tool's cache-bypass flag
  (`--no-cache` or equivalent) for the verification read.
- **Never live-test broadcast/fan-out paths.** A "create in all
  contexts" branch verified live would spam every real context; pin it
  with a unit test and say so explicitly in the PR.
- **`gh` posts as the maintainer's account**, so "latest comment by
  <maintainer>" may be your own relay. When checking for new review
  feedback, read PR reviews, issue comments, and inline comments
  separately, in timestamp order.
- **A PR's feedback lives under THREE different API endpoints — sweep
  all of them, by endpoint, not via `gh pr view`:**
  `repos/O/R/issues/N/comments` (ordinary discussion comments — the kind
  a maintainer leaves outside any review; missing this one cost a full
  review round in the campaign), `repos/O/R/pulls/N/comments` (inline
  code comments), and `repos/O/R/pulls/N/reviews` (review verdicts and
  bodies). A review in state PENDING hides its inline comments from the
  normal listing until submitted — but since `gh` authenticates as the
  author, `pulls/N/reviews/<id>/comments` reads the drafts.
- **Route review fixes through the original agent when the change is a
  redesign** (it has the file context; resume it with the maintainer's
  comment verbatim). Apply small mechanical review fixes (naming,
  formatting, labels) yourself directly — a resume costs more than the
  edit.
- Search the tracker before filing follow-ups: parallel reviewers
  rediscover known issues, and a planned fix may already have an issue
  to reference instead of a duplicate.
- **Close the loop with `Fixes #N`.** When a fix branch addresses a filed
  issue, the PR body must carry the closing keyword so the merge closes
  the issue. Campaign PRs fixing *internal* findings need none — but the
  check runs both ways: before opening each PR, search the tracker for an
  issue it resolves, and watch for the stale case where an already-merged
  PR implemented an open issue without referencing it (close manually,
  naming the PR).
