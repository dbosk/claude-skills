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
