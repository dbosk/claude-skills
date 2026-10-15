"""offline_run.py and mutate.py, run as real subprocesses on real files."""

import os
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
    assert "blocked by offline_run" in result.stdout + result.stderr


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


def test_offline_run_still_runs_the_shadowed_sitecustomize(tmp_path):
    # The distribution's sitecustomize must run, silently.
    other = tmp_path / "site"
    other.mkdir()
    (other / "sitecustomize.py").write_text("import os\nos.environ['SHADOWED_RAN'] = '1'\n")
    code = "import os; print('ran', os.environ.get('SHADOWED_RAN'))"
    env = {**os.environ, "PYTHONPATH": str(other)}
    result = subprocess.run([sys.executable, str(SCRIPTS / "offline_run.py"), "--",
                             sys.executable, "-c", code],
                            capture_output=True, text=True, env=env, timeout=60)
    assert "ran 1" in result.stdout
    assert "Error" not in result.stderr, result.stderr


def test_blocked_connections_are_not_retried_as_network_errors():
    # requests/urllib3 retry OSError with backoff; a block must end the call.
    code = ("import socket\n"
            "try:\n    socket.create_connection(('192.0.2.1', 443), timeout=2)\n"
            "except OSError:\n    print('retryable')\n"
            "except BaseException as err:\n    print('final', type(err).__name__)\n")
    result = run("offline_run.py", "--", sys.executable, "-c", code)
    assert "final" in result.stdout, result.stdout + result.stderr


def test_offline_run_strips_credentials_from_the_environment():
    code = ("import os\nfor k in ('LADOK_PASS', 'CANVAS_TOKEN', 'MY_API_KEY', 'PATH', 'LANG'):\n"
            "    print(k, k in os.environ)\n")
    env = {**os.environ, "LADOK_PASS": "x", "CANVAS_TOKEN": "x", "MY_API_KEY": "x",
           "LANG": "C.UTF-8"}
    result = subprocess.run([sys.executable, str(SCRIPTS / "offline_run.py"), "--",
                             sys.executable, "-c", code],
                            capture_output=True, text=True, env=env, timeout=60)
    out = result.stdout
    for name in ("LADOK_PASS", "CANVAS_TOKEN", "MY_API_KEY"):
        assert f"{name} False" in out
    assert "PATH True" in out and "LANG True" in out
    # names are reported so nobody needs to list the environment; values never
    assert "LADOK_PASS" in result.stderr and "=x" not in result.stderr


def test_mutate_refuses_a_red_baseline(tmp_path):
    mod = make_project(tmp_path, "assert add(2, 3) == 6")  # already failing
    result = run("mutate.py", mod, "a + b", "a - b", "--", *PYTEST, cwd=tmp_path)
    assert result.returncode == 2 and "baseline" in result.stdout + result.stderr


def test_offline_run_kills_a_hanging_command():
    import time
    start = time.monotonic()
    result = run("offline_run.py", "--timeout", "1", "--", sys.executable, "-c",
                 "import time; time.sleep(30)")
    assert result.returncode == 124 and "killed after" in result.stderr
    assert time.monotonic() - start < 15  # killed, not waited for


def test_mutate_never_runs_stale_bytecode(tmp_path):
    # A cached .pyc of the original that Python would use without checking
    # the source: the mutant must still be what the tests run.
    import importlib.util
    import py_compile
    mod = make_project(tmp_path, "assert add(2, 3) == 5")
    py_compile.compile(str(mod), cfile=importlib.util.cache_from_source(str(mod)),
                       invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)
    result = run("mutate.py", mod, "a + b", "a - b", "--", *PYTEST, cwd=tmp_path)
    assert result.returncode == 0 and "killed" in result.stdout, result.stdout


def test_isolate_home_hides_the_users_files():
    code = "import os; print(os.environ['HOME'], os.environ['XDG_CACHE_HOME'])"
    out = run("offline_run.py", "--isolate-home", "--", sys.executable, "-c", code).stdout
    home, cache = out.split()
    assert home != os.path.expanduser("~") and cache.startswith(home)


HANG = ("return a + b", "while True: pass")


def test_a_timeout_in_offline_run_still_restores_the_mutated_file(tmp_path):
    mod = make_project(tmp_path, "assert add(2, 3) == 5")
    before = mod.read_bytes()
    run("offline_run.py", "--timeout", "4", "--", sys.executable,
        SCRIPTS / "mutate.py", "--no-baseline", mod, *HANG, "--", *PYTEST, cwd=tmp_path)
    assert mod.read_bytes() == before


def test_mutate_counts_a_hang_as_killed_and_restores(tmp_path):
    import time
    mod = make_project(tmp_path, "assert add(2, 3) == 5")
    before = mod.read_bytes()
    start = time.monotonic()
    result = run("mutate.py", "--timeout", "3", mod, *HANG, "--", *PYTEST, cwd=tmp_path)
    assert result.returncode == 0 and "killed" in result.stdout, result.stdout
    assert "timeout" in result.stdout
    assert mod.read_bytes() == before
    assert time.monotonic() - start < 30
