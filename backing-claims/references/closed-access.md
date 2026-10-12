# Closed-access full texts through the university network

Some publishers serve a subscribed full text only to the university's
network. A SOCKS tunnel through the faculty shell server gives requests a
KTH address. The commands below are the skill's `allowed-tools`, so the
permission system lets them run unprompted while this skill is active.
Run them in exactly that form; a loop or wrapper script around them does
not match the rule.

## Open, fetch, close

```bash
# 1. open the tunnel (once per session)
ssh -o BatchMode=yes -o ExitOnForwardFailure=yes -f -N -D 127.0.0.1:1081 faculty-shell.sys.kth.se

# 2a. scholar's fetcher, through the tunnel (lands in scholar's PDF cache)
SCHOLAR_PROXY=socks5h://127.0.0.1:1081 \
  ~/.claude/skills/backing-claims/scripts/fetch_pdf.py --text <url-or-doi> ...
#     scholar without --proxy (before dbosk/scholar#118): fetch_pdf.py says
#     so and stops; use the requests variables instead
HTTPS_PROXY=socks5h://127.0.0.1:1081 HTTP_PROXY=socks5h://127.0.0.1:1081 \
  ~/.claude/skills/backing-claims/scripts/fetch_pdf.py --text <url-or-doi> ...

# 2b. curl, through the tunnel (one call, several -o FILE URL pairs)
curl -sL --max-time 40 -x socks5h://127.0.0.1:1081 \
  -w '%{http_code} %{content_type} %{size_download}\n' \
  -o <dir>/<Key>.pdf <url> ...

# 3. close it when done
pkill -f '[D] 127.0.0.1:1081'
```

`fetch_pdf.py` prints the route it takes (`# route: proxy
socks5h://127.0.0.1:1081 (SCHOLAR_PROXY)`) and stops with exit 2 on a
proxy URL that cannot work, e.g. SOCKS without PySocks in scholar's venv
(`pipx inject scholarcli PySocks`). Use `socks5h://`, not `socks5://`:
with `h` the tunnel also resolves the host names, so DNS answers come
from the campus side too.

Check the exit address first:
`curl -sL --max-time 40 -x socks5h://127.0.0.1:1081 https://api64.ipify.org`
must print a KTH address (2001:6b0:…). With a scholar that has the
network layer, `scholar --proxy socks5h://127.0.0.1:1081 providers check
--show-ip` prints the route and the exit address and probes every
provider from there (it asks ipify, a third party, only with
`--show-ip`); it is not one of the allowed commands, so it prompts.

## What works and what does not (fetch round 2026-10-10, 41 sources)

- **Prefer 2a, fall back to 2b.** In that round `fetch_pdf.py` sent
  Python `requests`' default user agent, which most publishers refused
  (403, or an HTML page instead of the PDF) whatever the address; curl
  got through where Python did not. Scholar now sends its own
  `scholar/<version> (+https://github.com/dbosk/scholar)` user agent
  (dbosk/scholar#118; no e-mail address in it); whether publishers
  treat that better has not been tested yet, so keep 2b as the fallback
  and note which publishers answer 2a in the next round.
- **Never imitate a browser.** Do not set a browser user agent on curl
  (`-A`) or through `SCHOLAR_USER_AGENT`, and do not reach for
  browser-automation tools to get a PDF. A browser `-A` string made
  Springer switch to a "Client Challenge" page for every later request;
  curl's default agent then fetched the PDFs again.
- **Stop at a challenge.** A bot check (Cloudflare, a "Client
  Challenge" page, a login page) is a stopping point: do not retry or
  vary the request. Retries escalate the blocking, and getting past a
  bot check is circumvention, not access. The paper goes on the
  leftover list below.
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
