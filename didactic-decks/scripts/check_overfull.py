#!/usr/bin/env python3
"""List the overfull lines in a LaTeX log that are wider than a threshold.

TeX logs a line it could not break inside the measure as

    Overfull \\hbox (67.15994pt too wide) in paragraph at lines 864--864

followed by a dump of the line's contents and a blank line.  A few points
are invisible; tens of points are an inline code literal or a URL running
out of the text block, possibly over a margin note.  No other check sees
it: the margin-note check compares note and marker, not where the body
text ends.

For every such line wider than --pt (default 5) the check prints

  * the width;
  * where TeX was reading: the innermost file open in the log and the
    line range TeX gives (`in paragraph at lines a--b`, `in alignment at
    lines a--b`, `detected at line a`).  In a deck the file is usually
    the woven contents.tex, whose line numbers are not contents.nw's;
  * the start of the line as typeset, from the log's dump of the box
    (font switches and empty boxes dropped, the hyphens are TeX's
    possible break points): grep the .nw for a word of it;
  * the page: the PDF page being built when the warning is logged, i.e.
    one after the last shipout marker `[n`.  It is approximate: TeX logs
    the warning when it breaks the paragraph, and the paragraph can still
    end up on the next page.  When a paragraph begins in one file and
    ends in another (an \\input transcript), TeX gives a range like
    3197--1: the first number is the other file's.

TeX also typesets boxes that never reach the page: a frame marked
<presentation> is set and thrown away in the notes, and one with a wide
column gave a 335pt line that is nowhere in the PDF.  With --pdf the
check looks for the line's longest stretch of text between two boxes,
letters and digits only (so hyphens and line breaks do not matter), in
the PDF's text on that page and its neighbours; a line whose stretch is
not there is listed as "not in the PDF" and does not count.  A line with
too little text to tell (code, a table, a picture) is always counted.

Whether the box is a margin note the log does not say: it records neither
the width of the measure nor which box the paragraph went into.  The one
case it does name is a box built while the output routine runs (running
head or foot, or something the output routine typesets); that is printed
as "in the output routine".  When memoir logged its layout, the summary
gives marginparsep: a body line more than that too wide reaches into the
margin column, where the notes are.

The file names are read by following the parentheses TeX writes as it
opens and closes files, as log parsers do; a message with an unbalanced
parenthesis can throw it off, so treat the file as a strong hint.

Exit status: 0 nothing over the threshold (in the PDF); 1 at least one
line over it; 2 no log.
"""

import argparse
import re
import subprocess
import sys

OVERFULL_RE = re.compile(
    r"^Overfull \\hbox \(([\d.]+)pt too wide\) "
    r"(?:in paragraph at lines (\d+)--(\d+)"
    r"|in alignment at lines (\d+)--(\d+)"
    r"|detected at line (\d+)"
    r"|(has occurred while \\output is active))")
# A font switch in a box dump, "\\T1/pplj/b/n/10 ", and a nested box "[]"
# (inline code from minted, a picture, a footnote marker).
FONT_RE = re.compile(r"\\[^\s\\]+/[^\s\\]* ?")
BOX = "[]"
# Any box warning is followed by a dump of the box's contents up to
# a blank line; the dump holds the typeset text, parentheses and all.
DUMP_RE = re.compile(r"^(?:Over|Under)full \\[hv]box")
# pdfTeX logs "[<page counter>" as it ships out each page (as in
# check_margin_notes.py).
SHIPOUT_RE = re.compile(r"(?:^|(?<=[\s\]]))\[(\d+)(?=[\]\s{<]|$)")
# A parenthesis opening a file: "(./ltxobj/x.minted", "(contents.tex".
FILE_RE = re.compile(r"\(((?:\.{0,2}/)?[^\s()]*\.[A-Za-z][A-Za-z0-9]{0,7})"
                     r"(?=[\s()]|$)")
# memoir logs its layout; a body line more than marginparsep too wide
# reaches into the margin column.
SEP_RE = re.compile(r"^Marginparsep and marginparwidth: ([\d.]+)pt", re.M)
# What is kept of a text when comparing a dump with the PDF.
NOT_ALNUM_RE = re.compile(r"[\W_]+")
# The shortest stretch (letters and digits) that can tell a line is not
# in the PDF: shorter ones match by chance.
MIN_STRETCH = 20
# TeX breaks log lines at max_print_line characters.
LOG_LINE_MAX = 79


def logical_lines(raw):
    """Join the lines TeX broke at max_print_line back together.  A line
    that happened to fill max_print_line exactly is not joined to a box
    warning: TeX starts those on a line of their own."""
    out, buf = [], ""
    for line in raw.split("\n"):
        if buf and DUMP_RE.match(line):
            out.append(buf)
            buf = ""
        buf += line
        if len(line) != LOG_LINE_MAX:
            out.append(buf)
            buf = ""
    if buf:
        out.append(buf)
    return out


def track_parens(line, stack):
    """Push a file (or None) at every '(', pop at every ')'."""
    i = 0
    while i < len(line):
        c = line[i]
        if c == "(":
            m = FILE_RE.match(line, i)
            if m:
                stack.append(m.group(1))
                i = m.end()
                continue
            stack.append(None)
        elif c == ")" and stack:
            stack.pop()
        i += 1


def typeset_text(dump):
    """The text of a box dump, without font switches; the nested boxes
    are kept as "[]"."""
    return " ".join(FONT_RE.sub("", " ".join(dump)).split())


def alnum(text):
    return NOT_ALNUM_RE.sub("", text)


def scan(text):
    """Yield (width, file, first, last, how, pdf_page, counter, text) per
    overfull \\hbox in the log."""
    stack, shipped, counter, in_dump = [], 0, None, False
    hit, dump = None, []
    for line in logical_lines(text):
        if in_dump:
            if line.strip():
                dump.append(line)
                continue
            in_dump = False
            if hit:
                yield hit + (typeset_text(dump),)
            hit, dump = None, []
            continue
        m = OVERFULL_RE.match(line)
        if m:
            width = float(m.group(1))
            if m.group(2):
                first, last, how = int(m.group(2)), int(m.group(3)), "par"
            elif m.group(4):
                first, last, how = int(m.group(4)), int(m.group(5)), "align"
            elif m.group(6):
                first = last = int(m.group(6))
                how = "hbox"
            else:
                first = last = None
                how = "output"
            current = next((f for f in reversed(stack) if f), None)
            hit = (width, current, first, last, how, shipped + 1,
                   None if counter is None else counter + 1)
            in_dump = True
            continue
        if DUMP_RE.match(line):
            in_dump = True
            continue
        for n in SHIPOUT_RE.findall(line):
            shipped += 1
            counter = int(n)
        track_parens(line, stack)
    if hit:
        yield hit + (typeset_text(dump),)


def pdf_text(pdf, page, cache={}):
    """The letters and digits on PDF pages page-1..page+1, or None
    without pdftotext."""
    if page not in cache:
        try:
            out = subprocess.run(
                ["pdftotext", "-f", str(max(page - 1, 1)),
                 "-l", str(page + 1), pdf, "-"],
                capture_output=True, text=True, check=True).stdout
        except (OSError, subprocess.CalledProcessError):
            cache[page] = None
        else:
            cache[page] = alnum(out)
    return cache[page]


def in_pdf(pdf, page, typeset):
    """False when the line's longest stretch of text is not on the page or
    its neighbours, True when it is, None when it cannot tell."""
    stretch = max((alnum(t) for t in typeset.split(BOX)), key=len)
    if not pdf or len(stretch) < MIN_STRETCH:
        return None
    text = pdf_text(pdf, page)
    if text is None:
        return None
    return stretch in text


def main():
    ap = argparse.ArgumentParser(
        description="List overfull \\hbox lines wider than a threshold.")
    ap.add_argument("log", help="the LaTeX log, e.g. ltxobj/notes.log")
    ap.add_argument("--pt", type=float, default=5.0,
                    help="threshold in points (default 5)")
    ap.add_argument("--pdf",
                    help="the PDF the log belongs to: a line whose words "
                         "are not in it is listed, not counted")
    args = ap.parse_args()

    try:
        with open(args.log, encoding="latin-1") as f:
            text = f.read()
    except OSError as e:
        print(f"check_overfull.py: {e}", file=sys.stderr)
        return 2

    found = total = absent = 0
    for width, name, first, last, how, page, counter, typeset in scan(text):
        total += 1
        if width <= args.pt:
            continue
        shown = in_pdf(args.pdf, page, typeset) is not False
        if shown:
            found += 1
        else:
            absent += 1
        if how == "output":
            where = "in the output routine"
        else:
            lines = str(first) if first == last else f"{first}--{last}"
            if last < first:
                lines += ", begun in another file"
            what = {"par": "paragraph", "align": "alignment",
                    "hbox": "\\hbox"}[how]
            where = f"{name or '?'}:{lines} ({what})"
        pg = f"page ~{page}"
        if counter is not None and counter != page:
            pg += f" (page counter {counter})"
        print(f"{width:.1f}pt too wide, {pg}, {where}"
              + ("" if shown else ", not in the PDF (not counted)"))
        typeset = " ".join(typeset.replace(BOX, " ").split())
        if typeset:
            # The overflow is at the end of the line: keep both ends.
            if len(typeset) > 72:
                typeset = typeset[:30] + " ... " + typeset[-37:]
            print(f"    {typeset}")
    print(f"{found} of {total} overfull \\hbox wider than {args.pt:g}pt"
          + (f" ({absent} more not in the PDF)" if absent else ""))
    sep = SEP_RE.search(text)
    if found and sep:
        print(f"(marginparsep is {float(sep.group(1)):g}pt: a body line more "
              "than that too wide reaches into the margin column)")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
