---
name: remarkable
description: Work with a reMarkable tablet through the remarkable-mcp MCP server — upload PDFs/EPUBs, browse/search the cloud, render pages as images, read page text/OCR, and read back handwritten annotations. Use when: (1) the user asks to send/upload a document, paper, or PDF to their reMarkable ("put this on my reMarkable", "upload to remarkable"), (2) the user asks to read, render, or check an annotation/note they made on the tablet, (3) the user mentions reMarkable, remarkable-mcp, rmapi, or their tablet, (4) setting up or troubleshooting the remarkable MCP server. Covers registration/auth, the tool inventory, and the non-obvious gotchas (path-not-uuid addressing, 1-based pages, mid-session MCP loading, and the annotation-sync trap).
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
| `remarkable_read` | page text / OCR of a doc | `document`, `page`, `include_ocr` |
| `remarkable_image` | render a page to PNG (optionally with ink) | `document`, `page`, `render_merged`, `output_format` |
| `remarkable_canvas` | interactive canvas render of a page | `document`, `page` |
| `remarkable_upload` | upload a local file | `file_path` (req), `parent_folder`, `document_name` |
| `remarkable_mkdir` / `move` / `rename` / `delete` | manage docs/folders | see schema |

Get exact schemas at runtime with `tools/list` (see the script below).

## Gotchas (learned the hard way — read before using)

1. **Address documents by PATH or name, not the upload UUID.** `remarkable_upload`
   returns a `uuid`, but `remarkable_read`/`remarkable_image` look up by path
   (e.g. `/My Paper (draft)`) or name — passing the uuid gives
   `document_not_found`. After uploading, call `remarkable_search`/`remarkable_recent`
   to get the `path`, then use that.

2. **Pages are 1-based.** `page=0` → `page_out_of_range` ("use page=1 to N").

3. **Mid-session `claude mcp add` does not load the tools into the current
   session.** `claude mcp list` shows `✔ Connected`, but the `mcp__remarkable__*`
   tools are only registered at session start, so `ToolSearch` won't find them
   until a **new** session. To act immediately in the same session, drive the
   stdio server directly with `scripts/rm_mcp.py` (a JSON-RPC client).

4. **Annotations only exist in the cloud once the tablet has synced.** A
   handwritten layer made on the device is invisible to the cloud API until the
   tablet syncs up. Symptoms of an un-synced annotation:
   - the document's `modified` time still equals the upload time;
   - `remarkable_image` with `render_merged=true` falls back to the tablet's
     native PDF export and notes *"local stroke render unavailable"* — the ink
     is missing;
   - `remarkable_read` with `include_ocr=true` returns only the **printed** PDF
     text, never the un-synced handwriting.
   If the ink is missing, do not conclude there is no annotation — ask the user
   to sync the tablet (Wi-Fi, wake the device / manual sync), then re-render.

5. **Image results come back as an MCP resource blob.** In the `tools/call`
   result, `content[]` holds an item of type `resource` with base64 in
   `resource.blob` (or type `image` with `data`). Save those bytes to a `.png`
   and Read it. Do **not** rely on `resources/read` of the `remarkableimg:///…`
   URI — spaces/parentheses in document names break it ("unbalanced
   parenthesis"); use the inline blob from `tools/call` instead.

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

# render page 1 with ink merged, saving the PNG to read back an annotation
scripts/rm_mcp.py render "/My Paper (draft)" 1 out.png
```

Then Read the saved PNG to view the page/annotation visually. The script is
small and provider-agnostic; read it before extending.

## Verify an upload

`remarkable_upload` returns `"uploaded": true` with a uuid; confirm it landed
with `remarkable_recent`/`remarkable_search` (the cloud may take a moment to
index). It syncs to the physical device when the tablet is online.
