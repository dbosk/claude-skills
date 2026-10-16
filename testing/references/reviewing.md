# Reviewing an existing test suite

## Contents
- Ground rules
- 1. Read before running
- 2. A safe baseline
- 2a. Order, time zones and the clock
- 3. Inventory
- 4. Anti-patterns to grep for
- 5. Mutations
- 6. Privacy sweep
- 7. The report
- Working in a copy
- Migration order

Use this when asked to review, audit or improve someone's tests. The
rules in SKILL.md say what good tests look like; this file says how to
find out how far a suite is from them without doing harm on the way.

## Ground rules

- Change nothing in the repository unless asked. Work in a copy (see
  "Working in a copy").
- Contact no live service. A suite may log in with the user's stored
  credentials and write to a service, and a test environment may hold
  copies of real people's records.
- Never list the environment (`env`, `printenv`, `set`, `env -u X` with no
  command) to see which credentials exist: it prints every secret into
  the transcript. Test one variable with `[ -n "$SERVICE_USER" ] && echo
  set`, or read the names `offline_run.py` reports as removed.
- Personal data found in the sources is reported as file:line and kind,
  never the value (`src/mod.nw:120: personnummer, valid checksum`). IDs from an environment that copies production (student
  UIDs) count as personal data: they are pseudonymous, not anonymous.

## 1. Read before running

Find how the tests are run and what they touch: `Makefile`,
`pyproject.toml`, CI configuration, `CLAUDE.md`, `conftest.py`. Look for
module-level sessions and logins, credentials read at import, tests that
create, update or delete, and anything that runs at documentation build
time. In a literate project read the `.nw` test chunks, not the tangled
files: a test chunk may include production chunks
(`<<compute the result>>`), and then a test that looks like a
re-implementation does call production code.

Then find what reaches past Python, before anything runs. `offline_run.py`
refuses the usual network programs and drops AFS tokens, but not every
path out (a nytid review wrote to the live AFS cell through `pts` and
`rmtree` under `/afs` before these were covered):

    grep -rnE 'subprocess|os\.system|Popen|check_output|check_call' tests/ $(git ls-files '*.nw')
    grep -rnE '/afs/|/net/|/mnt/|/media/|expanduser|Path\.home|\$HOME' tests/ $(git ls-files '*.nw')

Read which programs and paths the hits use. A program called by absolute
path, an NFS, SMB or sshfs mount, and a fixed path into the user's real
files are not covered: `--ignore` those modules for the baseline and say
so in the report. Note module-level `shutil.rmtree`, `os.remove` and file
writes: they run at collection, also under `-k` and `--collect-only`.

## 2. A safe baseline

    ~/.claude/skills/testing/scripts/offline_run.py -- make test

It blocks the network for Python processes with an error that HTTP
clients do not retry, refuses programs that reach services themselves
(ssh, curl, gh, AFS's pts and fs; git and rsync only towards another
host), starts the run in a fresh AFS PAG and hides the Kerberos ticket,
removes credential-like variables, disables the keyring, keeps
collecting past import errors, and kills the run after 600 s
(`--timeout`). Its first line says which of these apply. If the project
keeps credentials or cached sessions in files under HOME, add
`--isolate-home`; a tool that keeps its virtual environments there
(poetry) then needs the venv's python called directly. The temporary
HOME is named and kept: `find <that dir> -type f` shows what the tests
wrote. Writes elsewhere under the real home show with a stamp file:
`touch <scratch>/stamp` before, and after the run
`find ~ -xdev -newer <scratch>/stamp -type f | sed 's|/[^/]*$||' | sort | uniq -c`
(directories only; `-xdev` keeps `find` out of `/afs`).

Read the Makefile for how flags reach pytest (`PYTESTFLAGS`,
`PYTEST_FLAGS`, `PYTEST`...): make ignores a misspelt variable without a
word. Pass `-rfEs` and check that the reasons appear, which shows the
flags arrived.

Report the counts (passed, failed, errors, skipped) and the reason for
each group. A collection error hides every test in its module, and
pytest reports it as one error: count those tests from the source and
report them as "not collected". A failure that was there before the
review is a finding in its own right; do not "fix" it by loosening the
test.

## 2a. Order, time zones and the clock

Cheap, and they find real bugs; run them in the copy, through
`offline_run.py`, and only on a green (or narrowed) baseline:

- Order: `--with pytest-randomly` (active once installed) with
  `--randomly-seed=1` and `--randomly-seed=2`, or `--with pytest-reverse`
  and `--reverse`; then each module alone
  (`for f in tests/test_*.py; do pytest -q "$f" >/dev/null || echo "$f"; done`).
  A test that passes only after another one shares state through a
  global, a config file or the service.
- Time zones: `TZ=UTC`, `TZ=Pacific/Kiritimati` (UTC+14) and
  `TZ=America/Los_Angeles`. Failures are a test that builds dates in
  local time against data in UTC, or code that compares instants where
  the domain means calendar dates; the second is a question for the user.
- The clock: tests that read `datetime.now()`, `date.today()` or
  `time.time()` and compare with what the program computed from its own
  clock fail around midnight, the end of a week, month or year. With
  libfaketime installed, `faketime '2026-12-31 23:59:50' make test` shows
  them; otherwise grep and read.

One row per test module:

| Module (source) | Tests | Needs the service | Writes | Rung | Doubles used |
|---|---|---|---|---|---|

"Rung" is the ladder in SKILL.md section 1. "Doubles used" names fakes,
monkeypatches and mocks, and whether they replace our own code or the
I/O boundary. Hand-built objects of a third-party SDK (a `MagicMock` for
a canvasapi `Course`, a `SimpleNamespace` submission) are rung 4 only
when typed against the SDK (`spec=`, `create_autospec`); unspecced they
are rung 5, and "needs the service: no" in every row then means nothing
checks what the service returns. Say which.

## 4. Anti-patterns to grep for

| Pattern | What it indicates |
|---|---|
| a session or login at module level (`client = Client.login()` outside a function) | aborts collection without credentials; hangs or writes with them |
| `assert json.dumps(`, `assert type(x) ==`, `assert x` on a container | cannot fail on `[]`, `{}` or `None` |
| `except Exception` around assertions | swallows `AssertionError` |
| `global`, module variables set by one test and read by another | order dependence; leftovers on the service |
| `monkeypatch.setattr(our_module, ...)`, `patch("our_package.` | mocking owned code |
| `call_count`, `assert_called_with`, lists of recorded calls | interaction assertions |
| hand-written dicts shaped like service responses | bodies that could be recorded |
| tests with no call into the package | tautologies |
| `assert "a" in out or "b" in out` | passes on either branch |
| `Mock()`, `MagicMock()` without `spec=` for an SDK object | any attribute works, so a misspelling or a renamed field passes |
| `patch.dict(os.environ, ..., clear=True)` | deletes HOME too: `Path.home()` falls back to the real home and the sandbox is gone |
| `datetime.now()`, `date.today()` in a test compared with program output | midnight and period-boundary failures (section 2a) |
| module state set by production code during a test (a cache, a key) and never reset | leaks into later tests |
| module-level `rmtree`, `remove`, writes | runs at collection, whatever is selected |
| `\begin{pycode}`, `\py{`, `subprocess` in documentation that prints a config, an environment or records | secrets and personal data in the PDF (literate.md) |
| literal personnummer, emails, names, IDs | privacy (section 6) |

Each hit is a lead, not a finding: read the test before reporting it.

## 5. Mutations

Pick the weakest-looking tests and break the code they claim to cover:

    ~/.claude/skills/testing/scripts/mutate.py src/pkg/mod.nw "if x > 0" "if x >= 0" -- make test

`mutate.py` first runs the command unmutated and refuses a red
baseline, since then every mutant would look killed. Narrow the command
to tests that pass, with `--ignore` for modules that fail to collect and
`-k` for failing tests:

    mutate.py src/pkg/mod.nw OLD NEW -- make test \
        "PYTESTFLAGS=-q --ignore=test_api.py -k 'not test_known_red'"

Keep the inner quotes: make hands the flags to a shell. Node IDs for
`--deselect` are relative to pytest's rootdir, not to the directory make
runs in, so `-k` is the safer choice. For several mutants write a batch
file and run it once (`mutate.py --timeout 300 --batch mutants.txt --
make test ...`): it checks that every OLD occurs exactly once before
anything runs, runs the baseline once, prints a table (label, file:line,
result) and keeps each run's output in a log. Old and new text are
written as `- ` and `+ ` lines, so several lines and backslashes need no
escaping:

    M1 src/pkg/hr.nw
    - if part_hour > QUARTER:
    + if part_hour >= QUARTER:

The batch file is also the record of what was tried: keep it with the
report. Give `mutate.py` its own `--timeout`, a little
above the suite's normal run time: a mutant that makes a test loop
forever then counts as killed and the file is restored. (`offline_run.py`
stops it with SIGTERM first, which `mutate.py` also survives, but its
default limit is long.) In a literate project, rebuild after a batch: the
tangled files still hold the last mutant.
Report killed and surviving mutants alike: a killed mutant shows a test
earns its keep. Tests that need the service cannot be mutated offline;
say so instead of guessing. A predicted result ("this mutant would
survive"), from a helper or from reading, is not a result: run it. With
`--no-baseline`, check the selection first (pytest's exit 5, "no tests
ran", is reported as an error, but a make target may turn it into a
plain failure that looks like a kill).

## 6. Privacy sweep

- `scan_leaks.py` with no paths scans `tests/` and every tracked `.nw`
  file. Pass other sources (examples, notebooks) explicitly.
- Generated documentation that ran live calls: the PythonTeX outputs
  and the PDF (`pdftotext doc.pdf - | scan_leaks.py -`). Check which
  record keys reach the output, for example by counting keys in the
  generated JSON, rather than reading the values.
- Free text and names match no pattern. `scan_leaks.py --key-census
  <paths>` lists every JSON or Python-repr key with its number of
  distinct values and the longest, never the values: a scrubbed key has
  one value, a leaking note or name field has many long ones.
- Recorded responses pasted into prose or docstrings as examples are
  data too: read them as you would a cassette.
- Configuration printed into documentation is the most likely place for
  a secret link: a private calendar address, a schedule URL with a
  token. `scan_leaks.py` reports these as `capability-url`, `url-secret`
  and `url-token`. Such a link is a credential: if it reached a
  published PDF or release, ask the user to reset it.
- `--warn-ids` lists numeric user IDs in URLs (`/users/N`,
  `/submissions/N`), which pattern scans otherwise miss.
- For a hit, find how long it has been public without typing the value,
  since the command line lands in the transcript too:
  `git log --reverse --format='%h %ad' -S"$(sed -n 120p src/mod.nw | grep -oE '[0-9]{8}-?[0-9]{4}')" | head -1`.
  Whether to rewrite history is the user's decision.

## 7. The report

A subagent cannot write report files (the harness refuses them): it
returns the report as its final message, and the lead saves it.

0. Incidents first: any contact with a live service or a credential
   during the review, what it did, and what was not checked afterwards.
1. Baseline: command, counts, reasons.
2. Inventory table.
3. Findings, most important first: file:line, the rule from SKILL.md,
   what the test does, the concrete consequence (the bug that slips
   through, what leaks, what is left on the service), the fix.
4. What is good and should be kept, with the killed mutants as evidence.
5. A plan in order, with rough effort.

## Working in a copy

- Copy with `rsync -a --exclude __pycache__ --exclude .pytest_cache` or
  `git clone --local` into a scratch directory, never `git worktree
  add`, which writes to the repository's metadata. Copied bytecode keeps
  the original paths, so tracebacks point into the original repository.
- `rsync` also copies gitignored generated files (tangled tests, built
  docs) that may be stale. Run the baseline again after a clean build
  (`make clean`, then the tests) as from a fresh checkout; it is slower.
- A literate `make test` writes into the tree it runs in (tangled files,
  woven documents, generated completions): another reason for the copy.
- An editable install (`pip install -e`, poetry, uv) puts a `.pth` file
  in the venv pointing at the *original* `src/`. Code run in the copy
  then imports the original, and every mutation "survives". Run the
  venv's python with `PYTHONPATH=<copy>/src` first, and check with one
  mutation that must be killed. A conftest that inserts a relative path
  (`sys.path.insert(0, "../src")`) depends on the working directory: run
  from elsewhere it adds nothing, and the `.pth` wins.
- `poetry run` in a copy creates a new virtual environment (and contacts
  PyPI). Call the existing venv's python directly instead. When a make
  target hard-codes `poetry run`, put an executable `poetry` shim in a
  scratch `bin/` and that first on PATH
  (`PATH=<scratch>/bin:$PATH offline_run.py -- make test`):

      #!/bin/sh
      [ "$1" = run ] || exit 1; shift
      PATH=<venv>/bin:$PATH PYTHONPATH=<copy>/src exec "$@"

  `poetry env info -p`, run in the original, prints `<venv>`.

## Migration order

For a suite far from the rules, in this order:

1. Make it run offline: sessions into fixtures that skip without
   credentials, pure tests out of modules that need the service.
2. Fix what is red, and the privacy findings.
3. Replace tautologies and assertions that cannot fail with invariants
   that hold on live data.
4. Replace mocks of owned code with the real objects over a fake I/O
   layer.
5. Record the read-only service tests (most-used endpoints first), then
   turn the remaining live tests into replayed ones and delete the
   duplicates.
6. Writes last: one fixture per test with teardown, marked `mutates`.
