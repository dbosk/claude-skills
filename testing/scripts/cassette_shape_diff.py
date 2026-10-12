#!/usr/bin/env python3
"""Compare two cassette directories by structure, never by value.

    cassette_shape_diff.py COMMITTED_DIR LIVE_DIR [--strict]

Shapes are status codes, content types, and JSON key paths with value
types, grouped by request (method + path with numeric ids, pseudonyms and
UUIDs abstracted).  Only paths and types are printed, so the output is safe
to show in a transcript even when the live data is personal.

Exit status: 0 no drift, 1 drift (removed/changed structure, or with
--strict also additions), 2 usage error.  Needs PyYAML for .yaml cassettes
(`uv run --with pyyaml ...`).
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "assets"))
import vcr_support  # noqa: E402


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("committed", type=Path)
    parser.add_argument("live", type=Path)
    parser.add_argument("--strict", action="store_true",
                        help="treat added fields and requests as drift too")
    args = parser.parse_args(argv)
    for d in (args.committed, args.live):
        if not d.is_dir():
            parser.error(f"not a directory: {d}")

    findings = vcr_support.compare_directories(args.committed, args.live)
    failing = {"drift", "info"} if args.strict else {"drift"}
    bad = 0
    for severity, cassette, key, message in findings:
        if message == "not re-recorded in the live run":
            continue
        if severity in failing and message != "new cassette (not committed yet)":
            bad += 1
            severity = "drift"
        print(f"{severity}: {cassette} {key}: {message}")
    print(f"{bad} drift finding(s)" if bad else "no structural drift")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
