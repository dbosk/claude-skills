#!/usr/bin/env python3
r"""Find verbatim lines that are clipped at the right edge of a page, or
that run out of the notes' text block into the margin column.

Three detectors, because each alone misses cases:

  A. prefix test -- a line pdftotext extracts from page N is a strict
     prefix of a line in the deck's tangled programs or PythonTeX
     transcripts.  Catches text clipped clean off the page, which the
     bbox test cannot see (the clipped word never reaches pdftotext).
     A line minted wrapped (breaklines, continued behind a mark on the
     next line) is not a cut: when the line and the next one joined are
     still the source line's prefix, the hit is dropped.  The next line
     may be one further down, past a line of margin text alone.
  B. bbox test -- a word's xMax exceeds the page width.  Catches a line
     that hangs over the edge and is only partly drawn.
  C. margin test (notes) -- from the word boxes and the margin column's
     left edge, read from the "didactic-margin: odd= even= width=" line
     didactic writes to the job's log (ltxobj/<job>.log); without that
     line (slides, an older didactic) the test is skipped and says so.
     C1, OVERPRINT: two word boxes overlap, one of them reaching into the
     margin column.  Typeset text never overlaps, so this is a line
     printed over a margin note (or two notes over each other).
     C2, MARGIN: a run of words on a body line ends more than OVER_PT past
     the text block (the column's edge less \marginparsep), whether or
     not a note stands beside it.  Not a body line: a line of a full-width
     block (didactic's definitions, examples and wide code start left of
     the body's edge and span the column on purpose; lines of the same
     display, BLOCK_GAP or less apart, count with it) and a line that
     starts right of the text block's middle (the right column of two
     programs side by side).
     Why it is needed: minted (fvextra) sets each verbatim line as
     \hbox to \linewidth{<line>\hss}, and the \hss absorbs any excess, so
     a transcript line that runs into the margin logs no Overfull \hbox
     and check_overfull.py cannot see it; A misses it when pdftotext puts
     the note's words on the same layout line.
     What C misses: an overflowing line inside a full-width display or
     within BLOCK_GAP of one (taken as part of it), the right column of a
     side-by-side pair overflowing past the full width, and a line that
     overflows by OVER_PT or less.  C2 also reports prose lines more than
     OVER_PT too wide, which check_overfull.py reports from the log too.

Usage: cutcheck.py <deck-dir> [notes|slides ...]
"""
import collections
import glob
import html
import os
import re
import subprocess
import sys


def sources(deck):
    out = set()
    # The transcripts are in the output directories since didactic
    # v2.18.1, beside the sources before that.
    pats = [os.path.join(deck, "examples", "*.py"),
            os.path.join(deck, "didactic_output_*.txt"),
            os.path.join(deck, "ltxobj*", "didactic_output_*.txt")]
    for pat in pats:
        for f in glob.glob(pat):
            try:
                text = open(f, encoding="utf-8").read()
            except UnicodeDecodeError:
                continue
            for ln in text.splitlines():
                ln = ln.strip()
                if len(ln) >= 25:
                    out.add(ln)
    return out


# pdftotext -layout indents a line that holds only margin text this many
# columns or more deeper than the body lines around it (about 90 on a
# didactic notes page, whose text block is some 85 columns wide).
MARGIN_INDENT = 40


def indent(text):
    return len(text) - len(text.lstrip())


def squash(text):
    """Text without spaces: a wrapped line's halves lose the space at the
    break, or gain one, depending on where minted broke it."""
    return re.sub(r"\s+", "", text)


# didactic logs the margin column's left edge per page parity, in bp.
MARGIN_LINE_RE = re.compile(
    r"didactic-margin:\s*odd=([0-9.]+)\s+even=([0-9.]+)\s+width=([0-9.]+)")
# Words whose baselines (yMax) differ by less than this sit on one line.
SAME_LINE = 1.0
# Words on one line further apart than this belong to different runs (a
# body line and a margin note beside it).  Larger than one interword space
# in body text or verbatim, smaller than \marginparsep (7pt).
RUN_GAP = 6.0
# \marginparsep: the text block ends this far left of the margin column.
MARGINPARSEP = 7.0
# A line ending this far past the text block is reported, the same
# tolerance as check_overfull.py's default --overfull-pt.
OVER_PT = 5.0
# Two word boxes that overlap by more than this, both ways, overprint.
OVERLAP_X = 1.0
OVERLAP_Y = 2.0
# Lines whose baselines are at most this far apart belong to one display
# (one blank verbatim line is about 18.4pt).  Used to find the lines of a
# full-width block that start indented, right of the body's left edge.
BLOCK_GAP = 19.5
# Margin notes start at the column's left edge, to within this.  Body
# verbatim rarely does: the character grids of the body (66.0 + 4.08k bp)
# and of full-width blocks (46.1 + 4.08k bp) miss 431.65 +- 0.5 bp in the
# intropy layout.  A verbatim line on another grid (a list, a right
# column) with a word starting there is split at it and goes unreported
# by C2; C1 still sees it when a note stands beside it.
NOTE_EDGE = 0.5
# didactic's full-width blocks start about 20pt left of the body text; a
# line starting this far left of it opens one.
FULLWIDTH_LEFT = 3.0


def margin_columns(log):
    """(odd, even) left edges of the margin column, or None."""
    try:
        text = open(log, encoding="latin-1").read()
    except OSError:
        return None
    found = MARGIN_LINE_RE.findall(text)
    if not found:
        return None
    odd, even, _ = (float(v) for v in found[-1])
    return odd, even


def words_by_page(bbox_html):
    """{page: [(xMin, yMin, xMax, yMax, word)]} from pdftotext -bbox."""
    pages, page = {}, 0
    for line in bbox_html.splitlines():
        if "<page" in line:
            page += 1
            pages[page] = []
            continue
        m = re.search(r'xMin="([0-9.]+)" yMin="([0-9.]+)" '
                      r'xMax="([0-9.]+)" yMax="([0-9.]+)">([^<]*)</word>',
                      line)
        if m and page:
            x0, y0, x1, y1 = (float(v) for v in m.groups()[:4])
            pages[page].append((x0, y0, x1, y1, html.unescape(m.group(5))))
    return pages


def text_lines(words):
    """Words grouped into lines by baseline, each sorted left to right."""
    lines = []
    for w in sorted(words, key=lambda w: (w[3], w[0])):
        if lines and abs(lines[-1][0][3] - w[3]) < SAME_LINE:
            lines[-1].append(w)
        else:
            lines.append([w])
    for line in lines:
        line.sort(key=lambda w: w[0])
    return lines


def runs(line, lo=None):
    """A line's words split into runs at gaps wider than RUN_GAP, and
    before a word starting at the margin column's edge lo: a margin note's
    first word, beside a body line that ends in the 7pt gap before it."""
    out = [[line[0]]]
    for w in line[1:]:
        if (w[0] - out[-1][-1][2] > RUN_GAP
                or (lo is not None and abs(w[0] - lo) <= NOTE_EDGE)):
            out.append([w])
        else:
            out[-1].append(w)
    return out


def body_left_edge(pages, cols):
    """The x where most lines left of the margin column start, per parity:
    the body text's left edge."""
    edges = {}
    for parity in (0, 1):
        starts = collections.Counter()
        for p, words in pages.items():
            if p % 2 != parity or not words:
                continue
            lo = cols[0] if p % 2 else cols[1]
            for line in text_lines(words):
                if line[0][0] < lo - RUN_GAP:
                    starts[round(line[0][0])] += 1
        edges[parity] = starts.most_common(1)[0][0] if starts else None
    return edges


def overprints(words, lo):
    """C1: pairs of word boxes that overlap, one of them reaching into the
    margin column.  Typeset text never overlaps, so this is a line running
    over a margin note (or two notes printed over each other)."""
    near = sorted(w for w in words if w[2] > lo)
    pairs = []
    for i, a in enumerate(near):
        for b in near[i + 1:]:
            if b[0] >= a[2] - OVERLAP_X:
                break
            if (min(a[2], b[2]) - max(a[0], b[0]) > OVERLAP_X
                    and min(a[3], b[3]) - max(a[1], b[1]) > OVERLAP_Y):
                pairs.append((a, b))
    # Word boxes left of the column can overlap a word reaching into it.
    far = [w for w in words if w[2] <= lo]
    for a in near:
        for b in far:
            if (min(a[2], b[2]) - max(a[0], b[0]) > OVERLAP_X
                    and min(a[3], b[3]) - max(a[1], b[1]) > OVERLAP_Y):
                pairs.append((b, a))
    return pairs


def full_width(line, left):
    """A line of a full-width block: a run starts left of the body's left
    edge and crosses it.  noweb's chunk labels (14b) also stand left of the
    edge, but end before it."""
    for run in runs(line):
        if run[0][0] >= left - FULLWIDTH_LEFT:
            return False
        if run[-1][2] > left:
            return True
    return False


def overprint_spots(pairs):
    """Overlapping pairs merged into spots: pairs whose boxes overlap
    vertically are one spot, reported once."""
    spots = []
    for a, b in sorted(pairs, key=lambda ab: min(ab[0][1], ab[1][1])):
        top = min(a[1], b[1])
        if spots and top < spots[-1][1]:
            spots[-1][0].append((a, b))
            spots[-1][1] = max(spots[-1][1], a[3], b[3])
        else:
            spots.append([[(a, b)], max(a[3], b[3])])
    return [pairs for pairs, _ in spots]


def overflows(words, lo, left):
    """C2: runs of a body line that end past the text block, OVER_PT or
    more into the gap before the margin column or into the column itself.

    A body line starts at the body's left edge or indented from it, left of
    the text block's middle; the right column of two programs side by side
    starts further right and is not a body line.  A line of a full-width
    block (didactic's definitions, examples and code set across the margin
    column) is not one either: the block starts left of the body's edge,
    and so does at least one line of the display it belongs to, so lines
    BLOCK_GAP or less apart are taken as one display and judged together.
    """
    right = lo - MARGINPARSEP
    middle = (left + right) / 2
    lines = [ln for ln in text_lines(words) if ln[0][0] < lo - RUN_GAP]
    displays, cur = [], []
    for line in lines:
        if cur and line[0][3] - cur[-1][0][3] > BLOCK_GAP:
            displays.append(cur)
            cur = []
        cur.append(line)
    if cur:
        displays.append(cur)
    out = []
    for display in displays:
        if any(full_width(ln, left) for ln in display):
            continue
        for line in display:
            if line[0][0] >= middle:
                continue
            for run in runs(line, lo):
                end = max(w[2] for w in run)
                if run[0][0] < lo - RUN_GAP and end > right + OVER_PT:
                    out.append((run, end))
    return out


def margin_check(log, pages):
    """C. lines that run into the margin column, from the word boxes and
    the column's left edge in the job's log."""
    cols = margin_columns(log)
    if cols is None:
        print(f"  (margin test skipped: no didactic-margin line in {log})")
        return 0
    lefts = body_left_edge(pages, cols)
    bad = 0
    for p, words in sorted(pages.items()):
        lo = cols[0] if p % 2 else cols[1]
        left = lefts[p % 2]
        for spot in overprint_spots(overprints(words, lo)):
            bad += 1
            ws = sorted({w for pair in spot for w in pair})
            top = min(w[1] for w in ws)
            bottom = max(w[3] for w in ws)
            text = " / ".join(w[4] for w in ws)
            print(f"  OVERPRINT p{p} y={top:.0f}..{bottom:.0f}: words print "
                  f"over each other at x={ws[0][0]:.1f}..{max(w[2] for w in ws):.1f}: "
                  f"{text[:90]!r}")
        if left is None:
            continue
        for run, end in overflows(words, lo, left):
            bad += 1
            text = " ".join(w[4] for w in run)
            print(f"  MARGIN p{p} y={run[0][3]:.0f}: runs to x={end:.1f}, "
                  f"past the text block (ends x={lo - MARGINPARSEP:.1f}): "
                  f"{text[-70:]!r}")
    return bad


def check(pdf, src):
    info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    if "Pages:" not in info:
        print(f"  cannot read {pdf}: build the deck first")
        return 1
    n = int(info.split("Pages:")[1].split()[0])
    pw = float(info.split("Page size:")[1].split()[0])
    bad = 0

    # A. prefix test, per page
    for p in range(1, n + 1):
        txt = subprocess.run(
            ["pdftotext", "-layout", "-f", str(p), "-l", str(p), pdf, "-"],
            capture_output=True, text=True).stdout
        raw = txt.splitlines()
        lines = [ln.strip() for ln in raw]
        for i, line in enumerate(lines):
            if len(line) < 25 or line in src:
                continue
            hits = [s for s in src if s.startswith(line) and s != line]
            # A line minted wrapped (breaklines) goes on in the next line,
            # behind a continuation mark: the joined text is still the
            # source line's prefix, so the line is not cut.
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            nexts = [nxt]
            # A margin-note line can sit between the wrapped line and its
            # continuation in pdftotext's layout, alone and indented to
            # the margin column: then the continuation is one line further.
            if (i + 2 < len(lines)
                    and indent(raw[i + 1]) - indent(raw[i]) > MARGIN_INDENT):
                nexts.append(lines[i + 2])
            if hits and nxt:
                # pdftotext gives the mark as "↪" or ",→"; try the next
                # line with and without it, since a line may begin with ",".
                # A margin note beside the continuation follows it on the
                # same layout line after a wide gap: try the part before.
                tails = {t for n in nexts
                         for b in (n, re.split(r"\s{3,}", n)[0])
                         for t in (b, re.sub(r"^[,↪→\s]+", "", b))}
                joined = [squash(line + t) for t in tails]
                hits = [s for s in hits
                        if not any(squash(s).startswith(j) for j in joined)]
            if hits:
                bad += 1
                print(f"  CUT   p{p}: {line!r}")
                print(f"         full: {hits[0]!r}")

    # B. bbox test, whole file
    out = subprocess.run(["pdftotext", "-bbox", pdf, "-"],
                         capture_output=True, text=True).stdout
    page = 0
    worst = {}
    for line in out.splitlines():
        if "<page" in line:
            page += 1
        m = re.search(r'xMax="([0-9.]+)"', line)
        if m:
            x = float(m.group(1))
            if x > pw - 2:
                w = re.search(r">([^<]*)</word>", line)
                if x > worst.get(page, (0, ""))[0]:
                    worst[page] = (x, w.group(1) if w else "")
    for p in sorted(worst):
        bad += 1
        print(f"  OVER  p{p}: xMax={worst[p][0]:.1f} > {pw} word={worst[p][1]!r}")

    # C. margin test, from the same word boxes and the job's log
    log = os.path.splitext(pdf)[0] + ".log"
    bad += margin_check(log, words_by_page(out))

    print(f"  {os.path.basename(pdf)}: {n} pages, {bad} problem(s)")
    return bad


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(2)
    deck = sys.argv[1].rstrip("/")
    jobs = sys.argv[2:] or ["slides", "notes"]
    src = sources(deck)
    total = 0
    for job in jobs:
        # A bilingual deck's -sv jobs build in ltxobj-sv (build_deck.sh's
        # OTHER_EDITIONS), with their log beside the PDF for detector C.
        out = "ltxobj-sv" if job.endswith("-sv") else "ltxobj"
        pdf = os.path.join(deck, out, job + ".pdf")
        print(f"== {pdf}")
        total += check(pdf, src)
    sys.exit(1 if total else 0)
