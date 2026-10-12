# Testing practices for coding agents

Prompt phrasings and the reasoning behind section 5 of SKILL.md. Most come
from Simon Willison's *Agentic Engineering Patterns* (chapters "Red/green
TDD", "First run the tests", "Agentic manual testing") and the Claude Code
best-practices guide. Practices that rest on practitioner experience rather
than studies are marked as such in `sources.md`.

## First run the tests

Prompt: "First run the tests" (or the exact command, e.g. `uv run pytest`).

Why:
- the agent finds out how to run the suite, so it is likely to run it
  again after changes;
- the number of tests hints at the project's size and where to read;
- it sets a testing mindset for the rest of the session;
- it gives a **baseline**, so a failure that was already there is not
  blamed on the new change, and is not "fixed" by weakening it.

## Red/green

Prompt suffix: "Use red/green TDD."

1. Write the test for the new behaviour or the bug.
2. Run it and confirm it fails, and that it fails for the expected
   reason: the assertion about the behaviour, not an import error or a
   typo.
3. Implement until it passes.
4. Run the whole suite.

A test that was never red has not shown it can detect anything. For bug
fixes, the red run *is* the reproduction.

Write the test from the spec, the issue or the bug report, not by reading
the implementation. When an LLM writes tests after seeing faulty code, the
tests tend to agree with the fault: Konstantinou et al. (2026) measured 14%
fault detection for tests generated after faulty code against 25% for
tests generated from the task description alone.

The evidence is about *where the test comes from*, not about TDD as a
method. Studies of human TDD are mixed: meta-analyses find small quality
gains and no productivity gain, and the order of writing matters less than
working in small steps (see `sources.md`). And telling a small model
*how* to do TDD can backfire: in Alonso et al. (2026), a procedural TDD
prompt raised regressions from 6.1% to 9.9%, while telling the agent
*which* tests cover the code it changed cut them to 1.8%. So keep the
instruction short, and point the agent at the relevant tests.

## Do not game the tests

An agent optimising for green can weaken the check instead of fixing the
code. Forbidden unless stated openly, with the reason:

- editing an expected value to match the current output;
- adding `skip`/`xfail`, deleting a test, or catching the exception in the
  test;
- loosening tolerances or replacing an exact assertion with `is not None`;
- special-casing inputs in the implementation (`if x == 42: return 7`);
- replacing a real dependency with a mock so that the failure disappears.

If a test is genuinely wrong, say so and fix it as a separate step, with
the evidence for why it is wrong.

## Show evidence

Report the command and its result ("`uv run pytest` → 214 passed, 2
skipped (live)"), not "all tests pass". Willison's Showboat tool and
similar demo documents formalise this: the `exec` step records what
actually happened, not what the agent hoped happened.

## Agentic manual testing

Passing tests do not prove the feature works: the app may crash on start,
or a case may be uncovered. So try it:

- Python library: "Try that new function on some edge cases using `python -c`".
- Other languages: write a scratch program in a temp directory, never in
  the repo, then compile and run it.
- JSON API: "Run a dev server and explore that new JSON API using `curl`".
- Web UI: drive a browser (Playwright, or the claude-in-chrome skill) and
  look at screenshots.

Every surprise becomes a red/green test, so the manual finding is kept.

For services with personal data, manual exploration goes against the
sandbox, never against production records (privacy layer 4).

## Check that the test can fail

When a new test goes green on the first run, or a suite passes suspiciously
easily, mutate the code on purpose: invert a condition, drop a filter,
return early. Confirm that some test goes red, then restore the code.
Doing it in a scratch copy keeps the working tree clean. The skill's own
tests were checked this way, and one mutation (gzip decoding switched off)
survived until a gzip test was added.

## Fresh-context review

For larger changes, have a subagent review the diff without the reasoning
that produced it. Ask specifically:

- Do the tests exercise behaviour through real code, or mirror the
  implementation (mocks returning what the code expects)?
- Is there a test that would fail if the feature were removed?
- Did any test get weaker in this diff?

Tell the reviewer to report only gaps that affect correctness. A reviewer
asked to find problems will otherwise invent some.

What the evidence supports, and what it does not:

- Models correct their own mistakes poorly without external feedback
  (Huang et al. 2024; Kamoi et al. 2024). So the reviewer's most useful
  output is a runnable check, such as a mutation that should turn a test
  red, not an opinion.
- A second review in a fresh session beat a second review in the
  producing session (Song 2026, one model, planted errors). The same study
  did not show a fresh review beating a single self-review.
- Guey & Bougault (2026) found no self-preference when models judged
  machine-verified fixes to their own drafts. That was text, not code.

So use fresh-context review as a cheap second look, never as a substitute
for running the tests.

## Splitting writer and tester

For a feature with a clear spec, one session or subagent can write the
tests from the spec, and another can write code to pass them without
editing the tests. Separating the two removes the incentive to bend the
tests to the implementation.

## Literate programs

With noweb (`.nw`), red/green still governs the *order of work*: write the
test chunk, tangle, see it fail, then write the implementation chunk. The
*woven document* still places each test after the code it verifies, as the
literate-programming skill requires. One is the order of writing, the other
the order of reading.
