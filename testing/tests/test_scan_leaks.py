"""scan_leaks.py finds secrets and personal data without repeating them."""

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "scan_leaks.py"


def scan(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                          capture_output=True, text=True)


def test_clean_data_passes(tmp_path):
    (tmp_path / "c.yaml").write_text(
        "name: Person-3f9a1c\nemail: person-3f9a1c@example.invalid\n"
        "created: 1700000000\n")
    result = scan(tmp_path, "--originals", tmp_path / "none.txt")
    assert result.returncode == 0, result.stdout


def test_planted_leaks_fail_and_are_not_echoed(tmp_path):
    secrets = ["anna.svensson@kth.se", "19900101-0017",
               "Bearer abcdefghijklmnop1234",
               "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.c2lnbmF0dXJlLXZhbHVl"]
    (tmp_path / "c.yaml").write_text("\n".join(f"v: {s}" for s in secrets))
    result = scan(tmp_path, "--originals", tmp_path / "none.txt")
    assert result.returncode == 1
    for kind in ("email", "personnummer", "bearer-token", "jwt"):
        assert kind in result.stdout
    for s in secrets:
        assert s not in result.stdout


def test_originals_and_denylist_catch_names(tmp_path):
    (tmp_path / "c.yaml").write_text("note: graded by svensson today\n")
    originals = tmp_path / "originals.txt"
    originals.write_text("Anna Svensson\nSvensson\n")
    assert scan(tmp_path / "c.yaml", "--originals", originals).returncode == 1
    deny = tmp_path / "deny.txt"
    deny.write_text("# roster\nsvensson\n")
    assert scan(tmp_path / "c.yaml", "--originals", tmp_path / "x", "--denylist", deny).returncode == 1


def test_name_heuristic_only_warns(tmp_path):
    (tmp_path / "c.yaml").write_text("title: Erik Lindqvist\n")
    result = scan(tmp_path, "--originals", tmp_path / "x", "--warn-names")
    assert result.returncode == 0 and "warning: name-like" in result.stdout


def test_token_assignments_and_encoded_emails_are_found(tmp_path):
    (tmp_path / "c.yaml").write_text(
        "body: access_token=AbCdEfGhIjKlMnOpQrSt12\n"
        "uri: https://lms.example/users?search_term=anna.svensson%40kth.se\n")
    out = scan(tmp_path, "--originals", tmp_path / "none.txt").stdout
    assert "assigned-secret" in out and "email" in out


def test_missing_originals_file_is_reported(tmp_path):
    (tmp_path / "c.yaml").write_text("x: 1\n")
    result = scan(tmp_path, "--originals", tmp_path / "gone.txt")
    assert "originals file not found" in result.stdout + result.stderr


def test_folded_yaml_is_scanned_unfolded(tmp_path):
    # vcrpy's YAML dumper folds long strings; a name can straddle the fold.
    (tmp_path / "c.yaml").write_text(
        "interactions:\n- request: {uri: 'https://x.example/'}\n"
        "  response:\n    body:\n      string: 'graded by Anna\n        Svensson today'\n")
    originals = tmp_path / "o.txt"
    originals.write_text("Anna Svensson\n")
    assert scan(tmp_path / "c.yaml", "--originals", originals).returncode == 1


def test_originals_inside_url_hosts_are_not_hits():
    import vcr_support
    hits = list(vcr_support.scan_text("uri: https://canvas.kth.se/api/v1/users\n", ["KTH"]))
    assert hits == []
    assert list(vcr_support.scan_text("teacher: KTH Support\n", ["KTH"]))
