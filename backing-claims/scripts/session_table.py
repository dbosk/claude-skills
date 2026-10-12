#!/usr/bin/env python3
"""Turn a classified scholar session CSV into an auditable LaTeX longtable.

The table lists EVERY candidate a search returned, with the reason it was
kept or excluded, so a reader of the appendix can audit the screening
without access to the repository.  Rows are grouped

  cited > supports the claim > qualifies/contradicts it > adjacent
  subtopic > off-topic false hit > still pending > other (duplicates,
  reprints, errata of cited sources),

and machine-decided rows show the model's confidence.

Input: the CSV written by `scholar sessions export <session>` after the
session was classified with `scholar llm classify` (columns used: status,
title, year, provider, tags, decision_source, llm_confidence,
llm_review_outcome).  Tags may be separated by ";" or "|".  A row is

  * cited      -- kept by a human decision (decision_source human or
                  llm_reviewed) with a THEME tag (any tag that is neither a
                  category nor a bookkeeping tag) or no tag at all; --theme
                  maps the tag to text and, when given, is the allowlist
                  of theme tags (other free tags are shown as notes);
  * a category -- the LAST of supports-claim / qualifies-claim /
                  adjacent-subtopic / off-topic-false-hit present
                  (`sessions decide -t` appends, so the last one decides);
  * excluded   -- discarded although its category bears on the claim
                  (supports/qualifies): the status wins, so the row reads
                  "supports the claim, excluded", sorts among the other
                  rows and is counted on its own in the caption;
  * bookkeeping-- duplicate-record-of-cited-source, reprint, extended
                  report, earlier version, thesis, erratum, no-abstract:
                  shown as a parenthesised note, or as the reason when
                  nothing else applies.

Machine-labelled rows (decision_source llm, or an LLM decision a human
confirmed unchanged) show the model's confidence, or "n/a"/"saknas" when
none was recorded.

The caption's database sentence names the providers that occur in the
rows.  A session CSV records neither the searches that found nothing nor
those that failed, so a provider that answered every query with zero
hits is missing from the sentence, and partial failures are not noted:
`scholar sessions export -f table`, which reads the session's search
records, gets both right.

Fallback for a scholar without `sessions export -f table`; the rules
above follow that command.

Example:
  session_table.py --csv litteratursokning/dry-principle.csv \
      --label sok-dry --track "DRY-principen" --lang sv \
      --theme clones-faults="klonfel vid inkonsekvent ändring" \
      -o litteratursokning/dry-principle-full.tex
"""
import argparse
import csv
import pathlib
import re
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
BEARING_ORDER = 2   # categories up to this one bear on the claim
PENDING_ORDER = 5
OTHER_ORDER = 6

STRINGS = {
    "sv": {
        "cited": "citerad",
        "supports-claim": "stöder påståendet",
        "qualifies-claim": "kvalificerar eller motsäger påståendet",
        "adjacent-subtopic": "angränsande delämne",
        "off-topic-false-hit": "annat ämne (felträff)",
        "pending": "ej klassad",
        "excluded": "utesluten",
        "no_confidence": "saknas",
        "notes": {
            "duplicate-record-of-cited-source": "dubblettpost av citerad källa",
            "duplicate-reprint-of-cited-source": "omtryck av citerad källa",
            "extended-tech-report": "utökad rapportversion av citerad källa",
            "earlier-version-of-cited-source": "tidigare version av citerad källa",
            "superseded-by-journal-version": "ersatt av tidskriftsversionen",
            "thesis-of-cited-source": "avhandling bakom citerad källa",
            "erratum-to-cited-source": "erratum till citerad källa",
            "recorded-not-cited": "noterad, inte citerad",
            "no-abstract-title-only": "bedömd på titel, sammanfattning saknas",
        },
        "head": ("Titel", "År", "Leverantör", "Skäl"),
        "cont": "\\GetTranslation{continued}",
        "next": "\\GetTranslation{continued on the next page}",
        "caption": ("Fullständig träfflista, %(track)s: %(n)d unika poster, "
                    "varav %(cit)d citerade, %(sup)d stöder påståendet, "
                    "%(qual)d kvalificerar eller motsäger det, %(adj)d "
                    "angränsande och %(off)d felträffar%(pend)s%(oth)s.  "
                    "Skälet till varje in- eller uteslutning står i sista "
                    "kolumnen; för maskinklassade rader anges modellens "
                    "konfidens.  %(databases)s"),
        "pendcap": ", %d ej klassade",
        "othcap": ", %d dubbletter eller andra versioner av citerade källor",
        "bearing": ("Träffar som rör påståendet, %(track)s: %(cit)d citerade, "
                    "%(sup)d som stöder påståendet och %(qual)d som "
                    "kvalificerar eller motsäger det, av %(n)d unika poster; "
                    "de %(adj)d angränsande och %(off)d felträffarna%(pend)s"
                    "%(oth)s listas inte.  Skälet står i sista kolumnen; för "
                    "maskinklassade rader anges modellens konfidens.  "
                    "%(databases)s"),
        "exclcap": ", %d uteslutna trots att de klassats som relevanta för "
                   "påståendet",
        "databases": "Databaser: %s.",
        "openalex_note": "inte \\foreignlanguage{english}{open access}",
    },
    "en": {
        "cited": "cited",
        "supports-claim": "supports the claim",
        "qualifies-claim": "qualifies or contradicts the claim",
        "adjacent-subtopic": "adjacent subtopic",
        "off-topic-false-hit": "other topic (false hit)",
        "pending": "pending, unclassified",
        "excluded": "excluded",
        "no_confidence": "n/a",
        "notes": {
            "duplicate-record-of-cited-source": "duplicate record of a cited source",
            "duplicate-reprint-of-cited-source": "reprint of a cited source",
            "extended-tech-report": "extended report version of a cited source",
            "earlier-version-of-cited-source": "earlier version of a cited source",
            "superseded-by-journal-version": "superseded by the journal version",
            "thesis-of-cited-source": "thesis behind a cited source",
            "erratum-to-cited-source": "erratum to a cited source",
            "recorded-not-cited": "recorded, not cited",
            "no-abstract-title-only": "judged on title, no abstract available",
        },
        "head": ("Title", "Year", "Provider", "Reason"),
        "cont": "\\GetTranslation{continued}",
        "next": "\\GetTranslation{continued on the next page}",
        "caption": ("Full hit list, %(track)s: %(n)d unique records, of which "
                    "%(cit)d cited, %(sup)d support the claim, %(qual)d "
                    "qualify or contradict it, %(adj)d adjacent and %(off)d "
                    "false hits%(pend)s%(oth)s.  The last column gives the "
                    "reason for inclusion or exclusion; machine-classified "
                    "rows show the model's confidence.  %(databases)s"),
        "pendcap": ", %d unclassified",
        "othcap": ", %d duplicates or other versions of cited sources",
        "bearing": ("Records bearing on the claim, %(track)s: %(cit)d cited, "
                    "%(sup)d supporting and %(qual)d qualifying or "
                    "contradicting it, out of %(n)d unique records; the "
                    "%(adj)d adjacent and %(off)d false hits%(pend)s%(oth)s "
                    "are not listed.  The last column gives the reason; "
                    "machine-classified rows show the model's confidence.  "
                    "%(databases)s"),
        "exclcap": ", %d excluded although classified as bearing on the "
                   "claim",
        "databases": "Databases: %s.",
        "openalex_note": "not open access",
    },
}

# provider -> (code in the Provider column, full name), in caption order;
# the same names as `scholar sessions export -f table`.
PROVIDERS = {
    "openalex": ("OA", "OpenAlex"),
    "dblp": ("DBLP", "DBLP"),
    "ieee": ("IEEE", "IEEE Xplore"),
    "wos": ("WoS", "Web of Science"),
    "scopus": ("Scopus", "Scopus"),
    "s2": ("S2", "Semantic Scholar"),
    "arxiv": ("arXiv", "arXiv"),
    "hal": ("HAL", "HAL"),
    "ssrn": ("SSRN", "SSRN"),
    "biorxiv": ("bioRxiv", "bioRxiv"),
    "medrxiv": ("medRxiv", "medRxiv"),
    "chemrxiv": ("ChemRxiv", "ChemRxiv"),
    "researchsquare": ("RSq", "Research Square"),
    "preprintsorg": ("Preprints", "Preprints.org"),
    "iacr": ("IACR", "IACR Cryptology ePrint Archive"),
}
PROVIDER_SHORT = {k: short for k, (short, _) in PROVIDERS.items()}

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
    parts = [x.strip() for x in re.split(r"[|,;]", p or "") if x.strip()]
    return [PROVIDER_SHORT.get(x.lower(), x) for x in parts]


def confidence_for(row, strings):
    """" (0.83)" for a machine-labelled row, " (n/a)" without a value, else ""."""
    src = (row.get("decision_source") or "").strip().lower()
    outcome = (row.get("llm_review_outcome") or "").strip().lower()
    if not (src == "llm" or (src == "llm_reviewed" and outcome != "changed")):
        return ""
    try:
        return " (%.2f)" % float((row.get("llm_confidence") or "").strip())
    except ValueError:
        return " (%s)" % strings["no_confidence"]


def reason_for(row, strings, themes):
    """(reason label, sort order, excluded) for one CSV row."""
    status = (row.get("status") or "").strip().lower()
    tags = [t.strip() for t in re.split(r"[;|]", row.get("tags") or "") if t.strip()]
    src = (row.get("decision_source") or "").strip().lower()
    notes = strings["notes"]
    category = next((t for t in reversed(tags) if t in CATEGORY_ORDER), None)
    note_texts = [notes[t] for t in tags if t in notes]
    theme_tags = [t for t in tags if t not in CATEGORY_ORDER and t not in notes]
    if themes:   # --theme is an allowlist; other free tags become notes
        note_texts += [tex(t) for t in theme_tags if t not in themes]
        theme_tags = [t for t in theme_tags if t in themes]
    human = src != "llm"     # human, or an LLM decision a human reviewed
    conf = confidence_for(row, strings)

    # A row a human kept with a theme tag (or no tag) is a cited source,
    # even if the model's category tag is still attached (`scholar
    # sessions decide -t` appends rather than replaces).  A theme tag on
    # an unreviewed LLM row is a copied tag, not a citation.
    if status == "pending":
        return strings["pending"], PENDING_ORDER, False
    if status == "kept" and human and (theme_tags or not tags):
        label = "\\emph{%s}" % strings["cited"]
        if theme_tags:
            label += ": " + tex(themes.get(theme_tags[0], theme_tags[0]))
        order = 0
    elif (status == "discarded" and category is not None
          and CATEGORY_ORDER[category] <= BEARING_ORDER):
        # The status wins: a discarded row never counts as evidence.
        label = "%s%s, %s" % (strings[category], conf, strings["excluded"])
        if note_texts:
            label += " (" + "; ".join(note_texts) + ")"
        return label, OTHER_ORDER, True
    elif category is not None:
        label, order = strings[category] + conf, CATEGORY_ORDER[category]
    elif note_texts:
        return "; ".join(note_texts), OTHER_ORDER, False
    elif not tags:
        return strings["pending"], PENDING_ORDER, False
    else:
        return tex(tags[0]) + conf, OTHER_ORDER, False
    if note_texts:
        label += " (" + "; ".join(note_texts) + ")"
    return label, order, False


def databases_sentence(rows, strings):
    """Name the providers in the rows, full name first, in caption order."""
    used = []
    for r in rows:
        for p in r["prov"]:
            if p not in used:
                used.append(p)
    names = []
    for key, (short, full) in PROVIDERS.items():
        if short not in used:
            continue
        notes = [] if full == short else [short]
        if key == "openalex":
            notes.append(strings["openalex_note"])
        names.append("%s (%s)" % (full, "; ".join(notes)) if notes else full)
        used.remove(short)
    names += [tex(p) for p in used]
    return strings["databases"] % ", ".join(names) if names else ""


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
            reason, order, excluded = reason_for(r, strings, themes)
            key = (title.lower(), year)
            if key in seen:                   # merge provider duplicates
                cur = seen[key]
                for p in prov:
                    if p and p not in cur["prov"]:
                        cur["prov"].append(p)
                if order < cur["order"]:      # the better-placed decision wins
                    cur.update(status=status, reason=reason, order=order,
                               excluded=excluded)
            else:
                seen[key] = dict(title=tex(title)[:180], year=year, prov=prov,
                                 status=status, reason=reason, order=order,
                                 excluded=excluded)
    return list(seen.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", required=True, help="session CSV from `scholar sessions export`")
    ap.add_argument("--label", required=True, help="LaTeX label suffix: \\label{tab:<label>}")
    ap.add_argument("--track", default="", help="free text for the caption, e.g. 'sökspår 1'")
    ap.add_argument("--lang", choices=sorted(STRINGS), default="sv")
    ap.add_argument("--theme", action="append", default=[],
                    metavar="TAG=TEXT", help="readable reason for a cited source's theme tag")
    ap.add_argument("--bearing-only", action="store_true",
                    help="list only cited/supports/qualifies rows; adjacent and "
                         "off-topic records appear as counts in the caption")
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
    excluded = sum(1 for r in rows if r["excluded"])
    listed = [r for r in rows if r["order"] <= 2] if args.bearing_only else rows
    body = "\n".join("%s & %s & %s & %s \\\\" % (
        r["title"], r["year"], ", ".join(r["prov"]), r["reason"]) for r in listed)
    caption = strings["bearing" if args.bearing_only else "caption"] % {
        "track": tex(args.track) or args.label,
        "n": len(rows), "cit": counts[0], "sup": counts[1], "qual": counts[2],
        "adj": counts[3], "off": counts[4],
        "pend": (strings["pendcap"] % counts[5]) if counts[5] else "",
        "oth": ((strings["othcap"] % (counts[6] - excluded))
                if counts[6] - excluded else "")
               + ((strings["exclcap"] % excluded) if excluded else ""),
        "databases": databases_sentence(rows, strings)}
    h0, h1, h2, h3 = strings["head"]
    pathlib.Path(args.out).write_text(TABLE % {
        "caption": caption, "label": args.label, "h0": h0, "h1": h1, "h2": h2,
        "h3": h3, "cont": strings["cont"], "next": strings["next"], "body": body},
        encoding="utf-8")
    print(f"{csv_path.name}: {len(rows)} rows ({len(listed)} listed) | cited "
          f"{counts[0]}, supports {counts[1]}, qualifies {counts[2]}, adjacent "
          f"{counts[3]}, off-topic {counts[4]}, pending {counts[5]}, other "
          f"{counts[6]} (excluded {excluded}) -> {args.out}")


if __name__ == "__main__":
    main()
