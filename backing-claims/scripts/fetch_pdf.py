#!/usr/bin/env python3
"""
Fetch full texts into scholar's PDF cache without opening a viewer.

`scholar pdf open <url>` downloads into the cache and then launches the
system PDF viewer (xdg-open), which is useless in an agent session and
pops windows on the user's desktop.  This script uses the same cache
(`scholar pdf path`, keyed by SHA-256 of the URL) through scholar's own
`get_pdf`, so a later session that asks for the same URL gets the cached
file instead of fetching again.

Usage:
    fetch_pdf.py [--text] [--quiet] <url-or-doi> ...
    cat urls.txt | fetch_pdf.py [--text]

Each argument (or stdin line) is a direct PDF URL or a DOI (resolved via
Unpaywall / Semantic Scholar, as scholar does).  Output is TSV, one line
per source:

    <source>\t<cache path or ->\t<OK | ERROR: message>[\t<text path>]

With --text the PDF is also extracted with `pdftotext -layout` to
`<cache path without .pdf>.txt` beside it (skipped if it exists), so the
full text can be grepped for QUOTE passages; the text path is printed as
a fourth column.  Exit status is 1 if any source failed.

The script re-executes itself under the interpreter of the installed
`scholar` command (a pipx venv) when the `scholar` package is not
importable from the current Python.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def reexec_under_scholar_python() -> None:
    """Re-run this script with the Python that has `scholar` installed."""
    scholar_cmd = shutil.which("scholar") or os.path.expanduser(
        "~/.local/bin/scholar"
    )
    try:
        with open(scholar_cmd, "r", encoding="utf-8", errors="ignore") as fh:
            first = fh.readline().strip()
    except OSError:
        sys.exit(
            "fetch_pdf.py: cannot import scholar and cannot find the "
            "scholar command to borrow its interpreter"
        )
    if not first.startswith("#!"):
        sys.exit("fetch_pdf.py: the scholar command has no shebang line")
    interpreter = first[2:].split()[0]
    if interpreter == sys.executable:
        sys.exit("fetch_pdf.py: scholar's interpreter cannot import scholar")
    os.execv(interpreter, [interpreter, __file__] + sys.argv[1:])


try:
    from scholar.pdf import PDFDownloadError, get_pdf  # type: ignore
except ImportError:
    reexec_under_scholar_python()


def extract_text(pdf_path: Path) -> Path | None:
    """Write pdftotext -layout output beside the PDF; return its path."""
    txt_path = pdf_path.with_suffix(".txt")
    if txt_path.exists() and txt_path.stat().st_size > 0:
        return txt_path
    if shutil.which("pdftotext") is None:
        return None
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), str(txt_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return txt_path


def main(argv: list[str]) -> int:
    want_text = "--text" in argv
    quiet = "--quiet" in argv
    sources = [a for a in argv if not a.startswith("--")]
    if not sources:
        sources = [line.strip() for line in sys.stdin if line.strip()]
    failures = 0
    for source in sources:
        if source.startswith("#"):
            continue
        try:
            path = get_pdf(
                source,
                progress_callback=None
                if quiet
                else (lambda msg: print(f"# {msg}", file=sys.stderr)),
            )
        except PDFDownloadError as exc:  # scholar's own failure type
            failures += 1
            print(f"{source}\t-\tERROR: {exc}")
            continue
        except Exception as exc:  # network, parsing, anything else
            failures += 1
            print(f"{source}\t-\tERROR: {type(exc).__name__}: {exc}")
            continue
        line = f"{source}\t{path}\tOK"
        if want_text:
            txt = extract_text(Path(path))
            line += f"\t{txt if txt else '-'}"
        print(line)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
