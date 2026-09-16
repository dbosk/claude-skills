#!/usr/bin/env python3
"""Find verbatim lines that are clipped at the right edge of a page.

Two detectors, because either alone misses cases:

  A. prefix test -- a line pdftotext extracts from page N is a strict
     prefix of a line in the deck's tangled programs or PythonTeX
     transcripts.  Catches text clipped clean off the page, which the
     bbox test cannot see (the clipped word never reaches pdftotext).
  B. bbox test -- a word's xMax exceeds the page width.  Catches a line
     that hangs over the edge and is only partly drawn.

Usage: cutcheck.py <deck-dir> [notes|slides ...]
"""
import glob
import os
import re
import subprocess
import sys


def sources(deck):
    out = set()
    pats = [os.path.join(deck, "examples", "*.py"),
            os.path.join(deck, "didactic_output_*.txt")]
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


def check(pdf, src):
    info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    n = int(info.split("Pages:")[1].split()[0])
    pw = float(info.split("Page size:")[1].split()[0])
    bad = 0

    # A. prefix test, per page
    for p in range(1, n + 1):
        txt = subprocess.run(
            ["pdftotext", "-layout", "-f", str(p), "-l", str(p), pdf, "-"],
            capture_output=True, text=True).stdout
        for line in txt.splitlines():
            line = line.strip()
            if len(line) < 25 or line in src:
                continue
            hits = [s for s in src if s.startswith(line) and s != line]
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

    print(f"  {os.path.basename(pdf)}: {n} pages, {bad} problem(s)")
    return bad


if __name__ == "__main__":
    deck = sys.argv[1].rstrip("/")
    jobs = sys.argv[2:] or ["slides", "notes"]
    src = sources(deck)
    total = 0
    for job in jobs:
        pdf = os.path.join(deck, "ltxobj", job + ".pdf")
        print(f"== {pdf}")
        total += check(pdf, src)
    sys.exit(1 if total else 0)
