"""The template conftest.py end to end, in a throwaway project.

One real local service; separate pytest processes for each mode, the way a
developer or agent would run them.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ASSETS = Path(__file__).resolve().parent.parent / "assets"

PROJECT_TEST = '''
import json, os, urllib.request
import pytest

URL = os.environ["SERVICE_URL"]

@pytest.mark.vcr
def test_users(service_token):
    request = urllib.request.Request(
        URL + "/api/v1/users", headers={"Authorization": f"Bearer {service_token}"})
    users = json.loads(urllib.request.urlopen(request).read())
    # Invariants, not values: this body must also hold against live data.
    assert users and all({"id", "name"} <= user.keys() for user in users)

@pytest.mark.live
def test_live_only_reaches_the_service():  # no cassette, no allowed host
    assert urllib.request.urlopen(URL + "/api/v1/users").read()
'''


@pytest.fixture
def project(tmp_path):
    tests = tmp_path / "proj" / "tests"
    tests.mkdir(parents=True)
    shutil.copy(ASSETS / "conftest.py", tests)
    shutil.copy(ASSETS / "vcr_support.py", tests)
    (tests / "test_service.py").write_text(PROJECT_TEST)
    (tmp_path / "proj" / "pyproject.toml").write_text(
        '[tool.pytest.ini_options]\naddopts = ["--block-network", "-p", "no:cacheprovider"]\n')
    return tmp_path / "proj"


def run(project, service, *args, secrets=True):
    env = {k: v for k, v in os.environ.items()
           if k not in ("SERVICE_TOKEN", "TEST_PSEUDONYM_KEY")}
    env.update(SERVICE_URL=service.url,
               TEST_ORIGINALS_FILE=str(project.parent / "originals.txt"),
               PYTHONDONTWRITEBYTECODE="1")
    if secrets:
        env.update(SERVICE_TOKEN="real-token-1234567890", TEST_PSEUDONYM_KEY="key")
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", *args],
                            cwd=project, env=env, capture_output=True, text=True)
    return result.returncode, result.stdout + result.stderr


def test_record_replay_live_drift_and_privacy(project, fake_service, roster):
    fake_service.routes["/api/v1/users"] = (200, roster)
    cassette = project / "tests" / "cassettes" / "test_service" / "test_users.yaml"

    code, out = run(project, fake_service, secrets=True)
    assert code != 0, "replay without a cassette must fail, not hit the network"

    code, out = run(project, fake_service, "--record-mode=once", secrets=False)
    assert code == 2 and "refusing to record" in out

    code, out = run(project, fake_service, "--record-mode=once")
    assert code == 0, out
    assert "Anna" not in cassette.read_text() and "real-token" not in cassette.read_text()

    code, out = run(project, fake_service, secrets=False)  # offline replay, no secrets
    assert code == 0, out

    code, out = run(project, fake_service, "--live")
    assert code == 0 and "no structural drift" in out and "2 passed" in out, out

    for user in roster:  # the service renames a field
        user["login"] = user.pop("login_id")
    code, out = run(project, fake_service, "--live")
    assert code == 1 and "DRIFT" in out and "removed $[].login_id" in out, out
    assert "user-" not in out and "Person-" not in out  # shapes only, no values

    roster[0]["nickname"] = "Svensson"  # a name in a field nobody listed
    code, out = run(project, fake_service, "--record-mode=rewrite")
    assert code == 1 and "PRIVACY" in out and "original" in out, out
    assert "Svensson" not in out


MORE_TESTS = '''
import json, os, urllib.request
import pytest

URL = os.environ["SERVICE_URL"]

def get(path):
    return json.loads(urllib.request.urlopen(URL + path).read())

def test_local_instance():  # rung 2: a localhost server, no cassette
    assert get("/api/v1/users")

@pytest.mark.live
def test_live_only():  # no cassette; must reach the service under --live
    assert get("/api/v1/users")

@pytest.mark.vcr
@pytest.mark.mutates
def test_writes_something():
    assert get("/api/v1/users")

@pytest.mark.vcr
@pytest.mark.synthetic_text("body")
def test_sandbox_prose():
    assert get("/api/v1/page")["body"] == "Synthetic sandbox prose"
'''


def test_template_modes_markers_and_layout(project, fake_service, roster):
    fake_service.routes["/api/v1/users"] = (200, roster)
    fake_service.routes["/api/v1/page"] = (200, {"title": "Lab", "body": "Synthetic sandbox prose"})
    (project / "tests" / "__init__.py").write_text("")  # package layout
    (project / "tests" / "test_more.py").write_text(MORE_TESTS)
    (project / "pyproject.toml").write_text(
        '[tool.pytest.ini_options]\naddopts = ["--block-network", '
        '"--allowed-hosts=127.0.0.1,::1,localhost", "-p", "no:cacheprovider"]\n')

    code, out = run(project, fake_service, "--record-mode=once", "tests/test_more.py")
    assert code == 0, out
    page = project / "tests" / "cassettes" / "test_more" / "test_sandbox_prose.yaml"
    assert "Synthetic sandbox prose" in page.read_text()

    code, out = run(project, fake_service, "tests/test_more.py", "-rs")
    assert code == 0 and "3 passed" in out, out  # replay; the live-only test skips

    live_dir = project.parent / "live"
    code, out = run(project, fake_service, "--live", f"--live-dir={live_dir}",
                    "tests/test_more.py", "-rs")
    assert code == 0, out
    assert "3 passed, 1 skipped" in out, out  # the live-only test reached the service
    assert "changes the service" in out  # the mutating test is skipped live
    assert (live_dir / ".pytest-live-cassettes").exists()

    precious = project.parent / "precious"
    precious.mkdir()
    (precious / "keep.txt").write_text("do not delete")
    code, out = run(project, fake_service, "--live", f"--live-dir={precious}",
                    "tests/test_more.py")
    assert code != 0 and "refusing" in out, out
    assert (precious / "keep.txt").exists()


WRITE_TEST = '''
import json, os, urllib.request
import pytest

URL = os.environ["SERVICE_URL"]

def call(method, path, body=None):
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(URL + path, data=data, method=method,
                                     headers={"Content-Type": "application/json"})
    return urllib.request.urlopen(request).read()

@pytest.mark.vcr
@pytest.mark.mutates
def test_set_grade():
    call("PUT", "/api/v1/results/7", {"grade": GRADE})
    if CLEANUP:
        call("DELETE", "/api/v1/results/7")
'''


def test_replay_checks_what_a_write_test_sends(project, fake_service):
    # Matching on method and URL alone lets a wrong body or a skipped request
    # (a cleanup step, a DELETE) pass in replay.
    fake_service.routes["/api/v1/results/7"] = (200, {"ok": True})
    test = project / "tests" / "test_service.py"

    def write(grade, cleanup):
        test.write_text(WRITE_TEST.replace("GRADE", repr(grade)).replace("CLEANUP", str(cleanup)))

    write("P", True)
    code, out = run(project, fake_service, "--record-mode=once")
    assert code == 0, out
    code, out = run(project, fake_service, secrets=False)
    assert code == 0, out

    write("F", True)  # sends the wrong grade
    code, out = run(project, fake_service, secrets=False)
    assert code != 0, out

    write("P", False)  # skips the cleanup
    code, out = run(project, fake_service, secrets=False)
    assert code != 0 and "not made" in out, out
