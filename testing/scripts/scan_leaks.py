#!/usr/bin/env python3
"""Fail if test data contains secrets or personal data.

    scan_leaks.py [PATH ...] [--originals FILE] [--denylist FILE]
                  [--warn-names] [--allow-names FILE]

Scans files and directories (default: tests/) for emails outside the
example.* domains, valid Swedish personnummer, JWTs, bearer tokens and
assigned secrets; plus every line of --originals (the values the
pseudonymizer replaced while recording; default: the file vcr_support
writes for the current directory, if it exists) and of --denylist (a
private list kept OUTSIDE the repo, e.g. names from a class roster).

Hits are printed as file:line: kind and a redacted stub, never the value.
Cassettes are also scanned unfolded ("file:unfolded"), because the YAML
dumper can split a name across two lines.
--warn-names also reports capitalized word pairs ("Anna Svensson") that
are not in --allow-names; these are warnings and do not fail the run.

Exit status: 0 clean, 1 leaks found.  Usable as a pre-commit hook.
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "assets"))
import vcr_support  # noqa: E402

BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".gz", ".pyc"}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("paths", nargs="*", default=["tests"])
    parser.add_argument("--originals", default=os.environ.get(vcr_support.ORIGINALS_ENV)
                        or vcr_support.default_originals_path("."))
    parser.add_argument("--denylist")
    parser.add_argument("--warn-names", action="store_true")
    parser.add_argument("--allow-names")
    args = parser.parse_args(argv)

    if args.originals and not Path(args.originals).exists():
        print(f"warning: originals file not found ({args.originals}); only "
              "patterns and the denylist are checked. It is written while "
              "recording and lives in the temp dir, so record again or pass "
              "--originals.", file=sys.stderr)
    originals = vcr_support.read_list(args.originals)
    denylist = vcr_support.read_list(args.denylist)
    allowed = vcr_support.read_list(args.allow_names)
    leaks = 0
    for f in vcr_support.iter_files(args.paths):
        if f.suffix in BINARY_SUFFIXES or "__pycache__" in f.parts:
            continue
        for where, kind, hit in vcr_support.scan_file(f, originals, denylist):
            print(f"{f}:{where}: {kind} {hit}")
            leaks += 1
        if args.warn_names:
            text = f.read_text(encoding="utf-8", errors="replace")
            for no, hit in vcr_support.name_like(text, allowed):
                print(f"{f}:{no}: warning: name-like {hit}")
    if leaks:
        print(f"{leaks} leak(s) found; scrub or delete the data, and if it was "
              "ever committed, treat it as published (rotate secrets, ask before "
              "rewriting history)")
    return 1 if leaks else 0


if __name__ == "__main__":
    sys.exit(main())
