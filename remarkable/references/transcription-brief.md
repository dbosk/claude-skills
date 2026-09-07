# Transcription-agent brief (template)

Hand this to a subagent as its whole task when the user has annotated a draft
on the tablet. Fill every `{{placeholder}}`. The agent needs the `remarkable`
skill (for the tool gotchas) and read access to the sources; it changes
nothing.

---

# Brief: transcribe the handwritten review of {{document name}}

The user has reviewed `{{/exact document name on the tablet}}` on their
reMarkable and annotated it. Transcribe every mark into a written comment list.
You do not fix anything and you do not edit the sources.

Sources: `{{path to the source directory}}` as of commit `{{sha}}` — the commit
the reviewed PDF was built from. The working tree may have moved on: check per
file whether the line numbers still match, and give both numbers where they
have shifted.

Scratch and renders: `/tmp/claude-1000/{{name}}/`. Report file:
`{{path}}/{{name}}-comments.md`.

## Steps

1. **Confirm you are reading the right version.** `remarkable_browse` /
   `remarkable_recent` the family; the annotated version is the one whose
   `modified` time is later than its own upload, which is not necessarily the
   newest upload. If nothing looks annotated, suspect the sync trap and ask
   before reporting "no comments".
2. **List the annotated pages**: `remarkable_read(document,
   content_type="annotations")`. It reports the pages carrying handwriting and
   any highlighted text. Do not scan the rest of the document.
3. **Render each annotated page twice** — merged (`render_merged=True`) and
   ink-only (`render_merged=False`) — and save both (`{{name}}-page-N.png`,
   `ink-N.png`). Crop and enlarge each ink group before transcribing it.
4. **Transcribe.** Read the ink-only layer whenever ink runs into a margin, off
   the trim, or across printed type.
5. **Anchor each comment** to the printed text it points at, then to the source
   `file:line` that produced that text.

## Reading the ink

- **Long crossbars are not strike-throughs.** A reviewer who crosses `t`/`tt`
  with one horizontal stroke carries the line over the following word; at page
  scale it looks exactly like a deletion. Verify every apparent strike-through
  against the ink-only layer. State the reviewer's habit once at the top of the
  report, and say explicitly where something *is* struck (a genuine strike is a
  separate stroke drawn across printed type at mid-x-height).
- **Printed marks are not ink.** A superscript footnote marker can read as a
  caret in the composite; if it is absent from the ink layer, it is print.
- **Describe, then conclude.** Write what the strokes are and where they sit
  before saying what they mean.

## Report format

Header: the document, the source path and commit, which pages the tablet
reported as annotated, which renders you made, how many comments on how many
pages, how many are ambiguous, and the handwriting note above.

Then one entry per comment, grouped by page:

- **Anchor** — what the ink points at, with the strokes described (leader
  lines, arrows, carets, what is struck and what is not).
- **Transcription** — verbatim, with `[?]` on any uncertain word.
- **Source** — `file:line` (plus every other place the same text occurs).
- **My reading of the request** — what the user wants changed.
- **Scope guess** — this document only, or a general rule for the project.
- **Relation to the previous round** — new, a repeat, or a follow-up.

Close with two lists: **ambiguous items** (each with both readings, for the
user to settle) and **problems and caveats** (clipped ink, pages you did not
sweep, page numbers that shifted between versions, tool failures).
