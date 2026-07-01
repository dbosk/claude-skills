#!/usr/bin/env python3
"""Minimal stdio JSON-RPC client for the remarkable-mcp server.

Use this when the `mcp__remarkable__*` tools are not loaded into the current
Claude session (a server added mid-session with `claude mcp add` only exposes
its tools to *new* sessions), or for scripted/batch use.

The reMarkable MCP server speaks newline-delimited JSON-RPC 2.0 over stdio:
one JSON message per line. This client performs the handshake
(initialize -> notifications/initialized) then issues one request.

Usage:
  rm_mcp.py list                       # list tools with required args
  rm_mcp.py call <tool> [json-args]    # call a tool; prints text content
  rm_mcp.py render <doc> <page> <out.png>   # render a page (ink merged) to a PNG

Notes / gotchas (see SKILL.md for the full list):
  * Address docs by PATH or name (e.g. "/My Paper"), NOT the upload uuid.
  * Pages are 1-based.
  * Image content arrives as an MCP resource blob (base64); this script decodes
    it to the output file.

The server binary is `remarkable-mcp` on PATH (override with REMARKABLE_MCP_CMD).
"""
import base64
import json
import os
import subprocess
import sys


def _server():
    cmd = os.environ.get("REMARKABLE_MCP_CMD", "remarkable-mcp").split()
    return subprocess.Popen(
        cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL, text=True, bufsize=1,
    )


class Client:
    def __init__(self):
        self.p = _server()
        self._id = 0
        self._send({"jsonrpc": "2.0", "id": self._next(), "method": "initialize",
                    "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                               "clientInfo": {"name": "rm_mcp", "version": "1"}}})
        self._read()
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def _next(self):
        self._id += 1
        return self._id

    def _send(self, obj):
        self.p.stdin.write(json.dumps(obj) + "\n")
        self.p.stdin.flush()

    def _read(self):
        line = self.p.stdout.readline()
        return json.loads(line) if line.strip() else None

    def request(self, method, params):
        self._send({"jsonrpc": "2.0", "id": self._next(), "method": method, "params": params})
        return self._read()

    def close(self):
        try:
            self.p.terminate()
        except Exception:
            pass


def _content_text(result):
    return "\n".join(c.get("text", "") for c in result.get("content", [])
                     if c.get("type") == "text")


def _save_blob(result, out):
    """Save the first image/resource blob in a tool result to `out`. Returns bool."""
    for c in result.get("content", []):
        if c.get("type") == "image" and c.get("data"):
            open(out, "wb").write(base64.b64decode(c["data"]))
            return True
        if c.get("type") == "resource":
            blob = c.get("resource", {}).get("blob")
            if blob:
                open(out, "wb").write(base64.b64decode(blob))
                return True
    return False


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]
    cl = Client()
    try:
        if cmd == "list":
            r = cl.request("tools/list", {})
            for t in r.get("result", {}).get("tools", []):
                req = t.get("inputSchema", {}).get("required", [])
                props = list(t.get("inputSchema", {}).get("properties", {}).keys())
                print(f"- {t['name']}  required={req} props={props}")
            return 0

        if cmd == "call":
            if not rest:
                print("usage: rm_mcp.py call <tool> [json-args]", file=sys.stderr)
                return 2
            tool = rest[0]
            args = json.loads(rest[1]) if len(rest) > 1 else {}
            r = cl.request("tools/call", {"name": tool, "arguments": args})
            res = r.get("result", r)
            print(_content_text(res) or json.dumps(res)[:2000])
            return 1 if res.get("isError") else 0

        if cmd == "render":
            if len(rest) < 3:
                print("usage: rm_mcp.py render <doc> <page> <out.png>", file=sys.stderr)
                return 2
            doc, page, out = rest[0], int(rest[1]), rest[2]
            r = cl.request("tools/call", {"name": "remarkable_image",
                           "arguments": {"document": doc, "page": page,
                                         "render_merged": True, "output_format": "png"}})
            res = r.get("result", {})
            if _save_blob(res, out):
                print(f"saved {out} ({os.path.getsize(out)} bytes)")
                note = _content_text(res)
                if "local stroke render unavailable" in note:
                    print("WARNING: ink layer not synced to cloud — annotation may be "
                          "missing; ask the user to sync the tablet, then retry.")
                return 0
            print("no image blob returned:\n" + _content_text(res)[:800])
            return 1

        print(f"unknown command: {cmd}", file=sys.stderr)
        return 2
    finally:
        cl.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
