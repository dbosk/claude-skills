#!/usr/bin/env python3
"""Export a Canvas course's pages and assignments to files, one per item.

Run with the interpreter of the canvaslms installation (see canvas.mk):

    $PY canvas_export.py COURSE_ID OUTDIR [--overwrite] [--jobs N]

Layout: OUTDIR/NN-<module>/<page>.md and OUTDIR/NN-<module>/assignments/
<assignment>.md, where NN is the module's position.  An item that sits in
several modules is written once, under the first of them; its `modules:`
front matter lists all of them.  Items in no module go in OUTDIR/unlisted/.

The body comes from `canvaslms pages|assignments view`, so course links are
in the course-independent symbolic form.  Each Markdown body is checked by
converting it back to HTML and comparing text and link targets with the
Canvas HTML; a body that does not survive is written as HTML instead
(file name *.html.md, pushed with --html).

Without --overwrite, existing files are left alone (the files are the source
of truth: Canvas strips HTML comments).  The paths of the files written are
printed on stdout, one per line.

Quiz assignments, SubHeaders and external links are not exported: they have
no body to keep here.  The rubric and null fields are dropped from the front
matter, so a push never sends them.
"""
import argparse
import html
import os
import re
import subprocess
import sys
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser

import yaml
from canvasapi import Canvas
from canvaslms.cli.content import markdown_to_html
from canvaslms.cli.login import load_credentials

DROP = ("rubric",)


def slug(text, maxlen=90):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"\(week [^)]*\)", "", text, flags=re.I)
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return text[:maxlen].rstrip("-") or "item"


class Digest(HTMLParser):
    """Text and link targets of an HTML fragment, for comparison."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text, self.links = [], []

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k in ("href", "src") and v:
                self.links.append(html.unescape(v))

    def handle_data(self, data):
        self.text.append(data)


def digest(fragment):
    d = Digest()
    d.feed(fragment or "")
    text = unicodedata.normalize("NFKC", " ".join(d.text))
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'),
                 ("”", '"'), ("–", "-"), ("—", "-"),
                 (" ", " "), ("…", "...")):
        text = text.replace(a, b)
    text = re.sub(r"\s+", "", text)
    return text, sorted(d.links)


def cli(*args):
    return subprocess.run(["canvaslms", "--no-cache", *args], check=True,
                          capture_output=True, text=True).stdout


def split(doc):
    m = re.match(r"---\n(.*?\n)---\n?(.*)", doc, re.S)
    if not m:
        sys.exit(f"no front matter in export:\n{doc[:200]}")
    return yaml.safe_load(m.group(1)), m.group(2)


def join(fm, body):
    fm = {k: v for k, v in fm.items() if v is not None and k not in DROP}
    head = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    return f"---\n{head}---\n{body}"


def export(course_id, kind, sel, api_html):
    """Return (file text, is_html) for one page or assignment."""
    cmd = ("pages", "view", "-c", str(course_id), "-p", sel) if kind == "page" \
        else ("assignments", "view", "-c", str(course_id), "-a", sel)
    fm, body = split(cli(*cmd))
    fm["regex"] = sel
    # Verify against Canvas' HTML using the untranslated links.
    _, raw = split(cli(*cmd, "--no-link-translation"))
    if digest(markdown_to_html(raw)) == digest(api_html):
        return join(fm, body), False
    _, hbody = split(cli(*cmd, "--html"))
    return join(fm, hbody), True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("course_id", type=int)
    ap.add_argument("outdir")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()

    host, token = load_credentials({})
    if not host.startswith("http"):
        host = "https://" + host
    course = Canvas(host, token).get_course(args.course_id)

    home = {}  # (kind, id) -> directory of the first module holding it
    for m in course.get_modules():
        mdir = f"{m.position:02d}-{slug(m.name)}"
        for it in m.get_module_items():
            if it.type == "Page":
                home.setdefault(("page", it.page_url), mdir)
            elif it.type == "Assignment":
                home.setdefault(("assignment", it.content_id), mdir)

    jobs = []
    for p in course.get_pages():
        page = course.get_page(p.url)
        mdir = home.get(("page", p.url), "unlisted")
        jobs.append(("page", f"^{re.escape(p.title)}$",
                     os.path.join(mdir, slug(p.title)), page.body))
    for a in course.get_assignments():
        if "online_quiz" in (a.submission_types or []):
            continue
        mdir = home.get(("assignment", a.id), "unlisted")
        jobs.append(("assignment", f"^{a.id}$",
                     os.path.join(mdir, "assignments", slug(a.name)),
                     a.description))

    def run(job):
        kind, sel, base, api_html = job
        md, htm = base + ".md", base + ".html.md"
        if not args.overwrite and any(
                os.path.exists(os.path.join(args.outdir, f)) for f in (md, htm)):
            return None
        text, is_html = export(args.course_id, kind, sel, api_html)
        rel = htm if is_html else md
        path = os.path.join(args.outdir, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)
        return rel

    seen = {}
    for kind, sel, base, _ in jobs:
        if base in seen:
            sys.exit(f"two items map to {base}: {seen[base]} and {sel}")
        seen[base] = sel
    with ThreadPoolExecutor(args.jobs) as pool:
        for rel in pool.map(run, jobs):
            if rel:
                print(rel, flush=True)


if __name__ == "__main__":
    main()
