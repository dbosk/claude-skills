#!/usr/bin/env python3
"""Read-only JSON snapshots of Canvas objects, for before/after diffs.

Run with the interpreter of the canvaslms installation, so that canvasapi and
the stored credentials are available:

    PY=$(head -1 "$(readlink -f "$(command -v canvaslms)")" | sed 's/^#!//')
    $PY canvas_snapshot.py assignment COURSE_ID ASSIGNMENT_ID > before.json
    $PY canvas_snapshot.py module COURSE_ID 'Module name' > inventory.json

`assignment` prints every API field except the update timestamps.
`module` prints one record per item: position, type, content id, title,
published, and for assignments the submission types and the full
description HTML (the backup to push back with --html).
It never writes to Canvas.
"""
import json
import sys

from canvasapi import Canvas
from canvaslms.cli.login import load_credentials


def course(course_id):
    host, token = load_credentials({})
    if not host or not token:
        sys.exit("no canvaslms credentials found (run: canvaslms login)")
    if not host.startswith("http"):
        host = "https://" + host
    return Canvas(host, token).get_course(int(course_id))


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in ("assignment", "module"):
        sys.exit(__doc__)
    kind, course_id, what = sys.argv[1:]
    c = course(course_id)
    if kind == "assignment":
        a = c.get_assignment(int(what))
        skip = ("updated_at", "updated_at_date")
        out = {
            k: v
            for k, v in vars(a).items()
            if not k.startswith("_") and k not in skip
        }
    else:
        out = []
        for m in c.get_modules():
            if m.name != what:
                continue
            for it in m.get_module_items():
                rec = {
                    "module": m.name,
                    "position": it.position,
                    "type": it.type,
                    "content_id": getattr(it, "content_id", None),
                    "title": it.title,
                    "published": getattr(it, "published", None),
                }
                if it.type == "Assignment":
                    a = c.get_assignment(it.content_id)
                    rec["submission_types"] = a.submission_types
                    rec["description"] = a.description or ""
                out.append(rec)
        if not out:
            sys.exit(f"no module named exactly {what!r}")
    json.dump(out, sys.stdout, indent=1, sort_keys=True, default=str,
              ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
