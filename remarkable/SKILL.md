---
name: remarkable
description: Work with a reMarkable tablet through the remarkable-mcp MCP server — upload PDFs/EPUBs, browse/search the cloud, render pages (optionally compositing annotations onto the PDF), read page text/OCR, extract highlighted text, and list which pages carry notes/highlights. Use when: (1) the user asks to send/upload a document, paper, or PDF to their reMarkable ("put this on my reMarkable", "upload to remarkable"), (2) the user asks to read/render/check an annotation, note, or highlight they made on the tablet, or to find/extract only the annotated pages, (3) the user mentions reMarkable, remarkable-mcp, rmapi, or their tablet, (4) setting up or troubleshooting the remarkable MCP server. Covers registration/auth, the tool inventory, the merged/annotation-extraction capabilities, and the non-obvious gotchas (path-not-uuid addressing, 1-based pages, mid-session MCP loading, the annotation-sync trap, and the render_merged version dependency).
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
