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


def test_many_originals_scan_quickly(tmp_path):
    # Real recordings append thousands of originals; the scan must stay
    # linear in the data, not rebuild a huge alternation per string.
    import time
    sys.path.insert(0, str(SCRIPT.parent.parent / "assets"))
    import vcr_support
    originals = [f"Person{i:05d} Efternamn{i:05d}" for i in range(4000)]
    originals += [f"Efternamn{i:05d}" for i in range(4000)]
    body = " ".join(f"word{i} Ankeborg" for i in range(200))
    interactions = "".join(
        f"- request:\n    body: null\n    headers: {{}}\n    method: GET\n"
        f"    uri: https://lms.example/api/{i}\n"
        f"  response:\n    body:\n      string: '{body}'\n    headers:\n"
        f"      Content-Type:\n      - application/json\n    status:\n      code: 200\n"
        for i in range(300))
    cassette = tmp_path / "c.yaml"
    cassette.write_text("interactions:\n" + interactions + "version: 1\n")
    start = time.monotonic()
    hits = list(vcr_support.scan_file(cassette, originals + ["word7"]))
    assert time.monotonic() - start < 10
    assert {kind for _, kind, _ in hits} == {"original"}


def test_originals_match_whole_words_longest_first():
    sys.path.insert(0, str(SCRIPT.parent.parent / "assets"))
    import vcr_support
    originals = ["Anna", "Anna Svensson"]
    assert not list(vcr_support.scan_text("Annalena and anna_b went home", originals))
    assert not list(vcr_support.scan_text("Anna Svenssonberg", ["Anna Svensson"]))
    hits = list(vcr_support.scan_text("graded by ANNA SVENSSON today", originals))
    assert [kind for _, kind, _ in hits] == ["original"]


def test_the_default_originals_file_is_announced(tmp_path):
    # After a recording, a scan of the sources silently matching its
    # originals (author names, common words) is confusing: say so.
    import os
    run_dir = tmp_path / "run"
    run_dir.mkdir(mode=0o700)
    project = tmp_path / "proj"
    (project / "tests").mkdir(parents=True)
    (project / "tests" / "data.yaml").write_text("x: 1\n")
    env = {k: v for k, v in os.environ.items() if k != "TEST_ORIGINALS_FILE"}
    env["XDG_RUNTIME_DIR"] = str(run_dir)
    sys.path.insert(0, str(SCRIPT.parent.parent / "assets"))
    import vcr_support
    old = os.environ.get("XDG_RUNTIME_DIR")
    os.environ["XDG_RUNTIME_DIR"] = str(run_dir)
    try:
        default = vcr_support.default_originals_path(project)
    finally:
        os.environ.pop("XDG_RUNTIME_DIR") if old is None else os.environ.update(XDG_RUNTIME_DIR=old)
    default.write_text("Svensson\n")
    result = subprocess.run([sys.executable, str(SCRIPT)], cwd=project, env=env,
                            capture_output=True, text=True)
    assert str(default) in result.stderr and "--originals /dev/null" in result.stderr


def test_capability_urls_are_leaks(tmp_path):
    # Anyone holding such a link can read the calendar or schedule: a secret,
    # even though it looks like configuration.  (Synthetic values.)
    urls = ["https://calendar.google.com/calendar/ical/x%40group.calendar.google.com/"
            "private-0123456789abcdef0123456789abcdef/basic.ics",
            "https://cloud.timeedit.example/uni/web/s/ri.html?h=t&sid=3"
            "&x=Qx7Zk2Lm9Pq4Rt6Vw8Yz1Ab3Cd5Ef7Gh",
            "https://cloud.timeedit.example/uni/web/s/ri.html?p=0A1B2C3D4E5F60718293A4B5C6D7E8F901",
            "https://api.example.org/feed?api_key=Zx81Kq0LmWw2"]
    (tmp_path / "config.stdout").write_text("\n".join(f"url = {u}" for u in urls))
    result = scan(tmp_path, "--originals", tmp_path / "none.txt")
    assert result.returncode == 1
    for kind in ("capability-url", "url-token", "url-secret"):
        assert kind in result.stdout, result.stdout
    assert result.stdout.count("url-token") == 2, result.stdout
    for secret in ("0123456789abcdef0123456789abcdef", "Qx7Zk2Lm9Pq4Rt6Vw8Yz1Ab3Cd5Ef7Gh",
                   "Zx81Kq0LmWw2"):
        assert secret not in result.stdout


def test_prose_placeholders_and_commit_links_are_not_secrets(tmp_path):
    (tmp_path / "doc.nw").write_text(
        "The token is a bearer credential---anyone holding it can log in.\n"
        'token = "your-canvas-token"\n'
        "API_KEY=YOUR_API_KEY_GOES_HERE\n"
        "See https://github.com/x/y/commit/0123456789abcdef0123456789abcdef01234567\n"
        "and https://blog.example/how-we-test-3-services-without-mocks-in-2024/\n"
        "and https://rfc.example/New-Properties-for-iCalendar-RFC-7986.html\n")
    result = scan(tmp_path, "--originals", tmp_path / "none.txt")
    assert result.returncode == 0, result.stdout


def test_user_ids_in_urls_are_warnings_on_request(tmp_path):
    (tmp_path / "t.nw").write_text(
        "preview = 'https://lms.example/courses/1/assignments/2/submissions/123456?x=1'\n")
    quiet = scan(tmp_path, "--originals", tmp_path / "none.txt")
    assert quiet.returncode == 0 and "url-id" not in quiet.stdout
    warned = scan(tmp_path, "--originals", tmp_path / "none.txt", "--warn-ids")
    assert warned.returncode == 0 and "warning: url-id" in warned.stdout
    assert "123456" not in warned.stdout
