#!/usr/bin/env python3
"""Turn a classified scholar session CSV into an auditable LaTeX longtable.

The table lists EVERY candidate a search returned, with the reason it was
kept or excluded, so a reader of the appendix can audit the screening
without access to the repository.  Rows are grouped

  cited > supports the claim > qualifies/contradicts it > adjacent
  subtopic > off-topic false hit > still pending (unclassified),

and machine-decided rows show the model's confidence.

Input: the CSV written by `scholar sessions export <session>` after the
session was classified with `scholar llm classify` (columns used: status,
title, year, provider, tags, decision_source, llm_confidence).

Interim implementation of the proposed `scholar sessions export --format
table`; drop this script when that command exists.

Example:
  session_table.py --csv litteratursokning/dry-principle.csv \
      --label sok-dry --track "DRY-principen" --lang sv \
      --theme dry-origin="principens ursprung" \
      -o litteratursokning/dry-principle-full.tex
"""
import argparse
import csv
import pathlib
import sys

# Unicode punctuation -> pdflatex-safe TeX (inputenc handles Latin accents).
PUNCT = {
    "“": "``", "”": "''", "‘": "`", "’": "'",
    "–": "--", "—": "---", "…": r"\dots{}",
    " ": " ", " ": " ", "​": "", "﻿": "",
    "ʼ": "'", "′": "'", "­": "",
}
SPECIAL = {"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
           "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
           "^": r"\textasciicircum{}", "\\": r"\textbackslash{}"}

# Category tag -> sort order.  0 is reserved for cited (kept + theme tag).
CATEGORY_ORDER = {
    "supports-claim": 1,
    "qualifies-claim": 2,
    "adjacent-subtopic": 3,
    "off-topic-false-hit": 4,
}
PENDING_ORDER = 5
UNKNOWN_ORDER = 6

STRINGS = {
    "sv": {
        "cited": "citerad",
        "supports-claim": "stöder påståendet",
        "qualifies-claim": "kvalificerar eller motsäger påståendet",
        "adjacent-subtopic": "angränsande delämne",
        "off-topic-false-hit": "annat ämne (felträff)",
        "pending": "ej klassad",
        "head": ("Titel", "År", "Databas", "Skäl"),
        "cont": "forts.",
        "next": "forts.\\ på nästa sida",
        "caption": ("Fullständig träfflista, %(track)s (session "
                    "\\texttt{%(sess)s}; %(n)d unika träffar: %(cit)d "
                    "citerade, %(sup)d stöder påståendet, %(qual)d "
                    "kvalificerar eller motsäger det, %(adj)d angränsande, "
                    "%(off)d felträffar%(pend)s).  Skälet till varje in- "
                    "eller uteslutning står i sista kolumnen; för "
                    "maskinklassade rader anges modellens konfidens."),
        "pendcap": ", %d ej klassade",
    },
    "en": {
        "cited": "cited",
        "supports-claim": "supports the claim",
        "qualifies-claim": "qualifies or contradicts the claim",
        "adjacent-subtopic": "adjacent subtopic",
        "off-topic-false-hit": "other field (false hit)",
        "pending": "unclassified",
        "head": ("Title", "Year", "Provider", "Reason"),
        "cont": "cont.",
        "next": "continued on next page",
        "caption": ("Full hit list, %(track)s (session \\texttt{%(sess)s}; "
                    "%(n)d unique hits: %(cit)d cited, %(sup)d support the "
                    "claim, %(qual)d qualify or contradict it, %(adj)d "
                    "adjacent, %(off)d false hits%(pend)s).  The last column "
                    "gives the reason for inclusion or exclusion; "
                    "machine-classified rows show the model's confidence."),
        "pendcap": ", %d unclassified",
    },
}

PROVIDER_SHORT = {"openalex": "OA", "dblp": "DBLP", "scopus": "Scopus",
                  "wos": "WoS", "ieee": "IEEE", "s2": "S2", "arxiv": "arXiv"}

TABLE = r"""\begingroup\footnotesize
\begin{longtable}{@{}%%
  >{\raggedright\arraybackslash}p{0.44\textwidth}c%%
  >{\raggedright\arraybackslash}p{0.13\textwidth}%%
  >{\raggedright\arraybackslash}p{0.26\textwidth}@{}}
\caption{%(caption)s}\label{tab:%(label)s}\\
\toprule
%(h0)s & %(h1)s & %(h2)s & %(h3)s \\
\midrule
\endfirsthead
\multicolumn{4}{@{}l}{\emph{\tablename~\thetable{} (%(cont)s)}}\\
\toprule %(h0)s & %(h1)s & %(h2)s & %(h3)s \\ \midrule
\endhead
\midrule \multicolumn{4}{r@{}}{\emph{%(next)s}}\\
\endfoot
\bottomrule
\endlastfoot
%(body)s
\end{longtable}
\endgroup
"""


def tex(s):
    s = s or ""
    for k, v in PUNCT.items():
        s = s.replace(k, v)
    out = []
    for ch in s:
        if ch in SPECIAL:
            out.append(SPECIAL[ch])
        elif ord(ch) > 0x2100:            # drop symbols pdflatex lacks
            out.append("")
        else:
            out.append(ch)
    return "".join(out).strip()


def short_provider(p):
    parts = [x.strip() for x in (p or "").replace("|", ",").split(",") if x.strip()]
    return ", ".join(PROVIDER_SHORT.get(x.lower(), x) for x in parts)


def reason_for(row, strings, themes):
    """(reason label, sort order) for one CSV row."""
    status = (row.get("status") or "").strip().lower()
    tags = [t.strip() for t in (row.get("tags") or "").split("|") if t.strip()]
    tag = tags[0] if tags else ""
    conf = (row.get("llm_confidence") or "").strip()
    src = (row.get("decision_source") or "").strip().lower()
    if status == "kept" and tag not in CATEGORY_ORDER:
        theme = themes.get(tag, tag)
        return "\\emph{%s}: %s" % (strings["cited"], tex(theme)), 0
    if tag in CATEGORY_ORDER:
        label, order = strings[tag], CATEGORY_ORDER[tag]
    elif status == "pending" or not tag:
        return strings["pending"], PENDING_ORDER
    else:
        label, order = tex(tag), UNKNOWN_ORDER
    if src == "llm" and conf:
        try:
            label += " (%.2f)" % float(conf)
        except ValueError:
            pass
    return label, order


def rows_for(csv_path, strings, themes):
    seen = {}
    with open(csv_path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            title = (r.get("title") or "").strip()
            if not title:
                continue                      # scholar exports stray lines
            year = tex(r.get("year", ""))
            prov = short_provider(r.get("provider", ""))
            status = (r.get("status") or "").strip().lower()
            reason, order = reason_for(r, strings, themes)
            key = (title.lower(), year)
            if key in seen:                   # merge provider duplicates
                cur = seen[key]
                for p in prov.split(", "):
                    if p and p not in cur["prov"]:
                        cur["prov"].append(p)
                if status == "kept" and cur["status"] != "kept":
                    cur.update(status="kept", reason=reason, order=order)
                elif cur["order"] > order and cur["status"] != "kept":
                    cur.update(reason=reason, order=order)
            else:
                seen[key] = dict(title=tex(title)[:180], year=year,
                                 prov=[p for p in prov.split(", ") if p],
                                 status=status, reason=reason, order=order)
    return list(seen.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", required=True, help="session CSV from `scholar sessions export`")
    ap.add_argument("--label", required=True, help="LaTeX label suffix: \\label{tab:<label>}")
    ap.add_argument("--track", default="", help="free text for the caption, e.g. 'sökspår 1'")
    ap.add_argument("--session", default=None, help="session name for the caption (default: CSV stem)")
    ap.add_argument("--lang", choices=sorted(STRINGS), default="sv")
    ap.add_argument("--theme", action="append", default=[],
                    metavar="TAG=TEXT", help="readable reason for a cited source's theme tag")
    ap.add_argument("-o", "--out", required=True, help="output .tex path")
    args = ap.parse_args()

    strings = STRINGS[args.lang]
    themes = {}
    for spec in args.theme:
        if "=" not in spec:
            sys.exit(f"--theme expects TAG=TEXT, got {spec!r}")
        k, v = spec.split("=", 1)
        themes[k.strip()] = v.strip()

    csv_path = pathlib.Path(args.csv)
    if not csv_path.exists():
        sys.exit(f"no such CSV: {csv_path}")
    rows = rows_for(csv_path, strings, themes)
    if not rows:
        sys.exit(f"no rows with a title in {csv_path}")
    rows.sort(key=lambda r: (r["order"], r["title"].lower()))
    counts = {o: sum(1 for r in rows if r["order"] == o) for o in range(0, 7)}
    body = "\n".join("%s & %s & %s & %s \\\\" % (
        r["title"], r["year"], ", ".join(r["prov"]), r["reason"]) for r in rows)
    caption = strings["caption"] % {
        "track": tex(args.track) or args.label, "sess": args.session or csv_path.stem,
        "n": len(rows), "cit": counts[0], "sup": counts[1], "qual": counts[2],
        "adj": counts[3], "off": counts[4],
        "pend": (strings["pendcap"] % counts[5]) if counts[5] else ""}
    h0, h1, h2, h3 = strings["head"]
    pathlib.Path(args.out).write_text(TABLE % {
        "caption": caption, "label": args.label, "h0": h0, "h1": h1, "h2": h2,
        "h3": h3, "cont": strings["cont"], "next": strings["next"], "body": body},
        encoding="utf-8")
    print(f"{csv_path.name}: {len(rows)} rows | cited {counts[0]}, supports "
          f"{counts[1]}, qualifies {counts[2]}, adjacent {counts[3]}, off-topic "
          f"{counts[4]}, pending {counts[5]}, other {counts[6]} -> {args.out}")


if __name__ == "__main__":
    main()
