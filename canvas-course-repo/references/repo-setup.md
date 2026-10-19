# Setting up a repository for an existing Canvas course

For a course whose content so far lives only in Canvas (typically a course
copy of the previous round). Worked first on DA2215 vetcyb26h,
`~/devel/edu/scientific-method/canvas/` (2026-10-19). Newer intropy keeps
hand-written pages in its module directories (`canvas.mk`, push only); tilkry
has per-week Makefiles with a pull that overwrites. This recipe is the one to
reuse: export once, then the files are the source of truth.

## Decide with the author first

- **Location**: `canvas/NN-<module>/` (NN = module position) when the repo's
  own directories are not one-to-one with Canvas modules; else the module
  directories, as in intropy.
- **Body format**: Markdown (readable) with an automatic HTML fallback per
  file, or HTML everywhere. The export script verifies each Markdown body.
- **Pull**: export-missing-only plus `diff-canvas` (recommended; never
  overwrites a file) or overwrite-and-review (tilkry).

## Steps

1. Snapshot the course to JSON (all assignments, modules with items, page
   bodies) as the backup. `scripts/canvas_snapshot.py` covers one module or
   assignment; for a whole course loop over `course.get_assignments()`,
   `get_modules()` + `get_module_items()`, `get_pages()` + `get_page(url)`.
2. Rename modules **before** exporting: the export writes each module's
   current name into `modules:` regexes.
3. Copy `scripts/canvas_export.py` to `<dir>/bin/` and `assets/canvas.mk` to
   `<dir>/`, add `include canvas.mk` (and a default `COURSE?=`) in
   `<dir>/Makefile`, and `.pushed.d/` to `<dir>/.gitignore`.
4. Export: `make pull` (or run the script directly; ~6 s per item with
   `--jobs 6`, so ~11 min for 120 items: run it in the background). Quizzes:
   `canvaslms quizzes export -I -c C -a '^Title$' > NN-x/quizzes/x.json` by
   hand; `push-quizzes` sends them with `--html` and never the questions.
5. `make mark-pushed`, then `git add` the export as the baseline, so that
   `git diff` shows exactly the edits and `make push` sends only those.
6. Edit (dates, titles, links), rename date-bearing files to date-free names
   with `git mv` (the next round inherits them), `make -n push | grep -c '
   edit '` to count, push renamed link targets first, then `make push`.
7. Verify: snapshot again and diff field by field. Expect `description` to
   differ on every Markdown-pushed item (pandoc's HTML replaces the editor's)
   and `secure_params` (a JWT embedding the description) on non-LTI items;
   compare text and link targets of those descriptions (the script's
   `digest()`), which must be equal. Module items, positions and published
   states must be unchanged. `make diff-canvas` should be empty apart from
   hand-written regexes.

## What the export script does and why

- One file per page/assignment; an item in several modules goes under the
  first, its `modules:` lists all. `unlisted/` for items in no module.
- Assignments get `regex: ^<id>$`; pages keep an exact-title regex.
- Drops `rubric:` (FeedbackFruits rubrics carry internal ids; omitted fields
  are never sent) and null fields (canvaslms does not send them anyway, so
  `unlock_at: null` in a file only misleads).
- Skips quiz assignments (`online_quiz`): their description is the quiz's.
- Verification: Markdown body → `canvaslms.cli.content.markdown_to_html` →
  text and `href`/`src` targets compared with the API HTML (untranslated
  export). Failures are written as `*.html.md` with the `--html` export.
  Nested styled lists (`<ol style=…>` inside lists) typically fail.
- Slugs up to 90 characters; the script aborts on two items with one slug
  (titles differing only at the end, e.g. "… (50328)" / "… (60152)").

## Gotchas found on the real course

- **canvaslms cannot clear a date**: `due_at: null` and `''` in front matter
  are not sent, so `unlock_at` stays set. Clearing is the author's step (web
  UI), or for a sandbox restore the API with an empty string
  (`assignment.edit(assignment={"unlock_at": ""})`; `None` is dropped too).
  Moving `due_at` before an existing `unlock_at` fails with "must be between
  availability dates".
- **A page rename changes its URL slug**; the old slug still resolves via
  the API (and Canvas redirects), so existing links survive.
- **Course copies leave dead links**: `$CANVAS_OBJECT_REFERENCE$/…/g<hex>`
  and `$CANVAS_COURSE_REFERENCE$/modules/items/g<hex>` in the stored HTML,
  plus `api-endpoint` attributes pointing at the old course. Grep the
  snapshot for `\$CANVAS|/courses/<old id>` and replace them with
  canvaslms's symbolic link by name:
  `[text]($CANVAS_COURSE_REFERENCE$/assignments/<urlquote(name, safe='')>
  "name"){course-type="assignments"}`. It resolves at push, so push the
  renamed target first.
- **Quiz edits without `--html` re-render the description** through
  Markdown; always push quiz JSON with `--html`. A classic quiz settings
  edit with the full export JSON changed only the edited field.
- **Two modules with one name** (e.g. two "Pass by participation"): a page in
  both gets the same `modules:` regex twice. Do not push it casually.
- `make -n` prints a backslash-continued recipe on two lines: count pushes
  with `grep -c ' edit '`, not by lines.
