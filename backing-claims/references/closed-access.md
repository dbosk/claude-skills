# Closed-access full texts through the university network

Some publishers serve a subscribed full text only to the university's
network. A SOCKS tunnel through the faculty shell server gives requests a
KTH address. The three commands below are the skill's `allowed-tools`, so
the permission system lets them run unprompted while this skill is
active. Run them in exactly that form; a loop or wrapper script around
them does not match the rule.

## Open, fetch, close

```bash
# 1. open the tunnel (once per session)
ssh -o BatchMode=yes -o ExitOnForwardFailure=yes -f -N -D 127.0.0.1:1081 faculty-shell.sys.kth.se

# 2a. scholar's fetcher, through the tunnel (lands in scholar's PDF cache)
HTTPS_PROXY=socks5h://127.0.0.1:1081 HTTP_PROXY=socks5h://127.0.0.1:1081 \
  ~/.claude/skills/backing-claims/scripts/fetch_pdf.py --text <url-or-doi> ...

# 2b. curl, through the tunnel (one call, several -o FILE URL pairs)
curl -sL --max-time 40 -x socks5h://127.0.0.1:1081 \
  -w '%{http_code} %{content_type} %{size_download}\n' \
  -o <dir>/<Key>.pdf <url> ...

# 3. close it when done
pkill -f '[D] 127.0.0.1:1081'
```

Check the exit address first:
`curl -sL --max-time 40 -x socks5h://127.0.0.1:1081 https://api64.ipify.org`
must print a KTH address (2001:6b0:…).

## What works and what does not (fetch round 2026-10-10, 41 sources)

- **Prefer 2a, fall back to 2b.** (dbosk/scholar#105 asks for first-class
  proxy and User-Agent settings in scholar; when it ships, 2a should do.)
  `fetch_pdf.py` uses Python `requests`,
  which most publishers refuse (403, or an HTML page instead of the PDF)
  whatever the address. curl got through where Python did not.
- **Keep curl's own user agent.** Setting a browser `-A` string made
  Springer switch to a "Client Challenge" page for every later request;
  curl's default agent then fetched the PDFs again.
- **Stop at a challenge.** After the first bot challenge from a host,
  do not retry or vary the request: retries escalate the blocking, and
  getting past a bot check is circumvention, not access.
- **Which publishers answered.** Springer
  (`link.springer.com/content/pdf/<doi>.pdf`) served PDFs. Open-access
  journals need no tunnel. Behind bot checks regardless of address:
  Elsevier/ScienceDirect, SAGE, Taylor & Francis, Wiley, ACM, Science
  and OUP (Cloudflare), APA PsycNET (a login page), and IEEE Xplore (418,
  then 502).
- **Where curl writes.** A download is untrusted: give it a fresh
  directory of its own in the scratch area, check each file with `file`
  (an HTML challenge page saved as `<Key>.pdf` is common) and delete the
  failures, then extract with `pdftotext -layout`. Do not compute
  scholar's cache path to write curl output into the cache: that was
  refused as a way around `fetch_pdf.py`.
- **Publisher PDF URLs.** Crossref's `link` field
  (`api.crossref.org/works/<doi>`) gives each publisher's PDF URL, and
  `alternative-id` gives Elsevier's PII.

## What is left over

Papers the tunnel cannot reach are the user's to fetch in a browser. Hand
them over as todos (the `nytid-todo` skill): one parent and one child per
paper, holding the DOI link and the publisher URL, load-bearing papers
first. Keep them flagged as read in abstract only in `VERIFIED` and in
the appendix until the PDF arrives. Close the tunnel when the round is
over.
