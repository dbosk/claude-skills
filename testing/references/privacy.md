# Privacy in test data

## Contents
- What counts as sensitive
- Layer 1: source
- Layer 2: scrubbing and pseudonymization
- Layer 3: verification
- Layer 4: output hygiene
- Keys and files
- When something leaked anyway

## What counts as sensitive

Secrets include tokens, API keys, cookies, session IDs, passwords, signed
URLs and JWTs, and capability links: a calendar's secret iCal address, a
schedule or document URL with a token in it. Whoever holds such a link
reads the data, so it is a credential even when it sits in a config
file. A leaked one is reset at the service, like a password.

Personal data is anything that identifies a person, directly or together
with other data:

- names, in any form or order;
- emails, postal addresses and phone numbers;
- usernames and login IDs;
- personnummer and samordningsnummer;
- student and employee IDs (`sis_user_id`, KTH-id);
- avatar and profile URLs;
- IP addresses;
- free text written by or about people (submissions, comments, messages);
- grades together with any of the above.

Pseudonymization reduces risk but does not make data anonymous (GDPR Art.
4(5), Recital 26). For whoever holds the key, pseudonymized data are
personal data (EDPB Guidelines 01/2025, para. 22). The CJEU has held that
pseudonymized data are not personal "in all cases and for every person":
for a recipient without the key, it depends on whether they have the means
to re-identify (C-413/23 P, *EDPS v SRB*, 2025, decided under Regulation
2018/1725, which uses the GDPR's definitions). For the controller's duty
to inform data subjects, the court assessed identifiability from the
controller's point of view at the time of collection; for our recordings
the controller is us, and we hold the key. Do not lean on the recipient
argument either: test data may later reach people who also have access to
the service, and a public service lets anyone re-identify through its API.
That is why the key stays out of the repository. The EDPB also notes that
a plain hash of an identifier can be reversed by hashing candidate values;
a keyed MAC, as used here, avoids that.

## Layer 1: source

Prefer data that was never personal. First find out whether the test
environment is: some are copies of production. LADOK's test environment
is re-synced from production every week, so every student in it is a
real person, and an ID or grade taken from it is real personal data. Ask
the service's administrators or read its documentation. If no one can
say, treat the environment as a copy. Then source data is not a layer at
all, and the scrubbing and the scan below carry the whole load.

For a personnummer in code, tests and documentation, use the fictive
Tolvan Tolvansson, 19121212-1212 (Skatteverket's test identity). The scan
does not report it.

- a sandbox course or test tenant populated with synthetic users and
  content (see the kth-data skill for the Canvas sandbox);
- synthetic inputs created by the test itself (rung 2);
- for tests that need prose, synthetic prose written into the sandbox.
  Real prose is redacted at record time.

## Layer 2: scrubbing and pseudonymization

`assets/vcr_support.py` `Pseudonymizer`, wired up by `vcr_config()`:

| Mechanism | What it does |
|---|---|
| `filter_headers`, `filter_query_parameters`, `filter_post_data_parameters` | drop credentials from the recorded request |
| response headers | `Authorization` and `X-Auth-Token` dropped; `Set-Cookie` kept with each value replaced by `redacted`, so cookie-based clients still work in replay; other values text-scrubbed |
| `SECRET_HEADERS` | request credentials, including CSRF headers (`X-XSRF-TOKEN`) |
| form secrets | `SAMLResponse`, `SAMLart` and the `SECRET_QUERY_PARAMS` names are redacted in form bodies and HTML `<input>` fields |
| `decode_compressed_response=True` | gzip bodies become text before the hooks run |
| `NAME_KEYS` | `Person-<hmac6>`; tokens are sorted first, so "Svensson, Anna" equals "Anna Svensson" |
| `AMBIGUOUS_NAME_KEYS` (`name`) | pseudonymized only in person-shaped objects: ones that also carry an identity field, or sit under a key in `PERSON_PARENT_KEYS` (`user`, `author`, `teachers`, …). Course, repo and file names stay readable, so tests can assert on them in both modes |
| `NON_PERSON_TYPES` | objects with `"type": "Organization"` or `"Bot"` (GitHub) keep their `login` and `name` |
| `EMAIL_KEYS` | `person-<hmac6>@example.invalid` |
| `LOGIN_KEYS` | `user-<hmac6>` (numbers too); a UUID becomes another UUID |
| `PNR_KEYS` | a fake personnummer `000000-NNNN`, by key, whether or not the checksum is valid |
| `CONTACT_KEYS` | postal address, postcode, city and phone: `[redacted contact]`. City and postcode (`UNLOGGED_CONTACT_KEYS`) are not added to the originals file: they also name courses and fill code tables |
| `ID_KEYS` (opt-in, empty by default) | same-type pseudonymous IDs; long ones also rewritten in URLs |
| `FREE_TEXT_KEYS` | replaced by `[redacted free text]`, except the keys a test names in `@pytest.mark.synthetic_text(...)` |
| `URL_IDENTITY_KEYS` | replaced by `https://example.invalid/redacted` |
| JSON in a string | a string value that holds a JSON object or array is scrubbed as JSON |
| request URIs | path and query values are also scrubbed percent-decoded, so `search_term=anna%40uni.example.se` is caught |
| second pass | every remaining string has known originals (full names, both orders, emails, logins, URL-quoted forms), any email and any valid personnummer replaced |

The defaults cover Canvas, GitHub and LADOK. LADOK's keys are
`Fornamn`, `Efternamn`, `Personnummer`, `Epostadress`, `Epost`,
`Anvandarnamn`, `SenastAndradAv` (the staff member who last changed a
record, as an email), `Utdelningsadress`, `Postnummer`, `Postort`,
`Telefonnummer`, the decision maker `Beslutsfattare` and the free-text
`Anteckning`. A person's `Uid` is pseudonymized as a login when the
object is person-shaped, keeping its UUID shape. But in LADOK the `Uid`
is also the opaque record ID that tests request by, so pseudonymizing it
breaks replay of any test that names one. To keep UIDs, pass
`login_keys=vcr_support.LOGIN_KEYS - {"uid"}` to the `Pseudonymizer` in
the copied `conftest.py`, and treat the cassettes as pseudonymous
personal data (chapter 10 of the literature review): a project may then
decide to keep them local and gitignored rather than commit them.

Configure per service by editing the key sets at the top of the copied
`vcr_support.py`. A person object that has only a `name` and sits under a
key not in `PERSON_PARENT_KEYS` is not recognised; add the key, and rely
on the denylist scan (layer 3) for what remains. Add the service's own
field names. Removing a key needs a
comment explaining why. A typical case is a test that parses prose, which
must then record from synthetic sandbox data.

Identifier fields such as `id` are kept by default, because replay
matching needs them for tests that hard-code an ID in a request. On a
service that requires login (Canvas, LADOK), an ID identifies a person only
to someone with access to that service. On a **public** service it
identifies the person to anyone: a GitHub user ID resolves to the account
through the public API. For such services, or whenever the IDs themselves
are sensitive:

- add the fields to `ID_KEYS`. Integers become integers with the same
  number of digits, UUIDs become other UUIDs, other strings become
  `id-<hmac8>`, and IDs of four or more
  digits are also rewritten inside URLs and text;
- drive those tests from IDs found in earlier responses, not hard-coded
  ones.

Encoded forms such as GitHub's base64 `node_id` are not decoded. Add such
fields to `URL_IDENTITY_KEYS`, which replaces the value with a placeholder.

**Non-JSON bodies** (XML such as LADOK's `application/vnd.ladok+xml`,
HTML, form posts) are not scrubbed by key: only names already learned from
JSON, emails and personnummer are replaced in them. Prefer the service's
JSON variant; otherwise record from a sandbox, and rely on the denylist
scan. Binary bodies are not scrubbed at all.

**Order.** The pseudonymizer lives for the whole pytest session and keeps
learning, so a name seen in one test is also rewritten in the free strings
of a later one. Recording a single test with `-k` can therefore give a
slightly different cassette than recording the whole suite; the scan
still runs on both.

## Layer 3: verification

- **During recording**, every original the pseudonymizer replaced is
  appended to an originals file. The default is
  `vcr-originals-<uid>/<hash>.txt` under `$XDG_RUNTIME_DIR` or the temp
  dir: a directory of mode 0700, a file of mode 0600, opened without
  following symlinks, and refused if anyone else owns it or can read it
  (the temp dir is shared on multi-user machines); override
  it with `TEST_ORIGINALS_FILE`. The file holds full values, name parts of
  three characters or more, and email local parts.
- **At session end**, the template scans every cassette it wrote for those
  originals (case-insensitive, whole words) and for the pattern set: email
  outside `example.*`, Luhn-valid personnummer, JWT, bearer tokens,
  assigned secrets (`access_token=…`, `client_secret: …`) and capability
  links (`/private-<hex>`, secret-named query parameters, long mixed
  tokens in URLs). A token must look random (digits or mixed case), so
  prose and placeholders such as `your-api-token` pass. Lines are also
  checked percent-decoded, and cassettes are also checked unfolded, since
  the YAML dumper can split a name across two lines. A hit fails the run.
  Name parts inside a URL host (`kth` in `canvas.kth.se`) are not hits. A
  name part that is also an ordinary word (Max, Will) can still give a
  false hit: check the stub, and if it is a false positive, delete that
  line from the originals file and run the scan again.
- **On real data the originals check can be noisy.** A first name such
  as Max matches `Cache-Control: max-age=0`, a surname matches a place
  name in a code table. The originals file also grows with every
  recording. If deleting lines by hand stops scaling, allow, *per
  cassette*, the originals that occur in that cassette's public text:
  translation and code-table keys (LADOK's `sv`, `en`, `Text`,
  `Benamning`, `Kod`), whole responses from endpoints that list no
  people (code tables, i18n, course information, but not a staff list on
  the same service) and header values other than cookies and
  credentials. Allowing globally would hide real hits, because a
  place-name table holds many surnames. Two traps in such a pass: the
  raw YAML has escapes, so `X` in `X\xF6` reads as a word, and an
  escaped `\n` glues an `n` onto the next word; split on the parsed
  strings instead. (The ladok3 project's `public_originals()` is a worked
  example.)
- **Before committing**, run
  `scan_leaks.py tests --denylist <private roster>`. The denylist catches
  people the recording never saw, such as a name typed into a hand-written
  fixture. `--warn-names` adds a heuristic for capitalized word pairs,
  which is noisy and only warns: on Swedish data most hits are course
  names. `--key-census` is the sharper tool for free text: it lists each
  key with its number of distinct values and the longest, never the
  values, so a note or name field that escaped scrubbing stands out
  (many long values where a placeholder should be). After a recording,
  `scan_leaks.py` also matches that recording's originals file and says
  so; pass `--originals /dev/null` to scan sources without it. Known false positives, such as a fixture's placeholder address,
  go in a file passed with `--allow` (exact values, or `re:REGEX`), which
  may be committed since it holds no personal data. With no paths, the
  scan covers `tests/` and every `.nw` file git tracks; `-` reads
  standard input. Add it as a pre-commit hook:

  ```yaml
  - repo: local
    hooks:
      - id: scan-test-data
        name: scan test data for personal data and secrets
        entry: python3 ~/.claude/skills/testing/scripts/scan_leaks.py
        language: system
        files: ^tests/
  ```

Hits are always printed redacted (`An…(13 chars)`), so the scan output is
itself safe to show.

## Layer 4: output hygiene

- In live tests, assert on derived facts: `assert all("name" in u for u in
  users)`, `assert len(rows) == expected_count`. Do not write
  `assert users == [...]`, because pytest prints both sides on failure.
- Do not print, log or dump live payloads. Use `-p no:cacheprovider` if
  test IDs could carry personal data (parametrize IDs end up in
  `.pytest_cache`).
- Generated documentation that runs live calls (PythonTeX, notebooks,
  README transcripts) is output too, and a published PDF reaches more
  readers than a terminal. Print only the keys the text needs, or scrub
  whole records with the `Pseudonymizer`, then scan the generated files
  (`pdftotext doc.pdf - | scan_leaks.py -`) before publishing. See
  `literate.md`.
- A project may already have its own scrubber (a function that replaces
  `Fornamn`, `Personnummer`, ... before printing). Such a list of keys to
  remove misses every key nobody thought of, free text included. Prefer
  keeping only the keys the output needs; otherwise run its output through
  `scan_leaks.py`, and extend it from the key lists here.
- Agents: never list the environment (`env`, `printenv`) to check for
  credentials; test one variable with `[ -n "$VAR" ]`. A listing prints
  every secret into the transcript.
- Agents: never `cat` a live response or a freshly recorded cassette before
  the scan has passed. Inspect structure with
  `vcr_support.json_shape(...)` or the shape diff. Anything printed lands
  in the transcript, which may be stored or shared.

## Keys and files

| Item | Where | Never |
|---|---|---|
| `TEST_PSEUDONYM_KEY` | keyring or password manager, exported for a recording session | in the repo, CI, or a dotfile in the project |
| service token | env var named in `SERVICE_TOKEN_ENV`, from the keyring | in a cassette (filtered) or the repo |
| originals file | private temp dir, 0600 | in the repo; delete it after committing (`scan_leaks.py` warns when one passed with `--originals` is missing) |
| denylist / roster | private directory outside any repo | in the repo |
| `--allow` list | the repo is fine: it holds placeholders, not people | real values, to silence a true hit |

Keep the key stable across recordings. A new key changes every pseudonym,
which makes re-record diffs unreadable. Create it once without printing
it, and export it from the keyring for a recording session:

```sh
python3 -c "import secrets; print(secrets.token_urlsafe(32), end='')" \
  | secret-tool store --label="test pseudonym key" service myproject key test-pseudonym
export TEST_PSEUDONYM_KEY="$(secret-tool lookup service myproject key test-pseudonym)"
```

## When something leaked anyway

1. Stop. Do not push. If it is already pushed, treat the data as published.
2. Rotate any secret that leaked. This is the only real fix for a secret.
3. Remove the data from the working tree, fix the scrubber (add the key),
   and re-record.
4. Ask the user before rewriting history (`git filter-repo`) or
   force-pushing. Mirrors, forks and caches may still hold the data.
5. For personal data, tell the user: a breach may need reporting under
   their organisation's GDPR routine.
