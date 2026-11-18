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
    % VERIFIED: <full-text | abstract> ; applies because <one line>
    % COUNTER: <counter-search query> -- <outcome>
    %   (or: none found, searched: <query>; or: see <other bibkey>)
    % DATE: 2026-06-24
    @inproceedings{bibkey, ... }

Checks per entry (errors make the exit status 1):
  - a provenance block is present immediately above the entry
  - CLAIM, FOUND-VIA, PICKED, QUOTE, VERIFIED and COUNTER are present
    and non-empty
  - no field is a placeholder: an unquoted TODO, a <template> value, or
    the QUOTE location "(<loc>)" that `scholar search -f bibtex+prov` emits
  - VERIFIED begins with the level read, "full-text" or "abstract"; never
    a title, a snippet, a machine summary (tldr) or memory
  - a causal or quantitative CLAIM (causes/improves/reduces/increases/
    decreases/prevents/leads to, N%, N-fold, N times, by N) is VERIFIED
    in full text, unless VERIFIED marks the source as corroboration
  - COUNTER names its search: "<query> -- <outcome>",
    "none found, searched: <query>", or "see <key>" for an entry in the
    same file whose own COUNTER names one
Warnings: missing DATE, missing or mismatched header, QUOTE without a
quoted passage or without a location.

With --quotes, each QUOTE is also looked up in the paper's full text: the
quoted passage, split at ellipses ("...", "…", "[...]") and bracketed
insertions, must occur fragment by fragment, in order. Both sides are
compared as case-folded letters and digits only, so whitespace, line
breaks, hyphenation at line ends, punctuation, quote styles, ligatures and
accents do not matter. The text comes from, in order:
  --text KEY=PATH            a PDF or text file for one entry
  --fulltext-dir DIR         DIR/<key>.txt or DIR/<key>.pdf
  the entry's file field     a local PDF or text file
  scholar's PDF cache        <cache>/<sha256(url)[:16]>.pdf/.txt for the
                             entry's url, pdf and https://doi.org/<doi>
  the entry's abstract field
  --fetch (network)          fetch_pdf.py --text <doi or url>, which
                             downloads into scholar's PDF cache
A QUOTE not found in any of them is an error; an entry with no full text
at all gets a warning (the quote was not checked). PDFs are read with
pdftotext (poppler-utils) in reading order, beside any .txt next to them.

Exit status: 0 if every entry passes, 1 if any entry has errors.

Usage:
    check_provenance.py <file.bib> [<file2.bib> ...]
    check_provenance.py --quiet refs/*.bib          # only print failures
    check_provenance.py --quotes refs.bib           # + QUOTEs in full text
    check_provenance.py --quotes --fetch refs.bib   # download missing texts
    check_provenance.py --quotes --text Key=paper.pdf refs.bib
"""

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

REQUIRED_FIELDS = ["CLAIM", "FOUND-VIA", "PICKED", "QUOTE", "VERIFIED",
                   "COUNTER"]
RECOMMENDED_FIELDS = ["DATE"]

# @article{key,  /  @inproceedings{ key ,  -- capture the entry type and key.
ENTRY_RE = re.compile(r"^\s*@(\w+)\s*\{\s*([^,\s}]+)\s*,")
# A comment line: optional whitespace then '%'.
COMMENT_RE = re.compile(r"^\s*%")
# A field header inside the block: '% FIELD:' or '% FIELD (loc):'.
FIELD_RE = re.compile(r"^\s*%\s*([A-Z][A-Z-]+)\s*(?:\(([^)]*)\))?\s*:(.*)$")
# The block header line: '% === provenance: key ===' (key optional).
HEADER_RE = re.compile(r"^\s*%\s*=+\s*provenance:\s*([^=\s]+)?\s*=*\s*$",
                       re.IGNORECASE)

# Placeholders: an unquoted TODO anywhere, or a value that is only a
# <template> from the schema.
QUOTED_SPAN_RE = re.compile(r'"[^"]*"|“[^”]*”|„[^“”]*[“”]|`[^`]*`')
TODO_RE = re.compile(r"\bTODO\b")
TEMPLATE_RE = re.compile(r"^\s*<[^<>]*>\s*$")
LOC_PLACEHOLDER = "<loc>"

# VERIFIED levels (references/verification-checklist.md, "What verified
# requires"): abstract or full text is the minimum; title-only,
# snippet-only, a machine summary and memory are never acceptable.
LEVEL_RE = re.compile(r"^\s*(full[- ]?text|abstract)\b", re.IGNORECASE)
NEGATED_FULL_RE = re.compile(
    r"^\s*full[- ]?text\s+(not|un\w*|could\s*n|was\s*n|is\s*n)",
    re.IGNORECASE)
NEVER_RE = re.compile(
    r"\b(title|snippet|tldr|summary|memory|recall\w*|not read|unread"
    r"|metadata)\b", re.IGNORECASE)
CORROBORATION_RE = re.compile(r"corroborat", re.IGNORECASE)
# Claims that need the results read in full text (the strength table in
# verification-checklist.md: "causes / improves", "reduces / increases
# by N"; a precise quantitative or causal claim).
CAUSAL_RE = re.compile(
    r"\b(caus(e|es|ed|ing)|improv(e|es|ed|ing)|reduc(e|es|ed|ing)"
    r"|increas(e|es|ed|ing)|decreas(e|es|ed|ing)|prevent(s|ed|ing)?"
    r"|leads? to|led to)\b", re.IGNORECASE)
QUANT_RE = re.compile(
    r"\d+(\.\d+)?\s*(%|percent\b|per cent\b|-?fold\b|times\b)"
    r"|\bby (a factor of )?\d", re.IGNORECASE)

# COUNTER forms (references/provenance-format.md, "Schema").
COUNTER_QUERY_RE = re.compile(r"\S.*\s--\s+\S")
COUNTER_NONE_RE = re.compile(r"\bsearched\s*:\s*\S", re.IGNORECASE)
COUNTER_SEE_RE = re.compile(r"^\s*(?:see|as for)\s+([^\s,;.]+)\s*[.;]?\s*$",
                            re.IGNORECASE)

# Splitting a quoted passage into verbatim fragments.
ELLIPSIS_RE = re.compile(r"\[\s*(?:\.\.\.|…)\s*\]|\.\.\.|…|\[[^\]]*\]")
OPEN_QUOTES = '"“„«'
ABSTRACT = "the entry's abstract field"
CLOSE_QUOTES = '"”“»'


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------

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
            if seen_comment:
                break
        else:
            break
        i -= 1
    block.reverse()
    return block


def parse_fields(block):
    """Map FIELD -> list of (location, value) from a provenance block.

    A field may occur more than once (two QUOTEs, `FOUND-VIA (here)`), so
    every occurrence is kept. Values continue onto following comment lines
    until the next FIELD header, so multi-line quotes are captured whole.
    """
    fields = {}
    current = None
    for line in block:
        m = FIELD_RE.match(line)
        if m:
            current = m.group(1).upper()
            loc = m.group(2).strip() if m.group(2) is not None else None
            fields.setdefault(current, []).append([loc, m.group(3).strip()])
        elif current is not None and COMMENT_RE.match(line):
            cont = re.sub(r"^\s*%\s?", "", line).rstrip()
            if cont:
                entry = fields[current][-1]
                entry[1] = (entry[1] + " " + cont).strip()
    return {name: [tuple(v) for v in values] for name, values in fields.items()}


def entry_text(lines, entry_idx):
    """Return the entry's source text, from '@type{' to its closing brace."""
    text = "\n".join(lines[entry_idx:])
    start = text.index("{")
    depth = 0
    for pos in range(start, len(text)):
        if text[pos] == "{":
            depth += 1
        elif text[pos] == "}":
            depth -= 1
            if depth == 0:
                return text[:pos + 1]
    return text


def bib_fields(entry):
    """Parse 'name = {value}' / "value" / bare fields of one entry."""
    body = entry[entry.index(",") + 1:] if "," in entry else ""
    fields = {}
    pos = 0
    name_re = re.compile(r"\s*,?\s*([A-Za-z][\w-]*)\s*=\s*")
    while pos < len(body):
        m = name_re.match(body, pos)
        if not m:
            break
        name = m.group(1).lower()
        pos = m.end()
        if pos >= len(body):
            break
        if body[pos] in "{\"":
            close = "}" if body[pos] == "{" else '"'
            depth = 0
            start = pos
            while pos < len(body):
                ch = body[pos]
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                if (close == "}" and depth == 0 and ch == "}") or (
                        close == '"' and depth == 0 and ch == '"'
                        and pos > start):
                    break
                pos += 1
            fields[name] = body[start + 1:pos]
            pos += 1
        else:
            m2 = re.compile(r"[^,}]*").match(body, pos)
            fields[name] = m2.group(0).strip()
            pos = m2.end()
    return fields


# --------------------------------------------------------------------------
# Field checks
# --------------------------------------------------------------------------

def is_placeholder(value):
    """True for an unquoted TODO or a value that is only a <template>."""
    unquoted = QUOTED_SPAN_RE.sub("", value)
    return bool(TODO_RE.search(unquoted) or TEMPLATE_RE.match(value))


def check_verified(key, verified, claims):
    """Errors for a VERIFIED value too weak for the entry's claims."""
    errors = []
    level = LEVEL_RE.match(verified)
    if level is None or NEGATED_FULL_RE.match(verified):
        never = NEVER_RE.search(verified)
        if never:
            errors.append(
                f"{key}: VERIFIED '{verified[:60]}' is never acceptable "
                f"('{never.group(0)}'): read the abstract or the full text, "
                "not a title, a snippet, a machine summary or memory")
        else:
            errors.append(
                f"{key}: VERIFIED must begin with the level read, "
                f"'full-text' or 'abstract' (got '{verified[:60]}')")
        return errors
    if level.group(1).lower() == "abstract" and not \
            CORROBORATION_RE.search(verified):
        for claim in claims:
            hit = CAUSAL_RE.search(claim) or QUANT_RE.search(claim)
            if hit:
                errors.append(
                    f"{key}: causal/quantitative CLAIM ('{hit.group(0)}') "
                    "VERIFIED at abstract level only: read the results in "
                    "full text (or mark the source as corroboration in "
                    "VERIFIED)")
                break
    return errors


def counter_is_own(value):
    """True if a COUNTER value names its counter-search itself."""
    return bool(COUNTER_QUERY_RE.search(value) or COUNTER_NONE_RE.search(value))


def validate_entry(key, block):
    """Return (errors, warnings, fields) for one entry's provenance block."""
    errors = []
    warnings = []

    if not block:
        errors.append(f"{key}: no provenance comment block above the entry")
        return errors, warnings, {}

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
            continue
        for loc, value in fields[field]:
            if not value:
                errors.append(f"{key}: field '{field}' is empty")
            elif is_placeholder(value):
                errors.append(
                    f"{key}: field '{field}' is a placeholder "
                    f"('{value[:40]}'): fill it in")

    for loc, value in fields.get("QUOTE", []):
        if loc == LOC_PLACEHOLDER:
            errors.append(
                f"{key}: QUOTE location is the placeholder '(<loc>)': give "
                "the page, section or (abstract)")
        elif not loc:
            warnings.append(
                f"{key}: QUOTE has no location -- write QUOTE (p.N): ...")
        if value and not is_placeholder(value) and not any(
                q in value for q in OPEN_QUOTES):
            warnings.append(
                f"{key}: QUOTE has no quoted \"...\" passage -- paste the "
                "verbatim text")

    claims = [v for _, v in fields.get("CLAIM", []) if v]
    for _, verified in fields.get("VERIFIED", []):
        if verified and not is_placeholder(verified):
            errors.extend(check_verified(key, verified, claims))

    for field in RECOMMENDED_FIELDS:
        if field not in fields:
            warnings.append(f"{key}: recommended field '{field}' missing")

    return errors, warnings, fields


def check_counters(entries):
    """Errors for COUNTER values that do not name their search.

    Runs over a whole file, since "see <key>" refers to another entry.
    """
    errors = []
    by_key = {key: fields for key, fields, _ in entries}
    for key, fields, _ in entries:
        for _, value in fields.get("COUNTER", []):
            if not value or is_placeholder(value) or counter_is_own(value):
                continue
            see = COUNTER_SEE_RE.match(value)
            if see:
                other = by_key.get(see.group(1))
                if other is None:
                    errors.append(
                        f"{key}: COUNTER refers to '{see.group(1)}', which "
                        "is not an entry of this file")
                elif not any(counter_is_own(v)
                             for _, v in other.get("COUNTER", [])):
                    errors.append(
                        f"{key}: COUNTER refers to '{see.group(1)}', whose "
                        "COUNTER does not name its search")
                continue
            errors.append(
                f"{key}: COUNTER does not name its search: write "
                "'<query> -- <outcome>' or 'none found, searched: <query>' "
                f"(got '{value[:60]}')")
    return errors


# --------------------------------------------------------------------------
# Quotes in the full text
# --------------------------------------------------------------------------

def normalise(text):
    """Case-folded letters and digits only, accents and ligatures removed."""
    text = text.replace("\ufffe", "").replace("\u00ad", "")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return "".join(c for c in text.casefold() if c.isalnum())


def detex(text):
    """Drop TeX commands and braces from a bib field value."""
    text = re.sub(r"\\[a-zA-Z]+\*?", "", text)
    return re.sub(r"\\[^a-zA-Z]", "", text)


def quoted_passage(value):
    """The text between the first opening and the last closing quote."""
    start = min((value.find(q) for q in OPEN_QUOTES if q in value),
                default=-1)
    if start < 0:
        return value
    end = max(value.rfind(q) for q in CLOSE_QUOTES)
    return value[start + 1:end] if end > start else value[start + 1:]


def quote_fragments(value):
    """Normalised verbatim fragments of a QUOTE, in order."""
    parts = ELLIPSIS_RE.split(quoted_passage(value))
    return [n for n in (normalise(p) for p in parts) if n]


def find_fragments(fragments, text):
    """Index of the first fragment not found in order, or None if all are."""
    pos = 0
    for i, fragment in enumerate(fragments):
        hit = text.find(fragment, pos)
        if hit < 0:
            return i
        pos = hit + len(fragment)
    return None


def pdf_cache_dir():
    """scholar's PDF cache: $SCHOLAR_CACHE_DIR/pdfs, else ~/.cache/scholar."""
    base = os.environ.get("SCHOLAR_CACHE_DIR")
    if not base:
        base = os.path.join(os.environ.get("XDG_CACHE_HOME")
                            or os.path.expanduser("~/.cache"), "scholar")
    return Path(base) / "pdfs"


def cached_paths(url):
    """The cache files scholar would use for a PDF URL (see pdf.nw)."""
    stem = hashlib.sha256(url.encode()).hexdigest()[:16]
    return [pdf_cache_dir() / f"{stem}.pdf", pdf_cache_dir() / f"{stem}.txt"]


def read_texts(path):
    """Texts of a .txt file, or of a PDF via pdftotext.

    A PDF is extracted twice, in reading order and in content-stream
    order (-raw): either can split a sentence that the other keeps whole
    (a word broken across columns, a float in the middle of a paragraph).
    """
    path = Path(path)
    if path.suffix.lower() != ".pdf":
        return [path.read_text(encoding="utf-8", errors="replace")]
    if shutil.which("pdftotext") is None:
        return []
    texts = []
    for mode in ([], ["-raw"]):
        result = subprocess.run(
            ["pdftotext", *mode, "-enc", "UTF-8", str(path), "-"],
            capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            texts.append(result.stdout)
    return texts


def fetch(source):
    """Download a source with fetch_pdf.py; return the files it reports."""
    script = Path(__file__).with_name("fetch_pdf.py")
    result = subprocess.run([sys.executable, str(script), "--text", "--quiet",
                             source], capture_output=True, text=True)
    paths = []
    for line in result.stdout.splitlines():
        cols = line.split("\t")
        if len(cols) >= 3 and cols[2] == "OK":
            paths += [Path(c) for c in [cols[1]] + cols[3:4] if c != "-"]
    return paths, result.stdout.strip() or result.stderr.strip()


def full_texts(key, bib, options):
    """Return [(label, normalised text)] for one entry, and fetch notes."""
    paths = []
    if key in options.text_for:
        paths.append(Path(options.text_for[key]))
    for directory in options.fulltext_dir:
        paths += [Path(directory) / f"{key}.txt", Path(directory) / f"{key}.pdf"]
    for part in re.split(r";", bib.get("file", "")):
        bits = part.split(":")
        candidate = bits[1] if len(bits) >= 3 else part
        if candidate.strip():
            paths.append(Path(os.path.expanduser(candidate.strip())))
    urls = [bib[f] for f in ("url", "pdf") if bib.get(f, "").startswith("http")]
    if bib.get("doi"):
        urls.append("https://doi.org/" + bib["doi"].strip())
    for url in urls:
        paths += cached_paths(url)

    texts = []
    seen = set()

    def add(path):
        if path in seen or not path.is_file():
            return
        seen.add(path)
        for raw in read_texts(path):
            texts.append((str(path), normalise(raw)))

    for path in paths:
        add(path)
    if bib.get("abstract"):
        texts.append((ABSTRACT, normalise(detex(bib["abstract"]))))
    note = None
    if options.fetch and all(label == ABSTRACT for label, _ in texts):
        source = bib.get("doi", "").strip() or bib.get("url", "").strip()
        if source:
            fetched, note = fetch(source)
            for path in fetched:
                add(path)
    return texts, note


def check_quotes(key, fields, bib, options):
    """Errors and warnings from looking each QUOTE up in the full text."""
    quotes = [(loc, v) for loc, v in fields.get("QUOTE", [])
              if v and not is_placeholder(v)]
    if not quotes:
        return [], []
    texts, note = full_texts(key, bib, options)
    if not texts:
        hint = f" (fetch: {note.splitlines()[0][:80]})" if note else ""
        return [], [f"{key}: QUOTE not checked: no full text found{hint}; "
                    "give --text KEY=PATH, --fulltext-dir or --fetch"]
    errors = []
    warnings = []
    for loc, value in quotes:
        fragments = quote_fragments(value)
        if not fragments:
            continue
        misses = [(find_fragments(fragments, text), label)
                  for label, text in texts]
        if any(miss is None for miss, _ in misses):
            continue
        best = max(misses)[0]
        missing = ELLIPSIS_RE.split(quoted_passage(value))
        missing = [p for p in missing if normalise(p)][best].strip()
        labels = ", ".join(dict.fromkeys(label for label, _ in texts))
        only_abstract = all(label == ABSTRACT for label, _ in texts)
        if only_abstract and "abstract" not in (loc or "").lower():
            warnings.append(
                f"{key}: QUOTE ({loc or 'no location'}) not checked: only "
                "the abstract field is available and the quote is not in it; "
                "give --text KEY=PATH, --fulltext-dir or --fetch")
            continue
        errors.append(
            f"{key}: QUOTE ({loc or 'no location'}) not in the text "
            f"[{labels}]: missing '{missing[:60]}'")
    return errors, warnings


# --------------------------------------------------------------------------
# Files and output
# --------------------------------------------------------------------------

def validate_file(path, options=None):
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
    entries = []
    for idx, line in enumerate(lines):
        m = ENTRY_RE.match(line)
        if not m:
            continue
        entry_type = m.group(1).lower()
        if entry_type in ("comment", "preamble", "string"):
            continue  # BibTeX control entries, not real references
        key = m.group(2)
        ent_errors, ent_warnings, fields = validate_entry(
            key, collect_block(lines, idx))
        errors.extend(ent_errors)
        warnings.extend(ent_warnings)
        entries.append((key, fields, idx))

    errors.extend(check_counters(entries))

    if options is not None and options.quotes:
        for key, fields, idx in entries:
            bib = bib_fields(entry_text(lines, idx))
            q_errors, q_warnings = check_quotes(key, fields, bib, options)
            errors.extend(q_errors)
            warnings.extend(q_warnings)

    return errors, warnings, len(entries)


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


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Validate citation-provenance comment blocks in BibTeX "
        f"files. Required fields: {', '.join(REQUIRED_FIELDS)}.")
    parser.add_argument("files", nargs="*", help=".bib files to check")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="print only files with errors or warnings")
    parser.add_argument("--quotes", action="store_true",
                        help="look each QUOTE up in the paper's full text")
    parser.add_argument("--text", action="append", default=[],
                        metavar="KEY=PATH",
                        help="full text (PDF or .txt) for one entry")
    parser.add_argument("--fulltext-dir", action="append", default=[],
                        metavar="DIR",
                        help="directory of <key>.pdf / <key>.txt files")
    parser.add_argument("--fetch", action="store_true",
                        help="download missing full texts with fetch_pdf.py "
                        "(network; implies --quotes)")
    options = parser.parse_args(argv)
    if options.text or options.fulltext_dir or options.fetch:
        options.quotes = True
    options.text_for = {}
    for item in options.text:
        if "=" not in item:
            parser.error(f"--text expects KEY=PATH, got '{item}'")
        key, value = item.split("=", 1)
        options.text_for[key] = value
    return parser, options


def main():
    parser, options = parse_args(sys.argv[1:])
    if not options.files:
        parser.print_usage()
        sys.exit(1)

    all_ok = True
    for path in options.files:
        errors, warnings, n_entries = validate_file(path, options)
        if not print_results(path, errors, warnings, n_entries, options.quiet):
            all_ok = False

    print()
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
