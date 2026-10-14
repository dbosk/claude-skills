"""offline_run.py and mutate.py, run as real subprocesses on real files."""

import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def run(script, *args, cwd=None):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                          capture_output=True, text=True, cwd=cwd, timeout=60)


CONNECT = """
import socket, sys
s = socket.socket()
s.settimeout(2)
try:
    s.connect((sys.argv[1], int(sys.argv[2])))
except OSError as err:
    print("error:", err)
"""


def test_offline_run_blocks_remote_hosts_in_every_python_process():
    # 192.0.2.1 (TEST-NET-1) never answers; the block must refuse at once.
    result = run("offline_run.py", "--", sys.executable, "-c",
                 f"import subprocess, sys; subprocess.run([sys.executable, '-c', {CONNECT!r},"
                 " '192.0.2.1', '443'])")
    assert "blocked by offline_run" in result.stdout, result.stdout + result.stderr


def test_offline_run_allows_loopback_and_sets_safe_defaults():
    code = """
import os, socket, threading, http.server
srv = http.server.HTTPServer(("127.0.0.1", 0), http.server.BaseHTTPRequestHandler)
threading.Thread(target=srv.handle_request, daemon=True).start()
socket.create_connection(("127.0.0.1", srv.server_port), timeout=5).close()
print("loopback ok")
print(os.environ["PYTHON_KEYRING_BACKEND"])
print(os.environ["PYTEST_ADDOPTS"])
"""
    result = run("offline_run.py", "--", sys.executable, "-c", code)
    out = result.stdout
    assert result.returncode == 0, out + result.stderr
    assert "loopback ok" in out and "fail.Keyring" in out
    assert "no:cacheprovider" in out and "--continue-on-collection-errors" in out


def test_offline_run_passes_the_exit_status_through():
    assert run("offline_run.py", "--", sys.executable, "-c", "raise SystemExit(3)").returncode == 3


def make_project(tmp_path, test_body):
    (tmp_path / "mod.py").write_text("def add(a, b):\n    return a + b\n")
    (tmp_path / "test_mod.py").write_text(f"from mod import add\n\ndef test_add():\n    {test_body}\n")
    return tmp_path / "mod.py"


PYTEST = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_mod.py"]


def test_mutate_reports_a_killed_mutant_and_restores(tmp_path):
    mod = make_project(tmp_path, "assert add(2, 3) == 5")
    before = mod.read_bytes()
    result = run("mutate.py", mod, "a + b", "a - b", "--", *PYTEST, cwd=tmp_path)
    assert result.returncode == 0 and "killed" in result.stdout, result.stdout
    assert mod.read_bytes() == before


def test_mutate_reports_a_surviving_mutant(tmp_path):
    mod = make_project(tmp_path, "assert add(0, 0) == 0")  # too weak to see the change
    before = mod.read_bytes()
    result = run("mutate.py", mod, "a + b", "a - b", "--", *PYTEST, cwd=tmp_path)
    assert result.returncode == 1 and "SURVIVED" in result.stdout, result.stdout
    assert mod.read_bytes() == before


def test_mutate_refuses_ambiguous_or_missing_text(tmp_path):
    mod = make_project(tmp_path, "assert add(2, 3) == 5")
    before = mod.read_bytes()
    assert run("mutate.py", mod, "nowhere", "x", "--", "true").returncode == 2
    assert run("mutate.py", mod, "a", "x", "--", "true").returncode == 2  # several matches
    assert mod.read_bytes() == before
