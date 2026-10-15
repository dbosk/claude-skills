#!/usr/bin/env python3
"""Fail if test data contains secrets or personal data.

    scan_leaks.py [PATH ...] [--originals FILE] [--denylist FILE]
                  [--allow FILE] [--warn-names] [--allow-names FILE] [--warn-ids]
                  [--key-census]

Scans files and directories for emails outside the example.* domains,
valid Swedish personnummer, JWTs, bearer tokens, SAML responses,
assigned secrets and links that are secrets themselves (a Google
Calendar private address, a secret-named query parameter, a long mixed
token in a URL: TimeEdit, shared documents); plus every line of --originals (the values the
pseudonymizer replaced while recording; default: the file vcr_support
writes for the current directory, if it exists) and of --denylist (a
private list kept OUTSIDE the repo, e.g. names from a class roster).

A path of - reads standard input (pdftotext doc.pdf - | scan_leaks.py -).
Default paths: tests/ and, in a git repository, every tracked literate
source (*.nw), since in a literate project tests/ is generated and the
.nw files are what gets committed.  Generated documentation (PythonTeX
*.stdout, notebooks) must be passed explicitly.

--allow FILE lists hits that are not leaks, one per line: an exact value
(any case) or `re:REGEX` matched against the whole hit.  The fictive
Tolvan personnummer (19121212-1212) is always allowed.

Hits are printed as file:line: kind and a redacted stub, never the value.
Cassettes are also scanned unfolded ("file:unfolded"), because the YAML
dumper can split a name across two lines.
Tokens must look random (digits or mixed case), so prose ("a bearer
credential") and placeholders ("your-api-token") pass.  A YYYYMMDD-HHMM
timestamp passes the personnummer checksum one time in ten: allow such
names with --allow 're:20[0-9]{6}-[0-9]{4}' only after checking them, since
students' files are named by personnummer too.
--warn-names also reports capitalized word pairs ("Anna Svensson") that
are not in --allow-names; these are warnings and do not fail the run.
It is meant for data (cassettes, fixtures, generated output): on prose
every Title Case phrase is a hit.
--warn-ids warns about numeric user IDs in URLs (/users/N, /submissions/N,
?student_id=N): pseudonymous, not anonymous, if they come from a real
service.
--key-census prints, instead of scanning, each JSON or Python-repr key
with its number of distinct values and the length of the longest, never
the values: a scrubbed key has one value, a free-text or name field that
leaks has many long ones (run it on generated docs and fixtures).

Exit status: 0 clean, 1 leaks found.  Usable as a pre-commit hook.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "assets"))
import vcr_support  # noqa: E402

BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".gz", ".pyc"}


def default_paths() -> list[str]:
    paths = ["tests"] if Path("tests").exists() else []
    tracked = subprocess.run(["git", "ls-files", "*.nw"], capture_output=True, text=True)
    if tracked.returncode == 0:
        paths += tracked.stdout.split()
    return paths


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--originals")
    parser.add_argument("--denylist")
    parser.add_argument("--allow")
    parser.add_argument("--warn-names", action="store_true")
    parser.add_argument("--allow-names")
    parser.add_argument("--warn-ids", action="store_true")
    parser.add_argument("--key-census", action="store_true")
    args = parser.parse_args(argv)

    asked = args.originals or os.environ.get(vcr_support.ORIGINALS_ENV)
    args.originals = asked or vcr_support.default_originals_path(".")
    if asked and not Path(asked).exists():
        print(f"warning: originals file not found ({args.originals}); only "
              "patterns and the denylist are checked. It is written while "
              "recording and lives in the temp dir, so record again or pass "
              "--originals.", file=sys.stderr)
    elif not asked and Path(args.originals).exists():
        print(f"scan_leaks: also matching the originals of the last recording here "
              f"({args.originals}); pass --originals /dev/null to scan without them",
              file=sys.stderr)
    # built once: matching thousands of originals is the slow part
    originals = vcr_support.Needles(vcr_support.read_list(args.originals))
    denylist = vcr_support.Needles(vcr_support.read_list(args.denylist))
    allowed = vcr_support.read_list(args.allow_names)
    allow = vcr_support.read_list(args.allow)
    leaks = 0
    paths = args.paths or default_paths()
    if args.key_census:
        texts = [f.read_text(encoding="utf-8", errors="replace")
                 for f in vcr_support.iter_files(p for p in paths if p != "-")
                 if f.suffix not in BINARY_SUFFIXES and "__pycache__" not in f.parts]
        if "-" in paths:
            texts.append(sys.stdin.read())
        for key, distinct, longest in vcr_support.key_census(texts):
            print(f"{key} distinct={distinct} longest={longest}")
        return 0
    if "-" in paths:
        paths = [p for p in paths if p != "-"]
        for no, kind, hit in vcr_support.scan_text(sys.stdin.read(), originals,
                                                   denylist, allow):
            print(f"<stdin>:{no}: {kind} {hit}")
            leaks += 1
    for f in vcr_support.iter_files(paths):
        if f.suffix in BINARY_SUFFIXES or "__pycache__" in f.parts:
            continue
        for where, kind, hit in vcr_support.scan_file(f, originals, denylist, allow):
            print(f"{f}:{where}: {kind} {hit}")
            leaks += 1
        if args.warn_names or args.warn_ids:
            text = f.read_text(encoding="utf-8", errors="replace")
        if args.warn_names:
            for no, hit in vcr_support.name_like(text, allowed):
                print(f"{f}:{no}: warning: name-like {hit}")
        if args.warn_ids:
            for no, hit in vcr_support.url_ids(text):
                print(f"{f}:{no}: warning: url-id {hit}")
    if leaks:
        print(f"{leaks} leak(s) found; scrub or delete the data, and if it was "
              "ever committed, treat it as published (rotate secrets, ask before "
              "rewriting history)")
    return 1 if leaks else 0


if __name__ == "__main__":
    sys.exit(main())
