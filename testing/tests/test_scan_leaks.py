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
    secrets = ["anna.svensson@uni.example.se", "20990315-1018",
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
        "uri: https://lms.example/users?search_term=anna.svensson%40uni.example.se\n")
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


def test_known_fictive_personnummer_pass(tmp_path):
    # Tolvan Tolvansson, Skatteverket's test identity, in its usual forms.
    (tmp_path / "c.py").write_text('PNR = "19121212-1212"\nOTHER = "121212-1212"\n')
    assert scan(tmp_path, "--originals", tmp_path / "x").returncode == 0


def test_allow_file_takes_exact_values_and_regexes(tmp_path):
    (tmp_path / "c.py").write_text('MAIL = "user@domain.se"\nPNR = "20990315-1018"\n')
    assert scan(tmp_path, "--originals", tmp_path / "x").returncode == 1
    allow = tmp_path / "allow.txt"
    allow.write_text("# fixtures\nuser@domain.se\nre:2099\\d{4}-?\\d{4}\n")
    result = scan(tmp_path / "c.py", "--originals", tmp_path / "x", "--allow", allow)
    assert result.returncode == 0, result.stdout


def test_saml_response_is_a_leak(tmp_path):
    blob = "PHNhbWxwOlJlc3BvbnNlIHhtbG5zOnNhbWxwPSJ1cm46b2FzaXM" * 3
    (tmp_path / "c.yaml").write_text(f"body: SAMLResponse={blob}\n")
    out = scan(tmp_path, "--originals", tmp_path / "x").stdout
    assert "saml-response" in out and blob not in out


def test_default_paths_cover_tracked_literate_sources(tmp_path):
    # In a literate project tests/ is generated; the .nw files are the truth.
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "mod.nw").write_text("<<test>>=\nassert f('20990315-1018')\n@\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", "src/mod.nw"], check=True)
    result = subprocess.run([sys.executable, str(SCRIPT), "--originals", "none"],
                            capture_output=True, text=True, cwd=tmp_path)
    assert result.returncode == 1 and "mod.nw" in result.stdout


def test_dash_scans_standard_input(tmp_path):
    # pdftotext doc.pdf - | scan_leaks.py -
    result = subprocess.run([sys.executable, str(SCRIPT), "-", "--originals", tmp_path / "x"],
                            input="Kontakt: anna.svensson@uni.example.se\n",
                            capture_output=True, text=True)
    assert result.returncode == 1 and "<stdin>:1: email" in result.stdout, result.stdout


def test_email_hits_show_the_domain_but_not_the_person(tmp_path):
    (tmp_path / "c.py").write_text('STAFF = "anna.svensson@uni.example.se"\n')
    out = scan(tmp_path, "--originals", tmp_path / "x").stdout
    assert "@uni.example.se" in out and "anna.svensson" not in out


def test_no_originals_warning_unless_one_was_asked_for(tmp_path):
    (tmp_path / "c.py").write_text("x = 1\n")
    env = {k: v for k, v in __import__("os").environ.items() if k != "TEST_ORIGINALS_FILE"}
    result = subprocess.run([sys.executable, str(SCRIPT), "c.py"], capture_output=True,
                            text=True, cwd=tmp_path, env=env)
    assert result.returncode == 0 and "originals" not in result.stderr


def test_secret_assigned_from_a_call_is_not_a_leak(tmp_path):
    (tmp_path / "c.py").write_text(
        "password = keyring.get_password('svc', user)\n"
        "token = os.environ.get_api_token_value()\n")
    result = scan(tmp_path, "--originals", tmp_path / "none.txt")
    assert result.returncode == 0, result.stdout


def test_key_census_counts_values_without_printing_them(tmp_path):
    (tmp_path / "out.stdout").write_text(
        "{'Anteckning': 'Granted after review by the board', 'Alias': 'Person-ab'}\n"
        '{"Anteckning": "Second free-text note", "Alias": "Person-ab"}\n'
        "{'Anteckning': \"It's a third note\", 'Alias': 'Person-ab'}\n")
    result = scan(tmp_path, "--originals", tmp_path / "none.txt", "--key-census")
    lines = result.stdout.splitlines()
    assert any(l.split()[:2] == ["Anteckning", "distinct=3"] for l in lines), lines
    assert any(l.split()[:2] == ["Alias", "distinct=1"] for l in lines), lines
    assert lines.index(next(l for l in lines if l.startswith("Anteckning"))) < \
        lines.index(next(l for l in lines if l.startswith("Alias")))
    for value in ("Granted", "Second", "third", "Person-ab"):
        assert value not in result.stdout
