#!/usr/bin/env python3
"""Check a keyword search with a search by meaning.

Asks OpenAlex's semantic search (`search.semantic`: embeddings of title,
abstract and venue; at most 50 works per question) one or more questions
in plain language and reports, for every work returned, how the given
scholar sessions classified it: bearing (supports/qualifies), adjacent,
another topic, or not in our records.  A relevant work that is "not in
our records" is a gap in the keyword queries.

The sessions are only read.  Write the questions down BEFORE running, one
per concept of the claim, and keep the output with the record of the
search: this is a documented complement, not the search itself (it gives
no count of matches, so "the search found none" cannot rest on it).

Usage:
  semantic_check.py -s SESSION [-s SESSION ...] [-t DOI-OR-TITLE-PART ...]
                    [-o OUTDIR] "question one" ["question two" ...]

  -s  scholar session to compare against (repeatable)
  -t  a known study to locate in the results, by DOI or by a part of its
      title (repeatable); its place is printed
  -o  directory for <n>.json (raw results) and <n>.txt (the list); default .
"""
import argparse
import collections
import json
import os
import re
import sys
import time
import unicodedata


def _reexec_under_scholar_python():
    """Re-run this script with the Python that has `scholar` installed
    (the interpreter named in the scholar command's first line)."""
    import shutil
    cmd = shutil.which("scholar") or os.path.expanduser("~/.local/bin/scholar")
    try:
        first = open(cmd, encoding="utf-8", errors="ignore").readline().strip()
    except OSError:
        sys.exit("cannot import scholar and cannot find the scholar command")
    interpreter = first[2:].split()[0] if first.startswith("#!") else ""
    if not interpreter or interpreter == sys.executable:
        sys.exit("scholar's interpreter cannot import scholar")
    os.execv(interpreter, [interpreter, __file__] + sys.argv[1:])


try:
    import pyalex  # type: ignore
    import requests  # type: ignore
    from scholar.providers import get_provider  # type: ignore
except ImportError:
    _reexec_under_scholar_python()

CATS = ["supports-claim", "qualifies-claim", "adjacent-subtopic", "off-topic-false-hit"]
SESSIONS = os.path.expanduser("~/.local/share/scholar/review_sessions")


def norm(title):
    text = unicodedata.normalize("NFKD", title or "").lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()[:70]


def index(sessions):
    idx = collections.defaultdict(set)
    for name in sessions:
        path = os.path.join(SESSIONS, name + ".json")
        if not os.path.exists(path):
            sys.exit(f"no such session: {name} ({path})")
        for dec in json.load(open(path, encoding="utf-8"))["decisions"]:
            cat = [t for t in dec["tags"] if t in CATS]
            value = cat[0] if cat else dec["status"]
            paper = dec["paper"]
            if paper.get("doi"):
                idx["doi:" + paper["doi"].lower()].add(value)
            if norm(paper.get("title")):
                idx["ti:" + norm(paper.get("title"))].add(value)
    return idx


def classify(idx, work):
    doi = (work.get("doi") or "").lower().replace("https://doi.org/", "")
    hit = (idx.get("doi:" + doi, set()) if doi else set()) | idx.get("ti:" + norm(work.get("title")), set())
    if hit & {"supports-claim", "qualifies-claim", "kept"}:
        return "bearing"
    if "adjacent-subtopic" in hit:
        return "adjacent"
    return "another topic" if hit else "not in our records"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-s", "--session", action="append", required=True)
    ap.add_argument("-t", "--target", action="append", default=[])
    ap.add_argument("-o", "--outdir", default=".")
    ap.add_argument("questions", nargs="+")
    a = ap.parse_args()
    get_provider("openalex")  # configures pyalex (key, address) as scholar does
    key = pyalex.config.api_key
    idx = index(a.session)
    os.makedirs(a.outdir, exist_ok=True)
    for n, question in enumerate(a.questions, 1):
        params = {"search.semantic": question[:2000], "per_page": 50,
                  "select": "id,doi,title,publication_year,relevance_score"}
        if key:
            params["api_key"] = key
        r = requests.get("https://api.openalex.org/works", params=params, timeout=60)
        if r.status_code != 200:
            body = r.text[:200].replace(key, "<key>") if key else r.text[:200]
            print(f"== question {n}: FAILED (HTTP {r.status_code}): {body}\n   {question}")
            continue
        works = r.json()["results"]
        json.dump({"question": question, "results": works},
                  open(os.path.join(a.outdir, f"{n}.json"), "w"), indent=0)
        tally = collections.Counter()
        rows = []
        places = collections.defaultdict(list)
        for i, w in enumerate(works, 1):
            cl = classify(idx, w)
            tally[cl] += 1
            doi = (w.get("doi") or "").lower()
            for t in a.target:
                if t.lower() in doi or t.lower() in (w.get("title") or "").lower():
                    places[t].append(i)
            rows.append(f"{i:2d} {cl:18s} {w.get('publication_year')} {(w.get('title') or '')[:100]}")
        open(os.path.join(a.outdir, f"{n}.txt"), "w").write(f"# {question}\n" + "\n".join(rows) + "\n")
        print(f"== question {n}: {question}")
        print(f"   {len(works)} works: " + ", ".join(f"{v} {k}" for k, v in tally.most_common()))
        for t in a.target:
            print(f"   known study '{t}': " + (f"place {places[t][0]}" if places[t] else "not returned"))
        for row in rows:
            if "not in our records" in row or "bearing" in row:
                print("   " + row)
        time.sleep(1.1)  # the endpoint allows one request a second


if __name__ == "__main__":
    main()
