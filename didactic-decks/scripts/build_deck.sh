#!/bin/bash
# build_deck.sh --- build a didactic deck (notes.pdf, slides.pdf) and run
# the pre-review checks.
#
# One job at a time (both jobs share ltxobj), converge the cross
# references by hand where latexmk stops short, then report every check
# with its number.  Exits non-zero when a hard check fails.
#
# Usage:
#   build_deck.sh --deck DIR [options]
#
#   --deck DIR        deck directory (required)
#   --makefiles DIR   passed as INCLUDE_MAKEFILES (default: the Makefile's)
#   --log FILE        build log (default: DIR/ltxobj/build_deck.log)
#   --title STR       running-head title, stripped before the blank-slide
#                     check (default: read from notes.tex)
#   --jobs LIST       comma-separated: notes,slides (default: notes,slides)
#   --check-only      skip the build, run the checks on existing PDFs
#   --exempt GLOB     path glob excluded from black --check; repeatable
#   -h, --help        this text
set -euo pipefail

# The block of comments at the top of this file is the help text.
usage() {
  awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "$0"
}

DECK=""; MAKEFILES=""; LOG=""; TITLE=""; JOBS="notes,slides"
CHECK_ONLY=0; EXEMPT=()

die() { echo "build_deck.sh: $*" >&2; exit 2; }

while [ $# -gt 0 ]; do
  case "$1" in
    --deck)       DECK="${2:-}"; shift 2 ;;
    --makefiles)  MAKEFILES="${2:-}"; shift 2 ;;
    --log)        LOG="${2:-}"; shift 2 ;;
    --title)      TITLE="${2:-}"; shift 2 ;;
    --jobs)       JOBS="${2:-}"; shift 2 ;;
    --check-only) CHECK_ONLY=1; shift ;;
    --exempt)     EXEMPT+=("${2:-}"); shift 2 ;;
    -h|--help)    usage; exit 0 ;;
    *)            die "unknown option: $1 (try --help)" ;;
  esac
done

[ -n "$DECK" ] || die "--deck is required"
[ -d "$DECK" ] || die "no such directory: $DECK"
DECK=$(cd "$DECK" && pwd)
[ -f "$DECK/Makefile" ] || die "no Makefile in $DECK"
cd "$DECK"

mkdir -p ltxobj
LOG=${LOG:-$DECK/ltxobj/build_deck.log}
: > "$LOG"

# The running head and foot (title, author, institute) appear on every
# slide; strip them before deciding a slide is blank.  The driver often
# wraps them over several lines, so flatten the file first.
STRIP=()
[ -n "$TITLE" ] && STRIP+=("$TITLE")
for f in notes.tex slides.tex; do
  [ -f "$f" ] || continue
  while IFS= read -r t; do
    [ -n "$t" ] && STRIP+=("$t")
  done < <(tr '\n' ' ' < "$f" \
           | grep -o '\\title{[^}]*}\|\\author{[^}]*}\|\\institute{[^}]*}' \
           | sed 's/^\\[a-z]*{//;s/}$//;s/%//g' | tr -s ' ' \
           | sed 's/^ *//;s/ *$//')
  break
done

IFS=',' read -r -a JOBLIST <<< "$JOBS"
for j in "${JOBLIST[@]}"; do
  case "$j" in notes|slides) ;; *) die "unknown job: $j" ;; esac
done

MAKEARGS=(LATEXFLAGS="-shell-escape -interaction=nonstopmode")
[ -n "$MAKEFILES" ] && MAKEARGS+=(INCLUDE_MAKEFILES="$MAKEFILES")

FAIL=0
note() { echo "$*"; }
bad()  { echo "FAIL: $*"; FAIL=1; }

# A killed build leaves ltxobj/_minted behind, and it hangs the next run.
pre_clean() { rm -rf ltxobj/_minted; }

# latexmk under -use-make can stop before the final passes: blank ToC
# frames on the slides, literal MINTED placeholders, unresolved refs.
# Run biber and pdflatex by hand while the log still asks for it.
converge() {
  local j=$1 i
  for i in 1 2 3 4; do
    [ -f "ltxobj/$j.log" ] || return 0
    if LC_ALL=C grep -a -q "run Biber" "ltxobj/$j.log"; then
      biber --output-directory ltxobj "ltxobj/$j" >> "$LOG" 2>&1 || true
    fi
    if LC_ALL=C grep -a -q \
        "Rerun to get\|undefined references\|run Biber\|Rerun LaTeX" \
        "ltxobj/$j.log"; then
      pdflatex -8bit -shell-escape -interaction=nonstopmode \
               -output-directory=ltxobj "$j.tex" >> "$LOG" 2>&1 || true
      note "$j: extra pass $i"
    else
      return 0
    fi
  done
  note "$j: still asking for a rerun after 4 extra passes"
}

if [ "$CHECK_ONLY" -eq 0 ]; then
  pre_clean
  for j in "${JOBLIST[@]}"; do
    # A make that finds the PDF up to date runs no pass and leaves the
    # previous run's log behind.  That is correct when nothing changed
    # (the log belongs to the PDF), and misleading after a failed run
    # that the fix did not touch; say which run the checks describe.
    stamp=$(mktemp "ltxobj/.stamp.$j.XXXXXX")
    set +e
    make "$j.pdf" "${MAKEARGS[@]}" >> "$LOG" 2>&1
    rc=$?
    set -e
    note "$j: make exit $rc"
    [ "$rc" -eq 0 ] || bad "$j: make failed (see $LOG)"
    if [ ! "ltxobj/$j.log" -nt "$stamp" ]; then
      note "$j: nothing was rebuilt (PDF up to date): the checks describe" \
           "the run that produced it; after a failed run, rm ltxobj/$j.pdf" \
           "to force a rebuild"
    fi
    rm -f "$stamp"
    converge "$j"
  done
fi

##### checks #####

for j in "${JOBLIST[@]}"; do
  if [ ! -f "$j.pdf" ] && [ ! -f "ltxobj/$j.pdf" ]; then
    bad "$j: no PDF"
    continue
  fi
  PDF=$j.pdf; [ -f "$PDF" ] || PDF=ltxobj/$j.pdf

  errors=0; reruns=0; vbox=0; hbox=0; emptycit=0
  if [ -f "ltxobj/$j.log" ]; then
    errors=$(LC_ALL=C grep -a -c '^!' "ltxobj/$j.log" || true)
    reruns=$(LC_ALL=C grep -a -c \
      'Rerun to get\|undefined references\|run Biber' "ltxobj/$j.log" || true)
    vbox=$(LC_ALL=C grep -a -c 'Overfull .vbox' "ltxobj/$j.log" || true)
    hbox=$(LC_ALL=C grep -a -c 'Overfull .hbox' "ltxobj/$j.log" || true)
    emptycit=$(LC_ALL=C grep -a -c 'empty citation' "ltxobj/$j.log" || true)
  else
    note "$j: no ltxobj/$j.log (check-only on a clean tree?)"
  fi
  pages=$(pdfinfo "$PDF" 2>/dev/null | awk '/Pages/{print $2}')
  qq=$(pdftotext "$PDF" - 2>/dev/null | grep -c '??' || true)

  note "== $j: errors $errors, rerun-msgs $reruns, overfull vbox $vbox," \
       "hbox $hbox, pages ${pages:-?}, ?? $qq, empty-cit $emptycit"

  [ "$errors" -eq 0 ]   || bad "$j: $errors LaTeX errors (^! in the log)"
  [ "$qq" -eq 0 ]       || bad "$j: $qq unresolved references (??)"
  [ "$emptycit" -eq 0 ] || bad "$j: $emptycit empty citations"
  # An Overfull \vbox on a slide is content off the bottom of the frame;
  # in the notes it is ordinary typesetting.
  if [ "$j" = slides ] && [ "$vbox" -ne 0 ]; then
    bad "slides: $vbox Overfull \\vbox (content off the frame)"
  fi
  # A rerun message left over after convergence is harmless only when ??
  # is 0 (a margin citation at a page boundary can two-cycle forever).
  if [ "$reruns" -ne 0 ] && [ "$qq" -eq 0 ]; then
    note "$j: $reruns rerun messages remain, but ?? is 0 --- harmless"
  fi
done

# Literal <MINTED> placeholders.  On the slides the build stopped one pass
# short; in the notes PythonTeX ran from the deck directory and every
# transcript is missing (see references/build-and-gotchas.md).
for j in "${JOBLIST[@]}"; do
  JPDF=$j.pdf; [ -f "$JPDF" ] || JPDF=ltxobj/$j.pdf
  [ -f "$JPDF" ] || continue
  m=$(pdftotext "$JPDF" - 2>/dev/null | grep -c MINTED || true)
  note "$j: MINTED placeholders $m"
  if [ "$m" -ne 0 ]; then
    if [ "$j" = notes ]; then
      bad "notes: $m MINTED placeholders (a PythonTeX run from the deck" \
          "directory: delete the stray notes.pytx* files and rebuild)"
    else
      bad "$j: $m MINTED placeholders (one more pass)"
    fi
  fi
done

# PythonTeX instance skew: a frame combining \pause with \runpython
# doubles the slides job's instances and the shared cache then prints the
# wrong transcripts in the notes.
if [ -f ltxobj/notes.pytxcode ] && [ -f ltxobj/slides.pytxcode ]; then
  n=$(wc -l < ltxobj/notes.pytxcode)
  s=$(wc -l < ltxobj/slides.pytxcode)
  d=$(( n > s ? n - s : s - n ))
  lim=$(( (n > s ? n : s) / 10 + 5 ))
  note "pytxcode lines: notes $n, slides $s (diff $d, tolerance $lim)"
  [ "$d" -le "$lim" ] || bad "pytxcode skew $d --- \\pause in a \\runpython frame?"
fi

# Blank-ish slides: a broken frame looks empty apart from the running
# head and foot.
case ",$JOBS," in *,slides,*)
  SPDF=slides.pdf; [ -f "$SPDF" ] || SPDF=ltxobj/slides.pdf
  if [ -f "$SPDF" ] && command -v pdfinfo > /dev/null; then
    n=$(pdfinfo "$SPDF" | awk '/Pages/{print $2}')
    GREPV=()
    for t in ${STRIP+"${STRIP[@]}"}; do GREPV+=(-e "$t"); done
    blanks=""
    for p in $(seq 1 "${n:-0}"); do
      if [ ${#GREPV[@]} -gt 0 ]; then
        w=$(pdftotext -f "$p" -l "$p" "$SPDF" - 2>/dev/null \
            | grep -vF "${GREPV[@]}" | tr -s ' \n' ' ' | wc -w)
      else
        w=$(pdftotext -f "$p" -l "$p" "$SPDF" - 2>/dev/null \
            | tr -s ' \n' ' ' | wc -w)
      fi
      [ "$w" -lt 6 ] && blanks="$blanks $p"
    done
    note "running head stripped: ${STRIP[*]:-(none found)}"
    note "blank-ish slides:${blanks:- none}"
    [ -z "$blanks" ] || note "  (check those pages by eye: poster frames" \
                             "and section pages are legitimately sparse)"
  fi
  ;;
esac

# Tangled Python must be black-clean: the tangle rule pipes it through
# black and the file has to match the slide byte for byte.
#
# The files are listed explicitly rather than handing black the directory.
# black honours the .gitignore at the git root, and a deck repository
# ignores examples/, so `black --check examples/` can answer "No Python
# files are present to be formatted" and exit 0 having checked nothing.
if [ -d examples ]; then
  PYFILES=()
  while IFS= read -r f; do
    skip=0
    for g in ${EXEMPT+"${EXEMPT[@]}"}; do
      # shellcheck disable=SC2254
      case "$f" in $g) skip=1 ;; esac
    done
    [ "$skip" -eq 0 ] && PYFILES+=("$f")
  done < <(find examples -name '*.py' -type f | sort)

  if [ ${#PYFILES[@]} -eq 0 ]; then
    note "black: no tangled Python examples to check"
  elif command -v black > /dev/null; then
    set +e
    out=$(black --check "${PYFILES[@]}" 2>&1)
    rc=$?
    set -e
    note "black: ${#PYFILES[@]} files checked --- $(echo "$out" | tail -1)"
    [ "$rc" -eq 0 ] || bad "black --check failed on examples/"
  else
    note "WARNING: black not found --- skipping the style check"
  fi
fi

# Source lines longer than 79 characters.
LONG=0
for f in contents.nw abstract.tex; do
  [ -f "$f" ] || continue
  c=$(awk 'length > 79' "$f" | wc -l)
  [ "$c" -eq 0 ] || { note "$f: $c lines > 79 chars"; LONG=$((LONG + c)); }
done
[ "$LONG" -eq 0 ] && note "line length: all <= 79"
[ "$LONG" -eq 0 ] || bad "$LONG source lines longer than 79 characters"

# Provenance blocks in the bibliography.  check_provenance.py is offline
# and cheap, so it belongs in every build; its companion check_metadata.py
# queries Crossref and is left to the reviewer.
PROV=~/.claude/skills/backing-claims/scripts/check_provenance.py
if [ -f ltnotes.bib ]; then
  if [ -f "$PROV" ]; then
    set +e
    out=$(python3 "$PROV" ltnotes.bib 2>&1)
    rc=$?
    set -e
    note "provenance: $(echo "$out" | grep -a 'Result:' | tail -1 \
                       | sed 's/^ *//')"
    if [ "$rc" -ne 0 ]; then
      echo "$out" | grep -a -A20 'ERRORS' | head -20
      bad "check_provenance.py failed on ltnotes.bib"
    fi
  else
    note "WARNING: $PROV not found --- provenance unchecked"
  fi
fi

command -v montage > /dev/null \
  || note "WARNING: montage not found --- render contact sheets elsewhere"

# Generated files must not be tracked or modified by hand.
if git rev-parse --git-dir > /dev/null 2>&1; then
  note "git status:"
  git status --short --ignore-submodules=all . | head -5
fi

if [ "$FAIL" -eq 0 ]; then
  note "ALL CHECKS PASSED"
  note "Still to do separately: check_margin_notes.py on the notes PDF;"
  note "  check_metadata.py on ltnotes.bib (needs the network); running the"
  note "  tangled examples; reading every slide and every notes page."
else
  note "CHECKS FAILED"
fi
exit "$FAIL"
