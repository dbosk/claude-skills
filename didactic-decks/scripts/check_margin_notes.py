#!/usr/bin/env python3
"""Check that every margin footnote prints on the page carrying its marker.

didactic sets footnotes -- and, under the verbose citation style, every
\\autocite -- as margin notes.  When the margin is at capacity the note is
pushed to the next page, away from the superscript marker that refers to
it.  That is a layout defect (fix it with a shorter note, the citation
moved earlier, or the prose moved or reworded; never a page break), and
it is invisible in the LaTeX log.

The check runs `pdftotext -bbox-layout`, which gives every word a bounding
box and groups the words into lines, and compares, per page:

  * superscript markers in the body -- a digits-only word that abuts the
    word before it on its line and is raised above that word's baseline;
  * note numbers in the margin -- a digits-only word that opens a margin
    line and is raised above the note text that follows it.

The defect is a number that is a marker on one page and a note on the page
beside it, but not a note on its own page: the note printed away from its
marker.  Footnote numbering restarts per chapter, so the pairing is only
made between neighbouring pages.  A marker or note with no counterpart on
its own page or either neighbour is reported as a warning: the check did
not recognise the other half (a marker inside a table cell, or split off
by a line break, are the known cases) -- look at that page by eye.

Where the margin column is comes from the build: didactic writes one line
to the job's log,

    didactic-margin: odd=<bp> even=<bp> width=<bp>

the x of the column's left edge on odd and even pages and its width, in
PDF points.  The log is looked for beside the PDF and in ltxobj/ beside
it; --log names it, --margin-x overrides it.  Without that line (a PDF
copied away from its build, an older didactic) the column is guessed from
the word positions, and the output says so: the guess has failed on wide
code reaching into the gutter and on decks with few margin notes.

marginfix (1.6 on) logs what it did with the notes that did not fit:

    marginfix-spill: page=<p> to=<q> intended     carried on purpose
    marginfix-spill: page=<p> to=<q> capped       carried, since ending
                                                  page p early would leave
                                                  more empty than the limit
                                                  (didactic noteyieldmaxgap)
    marginfix-spill: page=<p> to=<q> unresolved   should have fitted
    marginfix-yield: page=<p> before=<file>:<line>  page ended early

A note on the page after its marker is INTENDED, not a defect, when the
log has a matching intended spill, and CAPPED, not a defect either, when
it has a matching capped spill; the capped spills are also listed as
notices, since the note is away from its marker (look at the page: is it
still easy to find?).  Every unresolved spill is a failure, whether or
not the pairing found it.  The yields, and marginfix's warning
when such a page is less than half full, are printed as notices.  The
page numbers in the log are the page counter's, mapped to PDF pages
through the log's shipout markers.

Exit status: 0 clean; 1 a note printed away from its marker, or an
unresolved spill; 2 nothing was checked (no column found, no margin note
found), which is never a pass unless --no-margin-ok says the PDF really
has no margin notes.

Usage:
    check_margin_notes.py NOTES.pdf [--log FILE | --margin-x BP]
                          [--page N] [--verbose] [--no-margin-ok]

Requires pdftotext (poppler-utils).
"""

import argparse
import collections
import html
import os
import re
import shutil
import subprocess
import sys

# A word abutting the previous one: LaTeX puts no space before a footnote
# marker, while ordinary interword space in a 10pt text is around 3pt.
ABUT_GAP = 1.5
# How far above the neighbouring word's bottom edge a superscript sits.
# Measured in a 10pt memoir deck: 6.4pt above a word with a descender,
# 3.6pt above a word of digits (which has none).  A digit set on the
# baseline of its neighbour clears it by 0.
RAISE_MIN = 2.5
# A superscript is also set smaller than the word it follows.  Both tests
# are needed: the raise alone would accept a digit that abuts a word with
# a deep descender, the size alone would accept a baseline digit next to a
# word of digits.
SIZE_RATIO = 0.95
# The margin is set smaller than the body, so its superscripts clear the
# baseline by proportionally less.
MARGIN_RAISE_SCALE = 0.8
# Hanging indent between a margin note's number and its text.
NOTE_TEXT_GAP = 20.0
# A margin word may start a hair left of the edge didactic reports
# (rounding, a glyph's side bearing).
EDGE_SLACK = 1.0
# A note number set alone on a margin line is recognised by its size:
# clearly smaller than the margin's own text.
NOTE_SIZE_RATIO = 0.7

# The rest of the constants serve only the guess made without the log
# line.  The gutter between the body and the margin is narrow in this
# layout: 4pt in some decks, because margin material starts almost at the
# body's right edge.  A candidate narrower than this is noise.
MIN_GUTTER = 3.0
# An x position held by this few words is a stray, not an edge: a code
# line reaching across the gutter, a marker at the end of a line.  Three
# such words filled the 4pt gutter of a whole deck (2026-10-22).
STRAY_MAX = 2
# A real margin column holds at least this many words.  A count, not a
# share: a tutorial with few notes has well under 1% of its words there.
MIN_MARGIN_WORDS = 20
# The margin is set flush left, so its left edge is the commonest x
# position just beyond the gutter: held by at least MIN_EDGE_WORDS words
# and within MAX_EDGE_DIST of the gap.  A gap with no such edge beside it
# lies inside the body or a figure (one at x=309 passed a deck with
# nothing checked, 2026-09-29).
MIN_EDGE_WORDS = 10
MAX_EDGE_DIST = 6.0

WORD_RE = re.compile(
    r'<word\s+xMin="([\d.]+)"\s+yMin="([\d.]+)"\s+'
    r'xMax="([\d.]+)"\s+yMax="([\d.]+)"\s*>(.*?)</word>',
    re.DOTALL,
)
LINE_RE = re.compile(r"<line\b.*?</line>", re.DOTALL)
PAGE_RE = re.compile(r'<page\s+width="([\d.]+)"\s+height="([\d.]+)"\s*>')
DIGITS_RE = re.compile(r"^\d{1,3}$")
# Several citations at one point print as one comma-separated marker,
# "18,19,20,21", which pdftotext hands over as a single word.
MARKER_RE = re.compile(r"^\d{1,3}(?:,\d{1,3})*$")
NUM = r"(\d+(?:\.\d+)?)(?:bp|pt)?"
MARGIN_LINE_RE = re.compile(
    r"didactic-margin:\s*odd=" + NUM + r"\s+even=" + NUM
    + r"\s+width=" + NUM)
SPILL_RE = re.compile(
    r"marginfix-spill:\s*page=(\d+)\s+to=(\d+)\s+(intended|capped|unresolved)")
YIELD_RE = re.compile(r"marginfix-yield:\s*page=(\d+)\s+before=(\S+)")
# marginfix's warning for a page that ended early and is less than half
# full: its first line and the "(marginfix)" lines continuing it.
HALF_RE = re.compile(
    r"^Package marginfix Warning: Page \d+ ends early.*?"
    r"(?:\n\(marginfix\).*?)*$", re.M)
# pdfTeX logs "[<page counter>" as it ships out each page, so the n-th
# such marker gives the page counter of PDF page n.
SHIPOUT_RE = re.compile(r"(?:^|(?<=[\s\]]))\[(\d+)(?=[\]\s{<]|$)", re.M)
# TeX breaks log lines at max_print_line characters.
LOG_LINE_MAX = 79


class Word:
    __slots__ = ("x0", "y0", "x1", "y1", "text")

    def __init__(self, x0, y0, x1, y1, text):
        self.x0, self.y0, self.x1, self.y1, self.text = x0, y0, x1, y1, text


class Columns:
    """The margin column of each page: [lo, hi) in x, by page parity."""

    def __init__(self, odd, even, width=float("inf")):
        self.odd, self.even, self.width = odd, even, width

    def of(self, page_no):
        lo = self.odd if page_no % 2 else self.even
        return lo - EDGE_SLACK, lo + self.width

    def describe(self):
        if self.odd == self.even:
            return f"x={self.odd:.1f}bp"
        return f"x={self.odd:.1f}bp (odd pages), {self.even:.1f}bp (even)"


def in_margin(w, col):
    return col[0] <= w.x0 < col[1]


def run_pdftotext(pdf):
    if shutil.which("pdftotext") is None:
        sys.exit("check_margin_notes.py: pdftotext not found "
                 "(install poppler-utils)")
    try:
        return subprocess.run(
            ["pdftotext", "-bbox-layout", pdf, "-"],
            check=True, capture_output=True, text=True, errors="replace",
        ).stdout
    except subprocess.CalledProcessError as exc:
        sys.exit(f"check_margin_notes.py: pdftotext failed on {pdf}: "
                 f"{exc.stderr.strip()}")


def words_of(fragment):
    return [
        Word(float(m.group(1)), float(m.group(2)), float(m.group(3)),
             float(m.group(4)), html.unescape(m.group(5)).strip())
        for m in WORD_RE.finditer(fragment)
    ]


def parse_pages(xhtml):
    """Return one (width, [line]) per page, each line a list of Words in
    reading order.  poppler does the line grouping, which matters: a
    superscript's bottom edge is well above its line's, so grouping by
    coordinate alone would separate a marker from the word it follows."""
    pages = []
    starts = [(m.start(), m) for m in PAGE_RE.finditer(xhtml)]
    for i, (pos, m) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(xhtml)
        page_lines = [words_of(lm.group(0))
                      for lm in LINE_RE.finditer(xhtml, pos, end)]
        pages.append((float(m.group(1)),
                      [line for line in page_lines if line]))
    return pages


def default_logs(pdf):
    """notes.pdf is built in ltxobj/ and copied up beside the sources, so
    its log is beside it or in ltxobj/ beside it."""
    stem = os.path.splitext(os.path.basename(pdf))[0] + ".log"
    here = os.path.dirname(os.path.abspath(pdf))
    return [os.path.join(here, stem), os.path.join(here, "ltxobj", stem)]


def read_log(path):
    """The log's text with TeX's line breaks at LOG_LINE_MAX undone, or
    None when it cannot be read."""
    try:
        with open(path, encoding="latin-1") as f:
            raw = f.read().split("\n")
    except OSError:
        return None
    lines, buf = [], ""
    for line in raw:
        buf += line
        if len(line) != LOG_LINE_MAX:
            lines.append(buf)
            buf = ""
    if buf:
        lines.append(buf)
    return "\n".join(lines)


def columns_from_log(text):
    """The last didactic-margin line in the log, or None."""
    found = MARGIN_LINE_RE.findall(text or "")
    if not found:
        return None
    odd, even, width = (float(v) for v in found[-1])
    return Columns(odd, even, width)


class Marginfix:
    """What marginfix logged about the notes it moved, in PDF pages."""

    def __init__(self, text, npages):
        text = text or ""
        self.spills = [(int(p), int(q), kind)
                       for p, q, kind in SPILL_RE.findall(text)]
        self.yields = [(int(p), at) for p, at in YIELD_RE.findall(text)]
        self.half_empty = [
            " ".join(part.strip() for part in
                     re.sub(r"\(marginfix\)", "", m.group(0)).split("\n"))
            for m in HALF_RE.finditer(text)]
        labels = [int(n) for n in SHIPOUT_RE.findall(text)]
        self.mapped = len(labels) == npages
        self.labels = labels if self.mapped else list(range(1, npages + 1))

    def any(self):
        return bool(self.spills or self.yields or self.half_empty)

    def pdf_pages(self, page):
        return [n for n, lab in enumerate(self.labels, start=1)
                if lab == page]

    def pdf_pair(self, p, q):
        """The PDF pages (marker, note) of a spill from page p to q: the
        first page labelled q after a page labelled p."""
        for n in self.pdf_pages(p):
            for m in range(n + 1, len(self.labels) + 1):
                if self.labels[m - 1] == q:
                    return n, m
        return p, q

    def intended(self):
        return collections.Counter(self.pdf_pair(p, q)
                                   for p, q, kind in self.spills
                                   if kind == "intended")

    def capped(self):
        return collections.Counter(self.pdf_pair(p, q)
                                   for p, q, kind in self.spills
                                   if kind == "capped")

    def unresolved(self):
        return [self.pdf_pair(p, q) for p, q, kind in self.spills
                if kind == "unresolved"]


def guess_columns(pages):
    """Guess the margin's left edge from the word positions: the widest
    horizontal gap in the right half of the page, ignoring stray words,
    that has a substantial flush-left column just beyond it.  The body is
    justified, so its words' left edges are dense right up to the gutter,
    and the gutter shows as the gap."""
    if not pages:
        return None
    width = pages[0][0]
    all_x = [w.x0 for _, page_lines in pages for line in page_lines
             for w in line]
    if not all_x:
        return None
    held = collections.Counter(round(x, 1) for x in all_x if x > width / 2)
    xs = sorted(x for x, n in held.items() if n > STRAY_MAX)
    # The edge is counted in words of text only: noweb's chunk numbers
    # (h=4.9) line up at one x inside the body and posed as the edge of a
    # deck with almost no margin text.
    text_x = collections.Counter(
        round(w.x0, 1) for _, page_lines in pages for line in page_lines
        for w in line if w.x0 > width / 2 and not DIGITS_RE.match(w.text))
    candidates = sorted(((b - a, (a + b) / 2) for a, b in zip(xs, xs[1:])
                         if b - a >= MIN_GUTTER), reverse=True)
    for _, at in candidates:
        if sum(1 for x in all_x if x >= at) < MIN_MARGIN_WORDS:
            continue
        near = [(n, x) for x, n in text_x.items()
                if at <= x <= at + MAX_EDGE_DIST]
        if not near:
            continue
        n, edge = max(near)
        beyond = [m for x, m in text_x.items() if x >= at]
        if n >= MIN_EDGE_WORDS and n == max(beyond):
            return Columns(edge, edge)
    return None


def margin_text_height(pages, cols):
    """Median height of ordinary margin words, used to tell a note number
    set alone on its line from a number inside a note's text."""
    hs = sorted(w.y1 - w.y0
                for n, (_, page_lines) in enumerate(pages, start=1)
                for line in page_lines for w in line
                if in_margin(w, cols.of(n)) and not DIGITS_RE.match(w.text))
    return hs[len(hs) // 2] if hs else 0.0


def markers_and_notes(page_lines, col, note_h):
    """Body markers and margin note numbers on one page.

    poppler sometimes merges a body line and the margin line beside it
    into one <line>, so each line is cut at the margin's edges and the two
    parts are examined separately."""
    markers, notes = set(), set()
    for line in page_lines:
        body = [w for w in line if not in_margin(w, col)]
        margin = [w for w in line if in_margin(w, col)]

        for prev, w in zip(body, body[1:]):
            if (MARKER_RE.match(w.text)
                    and w.x0 - prev.x1 < ABUT_GAP
                    and prev.y1 - w.y1 >= RAISE_MIN
                    and w.y1 - w.y0 < (prev.y1 - prev.y0) * SIZE_RATIO):
                markers.update(int(n) for n in w.text.split(","))

        if not margin or not DIGITS_RE.match(margin[0].text):
            continue
        first = margin[0]
        if len(margin) >= 2:
            # Number and the note's first words on one line, set off by
            # the hanging indent.
            second = margin[1]
            if (second.x0 - first.x1 < NOTE_TEXT_GAP
                    and second.y1 - first.y1 >= RAISE_MIN * MARGIN_RAISE_SCALE
                    and first.y1 - first.y0
                        < (second.y1 - second.y0) * SIZE_RATIO):
                notes.add(int(first.text))
        elif first.y1 - first.y0 < note_h * NOTE_SIZE_RATIO:
            # The number alone on its line, with the note's text below it.
            notes.add(int(first.text))
    return markers, notes


def find_log(args):
    """The build log's path and text: --log, else the first log found
    beside the PDF.  (None, None) when there is none."""
    for log in [args.log] if args.log else default_logs(args.pdf):
        text = read_log(log)
        if text is not None:
            return log, text
    return None, None


def find_columns(args, log, text):
    """The margin column and a sentence saying where it came from."""
    if args.margin_x is not None:
        return (Columns(args.margin_x, args.margin_x),
                "from --margin-x")
    cols = columns_from_log(text)
    if cols is not None:
        source = f"from the didactic-margin line in {log}"
        try:
            if os.path.getmtime(log) < os.path.getmtime(args.pdf) - 600:
                source += (" (WARNING: the log is older than the PDF; "
                           "it may belong to another build)")
        except OSError:
            pass
        return cols, source
    where = log or " or ".join(default_logs(args.pdf))
    return None, (f"no didactic-margin line in {where} --- GUESSED from "
                  "the word positions; pass --log or --margin-x to make "
                  "it exact")


def main():
    ap = argparse.ArgumentParser(
        description="Check that margin footnotes print on the page that "
                    "carries their marker.")
    ap.add_argument("pdf", help="the notes PDF")
    ap.add_argument("--log", default=None,
                    help="the build log holding the didactic-margin and "
                         "marginfix lines (default: beside the PDF, or in "
                         "ltxobj/)")
    ap.add_argument("--margin-x", type=float, default=None,
                    help="x of the margin column's left edge in PDF points, "
                         "on every page (overrides the log)")
    ap.add_argument("--page", type=int, default=None,
                    help="check only this page (1-based)")
    ap.add_argument("--verbose", action="store_true",
                    help="report every page, not just the defective ones")
    ap.add_argument("--no-margin-ok", action="store_true",
                    help="exit 0 when no margin column or no margin note is "
                         "found (only for a PDF that really has none)")
    args = ap.parse_args()
    nothing = 0 if args.no_margin_ok else 2
    verdict = "accepted (--no-margin-ok)" if args.no_margin_ok else "FAIL"

    pages = parse_pages(run_pdftotext(args.pdf))
    if not pages:
        sys.exit(f"check_margin_notes.py: no pages parsed from {args.pdf}")

    log, text = find_log(args)
    cols, source = find_columns(args, log, text)
    if cols is None:
        print(source)
        cols = guess_columns(pages)
        source = "GUESSED"
    if cols is None:
        # A notes PDF always has margin notes, so failing to find the
        # column means the guess failed, not that the PDF is clean:
        # never pass silently.
        print(f"{verdict}: no margin column detected, nothing checked: either "
              "this PDF has no margin notes, or the guess failed; give "
              "the column with --log or --margin-x, or pass --no-margin-ok "
              "if it really has none")
        return nothing

    note_h = margin_text_height(pages, cols)
    print(f"{args.pdf}: {len(pages)} pages, margin column at "
          f"{cols.describe()} ({source}), "
          f"margin text {note_h:.1f}pt tall")

    per_page = {}
    for n, (_, page_lines) in enumerate(pages, start=1):
        if args.page is not None and n != args.page:
            continue
        markers, notes = markers_and_notes(page_lines, cols.of(n), note_h)
        per_page[n] = (markers, notes)
        if args.verbose:
            print(f"page {n}: markers {sorted(markers)}, "
                  f"notes {sorted(notes)}")

    mfx = Marginfix(text, len(pages))
    if mfx.any() and not mfx.mapped:
        print("NOTICE: the log's shipout markers do not match the PDF's "
              "pages; marginfix's page numbers are taken as PDF pages")
    for p, at in mfx.yields:
        where = ", ".join(str(n) for n in mfx.pdf_pages(p)) or "?"
        if where != str(p):
            where += f" (page counter {p})"
        print(f"NOTICE: marginfix ended page {where} early, before the "
              f"note called out at {at}")
    for w in mfx.half_empty:
        print(f"NOTICE: {w} (page counter; not a failure)")
    intended = mfx.intended()
    capped = mfx.capped()
    for (n, m), k in sorted(capped.items()):
        if args.page is None or args.page in (n, m):
            print(f"NOTICE: marginfix carried {k} note(s) marked on page "
                  f"{n} to page {m} instead of ending page {n} early "
                  f"(marginfix-spill capped; not a failure)")

    defects, warnings, carried = [], [], []
    total_markers = total_notes = 0
    empty = (set(), set())
    for n, (markers, notes) in sorted(per_page.items()):
        total_markers += len(markers)
        total_notes += len(notes)
        near_markers = (per_page.get(n - 1, empty)[0]
                        | per_page.get(n + 1, empty)[0])
        for k in sorted(markers - notes):
            if k in per_page.get(n + 1, empty)[1]:
                if intended[(n, n + 1)] > 0:
                    intended[(n, n + 1)] -= 1
                    carried.append(("INTENDED",
                                    f"page {n}: marker {k} is here, its "
                                    f"note carried to page {n + 1} on "
                                    f"purpose (marginfix-spill intended)"))
                elif capped[(n, n + 1)] > 0:
                    capped[(n, n + 1)] -= 1
                    carried.append(("CAPPED",
                                    f"page {n}: marker {k} is here, its "
                                    f"note carried to page {n + 1} "
                                    f"(marginfix-spill capped)"))
                else:
                    defects.append(f"page {n}: marker {k} is here, its "
                                   f"margin note is on the next page")
            elif k in per_page.get(n - 1, empty)[1]:
                defects.append(f"page {n}: marker {k} is here, its margin "
                               f"note is on the previous page")
            else:
                warnings.append(f"page {n}: marker {k} has no margin note "
                                f"here or beside it")
        for k in sorted(notes - markers):
            if k not in near_markers:
                warnings.append(f"page {n}: margin note {k} has no marker "
                                f"here or beside it")

    print(f"{total_markers} markers and {total_notes} margin notes found "
          f"on {len(per_page)} pages")
    for w in warnings:
        print(f"WARNING: {w} --- read that page by eye")
    for label, c in carried:
        print(f"{label}: {c}")
    for d in defects:
        print(f"DEFECT: {d}")
    unresolved = [(n, m) for n, m in mfx.unresolved()
                  if args.page is None or args.page in (n, m)]
    for n, m in unresolved:
        print(f"UNRESOLVED: marginfix could not fit the note marked on "
              f"page {n} and set it on page {m} (marginfix-spill "
              f"unresolved)")
    if defects or unresolved:
        print(f"FAIL: {len(defects)} margin notes print away from their "
              f"marker, {len(unresolved)} unresolved marginfix spills")
        return 1
    if total_notes == 0 and args.page is None:
        # Markers with no note at all, or neither: the notes were lost
        # (marginfix) or the column is wrong.  Either way nothing was
        # paired, so this is not a pass.
        print(f"{verdict}: no numbered margin note found, nothing paired: the "
              "notes were lost, or the margin column is wrong; pass "
              "--no-margin-ok if this PDF really has none")
        return nothing
    print("every margin note prints on the page carrying its marker")
    return 0


if __name__ == "__main__":
    sys.exit(main())
