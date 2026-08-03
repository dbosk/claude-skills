---
name: worktree-subagents
description: Orchestrate parallel fix/implementation subagents in isolated git
  worktrees without them testing the wrong code or colliding. Use proactively
  when (1) spawning Agent tasks with worktree isolation, (2) running a batch
  bug-fix or migration campaign where several agents edit the same repo in
  parallel, (3) a worktree agent reports import/venv/submodule build failures,
  (4) resuming subagents after a session limit or crash, or (5) writing
  prompts for agents that must build a generated-artifact project (e.g.
  noweb/literate programs) before testing. Documents obstacles observed in a
  real 47-branch campaign and the prompt preamble that avoids them.
---

# Running parallel subagents in git worktrees

Lessons from a real campaign: 7 review agents + dozens of fix agents, each in
its own worktree of a literate-programming (noweb) repo, one branch and PR per
fix. Every item below cost an agent real time at least once.

## The four worktree traps (put these in every agent prompt)

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

## Prompt-engineering the fix agents

- Include a SETUP preamble with the three traps above. Agents without it each
  lose ~15 minutes rediscovering the venv trap; agents with it don't.
- When several agents edit the same file on different branches, assign each an
  explicit region ("keep your diff to function X; branches A/B own areas Y/Z")
  and say which other branches exist. Conflicts still possible — note expected
  ones in the orchestrator's plan for integration time.
- Slow doc-weaving/`all` targets exceed the 120 s Bash timeout; tell agents to
  build narrow targets (`make module.py`) when iterating.
- Shared scratchpad directories collide between parallel agents — require
  uniquely named scratch files, kept out of the repo and cleaned up.
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
- A session limit kills all background agents mid-task. After reset, resume
  each by name with SendMessage — they continue from their transcript;
  committed work and worktrees survive. Resume is near-free; relaunching
  re-does everything.
- Branches created in worktrees are visible in the main repo — review diffs,
  push, and open PRs from the main repo; never merge or push from inside an
  agent worktree.
- Review every agent branch yourself before pushing: `git diff master..branch`
  plus the agent's test evidence. Treat security-classifier warnings on a
  subagent as "read the whole diff line by line", not as a verdict.
- Persist orchestration state (plan file with per-branch status, follow-up
  issue list) outside the conversation after every batch — sessions die.

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
- **Route review fixes through the original agent when the change is a
  redesign** (it has the file context; resume it with the maintainer's
  comment verbatim). Apply small mechanical review fixes (naming,
  formatting, labels) yourself directly — a resume costs more than the
  edit.
- Search the tracker before filing follow-ups: parallel reviewers
  rediscover known issues, and a planned fix may already have an issue
  to reference instead of a duplicate.
