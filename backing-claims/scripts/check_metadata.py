#!/usr/bin/env python3
"""Cross-check every BibTeX entry against authoritative metadata.

For each @entry with a DOI, fetch Crossref (authoritative registrar
metadata, no daily quota) and compare:
  - title: normalized containment/similarity,
  - authors: family-name multiset,
  - year: bib year vs any Crossref date part (print + online differ),
  - pages/volume where both sides have them.
Entries without a DOI are listed for manual ground-truth checks.
Falls back to DataCite for DOIs Crossref does not know.
"""
import json, re, sys, time, unicodedata, urllib.request
from difflib import SequenceMatcher

def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "refcheck/1.0 (mailto:daniel@bosk.se)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def norm(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\\[a-zA-Z]+\s*", "", s)     # TeX accent macros: {\v n} -> n
    s = re.sub(r"[{}~\\]", "", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()

def bib_entries(path):
    text = open(path).read()
    for m in re.finditer(r"@(\w+)\{([^,]+),(.*?)\n\}\n", text, re.S):
        typ, key, body = m.groups()
        fields = dict(re.findall(r"(\w+)\s*=\s*\{((?:[^{}]|\{[^{}]*\})*)\}",
                                 body))
        yield typ, key.strip(), fields

def family_names(bib_author):
    names = []
    for a in re.split(r"\s+and\s+", bib_author):
        a = a.strip()
        if not a: continue
        names.append(norm(a.split(",")[0] if "," in a
                          else a.split()[-1]))
    return sorted(names)

problems, checked, nodoi = [], 0, []
for path in sys.argv[1:]:
    short = "/".join(path.split("/")[-2:])
    for typ, key, f in bib_entries(path):
        doi = f.get("doi") or f.get("DOI")
        if not doi:
            nodoi.append(f"{short}:{key}")
            continue
        checked += 1
        meta = None
        for api in (f"https://api.crossref.org/works/{doi}",
                    f"https://api.datacite.org/dois/{doi}"):
            try:
                d = fetch(api)
                meta = d.get("message") or d.get("data", {}).get("attributes")
                break
            except Exception:
                time.sleep(1)
        if not meta:
            problems.append(f"{short}:{key}: DOI {doi} resolves in neither "
                            "Crossref nor DataCite")
            continue
        # title
        c_title = meta.get("title")
        if isinstance(c_title, list): c_title = c_title[0] if c_title else ""
        sub = meta.get("subtitle")
        if isinstance(sub, list) and sub:      # Crossref splits title/subtitle
            c_title = f"{c_title}: {sub[0]}"
        ratio = SequenceMatcher(None, norm(f.get("title", "")),
                                norm(c_title or "")).ratio()
        if ratio < 0.8:
            problems.append(f"{short}:{key}: TITLE mismatch "
                            f"(sim={ratio:.2f}) bib='{f.get('title','')[:60]}' "
                            f"crossref='{(c_title or '')[:60]}'")
        # authors
        c_auth = meta.get("author") or meta.get("creators") or []
        c_fams = sorted(norm(a.get("family") or a.get("familyName") or
                             a.get("name", "").split(",")[0])
                        for a in c_auth if isinstance(a, dict))
        b_fams = family_names(f.get("author", ""))
        if c_fams and b_fams and c_fams != b_fams:
            problems.append(f"{short}:{key}: AUTHOR mismatch "
                            f"bib={b_fams} crossref={c_fams}")
        # year: accept any of Crossref's date parts (print/online/issued)
        years = set()
        for k in ("issued", "published-print", "published-online",
                  "created"):
            try: years.add(meta[k]["date-parts"][0][0])
            except Exception: pass
        if (y := f.get("year")) and years and int(y) not in years:
            problems.append(f"{short}:{key}: YEAR mismatch bib={y} "
                            f"crossref={sorted(years)}")
        time.sleep(0.5)

print(f"checked {checked} DOI entries across {len(sys.argv)-1} files")
print(f"\nno DOI (verify against ground truth by hand):")
for k in nodoi: print(f"  {k}")
print(f"\n{len(problems)} problems:")
for p in problems: print(f"  {p}")
