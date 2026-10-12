# Record/replay in detail

## Contents
- pytest-recording and vcrpy basics
- Record modes
- Request matching
- The `--live` mechanics in the template
- Gotchas
- Non-HTTP services
- Snapshots of our own output
- Other languages

## pytest-recording and vcrpy basics

pytest-recording wraps vcrpy. A test marked `@pytest.mark.vcr` gets a
cassette at `tests/cassettes/<module>/<test>.yaml`. The plugin adds:

| Option | Effect |
|---|---|
| `--record-mode=MODE` | vcrpy record mode; the default is `none`, meaning replay only |
| `--block-network` | any real socket fails in a test without a cassette, or in replay mode; put it in `addopts` |
| `--allowed-hosts=LIST` | comma-separated exceptions to `--block-network`; use `127.0.0.1,::1,localhost` so local instances (rung 2) work |
| `--disable-recording` | vcr marks become no-ops and tests hit the network |

Fixtures you can override in `conftest.py`: `vcr_config` (kwargs for vcrpy,
function scope), `vcr_cassette_dir` (module scope), `default_cassette_name`,
and `record_mode` (session scope). Network blocking reads the **option**, not the
fixture. So a mode that must reach the network has to set
`config.option.record_mode` in `pytest_configure`, which is what the
template does for `--live`; it also turns `block_network` off there, so
that `live`-marked tests without a cassette reach the service.

## Record modes

| Mode | Behaviour | Use |
|---|---|---|
| `none` | replay only; an unrecorded request raises | default and CI |
| `once` | record if the cassette is missing, replay otherwise | a new test |
| `new_episodes` | replay known requests and append new ones | avoid: mixes old and new data in one file |
| `all` | always hit the network and rewrite | the template's `--live` (into a temp dir) |
| `rewrite` (pytest-recording) | delete the cassette and record afresh | deliberate re-record after drift |

## Request matching

The default `match_on` is method, scheme, host, port, path and query.
Headers are not matched, so filtering `Authorization` does not break
replay. Practical consequences:

- **Test inputs must be stable and non-personal.** If a test asks for
  `/users/<a real student's id>`, the request URL carries personal data.
  Drive tests with the IDs of synthetic sandbox objects instead.
- **An email or personnummer in a request URL ties the cassette to the
  key.** The scrubber replaces it with a keyed pseudonym when recording,
  and vcrpy runs the same hook on each request when matching. Replay
  without `TEST_PSEUDONYM_KEY` (CI, a colleague) uses a dummy key, gets a
  different pseudonym, and fails with "Matchers failed". Search by a
  synthetic identity at an RFC 2606 domain (`student1@example.com`, kept
  verbatim), or by an ID taken from an earlier response.
- **Self-consistent pseudonyms.** When code follows a link it found in a
  response, both the response body and the next request URL are rewritten
  through the same pseudonym map. Replay then requests the pseudonymized
  URL, which matches the recorded one.
- Volatile query parameters (timestamps, nonces) break matching. Strip
  them in `before_record_request` and in the code path, or match on a
  custom subset: `vcr_config = {"match_on": ["method", "path"]}`.
- Pagination: a live run may fetch more pages than the recording. The shape
  diff groups requests by method plus path (numeric segments become
  `{n}`), so an extra page is not reported as drift.

## The `--live` mechanics in the template

1. `pytest_configure` sets the record mode to `all` and points the cassette
   directory at `<private dir>/<project>-<hash>-live-cassettes/<same
   relative path>` (the same per-user 0700 directory as the originals
   file), or at `--live-dir=PATH` (write it with `=`: pytest would take a
   separate PATH for a test path). The directory is emptied first, so a
   stale run cannot mask drift, but only if it is empty or holds the
   `.pytest-live-cassettes` marker an earlier live run wrote; any other
   directory, and any directory containing the project, is refused.
   Tests marked `mutates` are skipped unless `--live-writes` is given.
2. Each test runs against the service, and its fresh cassette is scrubbed
   on the way to disk.
3. At session end the template:
   - scans the fresh cassettes for leaks;
   - compares each committed cassette directory with its live twin using
     `vcr_support.compare_directories`;
   - prints findings as paths and types only;
   - sets the exit status to 1 on structural drift.
4. Severity:
   - `drift`: a removed path, a changed type, a changed status code or
     content type, or a request that is no longer made;
   - `info`: an added path or a new request;
   - a path that is `null` on one side only is not a change;
   - a key the recording already showed to be optional (missing from some
     objects at its path, such as `grade` on ungraded submissions) is
     `info` when the live run never sees it;
   - a path missing under an array that held fewer items in the live run
     is `info`: the live sample may lack an item with that optional key.
     A renamed field in a shrunken array is therefore reported as one
     `info` removal plus one `info` addition; read the info lines when
     the live data is sparse.

   `cassette_shape_diff.py --strict` also fails on `info`.

Two kinds of signal come out of a live run:

- a **test failure**: our code or our assumptions no longer hold;
- **shape drift**: the recording no longer represents the service, even if
  our current assertions still pass.

Both mean "re-record and review".

## Gotchas

- **gzip**: without `decode_compressed_response=True`, bodies are stored
  as `!!binary` and the scrubbers never see them. The template sets it,
  and a test in `tests/test_recording.py` guards it.
- **Response headers**: vcrpy's `filter_headers` only touches *request*
  headers. `Set-Cookie` and similar response headers are dropped in
  `before_record_response`.
- **Content-Length**: scrubbing changes the body length, so the template
  rewrites `Content-Length` to match. Otherwise some clients truncate the
  body or hang on replay.
- **Streaming and SSE** (LLM APIs): vcrpy records the concatenated body.
  This works for `requests` and `httpx` in most cases. If it does not,
  record at the wrapper boundary (see below).
- **Binary bodies** (PDF, images) are not scrubbed. Avoid recording them:
  stub the download at our wrapper with a synthetic file (rung 2), or
  record from a sandbox.
- **Never use `yaml.load` with the full loader** on cassettes. vcrpy
  writes `!!binary` and sometimes `!!python/tuple` or a `BytesIO` body;
  `vcr_support.load_cassette` uses vcrpy's own safe loader, which accepts
  exactly those, and falls back to a safe loader with the tuple tag.
- **Non-JSON bodies** (XML, HTML, form posts) are only text-scrubbed, not
  scrubbed by key; see `privacy.md`.
- **Exceptions while recording**: vcrpy has `record_on_exception=True` by
  default, so a failing test still writes its cassette. Review before
  committing.

## Non-HTTP services

For SDKs that do not go through `http.client`/`requests`/`httpx`/`aiohttp`
(gRPC, database drivers, LDAP, a vendor CLI):

1. Put a thin wrapper of our own around the dependency, with one method per
   operation we use (Shore's *infrastructure wrapper*).
2. Give the wrapper a recording mode that saves `(operation, arguments) ->
   result` as JSON under `tests/recordings/`, scrubbed with
   `Pseudonymizer.scrub_json`.
3. Its replay mode answers from those files. The live mode calls the real
   thing and compares shapes with `vcr_support.json_shape`.

This is the same discipline as cassettes, one layer up.

## Snapshots of our own output

Use snapshots when the output is ours (rendered reports, CLI output,
generated LaTeX) and is too large to assert by hand:

- **inline-snapshot**: `assert result == snapshot()`. The value is written
  into the test source by `pytest --inline-snapshot=create` or `=fix`, and
  `=review` shows each change before it is applied.
- **syrupy**: `assert result == snapshot`, stored in `__snapshots__/`.
  Update with `pytest --snapshot-update`.

A snapshot update is a code change. Review the diff and never bulk-accept
it to get to green. Snapshots of output derived from recorded data inherit
its privacy, but scan them with `scan_leaks.py` anyway.

## Other languages

| Ecosystem | Record/replay | Notes |
|---|---|---|
| Ruby | VCR (the original) | same cassette model |
| Go | go-vcr (`dnaeon/go-vcr`) | recorder modes; hooks for scrubbing |
| JavaScript/TypeScript | Polly.js; nock (`nock.back`) | Polly has persister and matching config |
| Java/JVM | WireMock (record and playback); Betamax (unmaintained) | WireMock can proxy and record mappings |
| Any (proxy) | mitmproxy dumps; WireMock standalone | language-neutral, record at the network edge |

The principles carry over unchanged: replay by default, re-record live
into a temporary location, diff the structure, scrub before writing, and
scan before committing.
