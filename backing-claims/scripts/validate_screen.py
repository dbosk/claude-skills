#!/usr/bin/env python3
"""Validate one agent screener's output against the batch it answers.

Usage:
  python3 -I validate_screen.py OUTPUT BATCH [options] [--json]

OUTPUT  the screener's file: TSV with a header line, or JSON Lines.
        Columns/keys (aliases in brackets): id, verdict [decision],
        category, confidence [conf], reason [why]; optional exclusion
        [exclude], theme, no_abstract. A TSV without a header needs
        --columns; one written by csv.writer needs --csv-quoting.
BATCH   the batch the screener was given: a JSON array, JSON Lines or a
        TSV with a header; each record has id, title, abstract.

Checks (a failure of any one exits 1):
  ids          every batch id exactly once, in batch order
  columns      required columns present; verdict, category, exclusion and
               theme in their vocabularies; keep only with a keep category
               and a record that has an abstract
  confidence   a number in [0, 1]
  reasons      no empty or placeholder reason
  duplicates   more than --max-dup rows (default 3) with one normalised
               reason, counting rows with identical titles once
  flat-conf    in a batch of --flat-min-rows (20) or more, the most common
               confidence below --flat-ignore-above (0.9) on more than
               --flat-share (0.6) of the rows (plainly off-topic batches
               legitimately sit at 0.9-0.95; defaulted ones sat at 0.6-0.7)
  runs         more than --max-run (5) consecutive rows with one verdict,
               one category and near-identical reasons (similarity at least
               --run-similarity, 0.9)
  quotes       every quoted string of 3 or more words (split at ellipses)
               occurs in that row's own title + abstract after normalising
               case, whitespace, dashes, quote marks and ellipses; a miss
               is classed mixup (verbatim in another row of the batch),
               paraphrase (75% or more of its words in its own text) or
               unsupported

Vocabularies: --categories, --keep-categories, --exclusions, --themes
(comma lists) or --config FILE (JSON with the same keys, underscores for
dashes). Defaults: the four audit categories, keep = supports-claim and
qualifies-claim, exclusions and themes unchecked.

Exit codes: 0 clean, 1 failures, 2 usage error (unreadable file, unknown
format, missing columns). Standard library only.
"""
import argparse
import collections
import csv
import difflib
import json
import re
import sys
import unicodedata

csv.field_size_limit(sys.maxsize)

DEFAULT_CATEGORIES = ["supports-claim", "qualifies-claim",
                      "adjacent-subtopic", "off-topic-false-hit"]
DEFAULT_KEEP = ["supports-claim", "qualifies-claim"]
ALIASES = {
    "id": ["id", "paper_id", "record_id"],
    "verdict": ["verdict", "decision", "status"],
    "category": ["category", "cat"],
    "confidence": ["confidence", "conf"],
    "reason": ["reason", "why", "rationale"],
    "exclusion": ["exclusion", "exclude", "exclusion_tag"],
    "theme": ["theme"],
    "no_abstract": ["no_abstract", "noabstract"],
}
REQUIRED = ["id", "verdict", "category", "confidence", "reason"]
EMPTY = {"", "-"}
PLACEHOLDER = re.compile(
    r"^\s*(placeholder|todo|tbd|xxx+|lorem ipsum|n/?a|none|same( as above)?"
    r"|see above|ditto|as above|\.\.\.|…|reason)\b[\s.!:]*$|<[^>]*sentence[^>]*>",
    re.I)


class UsageError(Exception):
    pass


# ---------------------------------------------------------------- reading

def _first_char(path):
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            if line.strip():
                return line.lstrip()[0]
    return ""


def _canon(fields):
    """Map the file's column names onto canonical names."""
    low = {f.strip().lower(): f for f in fields}
    out = {}
    for canon, names in ALIASES.items():
        for n in names:
            if n in low:
                out[canon] = low[n]
                break
    return out


def read_records(path, columns=None, csv_quoting=False):
    """Return (list of dicts, format name) from JSON, JSONL or TSV.

    A TSV has a header line unless `columns` names its columns.  Its
    fields are taken as written (a screener's sheet is not CSV-quoted, so
    a reason may start with a quote mark); `csv_quoting` reads a file
    written by csv.writer with doubled quotes instead."""
    try:
        first = _first_char(path)
    except OSError as e:
        raise UsageError(f"cannot read {path}: {e}")
    except UnicodeDecodeError:
        raise UsageError(f"{path} is not UTF-8 text")
    if first == "":
        raise UsageError(f"{path} is empty")
    with open(path, encoding="utf-8-sig") as f:
        if first == "[":
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise UsageError(f"{path}: invalid JSON: {e}")
            if not all(isinstance(r, dict) for r in data):
                raise UsageError(f"{path}: JSON array of non-objects")
            return data, "json"
        if first == "{":
            rows = []
            for n, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as e:
                    rows.append({"__unparsable__": f"line {n}: {e}"})
                    continue
                if not isinstance(obj, dict):
                    raise UsageError(f"{path}: line {n} is not a JSON object")
                rows.append(obj)
            return rows, "jsonl"
        if csv_quoting:
            reader = csv.reader(f, delimiter="\t")
        else:
            reader = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        if columns:
            header, start = columns, 1
        else:
            try:
                header, start = next(reader), 2
            except StopIteration:
                raise UsageError(f"{path} is empty")
        rows = []
        for n, r in enumerate(reader, start):
            if not any(c.strip() for c in r):
                continue
            row = dict(zip(header, r))
            if len(r) != len(header):
                row["__columns__"] = f"line {n}: {len(r)} fields, header has {len(header)}"
            rows.append(row)
        return rows, "tsv"


def normalise_rows(rows, fields_needed, path):
    keys = set()
    for r in rows:
        keys.update(k for k in r if not k.startswith("__"))
    cmap = _canon(keys)
    missing = [f for f in fields_needed if f not in cmap]
    if missing:
        raise UsageError(f"{path}: no column for {', '.join(missing)} "
                         f"(found: {', '.join(sorted(keys))})")
    out = []
    for r in rows:
        o = {c: r.get(src) for c, src in cmap.items()}
        for k in ("__unparsable__", "__columns__"):
            if k in r:
                o[k] = r[k]
        out.append(o)
    return out, cmap


# ---------------------------------------------------------- normalising

DASHES = re.compile(r"[‐-―−­-]")
TAGS = re.compile(r"<[^>]{1,80}>")


def norm_text(s):
    s = unicodedata.normalize("NFKC", str(s or "")).lower().replace("\u00ad", "")
    s = TAGS.sub(" ", s)
    s = (s.replace("’", "'").replace("‘", "'")
          .replace("“", '"').replace("”", '"')
          .replace("…", "..."))
    s = DASHES.sub("-", s)
    s = re.sub(r"\s*-\s*", "-", s)
    return re.sub(r"\s+", " ", s).strip()


def norm_reason(s):
    return norm_text(s).strip(" .;:,!")


def words(s):
    return re.findall(r"[a-z0-9]+", norm_text(s))


QUOTE_RES = [
    re.compile(r'"([^"]+)"'),
    re.compile(r"“([^”]+)”"),
    re.compile(r"‘([^’]+)’(?![a-z])"),
    # ASCII single quotes only around a phrase, so apostrophes are skipped
    re.compile(r"(?:(?<=[\s(\[])|^)'([^']+?)'(?=[\s.,;:)\]!?]|$)"),
]
ELLIPSIS = re.compile(r"\s*(?:\[\s*(?:\.\.\.|…)\s*\]|\.\.\.|…)\s*")


def quotes_in(reason):
    found = []
    for rx in QUOTE_RES:
        found.extend(rx.findall(reason or ""))
    return found


def fragments(quote):
    for frag in ELLIPSIS.split(quote):
        f = norm_text(frag).strip(" .,;:!?'\"()[]")
        if len(f.split()) >= 3:
            yield f


# ---------------------------------------------------------------- checks

def check(out_rows, batch_rows, vocab, opts):
    """Return (failures: list of dicts, stats: dict)."""
    fails = []

    def fail(check_name, msg, ids=None):
        fails.append({"check": check_name, "message": msg,
                      "ids": list(ids or [])})

    for r in out_rows:
        if "__unparsable__" in r:
            fail("columns", f"unparsable JSON {r['__unparsable__']}")
        if "__columns__" in r:
            fail("columns", f"wrong field count, {r['__columns__']}",
                 [r.get("id")])
    out_rows = [r for r in out_rows if "__unparsable__" not in r]

    batch_ids = [str(r["id"]) for r in batch_rows]
    rec = {str(r["id"]): r for r in batch_rows}
    out_ids = [str(r.get("id")) for r in out_rows]

    # ids
    cnt = collections.Counter(out_ids)
    missing = [i for i in batch_ids if i not in cnt]
    extra = [i for i in cnt if i not in rec]
    dup = [i for i, n in cnt.items() if n > 1]
    if missing:
        fail("ids", f"{len(missing)} batch id(s) missing", missing)
    if extra:
        fail("ids", f"{len(extra)} id(s) not in the batch", extra)
    if dup:
        fail("ids", f"{len(dup)} id(s) more than once", dup)
    if not (missing or extra or dup) and out_ids != batch_ids:
        pos = next(k for k, (a, b) in enumerate(zip(out_ids, batch_ids)) if a != b)
        fail("ids", f"rows not in batch order from row {pos + 1}",
             [out_ids[pos]])

    cats = set(vocab["categories"])
    keep_cats = set(vocab["keep_categories"])
    excl = set(vocab["exclusions"]) if vocab.get("exclusions") else None
    themes = set(vocab["themes"]) if vocab.get("themes") else None
    has_excl = any("exclusion" in r for r in out_rows)
    has_theme = any("theme" in r for r in out_rows)

    confs = []
    bad = collections.defaultdict(list)
    for r in out_rows:
        i = str(r.get("id"))
        v = str(r.get("verdict") or "").strip().lower()
        c = str(r.get("category") or "").strip()
        e = str(r.get("exclusion") or "").strip()
        t = str(r.get("theme") or "").strip()
        b = rec.get(i, {})
        no_abs = not str(b.get("abstract") or "").strip()
        if v not in ("keep", "discard"):
            bad["verdict not keep/discard"].append(i)
        if c not in cats:
            bad["category not in vocabulary"].append(i)
        if v == "keep" and c in cats and c not in keep_cats:
            bad["keep with a discard category"].append(i)
        if v == "keep" and b and no_abs:
            bad["keep of a record without an abstract"].append(i)
        if has_excl:
            if v == "keep" and e not in EMPTY:
                bad["keep with an exclusion"].append(i)
            if v == "discard" and e in EMPTY:
                bad["discard without an exclusion"].append(i)
            if v == "discard" and excl and e not in EMPTY and e not in excl:
                bad["exclusion not in vocabulary"].append(i)
        elif v == "discard" and c in keep_cats and r.get("no_abstract") not in (True, "true", "True"):
            bad["discard with a keep category, no exclusion or no_abstract"].append(i)
        if has_theme:
            if v == "discard" and t not in EMPTY:
                bad["discard with a theme"].append(i)
            if themes and t not in EMPTY and t not in themes:
                bad["theme not in vocabulary"].append(i)
        try:
            cf = float(r.get("confidence"))
            if not 0 <= cf <= 1:          # also false for NaN
                raise ValueError
            confs.append(round(cf, 4))
        except (TypeError, ValueError):
            fail("confidence", f"not a number in [0,1]: {r.get('confidence')!r}", [i])
        reason = str(r.get("reason") or "")
        if len(reason.split()) < 2 or PLACEHOLDER.search(reason):
            fail("reasons", f"empty, one-word or placeholder reason: "
                 f"{reason[:60]!r}", [i])
        elif "\t" in reason or "\n" in reason:
            fail("reasons", "tab or newline inside the reason", [i])
    for msg, ids in bad.items():
        fail("columns", f"{len(ids)} row(s): {msg}", ids)

    # duplicate reasons
    groups = collections.defaultdict(list)
    for r in out_rows:
        nr = norm_reason(r.get("reason"))
        if nr:
            groups[nr].append(r)
    for nr, rows in groups.items():
        titles = {norm_text(rec.get(str(r.get("id")), {}).get("title")) for r in rows}
        if len(titles) > opts.max_dup:
            fail("duplicates",
                 f"{len(rows)} rows ({len(titles)} distinct titles) share the "
                 f"reason {nr[:100]!r}", [r.get("id") for r in rows])

    # flat confidence.  Values at or above --flat-ignore-above are not
    # candidates: a batch of plainly off-topic records, each with its own
    # reason, legitimately sits at the top of the scale (seen in 11 of 194
    # real batches); the defaulted batches sat flat in the middle (0.6, 0.7).
    n = len(confs)
    mid = collections.Counter(c for c in confs if c < opts.flat_ignore_above)
    if n >= opts.flat_min_rows and mid:
        val, top = mid.most_common(1)[0]
        if top / n > opts.flat_share:
            fail("flat-conf",
                 f"confidence {val:g} on {top} of {n} rows "
                 f"({top / n:.0%} > {opts.flat_share:.0%})")

    # long runs of near-identical rows
    k = 0
    while k < len(out_rows):
        a = out_rows[k]
        ra = norm_reason(a.get("reason"))
        j = k + 1
        while j < len(out_rows):
            b = out_rows[j]
            if (b.get("verdict"), b.get("category")) != (a.get("verdict"), a.get("category")):
                break
            rb = norm_reason(b.get("reason"))
            if rb != ra and difflib.SequenceMatcher(None, ra, rb).ratio() < opts.run_similarity:
                break
            j += 1
        if j - k > opts.max_run:
            fail("runs", f"rows {k + 1}-{j}: {j - k} consecutive rows "
                 f"{a.get('verdict')}/{a.get('category')} with near-identical "
                 f"reasons {ra[:80]!r}", [r.get("id") for r in out_rows[k:j]])
        k = j

    # quote check
    hay = {i: norm_text(f"{r.get('title') or ''} {r.get('abstract') or ''}")
           for i, r in rec.items()}
    nquotes = 0
    qkinds = collections.Counter()
    for r in out_rows:
        i = str(r.get("id"))
        if i not in hay:
            continue
        own = hay[i]
        for q in quotes_in(str(r.get("reason") or "")):
            frs = list(fragments(q))
            if not frs:
                continue
            nquotes += 1
            missing_frs = [f for f in frs if f not in own]
            if not missing_frs:
                continue
            elsewhere = [o for o, h in hay.items()
                         if o != i and all(f in h for f in missing_frs)]
            ws = [w for f in missing_frs for w in words(f)]
            own_words = set(words(own))
            share = sum(w in own_words for w in ws) / max(len(ws), 1)
            if elsewhere:
                kind = "mixup"
            elif share >= 0.75:
                kind = "paraphrase"
            else:
                kind = "unsupported"
            qkinds[kind] += 1
            msg = f"{kind}: {q[:100]!r}"
            if elsewhere:
                msg += f" (found verbatim in {elsewhere[0]})"
            fail("quotes", msg, [i])

    stats = {
        "rows": len(out_rows),
        "batch_rows": len(batch_rows),
        "verdict_category": {f"{v}/{c}": m for (v, c), m in collections.Counter(
            (r.get("verdict"), r.get("category")) for r in out_rows).most_common()},
        "confidence_top": [[v, m] for v, m in collections.Counter(confs).most_common(3)],
        "distinct_reasons": len(groups),
        "quotes_checked": nquotes,
        "quote_failures": dict(qkinds),
    }
    return fails, stats


# ------------------------------------------------------------------ main

def load_vocab(args):
    vocab = {"categories": DEFAULT_CATEGORIES, "keep_categories": DEFAULT_KEEP,
             "exclusions": None, "themes": None}
    if args.config:
        try:
            with open(args.config, encoding="utf-8") as f:
                cfg = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            raise UsageError(f"cannot read config {args.config}: {e}")
        for k, v in cfg.items():
            k = k.replace("-", "_")
            if k not in vocab:
                raise UsageError(f"config: unknown key {k!r}")
            vocab[k] = list(v)
    for k in vocab:
        v = getattr(args, k)
        if v:
            vocab[k] = [x.strip() for x in v.split(",") if x.strip()]
    if not set(vocab["keep_categories"]) <= set(vocab["categories"]):
        raise UsageError("keep categories must be among the categories")
    return vocab


def parse_args(argv):
    p = argparse.ArgumentParser(
        description="Validate an agent screener's output against its batch.",
        epilog="Exit codes: 0 clean, 1 failures, 2 usage error.")
    p.add_argument("output", help="screener output (TSV with header, or JSONL)")
    p.add_argument("batch", help="batch input (JSON array, JSONL or TSV)")
    p.add_argument("--json", action="store_true", help="print a JSON report")
    p.add_argument("--config", help="JSON file with vocabularies")
    p.add_argument("--columns",
                   help="comma list naming the columns of a header-less "
                        "OUTPUT TSV, e.g. id,verdict,category,exclusion,"
                        "theme,confidence,reason")
    p.add_argument("--csv-quoting", action="store_true",
                   help="the TSVs were written by csv.writer (fields in "
                        "doubled quotes); default: fields as written")
    p.add_argument("--categories", help="comma list of categories")
    p.add_argument("--keep-categories", dest="keep_categories",
                   help="comma list of categories a keep may have")
    p.add_argument("--exclusions", help="comma list of exclusion tags")
    p.add_argument("--themes", help="comma list of themes")
    p.add_argument("--max-dup", type=int, default=3,
                   help="rows (distinct titles) that may share a reason (3)")
    p.add_argument("--flat-share", type=float, default=0.6,
                   help="largest share of one confidence value (0.6)")
    p.add_argument("--flat-min-rows", type=int, default=20,
                   help="batch size from which flat confidence is checked (20)")
    p.add_argument("--flat-ignore-above", type=float, default=0.9,
                   help="confidences at or above this are not checked for "
                        "flatness (0.9; 1.01 checks all)")
    p.add_argument("--max-run", type=int, default=5,
                   help="longest allowed run of near-identical rows (5)")
    p.add_argument("--run-similarity", type=float, default=0.9,
                   help="reason similarity that counts as near-identical (0.9)")
    p.add_argument("--max-print", type=int, default=20,
                   help="failures listed in the human summary (20)")
    return p.parse_args(argv)


def main(argv=None):
    try:
        args = parse_args(argv)
    except SystemExit as e:
        return 0 if e.code == 0 else 2
    try:
        vocab = load_vocab(args)
        cols = [c.strip() for c in args.columns.split(",")] if args.columns else None
        out_raw, out_fmt = read_records(args.output, cols, args.csv_quoting)
        batch_raw, batch_fmt = read_records(args.batch, None, args.csv_quoting)
        broken = [r.get("__unparsable__") or r.get("__columns__")
                  for r in batch_raw if "__unparsable__" in r or "__columns__" in r]
        if broken:
            raise UsageError(f"{args.batch}: unreadable record, {broken[0]}")
        out_rows, _ = normalise_rows(out_raw, REQUIRED, args.output)
        batch_rows, _ = normalise_rows(batch_raw, ["id"], args.batch)
        bkeys = set().union(*(r.keys() for r in batch_raw)) if batch_raw else set()
        for need in ("title", "abstract"):
            if need not in {k.lower() for k in bkeys}:
                raise UsageError(f"{args.batch}: no {need} field")
        lower = [{k.lower(): v for k, v in r.items()} for r in batch_raw]
        for b, raw in zip(batch_rows, lower):
            b["title"] = raw.get("title")
            b["abstract"] = raw.get("abstract")
    except UsageError as e:
        print(f"validate_screen: {e}", file=sys.stderr)
        return 2
    fails, stats = check(out_rows, batch_rows, vocab, args)
    if args.json:
        json.dump({"output": args.output, "batch": args.batch,
                   "formats": [out_fmt, batch_fmt], "ok": not fails,
                   "stats": stats, "failures": fails},
                  sys.stdout, ensure_ascii=False, indent=1)
        print()
    else:
        status = "OK" if not fails else f"FAIL ({len(fails)} failures)"
        print(f"{args.output}: {stats['rows']} rows for {stats['batch_rows']} "
              f"batch records; {status}")
        print(f"  verdict/category: {stats['verdict_category']}")
        print(f"  top confidences: {stats['confidence_top']}; distinct reasons: "
              f"{stats['distinct_reasons']}; quotes checked: {stats['quotes_checked']}")
        by = collections.Counter(f["check"] for f in fails)
        if by:
            print(f"  failures by check: {dict(by)}")
        for f in fails[:args.max_print]:
            ids = f["ids"]
            shown = ", ".join(str(x) for x in ids[:3]) + (f" (+{len(ids) - 3})" if len(ids) > 3 else "")
            print(f"  [{f['check']}] {f['message']}" + (f" -- {shown}" if ids else ""))
        if len(fails) > args.max_print:
            print(f"  ... {len(fails) - args.max_print} more (use --json)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
