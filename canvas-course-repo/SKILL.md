---
name: canvas-course-repo
description: |
  Maintain Canvas LMS modules, pages and assignments from Markdown files in a
  git repository with the canvaslms CLI (the write side; canvas-info is the
  read side). Use proactively when: (1) creating, pushing, renaming, moving,
  publishing or detaching Canvas pages, assignments or module items with
  `canvaslms pages edit`, `assignments edit` or `modules ...`, (2) the user
  wants a Canvas module arranged "like that one", a module shape applied to
  other modules, or placeholder text headers added, (3) editing files with
  canvaslms front matter (`regex:`, `modules:`, `published:`) or a Makefile
  with push-pages targets, (4) the user mentions pushing to Canvas, module
  items, SubHeader, FeedbackFruits or LTI assignments in a module. Load
  BEFORE the first write: an empty file body silently replaces a description,
  and `modules:` in front matter is authoritative.
---

# Canvas course content from a git repository

The repository holds the pages and the facts about each module; `canvaslms`
pushes them. `canvas-info` covers reading; this skill covers writing. The
course's own module shape, names and make targets belong in that
repository's `CLAUDE.md`, not here.

## Rules that hold in every course

1. **The files are the source of truth. Never pull a page back.** Canvas
   strips HTML comments, so generator markers and TODO comments exist only
   locally. To see what Canvas has, read it; do not overwrite the file.
2. **Check Canvas before the first push of a session.** The author edits in
   the web UI too: publishes pages, moves items, renames things. Compare
   `modules view --show-position` and each item's `published` state with the
   files, and bring the *files* in line where the author's change is the
   newer decision. A stale `published: false` or `position:` undoes their
   work on the next push. The same holds for the **body**: the author may add
   content in the web editor (a recording `<iframe>`, a link, a corrected
   sentence). Before pushing a page, read its body as HTML through the API,
   diff it against the file, and carry the author's additions into the file
   (raw HTML passes through the Markdown) — then push. Never replace the
   file with the pulled page: that loses the local markers and comments
   (author, 2026-09-23: "pull it so that you can keep the embedding that I
   added to it … I don't want to lose that one on an update").
3. **`--no-cache` goes before the subcommand** (`canvaslms --no-cache pages
   edit ...`). Use it for every write and every verification read; the
   object cache has listed a page twice and hidden a server-side no-op.
4. **Create once, push routinely without `--create`.** Courses have
   duplicate-titled pages, and a changed title plus `--create` spawns a
   duplicate. To rename: push once with the old `regex` and the new
   `title`/`name`, then change the `regex`.
5. **New content goes in unpublished** (`published: false`) so the author
   reads it before students do. Flip the file when the author publishes.
6. **Rehearse every new kind of write in the sandbox course** (`kth-data`
   §1), with a JSON snapshot before and after
   (`scripts/canvas_snapshot.py`), and restore it. Never write-test a
   fan-out path.
7. **What canvaslms cannot do is the author's step.** Creating
   FeedbackFruits or other LTI content is done in the web UI; list it in
   the report, do not improvise with raw API calls. A missing canvaslms
   feature becomes an issue in `dbosk/canvaslms`.
8. **Writes are slow** (about 15 s per page push). Run a batch in the
   background with one summary line per file; do not run two batches
   against one module at the same time, since positions shift.

## Front matter semantics (verified against canvaslms 6.21)

| Field | Behaviour |
|---|---|
| `regex` | Identity: matched against title/name, URL slug or numeric id. Use `'^<id>$'` for assignments whose name is about to change. |
| `name` / `title` | Required, even when only another field changes. |
| `modules:` with entries | **Authoritative**: adds to the listed modules, moves to `position`, removes from every module not listed. |
| `modules: []` | Detaches from all modules; the object is kept. |
| `modules:` omitted | Membership untouched. |
| `published` | Sent when present. |
| body | **Always sent** as the page body or assignment description. An empty body replaces the description with `"\n"`, silently (dbosk/canvaslms#488). |

Only fields present in the file are sent, so `external_tool_tag_attributes`
(FeedbackFruits), rubric, points and dates survive a push that does not
name them.

### Changing metadata on an item that has a description

An assignment with an empty description (typical for LTI items) takes a
front-matter-only file. For anything else, carry the description through
verbatim:

```bash
# body = the API's HTML, byte for byte; see scripts/canvas_snapshot.py
canvaslms --no-cache assignments edit -c '^COURSE$' \
    --html --no-link-translation -f item.html.md
```

`--html` skips the Markdown conversion and `--no-link-translation` keeps the
course links as they are; together the round trip gives an empty JSON diff.
Never round-trip through `assignments view` Markdown: it is lossy.

## Module shapes

A module has a declared **shape**: an ordered list of item kinds and naming
patterns, written in the course's `CLAUDE.md`. To apply it to a module:

1. **Inventory** the module (`scripts/canvas_snapshot.py module`): position,
   type, content id, publish state, description length. Keep the JSON; it is
   the backup of every description.
2. **Map** each existing item to a slot of the shape: keep, rename, move,
   detach. Items the shape does not mention stay, after the last slot,
   unless the author said otherwise.
3. **Apply top to bottom.** Positions are 1-based and inserting shifts
   everything below, so create the pages first, then place each following
   item at the next position. Address assignments by id.
4. **Detach, do not delete.** `modules: []` plus `published: false`; old
   content stays reachable for the author.
5. **Placeholders are text headers** (SubHeader), e.g. "Anteckningar
   kommer", replaced when the real item exists. Add and remove them with
   `canvaslms modules add-item` / `remove-item` (canvaslms > 6.21, PR
   dbosk/canvaslms#490; run `canvaslms modules -h` to confirm they exist
   in the installed version):

   ```bash
   canvaslms --no-cache modules add-item -c '^COURSE$' '^Module$' \
       -t subheader --title 'Anteckningar kommer' -p 3
   canvaslms --no-cache modules remove-item -c '^COURSE$' '^Module$' \
       -i '^Anteckningar kommer$'
   ```

   `add-item` is idempotent (same title, or same content for `-t
   page|assignment|quiz --content REGEX`) and moves an existing item when
   `-p` is given, so a shape recipe can be re-run; new items are
   unpublished unless `--publish`. `remove-item` keeps the content and
   leaves a gap in the remaining positions.
6. **Audit**: `canvaslms --no-cache modules view -c C --show-position
   '^Module$'` must match the shape line by line; detached items show
   `modules: []`.
7. **Write the final positions back into the files**, so a later routine
   push keeps the shape. A position is tied to the module's current
   contents: when a placeholder is replaced by several items, update the
   positions below it in the same change.

Worked example with commands: `references/module-shape-example.md`.

## Pushing from a worktree

Make-based push targets keep their stamp files in the main checkout. From a
worktree, push single files (`canvaslms --no-cache pages edit -c C -f
file.md`) and leave the stamps alone; the next `make push-pages` in the main
checkout re-pushes unchanged content, which is harmless.

## Reporting

Say per module what was created, renamed, moved and detached, what is left
for the author (LTI content, publishing), and link any canvaslms issue
filed.
