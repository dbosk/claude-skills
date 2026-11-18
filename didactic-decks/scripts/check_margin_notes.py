#!/usr/bin/env python3
"""Check that every margin footnote prints on the page carrying its marker.

didactic sets footnotes -- and, under the verbose citation style, every
\\autocite -- as margin notes.  A note printed on another page than its
marker is hard to find; with didactic v2.19 it happens only where the
package says so in the log, and anything else off its page is a defect.

The check runs `pdftotext -bbox-layout`, which gives every word a bounding
box and groups the words into lines, and compares, per page:

  * superscript markers in the body -- a digits-only word that abuts the
    word before it on its line and is raised above that word's baseline;
  * note numbers in the margin -- a digits-only word that opens a margin
    line and is raised above the note text that follows it;
  * note numbers at the foot -- a digits-only word that opens a body line,
    raised above the note's text that follows it, which is smaller than
    the page's body text.  didactic sets a footnote that doesn't fit the
    margin at the foot of its page, whole, in the text's width, and logs
    nothing: on the page of its marker that is a placed note.

Footnote numbering restarts per chapter, so a marker and a note are only
paired on the same or neighbouring pages, or on the pages a warning names.
A marker or note with no counterpart there is reported as a WARNING: the
check did not recognise the other half (a marker inside a table cell, or
split off by a line break, are the known cases) -- look at that page by eye.

Where the margin column is comes from the build: didactic writes one line
to the job's log,

    didactic-margin: odd=<bp> even=<bp> width=<bp>

the x of the column's left edge on odd and even pages and its width, in
PDF points.  The log is looked for beside the PDF and in ltxobj/ beside
it; --log names it, --margin-x overrides it.  Without that line (a PDF
copied away from its build, an older didactic) the column is guessed from
the word positions, and the output says so: the guess has failed on wide
code reaching into the gutter and on decks with few margin notes.

The rule (didactic v2.19, marginfix 1.7).  A note printed on another page
than its marker passes if and only if a didactic warning

    Margin note called out at <file:line> on page <P> is set on page <Q>...

names it; the check pairs the warning's P and Q (page counters, mapped to
PDF pages through the log's shipout markers) with a marker on P whose note
is on Q.  Every warning about notes is classed and printed:

  CARRIED     "... is set on page Q: <why>": placed by the rules and
              named, not a failure.  Shorten the note or move its callout
              so that it fits beside its line or at the foot.
  PAST FOOT   "... runs <d>pt past the foot of the margin": fine to ship.
              Shorten a note above it if the page looks crowded.
  LOOK        footnotes set out of sequence ("... before the one called
              out at X, which is still waiting in the margin"); a page
              TeX ended short before a footnote's line ("... page P is <n>
              lines short"); a footnote in multicols set at the foot of
              another page; callouts that couldn't be read; \\nofiles.
              Not failures: read the page, reword or move the text near
              the callout.
  UNFORESEEN  "... (found from the last run): nothing said so in that
              run": a placement didactic didn't foresee.  A failure:
              rebuild from clean; if it stays, report it with the log.
  LOST        "... wasn't printed (found from the last run)", "A footnote
              in ... multicols ... is lost", "A margin note in multicols
              is lost": the note is not in the PDF.  A failure: move it
              out of the multicols, or out of the note it is nested in.
  INSTALL     "Can't place margin notes that don't fit: ...", "Couldn't
              patch \\<name>, ...": didactic and marginfix or the kernel
              don't match.  A failure: install the two together.
  NOTICE      "<n> footnote(s) wasn't/weren't plain", and the rest
              (foot works as carry in two columns, side captions or noweb
              chunks not patched, a reused footnote that repeats, any
              unclassified didactic warning that mentions a note).

The log is read as TeX wrote it: TeX breaks a log line at 79 bytes
(pdfTeX, LuaTeX) or characters (XeTeX), wherever that falls, and a
package continues a message after \\MessageBreak on lines that start with
"(didactic)".  The check joins both before it matches, with the rules of
didactic's testlog.py (41ab439), copied here so that the check does not
depend on that file.

Logs from an older didactic (before 2.19; the log's "Package: didactic
<date> v<version>" line says which) were made under marginfix 1.6's rule,
and are judged by it, as when they were built, with the rule said in the
output: a note carried to the next page passes when the log has a matching
`marginfix-spill: page=P to=Q intended` or `... capped` line (CAPPED is
also listed), and every `... unresolved` spill fails; `marginfix-yield`
lines and marginfix's half-empty-page warning are NOTICEs.  A log with no
version line is judged by whichever records it carries.  Both rules come
to the same for a note off its page that nothing names: a DEFECT.

Exit status: 0 clean; 1 a note printed away from its marker that nothing
names, or a warning classed UNFORESEEN, LOST or INSTALL (or an unresolved
spill in an old log); 2 nothing was checked (no column found, no margin
note found), which is never a pass unless --no-margin-ok says the PDF
really has no margin notes.

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
# A running head is set off from the text block by more than a line: memoir
# puts \headsep (about two lines) between them.  1.5 times the usual line
# spacing tells that from an ordinary line without mistaking a paragraph's
# first line, which sits only a little further down.
HEAD_GAP_RATIO = 1.5

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
VERSION_RE = re.compile(r"^Package: didactic \S+ v(\d+(?:\.\d+)*)", re.M)
# The version from which the rule is didactic's warnings, not marginfix's
# spill records.
ONEPASS = (2, 19)
# pdfTeX logs "[<page counter>" as it ships out each page, so the n-th
# such marker gives the page counter of PDF page n.
SHIPOUT_RE = re.compile(r"(?:^|(?<=[\s\]]))\[(\d+)(?=[\]\s{<]|$)", re.M)

# didactic v2.19's warnings about notes, matched on the joined log, where
# each message is one line.  <P> and <Q> are page numbers as TeX prints
# them; a reason, when there is one, follows a colon.
WARN = r"^Package didactic Warning: "
# A page number ends at a space, a colon, a parenthesis, a comma or the
# message's full stop.
PAGE = r"[^\s:(),.]+"
# PackageWarning (not ...NoLine) ends its message with the input line.
INPUT_LINE_RE = re.compile(r"\s+on input line \d+\.?$")
LATE_MOVE_RE = re.compile(
    WARN + r"Margin note called out at (?P<place>\S+) on page (?P<p>" + PAGE
    + r") is set on page (?P<q>" + PAGE + r") \(found from the last run\)",
    re.M)
CARRIED_RE = re.compile(
    WARN + r"Margin note called out at (?P<place>\S+) on page (?P<p>" + PAGE
    + r") is set on page (?P<q>" + PAGE + r")(?! \(found)(?P<why>.*)$",
    re.M)
NOT_PRINTED_RE = re.compile(
    WARN + r"Margin note called out (?:at (?P<place>\S+) )?on page (?P<p>"
    + PAGE + r")(?: \(no place known\))? wasn't printed \(found from the "
    r"last run\)", re.M)
MCOL_FOOT_RE = re.compile(
    WARN + r"Footnote called out at (?P<place>\S+) in multicols on page "
    r"(?P<p>" + PAGE + r") is set at the foot of page (?P<q>" + PAGE + r")",
    re.M)
PAST_FOOT_RE = re.compile(
    WARN + r"Margin note called out at (?P<place>\S+) on page (?P<p>" + PAGE
    + r") runs (?P<d>[\d.]+)pt past the foot of the margin", re.M)
OUT_OF_ORDER_RE = re.compile(
    WARN + r"Footnote called out at (?P<place>\S+) is set at the foot of "
    r"page (?P<p>" + PAGE + r") before the one called out at (?P<x>\S+), "
    r"which is still waiting in the margin", re.M)
SHORT_PAGE_RE = re.compile(
    WARN + r"TeX ended page (?P<p>" + PAGE + r") before the line of the "
    r"footnote called out at (?P<place>\S+),.* is (?P<n>\d+) lines short",
    re.M)
LOST_RE = re.compile(
    WARN + r"(?:A footnote in (?:nested multicols|multicols in a margin "
    r"note or a footnote)|A margin note in multicols) is lost", re.M)
INSTALL_RE = re.compile(
    WARN + r"(?:Can't place margin notes that don't fit|Couldn't patch \\)",
    re.M)
NOT_PLAIN_RE = re.compile(
    WARN + r"\d+ footnotes? (?:wasn't|weren't) plain", re.M)
LOOK_RE = re.compile(
    WARN + r"(?:Can't read the callouts of page (?P<p>" + PAGE + r")|With "
    r"\\nofiles, a margin note)", re.M)
# Patches of other features than the notes' placement.
OTHER_PATCH_RE = re.compile(
    WARN + r"Can't patch (?:memoir's side captions|noweb's code chunks)",
    re.M)
# Any other didactic warning about notes is printed as a NOTICE, except a
# box's badness in a note, which is typesetting, not placement.
NOTE_WORD_RE = re.compile(r"\bnote|\bfootnote|noteoverflow", re.I)
BOX_RE = re.compile(r"^Package didactic Warning: (?:Under|Over)full \\[hv]box")

# (kind, pattern), tried in this order on each warning: the first that
# matches classes it.
CLASSES = [
    ("UNFORESEEN", LATE_MOVE_RE),
    ("LOST", NOT_PRINTED_RE),
    ("LOST", LOST_RE),
    ("INSTALL", INSTALL_RE),
    ("CARRIED", CARRIED_RE),
    ("PAST FOOT", PAST_FOOT_RE),
    ("LOOK", MCOL_FOOT_RE),
    ("LOOK", OUT_OF_ORDER_RE),
    ("LOOK", SHORT_PAGE_RE),
    ("LOOK", LOOK_RE),
    ("NOTICE", NOT_PLAIN_RE),
    ("NOTICE", OTHER_PATCH_RE),
]
FAILING = ("UNFORESEEN", "LOST", "INSTALL")
# What the author does about each kind, said once per kind in the output.
ADVICE = {
    "CARRIED": "shorten the note or move its callout, so that it fits "
               "beside its line or at the foot",
    "PAST FOOT": "fine to ship; shorten a note above it if the page looks "
                 "crowded",
    "LOOK": "read the page; reword or move the text near the callout",
    "UNFORESEEN": "a placement didactic didn't foresee: rebuild from "
                  "clean, and if it stays, report it with the log",
    "LOST": "the note is not in the PDF: move it out of the multicols, or "
            "out of the note it is nested in; under TeX Live's marginfix "
            "1.2, shorten a note taller than the margin",
    "INSTALL": "didactic does not match marginfix or the kernel: install "
               "the two together",
}

# Before didactic v2.19: marginfix 1.6's records of the notes it moved.
SPILL_RE = re.compile(
    r"marginfix-spill:\s*page=(\d+)\s+to=(\d+)\s+(intended|capped|unresolved)")
YIELD_RE = re.compile(r"marginfix-yield:\s*page=(\d+)\s+before=(\S+)")
FOOT_LOG_RE = re.compile(r"^marginfix-foot: page=(\d+) at=(\S+)", re.M)
# marginfix's warning for a page that ended early and is less than half
# full, its "(marginfix)" lines joined to it.
HALF_RE = re.compile(r"^Package marginfix Warning: Page \d+ ends early.*$",
                     re.M)

# TeX breaks a log line at max_print_line, 79.
LOG_WRAP = 79
# A package's message goes on after \MessageBreak on lines that start with
# its name in parentheses.
GOESON_RE = re.compile(rb"\n\((?:didactic|marginfix|hyperref)\) *")


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
    """The log's text with TeX's line breaks undone and each message's
    continuation lines joined to it, one message per line, or None when it
    cannot be read.  The joining follows didactic's testlog.py (lines()
    and joined(), at 41ab439), copied so as not to depend on it."""
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return None
    first = data.split(b"\n", 1)[0]
    if b"XeTeX" in first:
        # XeTeX counts characters, not bytes.
        text = data.decode("utf-8", errors="replace")
        text = re.sub(r"(?m)^(.{%d})\n" % LOG_WRAP, r"\1", text)
        data = text.encode("utf-8")
    else:
        lua = b"LuaTeX" in first or b"LuaHBTeX" in first
        out, last = [], None
        for line in data.split(b"\n"):
            if last is not None and broken(last, line, lua):
                out[-1] += line
            else:
                out.append(line)
            last = line
        data = b"\n".join(out)
    return GOESON_RE.sub(b" ", data).decode("utf-8", errors="replace")


def broken(line, after, lua):
    """Whether TeX broke the physical line `line`, followed by `after`
    (bytes).  A line of exactly 79 bytes is always a break.  LuaTeX moves
    a character of several bytes that would cross the 79th to the next
    line, so its line is then shorter."""
    if len(line) == LOG_WRAP:
        return True
    if lua and after and after[0] >= 0xC0:
        size = 2 if after[0] < 0xE0 else 3 if after[0] < 0xF0 else 4
        return len(line) < LOG_WRAP <= len(line) + size
    return False


def columns_from_log(text):
    """The last didactic-margin line in the log, or None."""
    found = MARGIN_LINE_RE.findall(text or "")
    if not found:
        return None
    odd, even, width = (float(v) for v in found[-1])
    return Columns(odd, even, width)


ROMAN = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}


def page_number(label):
    """The page counter of a page number as TeX prints it (arabic or
    roman), or None."""
    if label is None:
        return None
    if label.isdigit():
        return int(label)
    s = label.lower()
    if s and all(c in ROMAN for c in s):
        total = 0
        for c, d in zip(s, s[1:] + " "):
            v = ROMAN[c]
            total += -v if d in ROMAN and ROMAN[d] > v else v
        return total
    return None


class Event:
    """One classed warning: its kind, its words, and the pages it names
    (page counters; q is None when it names one page)."""

    def __init__(self, kind, text, p=None, q=None):
        self.kind, self.text, self.p, self.q = kind, text, p, q


def warning_text(line):
    """A warning's words without the package's prefix and the input line."""
    text = line[len("Package didactic Warning: "):]
    return INPUT_LINE_RE.sub("", text).rstrip(".")


class Log:
    """What the build log says about the notes, in PDF pages."""

    def __init__(self, text, npages):
        text = text or ""
        m = VERSION_RE.search(text)
        self.version = m.group(1) if m else None
        self.events = []
        for line in re.findall(r"^Package didactic Warning: .*$", text, re.M):
            for kind, rx in CLASSES:
                m = rx.match(line)
                if m:
                    groups = m.groupdict()
                    self.events.append(Event(
                        kind, warning_text(line),
                        page_number(groups.get("p")),
                        page_number(groups.get("q"))))
                    break
            else:
                if NOTE_WORD_RE.search(line) and not BOX_RE.match(line):
                    self.events.append(Event("NOTICE", warning_text(line)))
        self.spills = [(int(p), int(q), kind)
                       for p, q, kind in SPILL_RE.findall(text)]
        self.yields = [(int(p), at) for p, at in YIELD_RE.findall(text)]
        self.feet = [(int(p), at) for p, at in FOOT_LOG_RE.findall(text)]
        self.half_empty = HALF_RE.findall(text)
        labels = [int(n) for n in SHIPOUT_RE.findall(text)]
        self.mapped = len(labels) == npages
        self.labels = labels if self.mapped else list(range(1, npages + 1))

    def version_tuple(self):
        if self.version is None:
            return None
        return tuple(int(x) for x in self.version.split("."))

    def old_records(self):
        """Whether the log carries marginfix 1.6's records."""
        return bool(self.spills or self.yields or self.feet
                    or self.half_empty)

    def pdf_pages(self, page):
        return [n for n, lab in enumerate(self.labels, start=1)
                if lab == page]

    def pdf_page(self, page):
        """The first PDF page with this page counter, or the counter."""
        return (self.pdf_pages(page) or [page])[0]

    def pdf_pair(self, p, q):
        """The PDF pages (marker, note) of a note called out on page p and
        set on page q: of the PDF pages labelled q, the nearest to a page
        labelled p (a later one first)."""
        best = None
        for n in self.pdf_pages(p):
            for m, lab in enumerate(self.labels, start=1):
                if lab == q and m != n:
                    key = (abs(m - n), m < n)
                    if best is None or key < best[0]:
                        best = (key, (n, m))
        return best[1] if best else (p, q)

    def covers(self):
        """The (marker page, note page) pairs that a warning or a record
        accounts for: for each, one entry per note, saying what names it."""
        c = collections.defaultdict(list)
        for e in self.events:
            if e.q is not None and e.p is not None and e.kind in (
                    "CARRIED", "LOOK"):
                c[self.pdf_pair(e.p, e.q)].append(
                    f"a didactic warning ({e.kind})")
        for p, q, kind in self.spills:
            if kind in ("intended", "capped"):
                c[self.pdf_pair(p, q)].append(
                    f"a marginfix-spill {kind} record")
        return c

    def unresolved(self):
        return [self.pdf_pair(p, q) for p, q, kind in self.spills
                if kind == "unresolved"]

    def where(self, e):
        """The PDF pages an event names, as (n, m), m None for one page."""
        if e.p is None:
            return None, None
        if e.q is None:
            return self.pdf_page(e.p), None
        return self.pdf_pair(e.p, e.q)


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


def baseline(words):
    """A line's baseline: the median bottom edge of its words, so that a
    raised marker does not move it."""
    ys = sorted(w.y1 for w in words)
    return ys[len(ys) // 2]


def running_head(page_lines, col):
    """The page's running head, as the index of its line, or None.

    The head is the topmost body line, set off from the text below it by
    more than the page's usual line spacing, with the page number at one
    of its ends.  It must be recognised because a head long enough to fill
    the line, as an appendix's title can be, puts the page number right
    after the last word of the title, in a smaller face, and the number
    then looks exactly like a marker (memoir's head on an appendix page:
    \"... help coding agents? 48\" read as marker 48)."""
    body = [(i, [w for w in line if not in_margin(w, col)])
            for i, line in enumerate(page_lines)]
    body = sorted(((baseline(ws), i, ws) for i, ws in body if ws),
                  key=lambda b: b[0])
    if len(body) < 3:
        return None
    gaps = sorted(b[0] - a[0] for a, b in zip(body, body[1:])
                  if b[0] - a[0] > 0)
    if not gaps:
        return None
    spacing = gaps[len(gaps) // 2]
    (top_y, top_i, top_words), (next_y, _, _) = body[0], body[1]
    ends_in_number = (DIGITS_RE.match(top_words[-1].text)
                      or DIGITS_RE.match(top_words[0].text))
    if ends_in_number and next_y - top_y > spacing * HEAD_GAP_RATIO:
        return top_i
    return None


def body_text_height(page_lines, col):
    """The median height of the body's words on a page, or 0."""
    hs = sorted(w.y1 - w.y0 for line in page_lines for w in line
                if not in_margin(w, col))
    return hs[len(hs) // 2] if hs else 0.0


def markers_and_notes(page_lines, col, note_h):
    """Body markers, margin note numbers and foot note numbers on one page.

    poppler sometimes merges a body line and the margin line beside it
    into one <line>, so each line is cut at the margin's edges and the two
    parts are examined separately.  The running head is skipped, since its
    page number can look like a marker."""
    markers, notes, foot = set(), set(), set()
    head = running_head(page_lines, col)
    body_h = body_text_height(page_lines, col)
    for i, line in enumerate(page_lines):
        if i == head:
            continue
        body = [w for w in line if not in_margin(w, col)]
        margin = [w for w in line if in_margin(w, col)]

        if (len(body) >= 2 and DIGITS_RE.match(body[0].text)
                and body[1].x0 - body[0].x1 < NOTE_TEXT_GAP
                and body[1].y1 - body[0].y1 >= RAISE_MIN * MARGIN_RAISE_SCALE
                and body[0].y1 - body[0].y0
                    < (body[1].y1 - body[1].y0) * SIZE_RATIO
                and body[1].y1 - body[1].y0 < body_h * SIZE_RATIO):
            # A note at the foot: its number opens the line, raised above
            # the note's text, which is set smaller than the body.
            foot.add(int(body[0].text))
            body = body[1:]

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
    return markers, notes, foot


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
                    help="the build log holding the didactic-margin line "
                         "and didactic's warnings (default: beside the PDF, "
                         "or in ltxobj/)")
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
        markers, notes, foot = markers_and_notes(page_lines, cols.of(n),
                                                 note_h)
        per_page[n] = (markers, notes, foot)
        if args.verbose:
            print(f"page {n}: markers {sorted(markers)}, "
                  f"notes {sorted(notes)}, at the foot {sorted(foot)}")

    log_ = Log(text, len(pages))
    print(rule_of(log_, text is not None))
    if (log_.events or log_.old_records()) and not log_.mapped:
        print("NOTICE: the log's shipout markers do not match the PDF's "
              "pages; its page numbers are taken as PDF pages")

    def on_page(n, m=None):
        return args.page is None or args.page in (n, m)

    # What the log says, classed; the failing kinds are counted.  With
    # --page, a warning that names pages is shown only for that page.
    events = [e for e in log_.events
              if log_.where(e)[0] is None or on_page(*log_.where(e))]
    failing = []
    seen = set()
    for e in events:
        n, m = log_.where(e)
        pages_said = ""
        if n is not None:
            pages_said = (f" [PDF page {n}" + (f" to {m}" if m else "")
                          + "]")
        print(f"{e.kind}: {e.text}{pages_said}")
        if e.kind in ADVICE and e.kind not in seen:
            seen.add(e.kind)
            print(f"  -> {ADVICE[e.kind]}")
        if e.kind in FAILING:
            failing.append(e)
    for p, at in log_.yields:
        print(f"NOTICE: marginfix ended page {log_.pdf_page(p)} early, "
              f"before the note called out at {at} (page counter {p})")
    for w in log_.half_empty:
        print(f"NOTICE: {w} (page counter; not a failure)")

    covers = log_.covers()
    defects, warnings, named = [], [], []
    total_markers = total_notes = total_foot = 0
    empty = (set(), set(), set())
    accounted = set()

    def placed(m):
        """The note numbers set on PDF page m, in the margin or at the
        foot."""
        _, notes, foot = per_page.get(m, empty)
        return notes | foot

    for n, (markers, notes, foot) in sorted(per_page.items()):
        total_markers += len(markers)
        total_notes += len(notes)
        total_foot += len(foot)
        for k in sorted(markers - notes - foot):
            m = next((m for (pn, m), c in sorted(covers.items())
                      if pn == n and c and k in placed(m)), None)
            if m is not None:
                how = covers[(n, m)].pop(0)
                accounted.add((m, k))
                named.append(f"page {n}: marker {k} is here, its note on "
                             f"page {m}, named by {how}")
            elif k in placed(n + 1):
                accounted.add((n + 1, k))
                defects.append(f"page {n}: marker {k} is here, its note is "
                               f"on the next page, and nothing in the log "
                               f"names it")
            elif k in placed(n - 1):
                accounted.add((n - 1, k))
                defects.append(f"page {n}: marker {k} is here, its note is "
                               f"on the previous page, and nothing in the "
                               f"log names it")
            else:
                warnings.append(f"page {n}: marker {k} has no margin note "
                                f"here or beside it")
    logged_feet = collections.Counter()
    for p, _ in log_.feet:
        logged_feet[log_.pdf_page(p)] += 1
    for n, (markers, notes, foot) in sorted(per_page.items()):
        near_markers = (per_page.get(n - 1, empty)[0]
                        | per_page.get(n + 1, empty)[0])
        if len(foot) < logged_feet[n]:
            warnings.append(f"page {n}: marginfix set {logged_feet[n]} "
                            f"note(s) at the foot, {len(foot)} found there")
        for k in sorted((notes | foot) - markers):
            if (n, k) in accounted or k in near_markers:
                continue
            where = "at the foot" if k in foot else "in the margin"
            warnings.append(f"page {n}: note {k} {where} has no marker here "
                            f"or beside it")

    print(f"{total_markers} markers, {total_notes} margin notes and "
          f"{total_foot} notes at the foot found on {len(per_page)} pages")
    for w in warnings:
        print(f"WARNING: {w} --- read that page by eye")
    for c in named:
        print(f"NAMED: {c}")
    for d in defects:
        print(f"DEFECT: {d}")
    unresolved = [(n, m) for n, m in log_.unresolved() if on_page(n, m)]
    for n, m in unresolved:
        print(f"UNRESOLVED: marginfix could not fit the note marked on "
              f"page {n} and set it on page {m} (marginfix-spill "
              f"unresolved)")
    look = collections.Counter(e.kind for e in events
                               if e.kind in ("CARRIED", "PAST FOOT", "LOOK"))
    if look:
        print("to look at: " + ", ".join(f"{k} {look[k]}" for k in
                                         ("CARRIED", "PAST FOOT", "LOOK")
                                         if look[k]))
    if defects or unresolved or failing:
        print(f"FAIL: {len(defects)} notes print away from their marker "
              f"unnamed, {len(failing)} warnings of a failing kind "
              f"({', '.join(FAILING)})"
              + (f", {len(unresolved)} unresolved marginfix spills"
                 if unresolved else ""))
        return 1
    if total_notes + total_foot == 0 and args.page is None:
        # Markers with no note at all, or neither: the notes were lost
        # or the column is wrong.  Either way nothing was paired, so this
        # is not a pass.
        print(f"{verdict}: no numbered margin note found, nothing paired: the "
              "notes were lost, or the margin column is wrong; pass "
              "--no-margin-ok if this PDF really has none")
        return nothing
    print("every margin note prints on the page carrying its marker"
          + (", in the margin or at its foot" if total_foot else "")
          + (", or where the log names it" if named else ""))
    return 0


def rule_of(log_, have_log):
    """Which rule judges the notes off their page, as a line of output."""
    v = log_.version_tuple()
    if not have_log:
        return ("rule: no log found, so no warning can name a note: every "
                "note off its marker's page is a DEFECT")
    if v is not None and v >= ONEPASS:
        line = (f"rule: didactic v{log_.version}: a note off its marker's "
                "page passes only when a didactic warning names it")
        if log_.old_records():
            line += ("\nNOTICE: the log also has marginfix-spill, -yield or "
                     "-foot lines, from a marginfix older than this "
                     "didactic expects (install the two together); its "
                     "intended and capped spills are honoured, unresolved "
                     "ones fail")
        return line
    if v is not None:
        return (f"rule: didactic v{log_.version}, older than 2.19: judged "
                "as when it was built, by marginfix's records (a "
                "marginfix-spill intended or capped line names a carried "
                "note, an unresolved one fails); rebuild under v2.19 for "
                "the current rule")
    if log_.old_records():
        return ("rule: no didactic version in the log; it has marginfix "
                "1.6's records, so they judge it (intended and capped "
                "spills name a note, unresolved ones fail), with any "
                "didactic warnings")
    return ("rule: no didactic version in the log: a note off its "
            "marker's page passes only when a didactic warning names it")


if __name__ == "__main__":
    sys.exit(main())
