"""Tests for validate_screen.py: real files in tmp_path, the real script run
as a subprocess (python3 -I), no mocks.  Records are invented.

Run: python3 -m pytest ~/.claude/skills/backing-claims/scripts/test_validate_screen.py
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).with_name("validate_screen.py")
HEADER = ["id", "verdict", "category", "exclusion", "theme", "confidence", "reason"]
EXCL = "off-question,no-abstract"


def batch(n=5):
    return [{"id": f"doi:10.1/x{i}",
             "title": f"Study {i} of reference errors in chatbots",
             "abstract": f"We audited {10 + i} answers and found {i} invented "
                         f"references in topic number {i}."}
            for i in range(n)]


WORDS = ("alpha bravo charlie delta echo foxtrot golf hotel india juliet "
         "kilo lima mike november oscar papa quebec romeo sierra tango "
         "uniform victor whiskey xray yankee zulu").split()


def good_rows(recs):
    """Distinct reasons: each quotes its own record and adds its own words."""
    return [[r["id"], "keep", "supports-claim", "-", "-", f"{0.5 + i / 50:.2f}",
             f'abstract: "found {i} invented references"; '
             f'{WORDS[i % 26]} {WORDS[(7 * i + 3) % 26]} {WORDS[(11 * i + 5) % 26]}']
            for i, r in enumerate(recs)]


def write(tmp, recs, rows, fmt="tsv"):
    b = tmp / "batch.jsonl"
    b.write_text("".join(json.dumps(r) + "\n" for r in recs))
    if fmt == "tsv":
        o = tmp / "out.screen.tsv"
        with open(o, "w", newline="") as f:
            w = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONE,
                           quotechar=None, escapechar=None)
            w.writerow(HEADER)
            w.writerows(rows)
    else:
        o = tmp / "out.jsonl"
        o.write_text("".join(json.dumps(dict(zip(HEADER, r))) + "\n"
                             for r in rows))
    return o, b


def run(o, b, *extra):
    p = subprocess.run([sys.executable, "-I", str(SCRIPT), str(o), str(b),
                        "--json", "--exclusions", EXCL, *extra],
                       capture_output=True, text=True)
    rep = json.loads(p.stdout) if p.stdout.strip().startswith("{") else None
    return p.returncode, rep, p.stderr


def checks(rep):
    return sorted({f["check"] for f in rep["failures"]})


def test_clean_tsv_passes(tmp_path):
    recs = batch()
    rc, rep, _ = run(*write(tmp_path, recs, good_rows(recs)))
    assert rc == 0 and rep["ok"] and rep["stats"]["quotes_checked"] == 5


def test_clean_jsonl_with_decision_alias_passes(tmp_path):
    recs = batch()
    rows = good_rows(recs)
    o, b = write(tmp_path, recs, rows, fmt="jsonl")
    o.write_text("".join(json.dumps({"id": r[0], "decision": r[1],
                                     "category": r[2], "confidence": float(r[5]),
                                     "reason": r[6]}) + "\n" for r in rows))
    rc, rep, _ = run(o, b)
    assert rc == 0, rep["failures"]


def test_missing_and_reordered_ids(tmp_path):
    recs = batch()
    rows = good_rows(recs)
    rc, rep, _ = run(*write(tmp_path, recs, rows[:-1]))
    assert rc == 1 and checks(rep) == ["ids"]
    rows[0], rows[1] = rows[1], rows[0]
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 1 and "order" in rep["failures"][0]["message"]


def test_vocabulary_and_consistency(tmp_path):
    recs = batch()
    rows = good_rows(recs)
    rows[0][2] = "supports"                       # unknown category
    rows[1][1] = "discard"                        # discard needs exclusion
    rows[2][1], rows[2][2], rows[2][3] = "keep", "adjacent-subtopic", "-"
    rows[3][1], rows[3][3] = "discard", "not-a-tag"
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    msgs = " ".join(f["message"] for f in rep["failures"])
    assert rc == 1
    for m in ("category not in vocabulary", "discard without an exclusion",
              "keep with a discard category", "exclusion not in vocabulary"):
        assert m in msgs


def test_keep_without_abstract_fails(tmp_path):
    recs = batch()
    recs[0]["abstract"] = ""
    rows = good_rows(recs)
    rows[0][6] = "title suggests an audit of invented references"
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 1
    assert any("without an abstract" in f["message"] for f in rep["failures"])


def test_confidence_range_and_placeholder(tmp_path):
    recs = batch()
    rows = good_rows(recs)
    rows[0][5] = "1.2"
    rows[1][5] = "high"
    rows[2][6] = "TODO"
    rows[3][6] = ""
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 1 and checks(rep) == ["confidence", "reasons"]
    assert sum(f["check"] == "reasons" for f in rep["failures"]) == 2


def test_duplicate_reasons_flagged_unless_titles_identical(tmp_path):
    recs = batch(6)
    rows = good_rows(recs)
    for r in rows[:4]:
        r[6] = "Audit of invented references."
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 1 and checks(rep) == ["duplicates"]
    for r in recs[:4]:                             # four copies of one work
        r["title"] = "One study of reference errors"
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 0, rep["failures"]
    rc, rep, _ = run(*write(tmp_path, recs, rows), "--max-dup", "0")
    assert rc == 1


def test_flat_confidence(tmp_path):
    recs = batch(25)
    rows = good_rows(recs)
    for r in rows[:16]:                            # 64% at 0.7
        r[5] = "0.70"
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 1 and checks(rep) == ["flat-conf"]
    for r in rows[:16]:                            # 64% at 0.95: plainly clear
        r[5] = "0.95"
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 0, rep["failures"]
    rc, rep, _ = run(*write(tmp_path, recs, rows), "--flat-ignore-above", "1.01")
    assert rc == 1 and checks(rep) == ["flat-conf"]


def test_flat_confidence_needs_enough_rows(tmp_path):
    recs = batch(10)
    rows = good_rows(recs)
    for r in rows:
        r[5] = "0.70"
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 0, rep["failures"]


def test_long_run_of_near_identical_reasons(tmp_path):
    recs = batch(8)
    rows = good_rows(recs)
    for i, r in enumerate(rows[:7]):               # differ in one digit only
        r[6] = f"Audit of invented references in chatbot answers, sample {i}"
    rc, rep, _ = run(*write(tmp_path, recs, rows), "--max-dup", "10")
    assert rc == 1 and checks(rep) == ["runs"]
    rows[3][1], rows[3][2], rows[3][3] = "discard", "adjacent-subtopic", "off-question"
    rc, rep, _ = run(*write(tmp_path, recs, rows), "--max-dup", "10")
    assert rc == 0, rep["failures"]


def test_quote_classes(tmp_path):
    recs = batch(4)
    rows = good_rows(recs)
    rows[0][6] = 'abstract: "We  AUDITED 10 answers" -- verbatim, case differs'
    rows[1][6] = 'abstract: "found 3 invented references in topic number 3"'
    rows[2][6] = 'abstract: "invented references were found in topic 2"'
    rows[3][6] = 'abstract: "the model never cites anything at all"'
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    kinds = sorted(f["message"].split(":")[0] for f in rep["failures"])
    assert rc == 1 and kinds == ["mixup", "paraphrase", "unsupported"]


def test_quote_normalisation_dashes_ellipses_short(tmp_path):
    recs = batch(2)
    recs[0]["abstract"] = ("A radical non- UNIX design – measured on "
                           "twelve systems, with results.")
    rows = good_rows(recs)
    rows[0][6] = ('abstract: “a radical non-UNIX design - measured” '
                  'and "measured on ... twelve systems" plus "two words"')
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 0, rep["failures"]


def test_apostrophes_are_not_quotes(tmp_path):
    recs = batch(2)
    rows = good_rows(recs)
    rows[0][6] = "the authors' audit and the model's errors are measured here"
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 0, rep["failures"]


def test_headerless_tsv_with_columns(tmp_path):
    recs = batch()
    o, b = write(tmp_path, recs, good_rows(recs))
    o.write_text("".join(o.read_text().splitlines(True)[1:]))
    rc, _, err = run(o, b)
    assert rc == 2 and "no column" in err
    rc, rep, _ = run(o, b, "--columns", ",".join(HEADER))
    assert rc == 0, rep["failures"]


def test_usage_errors_exit_2(tmp_path):
    recs = batch()
    o, b = write(tmp_path, recs, good_rows(recs))
    assert run(tmp_path / "nope.tsv", b)[0] == 2
    (tmp_path / "nt.jsonl").write_text('{"id": "a", "abstract": ""}\n')
    rc, _, err = run(o, tmp_path / "nt.jsonl")
    assert rc == 2 and "title" in err
    p = subprocess.run([sys.executable, "-I", str(SCRIPT)], capture_output=True)
    assert p.returncode == 2


def test_human_summary(tmp_path):
    recs = batch()
    o, b = write(tmp_path, recs, good_rows(recs))
    p = subprocess.run([sys.executable, "-I", str(SCRIPT), str(o), str(b),
                        "--exclusions", EXCL], capture_output=True, text=True)
    assert p.returncode == 0 and "OK" in p.stdout.splitlines()[0]


# ---- added after the independent review: bugs and surviving mutants ----

def messages(rep):
    return " | ".join(f"{f['check']}: {f['message']}" for f in rep["failures"])


def test_reason_starting_with_quote_is_still_checked(tmp_path):
    recs = batch(3)
    rows = good_rows(recs)
    rows[0][6] = '"the model never cites anything" says the abstract'
    rows[1][6] = '"found 2 invented references" is the finding'   # row x2's
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 1 and rep["stats"]["quotes_checked"] == 3
    assert "unsupported" in messages(rep) and "mixup" in messages(rep)


def test_csv_quoted_sheet_needs_flag(tmp_path):
    recs = batch(3)
    o, b = write(tmp_path, recs, good_rows(recs))
    with open(o, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(HEADER)
        w.writerows(good_rows(recs))
    assert run(o, b)[0] == 1                      # doubled quotes break quotes
    rc, rep, _ = run(o, b, "--csv-quoting")
    assert rc == 0, rep["failures"]


def test_non_object_and_broken_lines(tmp_path):
    recs = batch(3)
    o, b = write(tmp_path, recs, good_rows(recs), fmt="jsonl")
    good = o.read_text()
    o.write_text(good + "[1, 2]\n")
    rc, _, err = run(o, b)
    assert rc == 2 and "not a JSON object" in err
    o.write_text(good)
    b.write_text(b.read_text() + "{broken\n")
    rc, _, err = run(o, b)
    assert rc == 2 and "unreadable record" in err


def test_byte_order_mark_is_accepted(tmp_path):
    recs = batch(3)
    o, b = write(tmp_path, recs, good_rows(recs))
    o.write_text("﻿" + o.read_text(), encoding="utf-8")
    rc, rep, _ = run(o, b)
    assert rc == 0, rep["failures"]


def test_extra_and_duplicated_ids(tmp_path):
    recs = batch(3)
    rows = good_rows(recs)
    extra = rows + [["doi:10.1/zz", *rows[0][1:6], "a reason of its own here"]]
    rc, rep, _ = run(*write(tmp_path, recs, extra))
    assert rc == 1 and "not in the batch" in messages(rep)
    rc, rep, _ = run(*write(tmp_path, recs, rows + [rows[1]]))
    assert rc == 1 and "more than once" in messages(rep)


def test_each_column_rule_alone(tmp_path):
    cases = [
        (lambda r: r.__setitem__(1, "maybe"), "verdict not keep/discard"),
        (lambda r: r.__setitem__(3, "off-question"), "keep with an exclusion"),
        (lambda r: r.__setitem__(4, "no-such-theme"), "theme not in vocabulary"),
        (lambda r: (r.__setitem__(1, "discard"), r.__setitem__(2, "adjacent-subtopic"),
                    r.__setitem__(3, "off-question"), r.__setitem__(4, "t1")),
         "discard with a theme"),
    ]
    for change, msg in cases:
        recs = batch(3)
        rows = good_rows(recs)
        change(rows[0])
        rc, rep, _ = run(*write(tmp_path, recs, rows), "--themes", "t1,t2")
        assert rc == 1 and msg in messages(rep), (msg, messages(rep))


def test_discard_with_keep_category_without_exclusion_column(tmp_path):
    recs = batch(3)
    o, b = write(tmp_path, recs, good_rows(recs), fmt="jsonl")
    lines = [json.loads(x) for x in o.read_text().splitlines()]
    for x in lines:
        del x["exclusion"], x["theme"]
    lines[0]["verdict"] = "discard"
    o.write_text("".join(json.dumps(x) + "\n" for x in lines))
    rc, rep, _ = run(o, b)
    assert rc == 1 and "discard with a keep category" in messages(rep)
    lines[0]["no_abstract"] = True
    o.write_text("".join(json.dumps(x) + "\n" for x in lines))
    rc, rep, _ = run(o, b)
    assert rc == 0, rep["failures"]


def test_wrong_field_count(tmp_path):
    recs = batch(3)
    rows = good_rows(recs)
    rows[1] = rows[1][:6]
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 1 and "wrong field count" in messages(rep)


def test_vocabulary_from_flags_and_config(tmp_path):
    recs = batch(3)
    rows = good_rows(recs)
    rows[0][2] = "qualifies-claim"
    o, b = write(tmp_path, recs, rows)
    rc, rep, _ = run(o, b, "--keep-categories", "supports-claim")
    assert rc == 1 and "keep with a discard category" in messages(rep)
    cfg = tmp_path / "v.json"
    cfg.write_text(json.dumps({"categories": ["supports-claim", "other"],
                               "keep-categories": ["supports-claim"]}))
    rc, rep, _ = run(o, b, "--config", str(cfg))
    assert rc == 1 and "category not in vocabulary" in messages(rep)
    cfg.write_text(json.dumps({"bogus": []}))
    assert run(o, b, "--config", str(cfg))[0] == 2


def test_confidence_cases_alone(tmp_path):
    for bad in ("1.2", "-0.1", "nan", "high"):
        recs = batch(3)
        rows = good_rows(recs)
        rows[0][5] = bad
        rc, rep, _ = run(*write(tmp_path, recs, rows))
        assert rc == 1 and checks(rep) == ["confidence"], bad
    recs = batch(3)
    rows = good_rows(recs)
    rows[0][5], rows[1][5] = "0", "1"
    assert run(*write(tmp_path, recs, rows))[0] == 0


def test_reason_rules_alone(tmp_path):
    for reason in ("same as above", "Poems.", "TBD", "<one sentence>"):
        recs = batch(3)
        rows = good_rows(recs)
        rows[0][6] = reason
        rc, rep, _ = run(*write(tmp_path, recs, rows))
        assert rc == 1 and checks(rep) == ["reasons"], reason
    recs = batch(3)
    o, b = write(tmp_path, recs, good_rows(recs), fmt="jsonl")
    lines = [json.loads(x) for x in o.read_text().splitlines()]
    lines[0]["reason"] = "first line\nsecond line of the reason"
    o.write_text("".join(json.dumps(x) + "\n" for x in lines))
    rc, rep, _ = run(o, b)
    assert rc == 1 and "tab or newline" in messages(rep)


def test_duplicate_boundary_and_normalisation(tmp_path):
    recs = batch(6)
    rows = good_rows(recs)
    for r, text in zip(rows[:3], ("Audit of errors.", "audit  of ERRORS",
                                  "Audit of errors;")):
        r[6] = text
    rc, rep, _ = run(*write(tmp_path, recs, rows))   # 3 rows: allowed
    assert rc == 0, rep["failures"]
    rows[3][6] = "AUDIT of errors"                    # 4 rows: flagged
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 1 and "4 rows" in messages(rep)


def test_flat_boundaries(tmp_path):
    recs = batch(20)
    rows = good_rows(recs)
    for r in rows[:12]:                               # exactly 60%: allowed
        r[5] = "0.70"
    assert run(*write(tmp_path, recs, rows))[0] == 0
    rows[12][5] = "0.70"                              # 65%: flagged
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 1 and checks(rep) == ["flat-conf"]
    rc, rep, _ = run(*write(tmp_path, recs[:19], rows[:19]))
    assert rc == 0, rep["failures"]                   # 19 rows: not checked
    for r in rows[:13]:                               # 0.90 is ignored
        r[5] = "0.90"
    assert run(*write(tmp_path, recs, rows))[0] == 0


def test_run_boundary_and_category_break(tmp_path):
    def rows_with_run(n):
        recs = batch(8)
        rows = good_rows(recs)
        for i, r in enumerate(rows[:n]):
            r[6] = f"Audit of invented references in chatbot answers, sample {i}"
        return recs, rows
    recs, rows = rows_with_run(5)
    assert run(*write(tmp_path, recs, rows), "--max-dup", "10")[0] == 0
    recs, rows = rows_with_run(6)
    rc, rep, _ = run(*write(tmp_path, recs, rows), "--max-dup", "10")
    assert rc == 1 and checks(rep) == ["runs"]
    rows[2][2] = "qualifies-claim"                    # same verdict, new category
    assert run(*write(tmp_path, recs, rows), "--max-dup", "10")[0] == 0


def test_other_quote_marks_and_markup(tmp_path):
    recs = batch(3)
    recs[0]["abstract"] = ("<p>We <i>audited</i> ten answers ‘by hand’ for the "
                           "“phantom citation” problem.</p>")
    rows = good_rows(recs)
    rows[0][6] = ("abstract: “we audited ten answers” and "
                  "‘we audited ten answers 'by hand' for the "
                  '"phantom citation" problem’')
    rows[1][6] = "abstract says ‘the model never cites anything’"
    rows[2][6] = "abstract says 'the model never cites anything' at all"
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rep["stats"]["quotes_checked"] == 4
    assert rc == 1 and [f["ids"][0] for f in rep["failures"]] == \
        [recs[1]["id"], recs[2]["id"]]


def test_paraphrase_threshold_and_short_quotes(tmp_path):
    recs = batch(2)
    rows = good_rows(recs)
    rows[0][6] = 'abstract: "audited answers and found invented things"'  # 5/6 own
    rows[1][6] = 'abstract: "wholly made up" and "three words here"'
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    kinds = [f["message"].split(":")[0] for f in rep["failures"]]
    assert kinds == ["paraphrase", "unsupported", "unsupported"]
    # at the 75% threshold: 3 of 4 words own -> paraphrase; 2 of 7 -> unsupported
    rows[0][6] = 'abstract: "audited answers found zebras"'
    rows[1][6] = 'abstract: "audited answers in the moon garden today"'
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    kinds = [f["message"].split(":")[0] for f in rep["failures"]]
    assert kinds == ["paraphrase", "unsupported"]
    rows[1][6] = 'abstract: "made up" twice "made up"'                 # 2 words
    rows[0][6] = "no quotes here at all, just words"
    assert run(*write(tmp_path, recs, rows))[0] == 0


def test_unparsable_output_line_is_reported(tmp_path):
    recs = batch(3)
    o, b = write(tmp_path, recs, good_rows(recs), fmt="jsonl")
    o.write_text(o.read_text() + '{"id": "doi:10.1/x9", broken\n')
    rc, rep, _ = run(o, b)
    assert rc == 1 and "unparsable JSON" in messages(rep)


def test_byte_order_mark_on_json_lines(tmp_path):
    recs = batch(3)
    o, b = write(tmp_path, recs, good_rows(recs))
    b.write_text("﻿" + b.read_text(), encoding="utf-8")
    rc, rep, _ = run(o, b)
    assert rc == 0, rep["failures"]


# ---- templated reasons (scholar #291's documented limit) ----

def test_reasons_templated_with_own_title_are_duplicates(tmp_path):
    """Book batch b193: 'Unrelated ...; subject is <title, cut>' on most rows."""
    recs = batch(6)
    topics = ["Voice foundation models for real-time autonomous interaction",
              "Electricity price forecasting with a comprehensive framework",
              "Structural health monitoring of historic masonry minarets",
              "Credit risk assessment using interpretable machine learning",
              "Point cloud quality assessment benchmark for diagnostics",
              "Tamil conversational agent for a closed domain"]
    for r, t in zip(recs, topics):
        r["title"] = t
    rows = good_rows(recs)
    for r, rec in zip(rows[:4], recs):
        r[6] = f"Unrelated to the question; subject is {rec['title']}."
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 1 and checks(rep) == ["duplicates"]
    assert "<title>" in messages(rep)
    for r, rec in zip(rows[:4], recs):            # 6 of 7-8 words, cut mid-word
        cut = " ".join(rec["title"].split()[:6]) + " ab"
        r[6] = f"Unrelated to the question; subject is {cut}"
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 1 and checks(rep) == ["duplicates"]


def test_reasons_templated_with_own_id_are_duplicates(tmp_path):
    recs = batch(6)
    rows = good_rows(recs)
    for r in rows[:4]:
        r[6] = f"Record {r[0]} is off the question."
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 1 and checks(rep) == ["duplicates"] and "<id>" in messages(rep)


def test_templating_spares_honest_reasons(tmp_path):
    recs = batch(6)
    rows = good_rows(recs)
    for r, rec in zip(rows, recs):                # title quoted, own words added
        r[6] = (f"{rec['title']}: {WORDS[int(r[0][-1])]} audit of "
                f"{WORDS[int(r[0][-1]) + 9]} answers")
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 0, rep["failures"]


def test_run_check_sees_templated_reasons(tmp_path):
    recs = batch(8)
    for i, r in enumerate(recs):
        r["title"] = f"{WORDS[i]} {WORDS[i + 8]} {WORDS[i + 16]} benchmark study"
    rows = good_rows(recs)
    for r, rec in zip(rows[:6], recs):
        r[6] = f"Unrelated to the question; subject is {rec['title']}"
    rc, rep, _ = run(*write(tmp_path, recs, rows), "--max-dup", "10")
    assert rc == 1 and checks(rep) == ["runs"]


# ---- --scholar: scholar sessions decide --dry-run (scholar >= e7dc5f5) ----
# The installed scholar predates the dry run, so these tests put a stub
# `scholar` first on PATH (testing ladder rung 4: the real command is not
# available).  The stub logs its arguments and the reasons files it gets.
# PATH holds only the stub's directory, so no test can reach a real
# scholar, even when the stub cannot run.

STUB = r'''#!PYTHON
import os, sys
log = os.environ["STUB_LOG"]
args = sys.argv[1:]
if "--help" in args:
    print("Usage: scholar sessions decide ..." +
          ("  --dry-run  Run every check" if os.environ.get("STUB_NEW") else ""))
    sys.exit(0)
with open(log, "a") as f:
    f.write(" ".join(args) + "\n")
    rf = args[args.index("--reasons-file") + 1]
    f.write(open(rf).read())
sys.exit(int(os.environ.get("STUB_EXIT", "0")))
'''


def stub_text(script=None):
    return (script or STUB).replace("PYTHON", sys.executable, 1)


def stub_env(tmp_path, new=True, exit_code=0):
    import os
    d = tmp_path / "bin"
    d.mkdir(exist_ok=True)
    s = d / "scholar"
    s.write_text(stub_text())
    s.chmod(0o755)
    env = dict(os.environ, PATH=str(d),
               STUB_LOG=str(tmp_path / "stub.log"), STUB_EXIT=str(exit_code))
    if new:
        env["STUB_NEW"] = "1"
    return env


def run_env(o, b, env, *extra):
    p = subprocess.run([sys.executable, "-I", str(SCRIPT), str(o), str(b),
                        "--json", "--exclusions", EXCL, *extra],
                       capture_output=True, text=True, env=env)
    rep = json.loads(p.stdout) if p.stdout.strip().startswith("{") else None
    return p.returncode, rep, p.stderr


def mixed_rows(recs):
    rows = good_rows(recs)
    rows[1][1:5] = ["discard", "off-topic-false-hit", "off-question", "-"]
    rows[2][1:5] = ["discard", "off-topic-false-hit", "off-question", "-"]
    rows[3][4] = "t1"
    return rows


def test_scholar_dry_run_groups_by_verdict_and_tags(tmp_path):
    recs = batch(4)
    env = stub_env(tmp_path)
    o, b = write(tmp_path, recs, mixed_rows(recs))
    rc, rep, err = run_env(o, b, env, "--scholar", "my-session", "--by", "scr-1")
    assert rc == 0, (err, rep)
    log = (tmp_path / "stub.log").read_text()
    calls = [l for l in log.splitlines() if l.startswith("sessions decide")]
    assert len(calls) == 3                       # keep, keep+t1, discard group
    for c in calls:
        for a in ("my-session", "--source agent", "--dry-run", "--strict",
                  "--by scr-1", "--reasons-file"):
            assert a in c
    disc = next(c for c in calls if "--discard" in c)
    assert "-t off-topic-false-hit" in disc and "-t off-question" in disc
    assert f"{recs[1]['id']}\t" in log and "\t0.52\n" in log
    assert [g["exit"] for g in rep["scholar"]["groups"]] == [0, 0, 0]


def test_scholar_refusal_fails_the_batch(tmp_path):
    recs = batch(4)
    o, b = write(tmp_path, recs, mixed_rows(recs))
    rc, rep, _ = run_env(o, b, stub_env(tmp_path, exit_code=2),
                         "--scholar", "my-session")
    assert rc == 1 and "scholar" in checks(rep)


def test_scholar_too_old_is_a_usage_error(tmp_path):
    recs = batch(4)
    o, b = write(tmp_path, recs, mixed_rows(recs))
    rc, _, err = run_env(o, b, stub_env(tmp_path, new=False),
                         "--scholar", "my-session")
    assert rc == 2 and "requires scholar" in err and "e7dc5f5" in err
    assert not (tmp_path / "stub.log").exists()


def test_session_prefixed_ids_templated_without_prefix(tmp_path):
    """Book batches use `session|paper-id`; a reason names the paper id."""
    recs = batch(6)
    for r in recs:
        r["id"] = "book-s1|" + r["id"]
    rows = good_rows(recs)
    for r in rows[:4]:
        r[6] = f"Record {r[0].split('|')[1]} is off the question."
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 1 and checks(rep) == ["duplicates"] and "<id>" in messages(rep)


# ---- round 2 review: honest subject-naming reasons, boundaries, --scholar ----

def test_reason_naming_its_subject_in_the_titles_words_is_honest(tmp_path):
    """'About <the title's opening words>, not <field>' names the subject in
    the screener's own words; only a long cut (40+ characters, or 60% of
    the title) counts as a templated title."""
    recs = batch(6)
    subjects = ["Blockchain consensus protocols", "Soil moisture sensing",
                "Coral reef bleaching", "Railway timetable optimisation",
                "Medieval manuscript dating", "Wind turbine blade icing"]
    for r, t in zip(recs, subjects):
        r["title"] = f"{t}: a survey of methods, datasets and open problems in the field"
    rows = good_rows(recs)
    for r, t in zip(rows[:5], subjects):
        r[6] = f"About {t.lower()}, not programming education."
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 0, rep["failures"]


def test_title_word_share_boundary(tmp_path):
    """A title counts as copied when the reason holds 75% of its words in
    one run: 6 of 8 words is the title, 5 of 8 is the screener's own."""
    def cut_rows(n):
        recs = batch(6)
        for i, r in enumerate(recs):
            r["title"] = " ".join(WORDS[(i + 3 * j) % 26] for j in range(8))
        rows = good_rows(recs)
        for r, rec in zip(rows[:4], recs):
            kept = " ".join(rec["title"].split()[:n])
            r[6] = f"Unrelated to the question; subject is {kept}"
        return recs, rows
    recs, rows = cut_rows(6)
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 1 and "<title>" in messages(rep)
    recs, rows = cut_rows(5)
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 0, rep["failures"]


def test_ten_rows_title_then_not_relevant(tmp_path):
    recs = batch(12)
    for i, r in enumerate(recs):
        r["title"] = f"{WORDS[i]} {WORDS[i + 12]} in practice"
    rows = good_rows(recs)
    for r, rec in zip(rows[:10], recs):
        r[6] = f"{rec['title']} \u2014 not relevant"
    rc, rep, _ = run(*write(tmp_path, recs, rows), "--max-run", "50")
    assert rc == 1 and checks(rep) == ["duplicates"]
    assert "10 rows" in messages(rep)


def test_b193_shape_cut_at_a_fixed_reason_length(tmp_path):
    """b193 cut each reason at a fixed length, keeping 30-100% of the
    title's words; the rows that keep 75% or more still share a reason."""
    recs = batch(10)
    lengths = [3, 4, 5, 6, 8, 10, 12, 14, 16, 20]       # words per title
    for r, n in zip(recs, lengths):
        r["title"] = " ".join(WORDS[(int(r["id"][-1]) * 5 + j) % 26] + "x"
                              for j in range(n))
    rows = good_rows(recs)
    stem = "Unrelated to LLM references or citations; subject is "
    for r, rec in zip(rows, recs):
        r[6] = (stem + rec["title"])[:110]
    rc, rep, _ = run(*write(tmp_path, recs, rows), "--max-run", "50")
    assert rc == 1 and checks(rep) == ["duplicates"]


def test_reviewer_fp1_about_subject_not_field(tmp_path):
    # the reviewer's sheet, with titles shortened to five words so that the
    # three-word subject is 60% of each title's words (75% of its letters)
    titles = ["Blockchain consensus protocols for IoT",
              "Deep reinforcement learning for grasping",
              "Electricity price forecasting with boosting",
              "Structural health monitoring of towers",
              "Credit risk scoring with models"]
    recs = batch(5)
    for r, t in zip(recs, titles):
        r["title"] = t
    rows = good_rows(recs)
    for r, t in zip(rows, titles):
        r[1:4] = ["discard", "off-topic-false-hit", "off-question"]
        r[6] = f"About {' '.join(t.split()[:3]).lower()}, not programming education."
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 0, rep["failures"]


def test_reviewer_fp2_topic_word_opens_the_title(tmp_path):
    topics = [("loops", "Python: an interview study"),
              ("variables", "Java: a survey"),
              ("recursion", "Scheme: a think-aloud study"),
              ("references", "C: an exam analysis")]
    recs = batch(4)
    for r, (w, rest) in zip(recs, topics):
        r["title"] = f"Novice misconceptions about {w} in {rest}"
    rows = good_rows(recs)
    for r, (w, _) in zip(rows, topics):
        r[6] = (f"Novice misconceptions about {w}: an empirical study of "
                "exactly the claimed misconception.")
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 0, rep["failures"]


def test_non_latin_titles_are_templated_too(tmp_path):
    recs = batch(6)
    for i, r in enumerate(recs):
        r["title"] = f"\u0410\u0432\u0442\u043e{i} \u043a\u0430\u043a \u0442\u0438\u043f {i}"
    rows = good_rows(recs)
    for r, rec in zip(rows[:4], recs):
        r[6] = f"Unrelated; subject is {rec['title']}"
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 1 and "<title>" in messages(rep)


def test_scholar_timeout_is_a_failure(tmp_path):
    recs = batch(4)
    o, b = write(tmp_path, recs, mixed_rows(recs))
    env = stub_env(tmp_path)
    s = tmp_path / "bin" / "scholar"
    s.write_text(stub_text(STUB.replace(
        'with open(log, "a") as f:', 'import time; time.sleep(5)\nwith open(log, "a") as f:', 1)))
    rc, rep, _ = run_env(o, b, env, "--scholar", "my-session",
                         "--scholar-timeout", "1")
    assert rc == 1
    assert all(g["exit"] == -1 for g in rep["scholar"]["groups"])
    assert "timed out" in rep["scholar"]["groups"][0]["stderr"]


def test_reason_naming_the_bare_doi(tmp_path):
    recs = batch(6)
    rows = good_rows(recs)
    for r in rows[:4]:
        r[6] = f"Record {r[0][4:]} is off the question."     # without doi:
    rc, rep, _ = run(*write(tmp_path, recs, rows))
    assert rc == 1 and "<id>" in messages(rep)


def test_scholar_reasons_file_content_and_prefixed_ids(tmp_path):
    recs = batch(4)
    recs[0]["id"] = "book-s1|" + recs[0]["id"]
    recs[1]["id"] = "book-s2|" + recs[1]["id"]
    rows = mixed_rows(recs)
    o, b = write(tmp_path, recs, rows, fmt="jsonl")
    lines = [json.loads(x) for x in o.read_text().splitlines()]
    lines[0]["reason"] = 'abstract: "found 0 invented references";\tsecond part'
    o.write_text("".join(json.dumps(x) + "\n" for x in lines))
    rc, rep, err = run_env(o, b, stub_env(tmp_path), "--scholar", "other")
    log = (tmp_path / "stub.log").read_text()
    calls = [l for l in log.splitlines() if l.startswith("sessions decide")]
    # one call per session and group: book-s1 keep, book-s2 discard,
    # 'other' discard (row 2) and 'other' keep+t1 (row 3)
    assert sorted(c.split()[2] for c in calls) == ["book-s1", "book-s2",
                                                   "other", "other"]
    assert (f"{recs[0]['id'].split('|')[1]}\tabstract: \"found 0 invented "
            f"references\"; second part\t0.50\n") in log
    assert "book-s1|" not in log.replace("sessions decide book-s1", "")
    assert rc == 1                                # the tab is still a failure
    assert "tab or newline" in messages(rep)


def test_scholar_failure_names_the_group_rows(tmp_path):
    recs = batch(4)
    o, b = write(tmp_path, recs, mixed_rows(recs))
    rc, rep, _ = run_env(o, b, stub_env(tmp_path, exit_code=2),
                         "--scholar", "my-session")
    ids = sorted(i for f in rep["failures"] if f["check"] == "scholar"
                 for i in f["ids"])
    assert ids == sorted(r["id"] for r in recs)


def test_scholar_missing_from_path(tmp_path):
    recs = batch(4)
    o, b = write(tmp_path, recs, mixed_rows(recs))
    env = stub_env(tmp_path)
    env["PATH"] = str(tmp_path / "empty")
    rc, _, err = run_env(o, b, env, "--scholar", "my-session")
    assert rc == 2 and "requires scholar" in err


def test_scholar_call_that_cannot_start_is_a_failure(tmp_path):
    """The stub answers --help, then makes itself non-executable, so the
    decide call itself fails to start (OSError)."""
    recs = batch(4)
    o, b = write(tmp_path, recs, mixed_rows(recs))
    env = stub_env(tmp_path)
    s = tmp_path / "bin" / "scholar"
    s.write_text(stub_text(STUB.replace(
        '    sys.exit(0)\n', '    os.chmod(sys.argv[0], 0o644)\n    sys.exit(0)\n', 1)))
    rc, rep, _ = run_env(o, b, env, "--scholar", "my-session")
    assert rc == 1
    assert all(g["exit"] == -1 for g in rep["scholar"]["groups"])
