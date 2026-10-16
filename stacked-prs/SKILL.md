---
name: stacked-prs
description: Create, update, merge and repair stacks of GitHub pull requests
  where each PR is based on the previous PR's branch instead of main. Use
  proactively when (1) opening a PR whose base is another feature branch, or
  writing "Stacked on #N" in a PR body, (2) the user asks to merge several or
  "all ready" PRs, or to run gh pr merge on a PR whose base is not main,
  (3) a PR in a chain was closed unexpectedly, is "no longer listed", shows
  base_ref_deleted, or cannot be reopened, (4) a PR was merged into a feature
  branch instead of main, (5) the user mentions stacked, chained or dependent
  PRs, or retargeting a PR's base. Load BEFORE the first merge in a stack:
  merging bottom-up and relying on GitHub's automatic retarget can close the
  rest of the stack.
---

# Stacked pull requests on GitHub

A stack is a chain of PRs where each PR's base is the branch of the PR
below it:

    main ← #1 feat-a ← #2 feat-b ← #3 feat-c

Each PR then shows only its own diff, which keeps reviews small. The danger
is in merging the stack.

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
2. Retarget the next PR to main **before** merging this one:
   `gh pr edit <next> --base main`. For a moment, the next PR's diff also
   shows this PR's commits.
3. Merge: `gh pr merge N --merge --delete-branch`, or with the repo's usual
   merge method. Deleting the branch is now safe, because no open PR uses it
   as a base.
4. Wait until the next PR reports `MERGEABLE CLEAN`. Right after a retarget
   or merge, the status is `UNKNOWN` for a few seconds, so poll. Stop if it
   reports `DIRTY`, `CONFLICTING` or `BLOCKED`.

`scripts/merge_stack.sh` does exactly this, given the PR numbers from the
bottom up:

    ~/.claude/skills/stacked-prs/scripts/merge_stack.sh 532 534 535 536

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
