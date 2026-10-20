#!/bin/bash
# Merge a stack of GitHub PRs bottom-up without relying on GitHub's
# automatic retargeting: each next PR is retargeted to the bottom PR's base
# BEFORE the PR below it is merged and its branch deleted.
#
# Usage: merge_stack.sh [-m merge|squash|rebase] PR1 PR2 ... (bottom first)
# Run from inside the repository's checkout (gh picks the repo from it).
set -u

method=merge
if [ "${1:-}" = "-m" ]; then method=$2; shift 2; fi
if [ $# -eq 0 ]; then
  echo "usage: $0 [-m merge|squash|rebase] PR... (bottom of stack first)" >&2
  exit 2
fi

for n in "$@"; do
  state=$(gh pr view "$n" --json state --jq .state) || exit 1
  if [ "$state" != "OPEN" ]; then
    echo "#$n is $state, not OPEN; drop it from the list" \
         "(see Repairing a broken stack if it was closed)." >&2
    exit 1
  fi
done

target=$(gh pr view "$1" --json baseRefName --jq .baseRefName) || exit 1
default=$(gh repo view --json defaultBranchRef --jq .defaultBranchRef.name)
if [ "$target" != "$default" ]; then
  echo "#$1 is based on '$target', not '$default'." \
       "Retarget it first, or pass the real bottom of the stack." >&2
  exit 1
fi

wait_clean() {
  local st
  for _ in $(seq 1 30); do
    st=$(gh pr view "$1" --json mergeable,mergeStateStatus \
           --jq '"\(.mergeable) \(.mergeStateStatus)"')
    case "$st" in
      "MERGEABLE CLEAN") echo "#$1: $st"; return 0 ;;
      *CONFLICTING*|*DIRTY*|*BLOCKED*|*BEHIND*)
        echo "#$1: $st, stopping" >&2; return 1 ;;
    esac
    sleep 5
  done
  echo "#$1: still '$st' after 150 s, stopping" >&2
  return 1
}

prs=("$@")
for i in "${!prs[@]}"; do
  n=${prs[$i]}
  next=${prs[$((i + 1))]:-}
  wait_clean "$n" || exit 1
  # Retarget every open PR based on the branch that is about to be deleted,
  # not just the next one in the list: sibling PRs on the same branch would
  # otherwise be closed when it disappears.
  head=$(gh pr view "$n" --json headRefName --jq .headRefName) || exit 1
  children=$(gh pr list --state open --base "$head" \
               --json number --jq '.[].number') || exit 1
  for child in $children; do
    gh pr edit "$child" --base "$target" >/dev/null || exit 1
    echo "retargeted #$child to $target"
  done
  if [ -n "$next" ]; then
    next_base=$(gh pr view "$next" --json baseRefName --jq .baseRefName) \
      || exit 1
    if [ "$next_base" != "$target" ]; then
      echo "#$next is based on '$next_base', not on #$n's branch or" \
           "'$target'; check the order of the list" >&2
      exit 1
    fi
  fi
  gh pr merge "$n" "--$method" --delete-branch || exit 1
  echo "merged #$n"
done
