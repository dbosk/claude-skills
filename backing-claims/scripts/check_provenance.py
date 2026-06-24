#!/usr/bin/env python3
"""
Validate citation-provenance comment blocks in BibTeX (.bib) files.

Every entry that backs a claim must be preceded by a provenance comment block
(see the backing-claims skill, references/provenance-format.md):

    % === provenance: bibkey ===
    % CLAIM: <the exact claim this reference backs>
    % FOUND-VIA: <reproducible tool + provider + query>
    % PICKED: <why this one among the results>
    % QUOTE (p.N / §X / abstract): "<verbatim passage that supports CLAIM>"
    % VERIFIED: <abstract | full-text> ; applies because <one line>
    % DATE: 2026-06-24
    @inproceedings{bibkey, ... }

Checks per entry:
  - a provenance block is present immediately above the entry
  - all required fields are present and non-empty
  - QUOTE contains a quoted passage (a "..." span)
  - the block header bibkey matches the entry key (warning if not)

Required fields: CLAIM, FOUND-VIA, PICKED, QUOTE, VERIFIED.
DATE is recommended (warning if missing), not required.

Exit status: 0 if every entry passes, 1 if any entry has errors.

Usage:
    check_provenance.py <file.bib> [<file2.bib> ...]
    check_provenance.py refs/*.bib
    check_provenance.py --quiet refs.bib      # only print failures
"""

import re
import sys
from pathlib import Path

REQUIRED_FIELDS = ["CLAIM", "FOUND-VIA", "PICKED", "QUOTE", "VERIFIED"]
RECOMMENDED_FIELDS = ["DATE"]

# @article{key,  /  @inproceedings{ key ,  -- capture the entry type and key.
ENTRY_RE = re.compile(r"^\s*@(\w+)\s*\{\s*([^,\s}]+)\s*,")
# A comment line: optional whitespace then '%'.
COMMENT_RE = re.compile(r"^\s*%")
# A field header inside the block: '% FIELD:' or '% FIELD (loc):'.
FIELD_RE = re.compile(r"^\s*%\s*([A-Z][A-Z-]+)\s*(?:\([^)]*\))?\s*:(.*)$")
# The block header line: '% === provenance: key ===' (key optional).
HEADER_RE = re.compile(r"^\s*%\s*=+\s*provenance:\s*([^=\s]+)?\s*=*\s*$",
                       re.IGNORECASE)


def collect_block(lines, entry_idx):
    """Return the contiguous comment lines immediately above an entry.

    Walks upward from the line before the entry, gathering comment lines.
    A single run of blank lines between the block and the entry is tolerated;
    any non-comment, non-blank line (or a second blank run) ends the block.
    """
    block = []
    i = entry_idx - 1
    seen_comment = False
    while i >= 0:
        line = lines[i]
        if COMMENT_RE.match(line):
            block.append(line)
            seen_comment = True
        elif line.strip() == "":
            # Allow blank lines only before we have started collecting
            # comments (i.e. between entry and block); stop once inside.
            if seen_comment:
                break
        else:
            break
        i -= 1
    block.reverse()
    return block


def parse_fields(block):
    """Map FIELD -> accumulated value text from a provenance comment block.

    Values may continue onto following comment lines until the next FIELD
    header, so multi-line quotes and rationales are captured in full.
    """
    fields = {}
    current = None
    for line in block:
        m = FIELD_RE.match(line)
        if m:
            current = m.group(1).upper()
            fields[current] = m.group(2).strip()
        elif current is not None and COMMENT_RE.match(line):
            # Continuation line: strip the leading '%' and append.
            cont = re.sub(r"^\s*%\s?", "", line).rstrip()
            if cont:
                fields[current] = (fields[current] + " " + cont).strip()
    return fields


def validate_entry(key, block):
    """Return (errors, warnings) for one entry's provenance block."""
    errors = []
    warnings = []

    if not block:
        errors.append(f"{key}: no provenance comment block above the entry")
        return errors, warnings

    header_key = None
    for line in block:
        hm = HEADER_RE.match(line)
        if hm:
            header_key = hm.group(1)
            break
    if header_key is None:
        warnings.append(f"{key}: missing '% === provenance: {key} ===' header")
    elif header_key != key:
        warnings.append(
            f"{key}: header bibkey '{header_key}' does not match entry key")

    fields = parse_fields(block)

    for field in REQUIRED_FIELDS:
        if field not in fields:
            errors.append(f"{key}: missing required field '{field}'")
        elif not fields[field]:
            errors.append(f"{key}: field '{field}' is empty")

    # A QUOTE must actually contain a quoted passage.
    quote = fields.get("QUOTE", "")
    if quote and '"' not in quote and "“" not in quote:
        warnings.append(
            f"{key}: QUOTE has no quoted \"...\" passage -- paste the verbatim text")

    for field in RECOMMENDED_FIELDS:
        if field not in fields:
            warnings.append(f"{key}: recommended field '{field}' missing")

    return errors, warnings


def validate_file(path):
    """Validate every entry in one .bib file. Returns (errors, warnings, n)."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return ([f"File not found: {path}"], [], 0)
    except OSError as exc:
        return ([f"Cannot read {path}: {exc}"], [], 0)

    lines = text.splitlines()
    errors = []
    warnings = []
    n_entries = 0
    for idx, line in enumerate(lines):
        m = ENTRY_RE.match(line)
        if not m:
            continue
        entry_type = m.group(1).lower()
        if entry_type in ("comment", "preamble", "string"):
            continue  # BibTeX control entries, not real references
        n_entries += 1
        key = m.group(2)
        block = collect_block(lines, idx)
        ent_errors, ent_warnings = validate_entry(key, block)
        errors.extend(ent_errors)
        warnings.extend(ent_warnings)

    return errors, warnings, n_entries


def print_results(path, errors, warnings, n_entries, quiet):
    """Print a per-file report. Returns True if the file passed (no errors)."""
    ok = not errors
    if quiet and ok and not warnings:
        return ok

    print(f"\n{'=' * 60}")
    print(f"  {path}  ({n_entries} entr{'y' if n_entries == 1 else 'ies'})")
    print(f"{'=' * 60}")

    if errors:
        print(f"\n  ERRORS ({len(errors)}):")
        for err in errors:
            print(f"    [x] {err}")

    if warnings:
        print(f"\n  WARNINGS ({len(warnings)}):")
        for warn in warnings:
            print(f"    [!] {warn}")

    if not errors and not warnings:
        print("\n  All entries carry complete provenance.")

    status = "FAIL" if errors else ("WARN" if warnings else "OK")
    print(f"\n  Result: {status}")
    return ok


def main():
    args = [a for a in sys.argv[1:] if a not in ("--quiet", "-q")]
    quiet = len(args) != len(sys.argv[1:])

    if not args:
        print("Usage: check_provenance.py [--quiet] <file.bib> [<file2.bib> ...]")
        print("\nValidates citation-provenance comment blocks in BibTeX files.")
        print(f"Required fields: {', '.join(REQUIRED_FIELDS)}.")
        sys.exit(1)

    all_ok = True
    for path in args:
        errors, warnings, n_entries = validate_file(path)
        ok = print_results(path, errors, warnings, n_entries, quiet)
        if not ok:
            all_ok = False

    print()
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
