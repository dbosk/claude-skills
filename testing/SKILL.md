---
name: testing
description: Write, run, review and maintain automated tests so that a green run means the real thing works: real code before fakes, recorded live data before hand-written mocks, live drift checks, and no personal data in test data. Use proactively when (1) writing, fixing, reviewing or deleting tests, adding tests or coverage, doing TDD or red/green, or making failing tests pass; (2) mock, MagicMock, patch, monkeypatch, responses, VCR, vcrpy, pytest-recording, cassettes or snapshots come up; (3) code under test calls an external service or API (Canvas, LADOK, GitHub, an LLM, a database); (4) tests are flaky, pass while the code is broken, or break on every refactor; (5) test data may hold names, emails, personnummer or tokens; (6) starting work in a repository that has tests (run them first). Pytest-centred, with principles for any language; covers literate (.nw) projects too.
---

# Testing

A test that passes while production breaks buys false confidence. Every
rule below serves one goal: **a green run should mean the real thing
works**, and the test data should never leak anyone's personal data.

## 1. The test-double ladder

Start at the top and step down only when the rung above is impossible or
impractical. **Write the reason for stepping down in the test** (a comment
or docstring).

| Rung | Use | Examples |
|---|---|---|
| 1. Real code | Default. Sociable tests through our real collaborators; assert on outputs and state, not on which functions were called. | pure functions, parsers, our own classes wired together |
| 2. Real local instance | When a dependency can run locally. | `tmp_path` files, SQLite or an in-memory DB, a real `git init` in tmp, `http.server` on localhost, a container |
| 3. Recorded replay | When the dependency is a remote service. Record the **live** responses once, pseudonymized (section 4), and replay them offline. A recording covers only what was recorded: error paths and edge cases need an injected failure (rung 5) or a fake (rung 4). | pytest-recording/vcrpy cassettes; JSON fixtures captured at our wrapper for non-HTTP SDKs |
| 4. Hand-written fake | Only when replay cannot express the case, for example a state machine across many calls. Put the fake behind our own thin wrapper (Shore's *Nullables*), and cover it with the live check in section 3. The wrapper is the owned code whose only job is I/O: one method per request, no decisions. Fake that layer only; everything with logic above it runs for real. | `FakeCanvas` implementing our `CanvasClient` interface |
| 5. Mock/patch | Only for things that cannot be recorded or made real: the clock, randomness, injected failures (timeouts, 500s, disk full). Even then, prefer passing the dependency in (a `now` parameter, a seeded `random.Random`) over `patch`. | `freezegun`, a seeded RNG, an injected 503 (`responses`, `respx`, or the rung-4 fake) |

Never:
- mock code we own just to isolate a unit;
- assert on call sequences (`assert_called_with`) when a result or state can be checked instead;
- hand-write a response body that we could have recorded from the live service;
- let tests share state: each test sets up what it needs, so order and
  parallel runs do not change the outcome;
- write a test that never calls the code under test, such as one that
  re-implements the logic or checks Python's arithmetic on a hand-built
  input: it passes whatever the code does;
- create a service session or log in at import time: take it from a
  fixture, so missing credentials skip those tests instead of aborting
  the whole run.

Interaction assertions tie a test to how the code works, so refactoring
tends to break them; keep them for effects that cannot be observed
otherwise, such as a call to an external service. Assert such effects at
the outermost owned boundary, on the recorded requests or the fake's
state, not on calls to our own domain objects. A hand-written body
encodes what we *believe* the service returns, and keeping such doubles in
step with the real service is a known, reported problem.

## 2. One test body, two modes

A test that touches a service should run in two modes, **with the same test
body**:

| Mode | Command | What it proves |
|---|---|---|
| Replay (default) | `pytest` with `--block-network` in `addopts` (section 6) | Our code handles the recorded responses. Fast, offline, deterministic. |
| Live | `pytest --live` | The service still behaves like the recording. |

The same body has to pass on live data too, so service-facing tests assert
the **strongest invariants** that stay true on live data ("the totals add
up"; "the synthetic test user is enrolled in the sandbox course"), not
exact values that change from day to day. Shapes alone are too weak:
assertions that check too little miss bugs. Keep exact-value assertions
for pure logic fed with synthetic inputs (rung 1).

Live runs are **local and opt-in**. No credentials go into CI. Run
`pytest --live` before a release, when the service announces changes, when a
replay test and real usage disagree, and periodically on long-lived
projects.

A live run repeats every request, writes included. Mark a test that changes
the service (POST, PUT, DELETE: publishing a page, setting a grade) with
`@pytest.mark.mutates`. It replays normally, but runs live only with
`pytest --live --live-writes`, against a sandbox, and it must be safe to
repeat: a fixture creates a fresh object and removes it in its teardown,
so a failure halfway leaves nothing behind. Never chain write tests
through module globals. In replay the template matches request bodies
and fails a test that skips a recorded request, so a wrong PUT body or a
missing DELETE is caught offline too.

The template assumes an API token. Services with cookies, a CSRF token,
SSO or MFA (LADOK, KTH login) need a session fixture instead, a login
outside the cassette, and attended live runs: see
`references/record-replay.md`.

## 3. Detecting outdated recordings

A recording is a snapshot of someone else's system, and it goes stale
silently: Web APIs often ship breaking changes without a major version
bump. `pytest --live` with the bundled template does three things:

1. runs every recorded test against the real service. A failure means our
   code or our assumptions are outdated;
2. re-records into a **temporary directory**, never over the committed
   cassettes;
3. compares the structure of the fresh and the committed cassettes: status
   codes, content types, JSON key paths and value types. Values are never
   compared and never printed. A key missing only because the live data
   had fewer items is reported as info, not drift.

When drift is found:
- read the drift report;
- fix the code if the change affects it;
- re-record deliberately with `pytest --record-mode=rewrite -k <test>`;
- review the cassette diff and commit.

A drift report is a task to restore consistency. Do **not** paper over it
by editing the cassette by hand.

To compare two cassette directories by hand:
`scripts/cassette_shape_diff.py COMMITTED LIVE [--strict]`.

## 4. Privacy: no personal data or secrets in tests

Names, emails, usernames, personnummer, student IDs, free-text comments and
tokens must never reach a committed file. The same goes for test output and
the agent's own transcript. The protection comes in layers, each catching
what the one before missed:

1. **Source.** Record against a sandbox or test account filled with
   synthetic data whenever one exists. Drive tests with identifiers of
   synthetic objects, never of real people. Check that the sandbox really
   is synthetic: some test environments are copies of production (LADOK's
   is re-synced from production every week), and then every person in it
   is real and layers 2 and 3 carry the whole load. In code, use the
   fictive Tolvan personnummer 19121212-1212, which the scan allows.
2. **Scrub at record time** (`assets/vcr_support.py`; recording refuses
   to start without the `TEST_PSEUDONYM_KEY` secret). Secrets are filtered;
   identities in person-shaped objects become keyed-HMAC pseudonyms, the
   same everywhere; free text is replaced wholesale, because prose can name
   anyone; known names are rewritten wherever else they appear, URLs
   included. Add the service's own field names to the key lists. For
   synthetic sandbox prose that a test must read, mark the test
   `@pytest.mark.synthetic_text("body")`.
3. **Verify.** After every recording, the template scans the written
   cassettes for every original value it replaced and for email,
   personnummer, JWT and token patterns. The run fails, printing only
   redacted stubs. Before committing, run `scripts/scan_leaks.py` with
   `--denylist` pointing at a roster kept *outside* the repo: it catches
   people the scrubber never recognised, for example in XML bodies, which
   are not scrubbed by key. Known false positives go in an `--allow` file.
4. **Output hygiene.** Live assertions must not echo records: assert on
   keys, counts and booleans, since pytest prints the compared values on
   failure. Do not `print` or `cat` live responses to inspect them, because
   whatever the agent reads ends up in its transcript. Use the shape diff
   instead. Generated documentation that runs live calls (PythonTeX,
   notebooks, README transcripts) is output too: print only the keys it
   needs, and scan the generated files before publishing.

For us, as holders of the key, pseudonymized data are still personal data,
so the key never goes into the repo. If a leak is ever committed, treat it
as published. `references/privacy.md` has the details and the GDPR
reasoning.

## 5. Working rules for agents

- **First run the tests** at the start of a session (Willison's prompt), so
  you know the baseline, the runner and the size of the suite. Run an
  unfamiliar suite through `scripts/offline_run.py -- <test command>`
  first: its tests may log in to a service or write to it. It blocks the
  network for every Python process, removes credential variables (naming
  them, so never list the environment yourself), disables the keyring,
  keeps collecting past modules that fail to import, and stops a run that
  hangs.
- **Red/green.** Write the test first, from the spec or the bug report
  rather than from the implementation, and watch it fail *for the right
  reason* before writing the fix. A test that already passed before the
  change has not shown it can detect what the change fixes, and tests
  derived from finished code tend to encode its bugs. For a bug, the
  failing test must reproduce the bug.
- **Never weaken a test to get green.** Do not edit an assertion, add a
  skip or xfail, delete a test, loosen a tolerance, or special-case the
  implementation to satisfy one test, unless you say so explicitly and say
  why. If the test is wrong, say that and fix the test as a separate,
  visible step.
- **Show evidence.** Report the command you ran and its result. Never
  claim "tests pass" without having run them.
- **Manual check, then pin it.** Try the change for real: `python -c`,
  the CLI, `curl` against a dev server. Turn every surprise into a
  red/green test.
- **Check that the test can fail.** After a green run that came too
  easily, break the code on purpose (a mutation) and confirm the test goes
  red: `scripts/mutate.py FILE OLD NEW -- <test command>` checks that the
  command passes as is, makes the change, runs it again and restores the
  file. This shows the test catches that break, not that the suite is
  adequate. Pass `--timeout` above the suite's run time, so a mutant that
  hangs counts as killed and is restored.
- **Fresh-context review** for larger changes: a subagent that sees only
  the diff checks whether the tests exercise behaviour or just mirror the
  implementation. Ask it for checks it can run (break the code: does a
  test go red?), not for an opinion.
- **Reviewing an existing suite**: work in a copy, contact no service,
  report personal data as file:line and kind only, and follow the steps
  in `references/reviewing.md` (baseline, inventory, greps, mutations,
  privacy sweep, report).

`references/agent-practices.md` has the prompt phrasings and the reasoning.

### Literate programs

Everything above applies to literate (`.nw`) projects, with the `.nw`
file as the place where tests live:

- tests are chunks in the `.nw`, *written* first (red/green) but *placed*
  after the code they verify in the woven document; the reason for
  stepping down the ladder goes in the prose before the chunk;
- edit and mutate the `.nw`, never the tangled `.py`; give the command
  that tangles and tests (`make test`) to `offline_run.py` and `mutate.py`;
- scan the `.nw` sources (the default of `scan_leaks.py`) and the woven
  outputs, not only the generated `tests/`.

Load the `literate-programming` skill, and see `references/literate.md`
for the templates, cassettes and `make clean`.

## 6. Setting up a project (pytest)

1. Add the test dependencies: `pytest`, `pytest-recording` (which brings
   vcrpy and PyYAML) and, for our own output formats, `syrupy` or
   `inline-snapshot`.
2. Copy `assets/conftest.py` and `assets/vcr_support.py` into `tests/`.
   Set `SERVICE_TOKEN_ENV`, and extend the key lists in `vcr_support.py`
   for the service's identity and free-text fields.
3. In `pyproject.toml`, under `[tool.pytest.ini_options]`, set
   `addopts = ["--block-network", "--allowed-hosts=127.0.0.1,::1,localhost"]`,
   so replay is offline while local instances (rung 2) still work.
4. Mark service tests with `@pytest.mark.vcr` and take the credential from
   the `service_token` fixture. Record each one with
   `TEST_PSEUDONYM_KEY=… pytest --record-mode=once -k test_name`.
5. Review every new cassette diff before committing it, then run
   `scan_leaks.py`.

| Task | Command |
|---|---|
| First run of an unfamiliar suite | `~/.claude/skills/testing/scripts/offline_run.py -- make test` (or `-- uv run pytest`) |
| Offline run | `pytest` |
| Record a new test | `pytest --record-mode=once -k test_x` |
| Check for drift | `pytest --live` (`--live-writes` to include `mutates` tests) |
| Re-record after drift | `pytest --record-mode=rewrite -k test_x` |
| Leak scan | `python3 ~/.claude/skills/testing/scripts/scan_leaks.py tests --denylist ~/private/roster.txt` |
| Does a test catch this break? | `~/.claude/skills/testing/scripts/mutate.py src/mod.py "a + b" "a - b" -- pytest -q` |
| Compare shapes by hand | `uv run --with vcrpy ~/.claude/skills/testing/scripts/cassette_shape_diff.py tests/cassettes <live dir printed by pytest --live>` |

## References

Read when needed:

- `references/record-replay.md`: when setting up recording, when replay
  does not match, for non-HTTP services, snapshots, or other languages.
- `references/privacy.md`: when configuring the key lists for a new
  service, or when something leaked.
- `references/agent-practices.md`: when writing prompts for a subagent or
  explaining the working rules.
- `references/literate.md`: in a literate (`.nw`) project.
- `references/reviewing.md`: when reviewing or auditing an existing suite
  (baseline, inventory, greps, mutations, privacy sweep, report).
- `tests/`: the skill's own tests (real local HTTP server, real files,
  real subprocesses, no mocks). Run them after changing the assets:
  `uv run --no-project --with pytest,pytest-recording,pyyaml pytest ~/.claude/skills/testing/tests`.

Audit trail, not needed for everyday work: `references/sources.md` gives
the verdict on each piece of advice; `references/literature-review.md` is
the full two-sided literature review behind it (one chapter per claim);
`references/literature/` holds the provenance BibTeX and the search
exports.
