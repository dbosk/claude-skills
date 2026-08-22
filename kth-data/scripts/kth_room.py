#!/usr/bin/env python3
"""Look up KTH rooms on https://www.kth.se/places/ and print their facts.

Usage: kth_room.py ROOM [ROOM ...]

For each room name (e.g. "V32", "B1", "Ka-Sal C") the script follows the
redirect from https://www.kth.se/places/room/<name> to the room's page and
prints a TSV line:

    name<TAB>seats<TAB>exam seats<TAB>type<TAB>building<TAB>address<TAB>url

Unknown rooms print "?" in the numeric columns and "not found" as type.
Exit status is 1 if any room was not found.
"""
import html
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://www.kth.se/places/room/"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def room_url(name):
    """Return the room's page URL, or None if kth.se/places does not know it."""
    opener = urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(BASE + urllib.parse.quote(name),
                                 headers={"User-Agent": "kth-data-skill"})
    try:
        opener.open(req, timeout=30)
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303, 307, 308):
            return urllib.parse.urljoin(BASE, e.headers.get("Location"))
        return None
    return None


def room_facts(url):
    """Scrape label/value pairs from a room page into a dict."""
    req = urllib.request.Request(url, headers={"User-Agent": "kth-data-skill"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        page = resp.read().decode("utf-8", "replace")
    text = html.unescape(re.sub(r"<[^>]+>", "\n", page))
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    facts = {}
    for i, line in enumerate(lines):
        if line.endswith(":") and i + 1 < len(lines):
            facts[line[:-1]] = lines[i + 1]
            # The room type ("Övningssal", "Hörsal", ...) is the unlabeled
            # line just before the address label.
            if line == "Adress:" and i > 0:
                facts["type"] = lines[i - 1]
    return facts


def main(argv):
    missing = 0
    for name in argv[1:]:
        url = room_url(name)
        if not url:
            print(f"{name}\t?\t?\tnot found\t\t\t")
            missing += 1
            continue
        facts = room_facts(url)
        print("\t".join([
            name,
            facts.get("Platser", "?"),
            facts.get("Examinationsplatser", "?"),
            facts.get("type", ""),
            facts.get("Byggnad", "").rstrip(","),
            facts.get("Adress", ""),
            url,
        ]))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
