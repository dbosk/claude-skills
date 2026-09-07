# Reader-agent brief (template)

An independent reader, one per 2–3 finished artifacts, that never saw the diff:
it reads the *product*, not the change. It needs no worktree — give it the
built artifacts and read-only sources. Copy this, fill the `{{placeholders}}`,
and hand it over as the agent's whole task.

---

# Brief: read {{artifact list}} page by page

You are reviewing finished {{documents/builds}} produced by another agent. You
did not write them and you must not fix them: your output is a defect list.
The artifacts are at {{paths}}; their sources at {{paths}}, as of commit
{{sha}}. Every line number you cite must match that commit — check, and say so
per file when the working tree has moved on.

## What to do

1. **Extract the text of every page** (`pdftotext -f N -l N`, or the
   equivalent for the format) and read all of it. Do not sample.
2. **Look at every page.** Contact sheets at low resolution (`pdftoppm -r 40`
   + `montage`, under `/tmp/claude-1000/{{name}}/`) show overprints, clipped
   margins, floats stranded on the wrong page, blank pages.
3. **Re-render at 110 dpi every page that looked wrong** and read it closely.
   A build log is not evidence about layout: a 19.5 pt overrun produced no
   warning at all in one campaign, and the defect was only visible in the
   render.
4. **Re-run every program the document generates** and compare its real output
   with the output printed in the document, character by character.
5. **Check the document against itself**: every count and every table
   reference in the prose against the thing it summarises, every caption
   against the thing it captions, every cross-reference against its target,
   every quoted claim against the source it names.
6. {{Domain checks — e.g. every footnote prints on the page carrying its
   marker; no placeholder text survived into the build; the check list in
   <project standard file> passes.}}

## What to report

Three severity levels. Give every item a `file:line` in the SOURCE (not in the
built artifact) plus the page where it shows:

- **Blockers** — output that is wrong, misleading or unreadable; anything a
  reader would trip over.
- **Should-fix** — real defects that do not break the document.
- **Nits** — typography, wording, consistency.

For each item: what is wrong, where, what it should be instead, and the
evidence you have (the render, the extracted text, the re-run output). Quote,
do not paraphrase. Number the items so the orchestrator can send back a
selection.

Do not edit anything, do not create branches, do not rebuild the sources. If a
defect turns on a judgement only the orchestrator can make, say so and give
both readings.
