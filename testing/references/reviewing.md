# Reviewing an existing test suite

## Contents
- Ground rules
- 1. Read before running
- 2. A safe baseline
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

## 2. A safe baseline

    ~/.claude/skills/testing/scripts/offline_run.py -- make test

It blocks the network for Python processes with an error that HTTP
clients do not retry, removes credential-like variables, disables the
keyring, keeps collecting past import errors, and kills the run after
600 s (`--timeout`). If the project keeps credentials or cached sessions
in files under HOME, add `--isolate-home`; a tool that keeps its virtual
environments there (poetry) then needs the venv's python called directly.

Report the counts (passed, failed, errors, skipped) and the reason for
each group. A failure that was there before the review is a finding in
its own right; do not "fix" it by loosening the test.

## 3. Inventory

One row per test module:

| Module (source) | Tests | Needs the service | Writes | Rung | Doubles used |
|---|---|---|---|---|---|

"Rung" is the ladder in SKILL.md section 1. "Doubles used" names fakes,
monkeypatches and mocks, and whether they replace our own code or the
I/O boundary.

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
| literal personnummer, emails, names, IDs | privacy (section 6) |

Each hit is a lead, not a finding: read the test before reporting it.

## 5. Mutations

Pick the weakest-looking tests and break the code they claim to cover:

    ~/.claude/skills/testing/scripts/mutate.py src/pkg/mod.nw "if x > 0" "if x >= 0" -- make test

`mutate.py` first runs the command unmutated and refuses a red
baseline, since then every mutant would look killed. Narrow the command
to tests that pass (`pytest -k`, or `PYTESTFLAGS=...` for a make target).
Report killed and surviving mutants alike: a killed mutant shows a test
earns its keep. Tests that need the service cannot be mutated offline;
say so instead of guessing.

## 6. Privacy sweep

- `scan_leaks.py` with no paths scans `tests/` and every tracked `.nw`
  file. Pass other sources (examples, notebooks) explicitly.
- Generated documentation that ran live calls: the PythonTeX outputs
  and the PDF (`pdftotext doc.pdf - | scan_leaks.py -`). Check which
  record keys reach the output, for example by counting keys in the
  generated JSON, rather than reading the values.
- For a hit, `git log -S` tells how long it has been public. Whether to
  rewrite history is the user's decision.

## 7. The report

1. Baseline: command, counts, reasons.
2. Inventory table.
3. Findings, most important first: file:line, the rule from SKILL.md,
   what the test does, the concrete consequence (the bug that slips
   through, what leaks, what is left on the service), the fix.
4. What is good and should be kept, with the killed mutants as evidence.
5. A plan in order, with rough effort.

## Working in a copy

- Copy with `rsync -a` or `git clone --local` into a scratch directory,
  never `git worktree add`, which writes to the repository's metadata.
- A literate `make test` writes into the tree it runs in (tangled files,
  woven documents, generated completions): another reason for the copy.
- An editable install (`pip install -e`, poetry, uv) puts a `.pth` file
  in the venv pointing at the *original* `src/`. Code run in the copy
  then imports the original, and every mutation "survives". Run the
  venv's python with `PYTHONPATH=<copy>/src` first, and check with one
  mutation that must be killed.
- `poetry run` in a copy creates a new virtual environment. Call the
  existing venv's python directly instead.

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
