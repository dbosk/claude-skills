---
name: stacked-prs
description: >-
  Create, update, merge and repair stacks of GitHub PRs where each PR is
  based on the previous PR's branch, as native stacks (`gh stack`) or plain
  base branches (merge_stack.sh). Use proactively when (1) opening a PR whose
  base is another feature branch (`gh pr create --base` other than the
  default), rebasing a branch onto another open PR's branch, or
  writing "Stacked on #N" or merge-order advice in a PR body, (2) the user
  asks to merge several or "all ready" PRs, or to run gh pr merge on a PR
  whose base is not main, or a merge is BLOCKED by a required review,
  (3) a PR in a chain was closed unexpectedly, is "no longer listed", shows
  base_ref_deleted, or cannot be reopened, (4) a PR was merged into a feature
  branch instead of main, (5) the user mentions stacked, chained or dependent
  PRs, gh stack, several PRs on one base branch, or retargeting a PR's base.
  Load BEFORE opening a stacked PR and before the first merge in a stack:
  GitHub's automatic retarget can close the rest of the stack.
---

# Stacked pull requests on GitHub

A stack is a chain of PRs where each PR's base is the branch of the PR
below it:

    main ← #1 feat-a ← #2 feat-b ← #3 feat-c

Each PR then shows only its own diff, which keeps reviews small. The danger
is in merging the stack.

## Choose: a native stack or a manual one

GitHub has native stacks, driven by the `gh stack` extension
(`gh extension install github/gh-stack`; docs at https://gh.io/stacks).
A native stack is a server-side object linking the PRs: when its lower PRs
merge, GitHub itself retargets and rebases the rest, so the failure in
"Why stacks break" below cannot happen. A manual stack is only PRs whose
bases happen to be each other's branches; nothing on GitHub knows they
belong together.

Use a **native stack** when all of these hold:

- stacks are enabled for the repository:
  `gh api 'repos/OWNER/REPO/stacks?pull_request=N'` answers 200 (`[]` when
  N is in no stack), and `gh stack` commands do not exit with code 9;
- the PRs form a **chain**, not a tree: no two PRs on the same base branch;
- the branches may be **rebased and force-pushed**: `gh stack sync` and
  `rebase` restack the chain that way, and `gh stack modify` refuses
  history with merge commits;
- **every PR can meet the trunk's merge requirements** as they stand:
  `gh stack merge` evaluates the bottom base's branch protection on every
  PR, and bypassing it is not supported for stacks.

Otherwise use a **manual stack**: siblings on one branch, branches that
bring lower changes up by merge commits, or a repository whose owner
merges past a required review (`reviewDecision` `REVIEW_REQUIRED` on
merged PRs in `gh pr list --state merged --json number,reviewDecision`).

Do not mix the two on one set of PRs. Once PRs are linked into a native
stack, merge them with `gh stack merge`; to handle them manually instead,
first `gh stack unstack <stack-number>` (this is a precaution: how GitHub
treats a plain `gh pr merge` inside a linked stack has not been checked).

## Native stacks with `gh stack`

`gh stack` opens editors and wizards in a terminal. From an agent's shell,
which has none, pass the non-interactive flags shown here.

- **Start**: `gh stack init feat-a feat-b` adopts existing branches (bottom
  first) or creates missing ones; `gh stack add feat-c` puts a new branch on
  top. `gh stack submit --auto --open` pushes, opens the missing PRs as
  ready for review (`--auto` alone makes drafts) with generated titles, and
  links them. Then set the titles and bodies with `gh pr edit`.
- **Existing PRs**: `gh stack link 41 42 43` (bottom first; numbers,
  branches or URLs) links them into a stack and corrects any base that does
  not match the chain. `gh stack link <stack-number> 44` grows a stack. It
  never removes PRs.
- **Updating**: `gh stack sync` fetches, rebases the chain only if the
  trunk moved, and pushes with `--force-with-lease`; `gh stack rebase`
  rebases always (`--continue`, `--abort` after a conflict). Rewriting the
  branches is the intended model here, because the whole chain is rebased
  together. Rebasing re-signs commits when `commit.gpgsign` is set, so it
  needs an unlocked gpg agent (see the worktree-subagents skill on
  signing).
- **Merging**: `gh stack merge <pr> --yes --merge` merges every PR up to
  and including `<pr>` into the trunk as one all-or-nothing operation: one
  unmergeable PR, and nothing is merged. Without `<pr>` it merges the
  current branch's whole stack. The PRs above `<pr>` stay open and GitHub
  retargets them. Merging is outward-facing, so get the user's go-ahead
  first.
- **View**: `gh stack view --json`; `gh stack unstack <n>` removes the
  stack on GitHub but leaves the PRs.
- **Exit codes**: 2 not in a stack, 3 rebase conflict, 4 GitHub API
  failure, 6 branch in several stacks, 9 stacks not enabled for the
  repository.

The rest of this skill is about manual stacks.

## Why stacks break

- **Automatic retargeting is unreliable.** When a PR's branch is deleted
  after its merge, GitHub is meant to move PRs based on that branch to the
  merged PR's base. In practice this sometimes does not happen, even with
  `delete_branch_on_merge` enabled. The timeline then shows
  `base_ref_deleted` followed by `closed`, and the next PR disappears from
  `gh pr list`. It can happen one merge after a retarget that did work.
- **A closed PR cannot be reopened while its base branch is missing.**
  `gh pr reopen` fails with `Could not open the pull request`.
- **Merging a PR whose base is not main merges it into that branch.** If #1
  was closed instead of retargeted and #2 is merged next, #2's commits land
  in `feat-a`. GitHub reports #2 as merged, but nothing reaches main. When
  `feat-b` is then deleted, #3 is closed as well.

## Opening a stack

- Set each PR's base to the previous branch:
  `gh pr create --base feat-a --head feat-b`.
- Start the body with `Stacked on #1 (← …). Merge those first.`
- Never write that GitHub will retarget the PR when its base merges: it may
  close it instead (see below). Say instead that it must be retargeted to
  main before #1 is merged.
- A branch rebased onto another open PR's branch (for example to resolve a
  conflict between two PRs ahead of time) makes a stack too, even when the
  two PRs are otherwise independent: the child's PR must use that branch as
  its base, or its diff shows the other PR's commits.
- **Siblings.** Several PRs may share one base branch
  (`main ← #1 feat-a`, with both `#2` and `#3` based on `feat-a`). That is
  a tree, not a chain: when `feat-a` is deleted, every PR on it is at risk,
  not just "the next" one. Note the sibling in each body.
- To bring a lower branch's changes up the stack, merge the base into the
  child (`git merge feat-a` on `feat-b`) and push. Do not rebase and
  force-push: that rewrites commits the PRs further up are built on.
- List the whole stack with
  `gh pr list --json number,baseRefName,headRefName,mergeStateStatus`.

## Merging a stack: retarget first, then merge

Never rely on automatic retargeting. For each PR, from the bottom up:

1. Check that the PR's base is `main`
   (`gh pr view N --json baseRefName`). Never merge a stacked PR into its
   feature-branch base unless that is explicitly the goal.
2. Retarget **every** open PR based on this PR's branch to main before
   merging this one, siblings included:
   `gh pr list --base <this-head-branch> --json number --jq '.[].number'`,
   then `gh pr edit <each> --base main`. For a moment, their diffs also show
   this PR's commits.
3. Merge: `gh pr merge N --merge --delete-branch`, or with the repo's usual
   merge method. Deleting the branch is now safe, because no open PR uses it
   as a base.
4. Wait until the next PR in the list reports `MERGEABLE CLEAN`. Right after a retarget
   or merge, the status is `UNKNOWN` for a few seconds, so poll. Stop if it
   reports `DIRTY`, `CONFLICTING` or `BLOCKED`.

`scripts/merge_stack.sh` does exactly this, given the PR numbers from the
bottom up. Before each merge it retargets every open PR based on the branch
being deleted, so siblings that are not in the list survive too (they are
retargeted, not merged). It is not on the PATH; give its full path:

    ~/.claude/skills/stacked-prs/scripts/merge_stack.sh 532 534 535 536

Run it from inside the repository's checkout. `-m squash` or `-m rebase`
picks another merge method.

**Required reviews.** When the trunk's protection requires an approving
review, every PR reports `MERGEABLE BLOCKED` once it is based on the
trunk; PRs further up show `CLEAN` only because their bases are still
unprotected feature branches. The script then stops at the first PR. If
the repository's owner merges past that requirement as an admin (as their
earlier merges show), `-a` passes `--admin` to `gh pr merge` and accepts
`BLOCKED`, but only once the PR's checks have finished and none failed;
a conflict still stops the run:

    ~/.claude/skills/stacked-prs/scripts/merge_stack.sh -a 531 537 548

The bypass is the owner's decision: use `-a` only when the user asked for
it or ran it themselves, never to get past a block on your own.

Merging is outward-facing, so get the user's go-ahead for the list first.
Afterwards, confirm that every head is in main:
`git fetch && git merge-base --is-ancestor <head-sha> origin/main`.

## Repairing a broken stack

First find out what happened, using each PR's timeline:

    gh api repos/OWNER/REPO/issues/N/timeline \
      --jq '.[] | select(.event!=null) | "\(.created_at) \(.event) \(.base_ref // "")"'

- **A PR was closed because its base branch was deleted.** Push the base
  branch back at its old commit, reopen the PR, retarget it, then delete
  the restored branch:

      git push origin <old-sha>:refs/heads/<base-branch>
      gh pr reopen N && gh pr edit N --base <new-base>
      git push origin --delete <base-branch>

  The old commit is the `headRefOid` of the PR that owned that branch
  (`gh pr view M --json headRefOid`). If the base was the merged bottom PR,
  any commit already in main will do. The new base is `main` for the new
  bottom PR, otherwise the branch of the PR below it.
- **A PR was merged into a feature branch instead of main.** Its commits
  now live in that branch, so the PR owning that branch carries them.
  Reopen or retarget that PR, and note in its body that it also contains
  #M. Then base the next PR on that branch.
- Check every revived PR with `gh pr view N --json mergeStateStatus`. A
  `DIRTY` status against a branch that has since been replaced often
  disappears after retargeting. To check without touching the worktree,
  run `git merge-tree --write-tree origin/<child> origin/<base>`: exit code
  0 means a clean merge.
- Update the `Stacked on` line in each revived PR's body.
