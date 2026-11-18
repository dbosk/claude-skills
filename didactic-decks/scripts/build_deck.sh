#!/bin/bash
# build_deck.sh --- build a didactic deck (notes.pdf, slides.pdf) and run
# the pre-review checks.
#
# One job at a time (both jobs share ltxobj), converge the cross
# references by hand where latexmk stops short, then report every check
# with its number.  Exits non-zero when a hard check fails.
#
# A deck with notes-sv.tex or slides-sv.tex is bilingual: those jobs build
# the Swedish edition into ltxobj-sv, every check runs per edition, and
# didactic-sync.py must find the two languages in step.
#
# Usage:
#   build_deck.sh --deck DIR [options]
#
#   --deck DIR        deck directory (required)
#   --makefiles DIR   passed as INCLUDE_MAKEFILES (default: the Makefile's)
#   --log FILE        build log (default: DIR/ltxobj/build_deck.log)
#   --title STR       running-head title, stripped before the blank-slide
#                     check (default: read from notes.tex, or from
#                     notes-body.tex when notes.tex is an edition driver)
#   --jobs LIST       comma-separated: notes,slides,notes-sv,slides-sv
#                     (default: notes,slides, and the -sv jobs whose
#                     drivers exist)
#   --check-only      skip the build, run the checks on existing PDFs
#   --exempt GLOB     path glob excluded from black --check; repeatable
#   --overfull-pt N   notes lines more than N pt too wide fail the build
#                     (default 5; marginparsep is 7pt in the didactic
#                     layout, so a wider line nears the margin notes)
#   --draft           report those lines but do not fail on them, for
#                     quick compiles for review
#   -h, --help        this text
#
# A deck whose notes really carry no margin notes opts out of the
# margin-note check with a committed file .no-margin-check in DIR whose
# first line says why; the check is then skipped and the reason printed.
set -euo pipefail

# The forced PythonTeX rerun below moves a job's .pytxmcr aside for the
# length of its make.  If the script is interrupted then, put it back (or
# drop it, when latexmk has already written a new one), so the next
# build finds the directory as it was.  The script sets no other trap.
ASIDE=""; ASIDE_TO=""
restore_aside() {
  if [ -n "$ASIDE" ] && [ -f "$ASIDE" ]; then
    if [ -f "$ASIDE_TO" ]; then
      rm -f "$ASIDE"
    else
      mv "$ASIDE" "$ASIDE_TO"
    fi
  fi
  ASIDE=""
}
trap restore_aside EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# The block of comments at the top of this file is the help text.
usage() {
  awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "$0"
}

DECK=""; MAKEFILES=""; LOG=""; TITLE=""; JOBS=""
CHECK_ONLY=0; EXEMPT=(); OVERFULL_PT=5; DRAFT=0

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
    --overfull-pt) OVERFULL_PT="${2:-}"; shift 2 ;;
    --draft)      DRAFT=1; shift ;;
    -h|--help)    usage; exit 0 ;;
    *)            die "unknown option: $1 (try --help)" ;;
  esac
done

[ -n "$DECK" ] || die "--deck is required"
[ -d "$DECK" ] || die "no such directory: $DECK"
DECK=$(cd "$DECK" && pwd)
[ -f "$DECK/Makefile" ] || die "no Makefile in $DECK"
cd "$DECK"

# The editions other than the course's main language, by the suffix of
# their drivers, PDFs and output directory: notes-sv.tex builds
# notes-sv.pdf in ltxobj-sv.  Another language is one more suffix here.
OTHER_EDITIONS=(-sv)

# A job's edition suffix ("" for the main edition), its base job (notes
# or slides) and its output directory.  Each edition builds in its own
# directory, since PythonTeX's files there do not say which job made them.
suffix_of() {
  local sfx
  for sfx in "${OTHER_EDITIONS[@]}"; do
    case "$1" in *"$sfx") echo "$sfx"; return ;; esac
  done
  echo ""
}
base_of() { local s; s=$(suffix_of "$1"); echo "${1%"$s"}"; }
outdir() { echo "ltxobj$(suffix_of "$1")"; }

BILINGUAL=0
for sfx in "${OTHER_EDITIONS[@]}"; do
  if [ -f "notes$sfx.tex" ] || [ -f "slides$sfx.tex" ]; then BILINGUAL=1; fi
done
if [ -z "$JOBS" ]; then
  JOBS="notes,slides"
  for sfx in "${OTHER_EDITIONS[@]}"; do
    [ -f "notes$sfx.tex" ] && JOBS="$JOBS,notes$sfx"
    [ -f "slides$sfx.tex" ] && JOBS="$JOBS,slides$sfx"
  done
fi

mkdir -p ltxobj
LOG=${LOG:-$DECK/ltxobj/build_deck.log}
: > "$LOG"

# The running head and foot (title, author, institute) appear on every
# slide; strip them before deciding a slide is blank.  The driver often
# wraps them over several lines, so flatten the file first.
#
# An edition driver (no \documentclass; it inputs notes-body.tex) holds
# no title: read its body.  A bilingual title is \ensv{English}{Svenska},
# so a file that uses \ensv or \didactictr is read with balanced braces
# and both halves are stripped; any other file keeps the one-level
# reading it always had.
title_parts() {
  python3 - "$1" <<'PYEOF'
import re, sys
text = open(sys.argv[1], encoding="utf-8").read()
# comments go first: a trailing "% sync ..." stamp is not part of a title
text = re.sub(r"(?<!\\)%[^\n]*", "", text)
def arg(s, i):
    # the balanced-brace argument whose "{" is at s[i]
    depth = 0
    for j in range(i, len(s)):
        depth += {"{": 1, "}": -1}.get(s[j], 0)
        if depth == 0:
            return s[i + 1:j], j + 1
    return s[i + 1:], len(s)
def parts(s):
    # the text outside the pairs, and both halves of each pair
    out, i = [], 0
    while (m := re.search(r"\\(?:ensv|didactictr)\s*\{", s[i:])):
        a, k = arg(s, i + m.end() - 1)
        k += len(s[k:]) - len(s[k:].lstrip())
        b, k = arg(s, k) if s[k:k + 1] == "{" else ("", k)
        out += [s[i:i + m.start()]] + parts(a) + parts(b)
        i = k
    return out + [s[i:]]
for m in re.finditer(r"\\(?:title|author|institute)\s*\{", text):
    body, _ = arg(text, m.end() - 1)
    for p in parts(body):
        p = " ".join(p.split())
        if p:
            print(p)
PYEOF
}
STRIP=()
[ -n "$TITLE" ] && STRIP+=("$TITLE")
for f in notes.tex slides.tex; do
  [ -f "$f" ] || continue
  if ! grep -q '\\documentclass' "$f" \
     && grep -q "\\\\input{\\?${f%.tex}-body" "$f"; then
    f=${f%.tex}-body.tex
    [ -f "$f" ] || continue
  fi
  if grep -q '\\ensv\|\\didactictr' "$f"; then
    while IFS= read -r t; do
      [ -n "$t" ] && STRIP+=("$t")
    done < <(title_parts "$f")
  else
    while IFS= read -r t; do
      [ -n "$t" ] && STRIP+=("$t")
    done < <(tr '\n' ' ' < "$f" \
             | grep -o '\\title{[^}]*}\|\\author{[^}]*}\|\\institute{[^}]*}' \
             | sed 's/^\\[a-z]*{//;s/}$//;s/%//g' | tr -s ' ' \
             | sed 's/^ *//;s/ *$//')
  fi
  break
done

IFS=',' read -r -a JOBLIST <<< "$JOBS"
for j in "${JOBLIST[@]}"; do
  case "$(base_of "$j")" in notes|slides) ;; *) die "unknown job: $j" ;; esac
  mkdir -p "$(outdir "$j")"
done

MAKEARGS=(LATEXFLAGS="-shell-escape -interaction=nonstopmode")
[ -n "$MAKEFILES" ] && MAKEARGS+=(INCLUDE_MAKEFILES="$MAKEFILES")

FAIL=0
note() { echo "$*"; }
bad()  { echo "FAIL: $*"; FAIL=1; }

# A killed build leaves ltxobj/_minted behind, and it hangs the next run.
pre_clean() {
  local sfx
  rm -rf ltxobj/_minted
  for sfx in "${OTHER_EDITIONS[@]}"; do rm -rf "ltxobj$sfx/_minted"; done
}

# latexmk under -use-make can stop before the final passes: blank ToC
# frames on the slides, literal MINTED placeholders, unresolved refs.
# Run biber and pdflatex by hand while the log still asks for it.
# Up to 8 passes: marginfix's records (anchor pages, early page ends and
# their cap, \marginnoteyieldlimit) settle a run at a time, and a notes
# PDF dense with citations in the margin has needed 6 after latexmk.
converge() {
  local j=$1 i od
  od=$(outdir "$j")
  for i in 1 2 3 4 5 6 7 8; do
    [ -f "$od/$j.log" ] || return 0
    if LC_ALL=C grep -a -q "run Biber" "$od/$j.log"; then
      biber --output-directory "$od" "$od/$j" >> "$LOG" 2>&1 || true
    fi
    if LC_ALL=C grep -a -q \
        "Rerun to get\|undefined references\|run Biber\|Rerun LaTeX" \
        "$od/$j.log"; then
      # -recorder keeps $od/$j.fls the record of the last pass, which
      # check_transcripts.py reads.
      pdflatex -8bit -shell-escape -interaction=nonstopmode -recorder \
               -output-directory="$od" "$j.tex" >> "$LOG" 2>&1 || true
      note "$j: extra pass $i"
    else
      return 0
    fi
  done
  note "$j: still asking for a rerun after 8 extra passes"
}

# Every \runpython must have left a non-empty transcript of its own in
# the job's PDF.  An incremental build that skips PythonTeX can drop them
# silently (no ??, no error, no MINTED), or print another job's: the
# other edition's programs if the editions were built into one
# directory, or the slides' shifted instances.  See check_transcripts.py.
TRANSCRIPTS=$(dirname "$0")/check_transcripts.py
declare -A TRANS_OUT TRANS_RC
transcripts() {
  local j=$1
  [ -f "$(outdir "$j")/$j.pytxcode" ] || return 0
  set +e
  TRANS_OUT[$j]=$(python3 "$TRANSCRIPTS" . "$j" 2>&1)
  TRANS_RC[$j]=$?
  set -e
}

if [ "$CHECK_ONLY" -eq 0 ]; then
  pre_clean
  for j in "${JOBLIST[@]}"; do
    # A make that finds the PDF up to date runs no pass and leaves the
    # previous run's log behind.  That is correct when nothing changed
    # (the log belongs to the PDF), and misleading after a failed run
    # that the fix did not touch; say which run the checks describe.
    od=$(outdir "$j")
    # The jobs that build in one directory share PythonTeX's .stdout files
    # there, and latexmk reruns PythonTeX only when the job's .pytxcode
    # changed.  After a small edit that leaves it unchanged, a job would
    # be typeset from the files the other job's run left behind, which is
    # wrong wherever the two run different code at the same instance (a
    # \runpython in \mode<article>, a \pause).  So when the last PythonTeX
    # run here was another job's, the job's .pytxmcr is moved aside:
    # latexmk's PythonTeX rule (the makefiles' latexmkrc) then has to run
    # again if latexmk runs at all.  If make finds the PDF up to date and
    # never calls latexmk, the file is put back unchanged.
    last=""
    for f in "$od"/*.pytxmcr; do
      [ -f "$f" ] || continue
      if [ -z "$last" ] || [ "$f" -nt "$last" ]; then last=$f; fi
    done
    aside=""
    if [ -n "$last" ] && [ "$last" != "$od/$j.pytxmcr" ] \
       && [ -f "$od/$j.pytxmcr" ]; then
      aside=$od/.$j.pytxmcr.aside
      mv "$od/$j.pytxmcr" "$aside"
      ASIDE=$aside; ASIDE_TO=$od/$j.pytxmcr
    fi
    stamp=$(mktemp "$od/.stamp.$j.XXXXXX")
    set +e
    make "$j.pdf" "${MAKEARGS[@]}" >> "$LOG" 2>&1
    rc=$?
    set -e
    note "$j: make exit $rc"
    [ "$rc" -eq 0 ] || bad "$j: make failed (see $LOG)"
    if [ "$BILINGUAL" -eq 1 ] && [ ! -f "$od/$j.log" ]; then
      # The checks below read $od; a Makefile without the edition's
      # TEX_OUTDIR builds into ltxobj, and they would check nothing.
      bad "$j: no $od/$j.log after make: does the Makefile set" \
          "TEX_OUTDIR=$od for the $(suffix_of "$j") jobs?"
    elif [ ! "$od/$j.log" -nt "$stamp" ]; then
      note "$j: nothing was rebuilt (PDF up to date): the checks describe" \
           "the run that produced it; after a failed run, rm $od/$j.pdf" \
           "to force a rebuild"
    fi
    rm -f "$stamp"
    if [ -n "$aside" ]; then
      if [ -f "$od/$j.pytxmcr" ]; then
        rm -f "$aside"
        note "$j: PythonTeX rerun for it (the last run in $od was" \
             "$(basename "$last" .pytxmcr)'s)"
      else
        mv "$aside" "$od/$j.pytxmcr"
      fi
      ASIDE=""
    fi
    # PythonTeX ran but latexmk saw no reason for another pass (nothing
    # it tracks changed): typeset once more, so that the PDF is the one
    # these outputs give.
    if [ -f "$od/$j.pytxmcr" ] && [ -f "$od/$j.log" ] \
       && [ "$od/$j.pytxmcr" -nt "$od/$j.log" ]; then
      pdflatex -8bit -shell-escape -interaction=nonstopmode -recorder \
               -output-directory="$od" "$j.tex" >> "$LOG" 2>&1 || true
      note "$j: one more pass after its PythonTeX run"
    fi
    converge "$j"
    # Check the job's transcripts now: the next job's PythonTeX run
    # rewrites and deletes the .stdout files both jobs of an edition share
    # in its output directory.  (The rerun forced above happens before
    # this job's make, so the check sees the job's own run.)
    transcripts "$j"
  done
fi

##### checks #####

for j in "${JOBLIST[@]}"; do
  od=$(outdir "$j")
  if [ ! -f "$j.pdf" ] && [ ! -f "$od/$j.pdf" ]; then
    bad "$j: no PDF"
    continue
  fi
  PDF=$j.pdf; [ -f "$PDF" ] || PDF=$od/$j.pdf

  errors=0; reruns=0; vbox=0; hbox=0; emptycit=0
  if [ -f "$od/$j.log" ]; then
    errors=$(LC_ALL=C grep -a -c '^!' "$od/$j.log" || true)
    reruns=$(LC_ALL=C grep -a -c \
      'Rerun to get\|undefined references\|run Biber' "$od/$j.log" || true)
    vbox=$(LC_ALL=C grep -a -c 'Overfull .vbox' "$od/$j.log" || true)
    hbox=$(LC_ALL=C grep -a -c 'Overfull .hbox' "$od/$j.log" || true)
    emptycit=$(LC_ALL=C grep -a -c 'empty citation' "$od/$j.log" || true)
  else
    note "$j: no $od/$j.log (check-only on a clean tree?)"
  fi
  pages=$(pdfinfo "$PDF" 2>/dev/null | awk '/Pages/{print $2}')
  qq=$(pdftotext "$PDF" - 2>/dev/null | grep -c '??' || true)

  note "== $j: errors $errors, rerun-msgs $reruns, overfull vbox $vbox," \
       "hbox $hbox, pages ${pages:-?}, ?? $qq, empty-cit $emptycit"

  [ "$errors" -eq 0 ]   || bad "$j: $errors LaTeX errors (^! in the log)"
  [ "$qq" -eq 0 ]       || bad "$j: $qq unresolved references (??)"
  [ "$emptycit" -eq 0 ] || bad "$j: $emptycit empty citations"
  # A malformed bib entry (e.g. an unclosed brace) makes biber skip it:
  # the citations then print as bold keys, with no "empty citation" in
  # the LaTeX log. biber's own log says ERROR.
  if [ -f "$od/$j.blg" ]; then
    biberr=$(LC_ALL=C grep -a -c '^\[[0-9]*\] .*ERROR\|> ERROR' \
               "$od/$j.blg" || true)
    [ "$biberr" -eq 0 ] || bad "$j: $biberr biber errors ($od/$j.blg)"
  fi
  # An Overfull \vbox on a slide is content off the bottom of the frame;
  # in the notes it is ordinary typesetting.
  if [ "$(base_of "$j")" = slides ] && [ "$vbox" -ne 0 ]; then
    bad "$j: $vbox Overfull \\vbox (content off the frame)"
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
  JPDF=$j.pdf; [ -f "$JPDF" ] || JPDF=$(outdir "$j")/$j.pdf
  [ -f "$JPDF" ] || continue
  m=$(pdftotext "$JPDF" - 2>/dev/null | grep -c MINTED || true)
  note "$j: MINTED placeholders $m"
  if [ "$m" -ne 0 ]; then
    if [ "$(base_of "$j")" = notes ]; then
      bad "$j: $m MINTED placeholders (a PythonTeX run from the deck" \
          "directory: delete the stray $j.pytx* files and rebuild)"
    else
      bad "$j: $m MINTED placeholders (one more pass)"
    fi
  fi
done

for j in "${JOBLIST[@]}"; do
  # --check-only: the files may have changed since the job's last pass;
  # the script then warns rather than fails.
  [ -n "${TRANS_RC[$j]+x}" ] || transcripts "$j"
  [ -n "${TRANS_RC[$j]+x}" ] || continue
  echo "${TRANS_OUT[$j]}" | sed 's/^/transcripts: /'
  case "${TRANS_RC[$j]}" in
    0) ;;
    1) bad "$j: a \\runpython has no transcript in the PDF, an empty" \
           "one or another job's; rm $(outdir "$j")/$j.pytxmcr and build" \
           "$j again, or rebuild clean (references/build-and-gotchas.md," \
           "\"Stale PythonTeX transcripts\")" ;;
    *) bad "$j: transcript check failed (exit ${TRANS_RC[$j]})" ;;
  esac
done

# PythonTeX instance skew: a frame combining \pause with \runpython
# doubles the slides job's instances and the shared cache then prints the
# wrong transcripts in the notes.  The two jobs of one edition share an
# output directory, and so the cache: compare within each edition.
for sfx in "" "${OTHER_EDITIONS[@]}"; do
  od=ltxobj$sfx
  if [ -f "$od/notes$sfx.pytxcode" ] && [ -f "$od/slides$sfx.pytxcode" ]; then
    n=$(wc -l < "$od/notes$sfx.pytxcode")
    s=$(wc -l < "$od/slides$sfx.pytxcode")
    d=$(( n > s ? n - s : s - n ))
    lim=$(( (n > s ? n : s) / 10 + 5 ))
    note "pytxcode lines: notes$sfx $n, slides$sfx $s (diff $d," \
         "tolerance $lim)"
    [ "$d" -le "$lim" ] \
      || bad "pytxcode skew $d --- \\pause in a \\runpython frame?"
  fi
done

# The editions of a bilingual deck must not build into one output
# directory: a directory that holds the logs of two editions' jobs was
# shared, in this build or an earlier one, and its .stdout files may be
# the other edition's.
if [ "$BILINGUAL" -eq 1 ]; then
  for d in ltxobj*/; do
    d=${d%/}
    eds=$(for f in "$d"/notes*.log "$d"/slides*.log; do
            [ -f "$f" ] || continue
            j=$(basename "$f" .log)
            case "$(base_of "$j")" in notes|slides) ;; *) continue ;; esac
            echo "edition$(suffix_of "$j")"
          done | sort -u | tr '\n' ' ')
    if [ "$(echo "$eds" | wc -w)" -gt 1 ]; then
      bad "$d holds the logs of two editions ($eds): they shared an" \
          "output directory; set TEX_OUTDIR per edition in the Makefile," \
          "remove $d and rebuild"
    fi
  done
fi

# Blank-ish slides: a broken frame looks empty apart from the running
# head and foot.  The main edition's lines carry no prefix.
for sj in "${JOBLIST[@]}"; do
  [ "$(base_of "$sj")" = slides ] || continue
  pfx=""; [ -z "$(suffix_of "$sj")" ] || pfx="$sj: "
  SPDF=$sj.pdf; [ -f "$SPDF" ] || SPDF=$(outdir "$sj")/$sj.pdf
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
    note "${pfx}running head stripped: ${STRIP[*]:-(none found)}"
    note "${pfx}blank-ish slides:${blanks:- none}"
    [ -z "$blanks" ] || note "  (check those pages by eye: poster frames" \
                             "and section pages are legitimately sparse)"
  fi
done

# Margin notes printed away from their marker.  check_margin_notes.py
# reads the margin column from the didactic-margin line in the notes log
# and exits 2 when it checked nothing (no column, no note found), so a
# skipped check cannot pass for a clean one.
MARGIN=$(dirname "$0")/check_margin_notes.py
for nj in "${JOBLIST[@]}"; do
  [ "$(base_of "$nj")" = notes ] || continue
  nod=$(outdir "$nj")
  pfx=""; [ -z "$(suffix_of "$nj")" ] || pfx="$nj "
  NPDF=$nj.pdf; [ -f "$NPDF" ] || NPDF=$nod/$nj.pdf
  if [ -f .no-margin-check ]; then
    note "${pfx}margin notes: skipped, .no-margin-check says:" \
         "$(head -1 .no-margin-check)"
  elif [ -f "$NPDF" ]; then
    MARGS=("$NPDF")
    [ -f "$nod/$nj.log" ] && MARGS+=(--log "$nod/$nj.log")
    set +e
    out=$(python3 "$MARGIN" "${MARGS[@]}" 2>&1)
    rc=$?
    set -e
    echo "$out" | grep -a -v '^WARNING:' | sed "s/^/${pfx}margin notes: /"
    w=$(echo "$out" | grep -a -c '^WARNING:' || true)
    [ "$w" -eq 0 ] || note "${pfx}margin notes: $w warnings (unpaired marker" \
                          "or note): python3 $MARGIN $NPDF lists them"
    case "$rc" in
      0) ;;
      1) bad "$nj: margin notes print away from their marker, or" \
             "marginfix logged an unresolved spill" ;;
      *) bad "$nj: margin-note check checked nothing (exit $rc);" \
             "if the deck really has no margin notes, say so in" \
             ".no-margin-check" ;;
    esac
  fi
done

# Overfull lines in the notes: an inline code literal or a URL running
# out of the text block, possibly over a margin note.  The margin check
# does not see it (it compares notes and markers, not the body's edge).
# A slide's overfull \hbox is left to the eye: beamer frames overflow
# by design (columns, wide code), and the vbox check catches the bad case.
OVERFULL=$(dirname "$0")/check_overfull.py
for nj in "${JOBLIST[@]}"; do
  [ "$(base_of "$nj")" = notes ] || continue
  nod=$(outdir "$nj")
  pfx=""; [ -z "$(suffix_of "$nj")" ] || pfx="$nj "
  NPDF=$nj.pdf; [ -f "$NPDF" ] || NPDF=$nod/$nj.pdf
  if [ -f "$nod/$nj.log" ]; then
    OARGS=(--pt "$OVERFULL_PT" "$nod/$nj.log")
    # With the PDF, a box TeX set and threw away (a <presentation> frame)
    # is listed as not in the PDF and does not count.
    [ -f "$NPDF" ] && OARGS+=(--pdf "$NPDF")
    set +e
    out=$(python3 "$OVERFULL" "${OARGS[@]}" 2>&1)
    rc=$?
    set -e
    echo "$out" | sed "s/^/${pfx}overfull: /"
    case "$rc" in
      0) ;;
      1) if [ "$DRAFT" -eq 1 ]; then
           note "${pfx}overfull: --draft, not failing on the lines above"
         else
           bad "$nj: lines more than ${OVERFULL_PT}pt too wide (fix them," \
               "or --draft for a quick compile for review)"
         fi ;;
      *) bad "$nj: overfull check failed (exit $rc)" ;;
    esac
  fi
done

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

# Source lines longer than 79 characters.  A trailing stamp,
# "% sync english=... swedish=...", does not count: only didactic-sync.py
# writes it, and it adds 37 characters to a line (31 more for each
# further pair ending there).  The pattern takes any language key, and
# only a comment at the end of the line with no further % in it.
LONG=0
for f in contents.nw abstract.tex; do
  [ -f "$f" ] || continue
  c=$(awk '{ sub(/[ \t]*% sync [A-Za-z]+=[^%]*$/, "") } length > 79' "$f" \
      | wc -l)
  [ "$c" -eq 0 ] || { note "$f: $c lines > 79 chars"; LONG=$((LONG + c)); }
done
[ "$LONG" -eq 0 ] && note "line length: all <= 79"
[ "$LONG" -eq 0 ] || bad "$LONG source lines longer than 79 characters"

# The two languages of a bilingual deck must be in step.  didactic-sync.py
# exits 1 when a pair is behind, unstamped, or a stamp has lost its pair,
# and 2 when a file cannot be read as blocks (an \end{onlyin} out of
# column 1, a block in a frame that is not [fragile], a source still in
# version 2.17's form, which names didactic-sync.py --migrate).  Both fail
# the build, so ALL CHECKS PASSED means the two languages are in step.
# It reads the deck's own sources: every .nw and .tex file except a woven
# X.tex beside its X.nw, nothing under the output directories, examples/ or
# mentipy-obj/, and in litteratursokning/ only what was written by hand: not
# the search tool's hit lists (*-full.tex, or a file whose head says
# "Generated by: scholar") nor its older standalone exports (a file that
# starts with \documentclass).
if [ "$BILINGUAL" -eq 1 ]; then
  SYNC=$(kpsewhich didactic-sync.py 2>/dev/null || true)
  SYNCFILES=()
  while IFS= read -r f; do
    case "$f" in *.tex) [ -f "${f%.tex}.nw" ] && continue ;; esac
    case "$f" in
      litteratursokning/*-full.tex) continue ;;
      litteratursokning/*.tex)
        head -n 12 "$f" | grep -q 'Generated by: scholar\|^\\documentclass' \
          && continue ;;
    esac
    SYNCFILES+=("$f")
  done < <(find . \( -name 'ltxobj*' -o -name examples -o -name '_minted*' \
                     -o -name 'pythontex-files-*' -o -name mentipy-obj \
                     -o -name '.?*' \) -prune \
                -o -type f \( -name '*.nw' -o -name '*.tex' \) -print \
           | sed 's|^\./||' | sort)
  if [ -z "$SYNC" ]; then
    bad "didactic-sync.py not found (kpsewhich): the two languages are" \
        "unchecked; install didactic v2.18 or later"
  elif [ ${#SYNCFILES[@]} -eq 0 ]; then
    bad "sync: no .nw or .tex sources found"
  else
    set +e
    out=$(python3 "$SYNC" "${SYNCFILES[@]}" 2>&1)
    rc=$?
    set -e
    case "$rc" in
      0) note "sync: all pairs in step (${#SYNCFILES[@]} files:" \
              "${SYNCFILES[*]})"
         [ -z "$out" ] || echo "$out" | sed 's/^/sync: /' ;;
      1) echo "$out" | sed 's/^/sync: /'
         bad "the two languages are not in step: read both sides of each" \
             "pair above, then didactic-sync.py --stamp FILE:LINE as named" ;;
      *) echo "$out" | sed 's/^/sync: /'
         bad "didactic-sync.py cannot read the sources (exit $rc)" ;;
    esac
  fi
fi

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

# Transcript files left beside the sources by didactic before v2.18.1,
# which writes them into the output directory; a build under a newer one
# no longer reads them.
legacy=$(find . -maxdepth 1 \( -name 'didactic_output_*.txt' \
                              -o -name 'didactic_pair_*.txt' \) | wc -l)
if [ "$legacy" -gt 0 ] \
   && grep -a -q 'ltxobj[^ ]*/didactic_output_' ltxobj*/*.fls 2>/dev/null; then
  note "$legacy transcript files beside the sources are left from didactic" \
       "before v2.18.1 and no longer read: rm -f didactic_output_*.txt" \
       "didactic_pair_*.txt"
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
  [ "$DRAFT" -eq 0 ] \
    || note "  (--draft: overfull lines reported, not checked)"
  note "Still to do separately: check_metadata.py on ltnotes.bib (needs"
  note "  the network); running the tangled examples; reading every slide"
  note "  and every notes page."
else
  note "CHECKS FAILED"
fi
exit "$FAIL"
