#!/bin/bash
# build_decks_detached.sh --- build several decks in sequence, one log per
# deck, for `nohup ... &` plus the Monitor tool.
#
# A full deck build outruns a foreground tool call, so run this detached
# and watch the logs instead of blocking:
#
#   nohup build_decks_detached.sh --logdir /tmp/build \
#         modules/exceptions/slides modules/iterations/slides \
#         > /tmp/build/driver.log 2>&1 &
#
# Then watch /tmp/build/driver.log for the final marker line
# "##### all done".  A trailing & backgrounds the whole && chain, so never
# join this with && to anything.
#
# Usage:
#   build_decks_detached.sh [--makefiles DIR] [--logdir DIR]
#                           [--jobs LIST] DECK [DECK ...]
#
#   --makefiles DIR   passed on to build_deck.sh
#   --logdir DIR      where the per-deck logs go (default: /tmp/deck-builds)
#   --jobs LIST       passed on to build_deck.sh (default: notes,slides)
#   --exempt GLOB     passed on to build_deck.sh (repeatable)
set -uo pipefail

# The block of comments at the top of this file is the help text.
usage() {
  awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "$0"
}

HERE=$(cd "$(dirname "$0")" && pwd)
BUILD=$HERE/build_deck.sh
MAKEFILES=""; LOGDIR=/tmp/deck-builds; JOBS="notes,slides"; EXEMPT=()

while [ $# -gt 0 ]; do
  case "$1" in
    --makefiles) MAKEFILES="${2:-}"; shift 2 ;;
    --logdir)    LOGDIR="${2:-}"; shift 2 ;;
    --jobs)      JOBS="${2:-}"; shift 2 ;;
    --exempt)    EXEMPT+=(--exempt "${2:-}"); shift 2 ;;
    -h|--help)   usage; exit 0 ;;
    --)          shift; break ;;
    -*)          echo "unknown option: $1" >&2; exit 2 ;;
    *)           break ;;
  esac
done

[ $# -gt 0 ] || { echo "no decks given (try --help)" >&2; exit 2; }
[ -x "$BUILD" ] || { echo "not executable: $BUILD" >&2; exit 2; }
mkdir -p "$LOGDIR"

RC=0
for d in "$@"; do
  echo "##### $d $(date +%H:%M)"
  if [ ! -d "$d" ]; then
    echo "$d: no such directory"; RC=1; continue
  fi
  # One log per deck, named after the deck's path.
  slug=$(echo "${d#./}" | tr '/' '-')
  log=$LOGDIR/$slug.log

  # The title is the running head the blank-slide check strips.
  title=""
  if [ -f "$d/notes.tex" ]; then
    title=$(grep -o '\\title{[^}]*' "$d/notes.tex" | head -1 \
            | sed 's/\\title{//;s/%//' | tr -d '\n' | sed 's/^ *//;s/ *$//')
  fi

  args=(--deck "$d" --log "$log" --jobs "$JOBS")
  [ -n "$MAKEFILES" ] && args+=(--makefiles "$MAKEFILES")
  [ -n "$title" ] && args+=(--title "$title")
  [ ${#EXEMPT[@]} -gt 0 ] && args+=("${EXEMPT[@]}")

  "$BUILD" "${args[@]}" 2>&1
  rc=$?
  [ "$rc" -eq 0 ] || RC=1
  echo "##### $d exit $rc, build log $log"
done
echo "##### all done $(date +%H:%M), exit $RC"
exit "$RC"
