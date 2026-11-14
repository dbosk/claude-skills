#!/usr/bin/env python3
"""Add to a scholar session the OpenAlex records that match a query in
TITLE OR ABSTRACT.

scholar's OpenAlex provider searches the full text, which returns ten to a
hundred times what Web of Science or Scopus return for the same query.
This runs the provider's own code (paging, conversion, merge into the
session) with one function replaced: the query goes to OpenAlex's
`title_and_abstract.search` filter.  The search is recorded in the session
under the query prefixed with "title_and_abstract.search:", so the audit
table and `sessions show` keep the two kinds of OpenAlex search apart.

It relies on two internals of the provider (`_base_query`,
`_search_uncached`) and stops if they are missing; scholar 1.29 has them.
OpenAlex's abstracts are incomplete (some records hold one sentence, some
none), so this is NOT the same search as title/abstract in Web of Science.

Usage:
  openalex_title_abstract.py SESSION "query one" ["query two" ...]
Write each query as it was sent to OpenAlex (no TS=(...) wrapper).
"""
import datetime
import os
import sys


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
    from scholar.providers import get_provider  # type: ignore
    from scholar.review import create_review_session, save_session  # type: ignore
    from scholar.scholar import SearchResult  # type: ignore
except ImportError:
    _reexec_under_scholar_python()

PREFIX = "title_and_abstract.search:"


def main():
    if len(sys.argv) < 3 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    name, queries = sys.argv[1], sys.argv[2:]
    prov = get_provider("openalex")
    for attr in ("_base_query", "_search_uncached"):
        if not hasattr(prov, attr):
            sys.exit(f"scholar's OpenAlex provider has no {attr}: this script "
                     "needs updating for the installed version")
    prov._base_query = lambda q: pyalex.Works().filter(title_and_abstract={"search": q})
    for q in queries:
        prov.last_error = None
        papers = prov._search_uncached(q, 10**9, None)
        result = SearchResult(query=PREFIX + q, provider="openalex",
                              timestamp=datetime.datetime.now().isoformat(),
                              papers=papers, filters=None, limit=10**9,
                              error=prov.last_error)
        session = create_review_session([result], PREFIX + q, session_name=name)
        save_session(session)
        state = f"failed ({prov.last_error})" if prov.last_error else f"{len(papers)} records"
        print(f"{state}; session {name}: {len(session.decisions)} records, "
              f"{len(session.pending_papers())} pending | {q[:70]}")


if __name__ == "__main__":
    main()
