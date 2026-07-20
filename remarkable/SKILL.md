---
name: remarkable
description: "IMPORTANT: load this skill BEFORE calling ANY remarkable-mcp tool — even a one-line upload — because the tools have silent-failure gotchas (address docs by path/name, NOT the UUID that upload returns; annotations only appear after the tablet syncs; render_merged needs the patched build). Work with a reMarkable tablet via the remarkable-mcp MCP server: upload PDFs/EPUBs, browse/search the cloud, render pages (optionally compositing annotations onto the PDF), read page text/OCR, extract highlighted text, and list which pages carry notes/highlights. Use when: (1) sending/uploading a document, paper, or PDF to the reMarkable ('put this on my reMarkable', 'upload to remarkable'); (2) reading/rendering/checking an annotation, note, or highlight, or extracting only the annotated pages; (3) the user mentions reMarkable, remarkable-mcp, rmapi, or their tablet; (4) setting up or troubleshooting the server. Covers auth, the tool inventory, annotation extraction, and more gotchas (1-based pages, mid-session MCP loading)."
---

# Working with the reMarkable via remarkable-mcp

`remarkable-mcp` is a stdio MCP server (binary at `~/.local/bin/remarkable-mcp`,
`uvx remarkable-mcp` also works) that talks to the reMarkable cloud (or the
tablet over SSH/USB). It exposes read and write tools for documents on the
tablet.

## Setup and auth

Register the server once, at **user** scope so it is available in every project:

```bash
claude mcp add remarkable -s user -- remarkable-mcp
claude mcp list        # expect: remarkable: remarkable-mcp - ✔ Connected
```

Auth uses a cloud token stored in `~/.rmapi`. If that file exists, the server is
already authenticated (`remarkable_status` reports `"authenticated": true`) — no
further action. To register a new device, get a one-time code from
`https://my.remarkable.com/device/desktop` and run:

```bash
remarkable-mcp --register <code>     # prints/stores the token
```

Transports: cloud API by default; `--ssh` (developer mode) or `--usb` for a
directly-connected tablet; `--no-cloud-fallback` to forbid the cloud fallback.
Write tools (upload/mkdir/move/rename/delete) are **on by default**; pass
`--read-only` to expose a read-only server.

## Tool inventory

| Tool | Purpose | Key args |
|------|---------|----------|
| `remarkable_status` | auth/transport/capabilities, document count | — |
| `remarkable_browse` | list a folder / filter | `path`, `query`, `tags` |
| `remarkable_recent` | most recently modified docs | `limit`, `include_preview` |
| `remarkable_search` | find a doc; returns `path` + page OCR text | `query`, `grep`, `limit`, `include_ocr` |
| `remarkable_read` | page text / OCR; `content_type=annotations` lists annotated pages + highlighted text | `document`, `page`, `content_type`, `include_ocr` |
| `remarkable_image` | render a page to PNG; `render_merged=true` composites PDF + strokes + highlights | `document`, `page`, `render_merged`, `output_format` |
| `remarkable_canvas` | interactive canvas render of a page | `document`, `page` |
| `remarkable_upload` | upload a local file | `file_path` (req), `parent_folder`, `document_name` |
| `remarkable_mkdir` / `move` / `rename` / `delete` | manage docs/folders | see schema |

Get exact schemas at runtime with `tools/list` (see the script below).

## Reading annotations: merged render + highlight/notes extraction

**Requires the patched build** — the fixes below live on the
`fix/render-merged-imported-pdfs` branch of `~/devel/remarkable-mcp`, installed
editable via `uv tool install --editable ~/devel/remarkable-mcp --force`. The
PyPI `remarkable-mcp` (≤ 1.0.0) still has the bugs listed under "Unpatched
release" — check with `uv tool list` (a `file://` / local version = patched).

With the patched build:

- **Composite an annotated page:** `remarkable_image(document, page,
  render_merged=True)` returns one PNG with the **PDF page + pen strokes + text
  highlights** at correct positions (PNG only; the page needs a PDF underlay).
  Save the blob and Read it (see the resource-blob gotcha).
- **Find/extract annotations without scanning every page:**
  `remarkable_read(document, content_type="annotations")` returns an **"Annotated
  pages"** section — only the pages that carry annotations, each showing whether
  it has handwritten notes and its **highlighted text**. The underlying
  extraction result also exposes `highlights` (flat list) and `annotated_pages`
  (`[{page, page_id, has_handwriting, highlights}]`, 1-based page numbers).

Highlight text is the reMarkable's stored text selection: great for *locating*
annotated passages, but occasionally glitchy (a dropped letter, or a sentence
split across entries) — treat it as a finder, not a verbatim transcript.

### Unpatched release (PyPI ≤ 1.0.0): use the native email export
On the release build, `render_merged` is broken for imported PDFs
(formatVersion-1 docs render annotation-only; the coordinate transform
mis-places ink — single strokes off-position, multi-stroke pages fill solid
black), text highlights never render, and `content_type=annotations` returns no
highlights. For correct output there, use reMarkable's **own on-device export**:

1. Tablet: open the document → **Page overview** → long-press the page → **⋯
   (More)** → **Send by email** → **PDF** (or **PNG**) → send to the user's own
   address.
2. Retrieve it via a connected Gmail/mail MCP (`claude mcp list` to check) — pull
   the attachment — or ask the user to share the file. Then Read it; positions
   are exact because reMarkable rendered it. You **cannot** trigger this export
   headlessly (no cloud endpoint); the user taps once, you fetch and read.

## Gotchas (learned the hard way — read before using)

1. **Address documents by PATH or name, not the upload UUID.** `remarkable_upload`
   returns a `uuid`, but `remarkable_read`/`remarkable_image` look up by path
   (e.g. `/My Paper (draft)`) or name — passing the uuid gives
   `document_not_found`. After uploading, call `remarkable_search`/`remarkable_recent`
   to get the `path`, then use that.

2. **Pages are 1-based.** `page=0` → `page_out_of_range` ("use page=1 to N").

3. **Mid-session `claude mcp add` (or reinstalling the tool) does not reach the
   current session.** `claude mcp list` shows `✔ Connected`, but the
   `mcp__remarkable__*` tools — and any freshly-installed build — are only picked
   up at session start, so `ToolSearch` won't find the tools until a **new**
   session. To act immediately in the same session, drive the stdio server
   directly with `scripts/rm_mcp.py` (a JSON-RPC client).

4. **Annotations only exist in the cloud once the tablet has synced.** A layer
   made on the device is invisible to the cloud API until the tablet syncs up.
   Signs it hasn't: the document's `modified` time still equals the upload time;
   `render_merged`/`content_type=annotations` show no ink or highlights. Do not
   conclude there is no annotation — ask the user to sync (Wi-Fi, wake the device
   / manual sync), then retry.

5. **Image results come back as an MCP resource blob.** In the `tools/call`
   result, `content[]` holds an item of type `resource` with base64 in
   `resource.blob` (or type `image` with `data`). Save those bytes to a `.png`
   and Read it. Do **not** rely on `resources/read` of the `remarkableimg:///…`
   URI — spaces/parentheses in document names break it ("unbalanced
   parenthesis"); use the inline blob from `tools/call` instead. Note some modes
   (`compatibility=true`) return the PNG as a `data:image/png;base64,…` string in
   a `data_uri` JSON field instead — handle that shape too.

## Driving the server directly (in-session fallback)

When the MCP tools are not yet loaded (gotcha 3), or for scripted/batch use, run
`scripts/rm_mcp.py`. It speaks the newline-delimited JSON-RPC stdio protocol
(`initialize` → `notifications/initialized` → `tools/call`) and handles saving
image blobs to files.

```bash
# discover tools and schemas
scripts/rm_mcp.py list

# status / find a just-uploaded doc's path
scripts/rm_mcp.py call remarkable_status
scripts/rm_mcp.py call remarkable_recent '{"limit":5}'

# upload a PDF (root folder)
scripts/rm_mcp.py call remarkable_upload \
  '{"file_path":"/abs/path/article.pdf","document_name":"My Paper (draft)"}'

# render page 1 with annotations composited onto the PDF (patched build)
scripts/rm_mcp.py render "/My Paper (draft)" 1 out.png

# list annotated pages + highlighted text
scripts/rm_mcp.py call remarkable_read \
  '{"document":"/My Paper (draft)","content_type":"annotations"}'
```

Then Read the saved PNG. On the patched build `render` composites the page + ink
+ highlights at correct positions; on the unpatched release it returns only the
(cropped, possibly mis-placed) ink layer — see the version note above. The script
is small and provider-agnostic; read it before extending.

## Verify an upload

`remarkable_upload` returns `"uploaded": true` with a uuid; confirm it landed
with `remarkable_recent`/`remarkable_search` (the cloud may take a moment to
index). It syncs to the physical device when the tablet is online.

## Versioned review workflow (send a draft, iterate, keep history)

The common loop is: send a document to the tablet, the user reviews and
annotates it there, you read the annotations, revise the source, and send
the revised build back. Do it as a **versioned trail**, not an overwrite.

**Why this matters:** `remarkable_upload` to the cloud is **add-only — it
never replaces**. Re-uploading a revised PDF under the same name creates a
*second* document with that same name, not a new revision of the first. So
uploads naturally accumulate; embrace that instead of fighting it.

The workflow, unless the user says otherwise:

1. **Bake the version into the name at upload time** — every upload gets a
   unique `document_name` with date and version, e.g.
   `"<Title> (draft YYYY-MM-DD, vN)"` (the vt-debug paper's convention;
   `"<Title> (review vN)"` works for non-drafts). Because no two uploads
   share a name, there is **no rename step and no name-collision
   ambiguity** — every later tool call addresses the document by its
   unique name. Never upload under a bare base name planning to rename
   afterwards.
2. **Leave the earlier versions in place.** The tablet then holds the
   whole review history, each version distinguishable at a glance, and
   the user can compare against their earlier annotations. Do **not**
   delete or overwrite prior versions unless the user asks (a version
   superseded within minutes, before the user opened it, is fair to offer
   to delete — still ask).
3. **Pick N by incrementing the last uploaded version** — from the
   conversation, the repo's commit messages (pairing each upload with its
   commit, message noting "uploaded as draft YYYY-MM-DD, vN", keeps this
   trail in git), or by `remarkable_search`-ing the title and taking the
   highest existing suffix. Version numbers are cheap: a same-day
   follow-up change gets vN+1, never a silent re-upload of vN.
4. **Read annotations from the version the user reviewed** — usually the
   latest, but if they name an older draft, read that one. Before
   concluding a version has no annotations, remember the sync trap
   (gotcha 4): ask the user to sync rather than report "no comments".

**If you did end up with two documents sharing a name** (e.g. an upload
that was meant to replace): rename by path/name, never the upload UUID
(gotcha 1 — the UUID lookup fails). `remarkable_browse`/`_recent` lists
the **most recently modified first**, so the fresh upload is the first
match and rename-by-name targets it — but **verify afterward**: re-browse
and check that the new name landed on the entry whose `modified` time is
the newest, not on an older version.

If the user instead wants a single evolving document (no history), the
add-only cloud API can't update in place — delete the prior version after a
successful new upload (ask first; deletion is destructive), or keep one
name and let them tell versions apart by modified date.

For research papers, the surrounding loop (read all annotated pages, apply
the round, rebuild, one commit per round named after the draft, push,
upload the next version) is owned by the **scientific-writing** skill;
this section owns only the tablet mechanics.
