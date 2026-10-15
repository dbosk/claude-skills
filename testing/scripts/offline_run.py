#!/usr/bin/env python3
"""Run a test command so that it cannot reach a real service.

    offline_run.py [--timeout SECONDS] [--isolate-home] -- COMMAND [ARG ...]
    offline_run.py -- make test
    offline_run.py -- uv run pytest

For the first run of an unfamiliar suite ("first run the tests"), when
some tests may log in to a service or write to it.  Every Python process
the command starts (and their Python subprocesses) gets:

- network connections refused, except to loopback (local instances still
  work), with an error that HTTP clients do not retry; `python -I` is
  not covered;

and the whole command, Python or not, gets:

- programs that reach a service by themselves refused, through stand-ins
  first on PATH (NETWORK_PROGRAMS below: ssh, curl, gh, AFS's pts and
  fs, ...; git and rsync only when they would talk to another host).  A
  program called by absolute path, or a library that opens sockets from
  C, is not covered.  A test that skips when `shutil.which("fs")` finds
  nothing finds the stand-in, so it fails (visibly) instead of skipping;
- AFS tokens dropped: the command starts in a fresh PAG (pagsh), so the
  AFS client treats it as an anonymous user and writes under /afs are
  refused.  Tokens live in the kernel, so a fake HOME does not hide them;
- the Kerberos ticket hidden (KRB5CCNAME points at a file that does not
  exist);
- credential-like variables removed from the environment (names with
  TOKEN, SECRET, PASS, KEY, LOGIN, USER, AUTH, SESSION, CREDENTIAL); their
  names, never their values, are printed, so there is no need to list
  the environment to see what the tests would have used;
- the keyring disabled (PYTHON_KEYRING_BACKEND=fail), so no stored
  credential is used and no unlock prompt appears;
- no .pyc files and no .pytest_cache (PYTHONDONTWRITEBYTECODE,
  -p no:cacheprovider), and --continue-on-collection-errors, so that a
  module that logs in at import time does not hide the other tests' results;
- UV_OFFLINE=1, so `uv run` does not try to download;
- a time limit (default 600 s) after which the whole process group gets
  SIGTERM, and SIGKILL 10 s later (so mutate.py can restore its file).

Other network file systems (NFS, SMB, sshfs) are not covered: check the
tests for such paths before the first run (references/reviewing.md).

--isolate-home also points HOME and the XDG directories at an empty temp
directory, hiding config files and cached sessions.  It is kept and
named, so that what the tests wrote there can be inspected.  Tools that keep
their environments there (poetry's virtualenvs) then cannot find them;
use the project's venv python directly in that case.

Tests that need the service then fail or skip, which is the baseline.
The exit status is the command's.
"""

import argparse
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

GRACE = 10  # seconds between SIGTERM and SIGKILL after --timeout
OFFLINE_DIR = Path(__file__).resolve().parent / "offline"
CREDENTIAL_NAME = re.compile(
    r"TOKEN|SECRET|PASS|API_?KEY|_KEY$|^KEY|LOGIN|_USER$|^USER_|AUTH|SESSION|CREDENTIAL",
    re.I)
KEEP = {"PATH", "USER", "LOGNAME", "HOME", "SHELL", "LANG", "TERM", "PWD"}
NETWORK_PROGRAMS = (
    "ssh", "scp", "sftp", "mosh", "curl", "wget", "http", "https", "gh", "glab",
    "hub", "nc", "ncat", "netcat", "telnet", "ftp", "lftp", "smbclient",
    "kinit", "aklog", "klog", "pts", "fs", "aws", "gcloud", "az",
    "git", "rsync",  # these two only when they would reach another host
)


def network_shims(directory: Path, path: str) -> None:
    """A stand-in for each program, which refuses it or runs the real one."""
    for name in NETWORK_PROGRAMS:
        real = shutil.which(name, path=path) or ""
        shim = directory / name
        shim.write_text(f'#!/bin/sh\nexec "{sys.executable}" -I '
                        f'"{OFFLINE_DIR / "refuse.py"}" {name} "{real}" "$@"\n')
        shim.chmod(0o755)


def credential_names(env: dict) -> list[str]:
    return sorted(k for k in env if k not in KEEP and CREDENTIAL_NAME.search(k))


def offline_env(env: dict) -> dict:
    env = {k: v for k, v in env.items() if k not in credential_names(env)}
    env["PYTHONPATH"] = os.pathsep.join(
        p for p in (str(OFFLINE_DIR), env.get("PYTHONPATH", "")) if p)
    env["PYTHON_KEYRING_BACKEND"] = "keyring.backends.fail.Keyring"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTEST_ADDOPTS"] = " ".join(
        p for p in (env.get("PYTEST_ADDOPTS", ""), "-p no:cacheprovider",
                    "--continue-on-collection-errors") if p)
    env["UV_OFFLINE"] = "1"
    return env


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--" not in argv or not argv[argv.index("--") + 1:]:
        print(__doc__, file=sys.stderr)
        return 2
    split = argv.index("--")
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=float, default=600)
    parser.add_argument("--isolate-home", action="store_true")
    args = parser.parse_args(argv[:split])
    command = argv[split + 1:]

    env = offline_env(os.environ)
    removed = credential_names(os.environ)
    shims = Path(tempfile.mkdtemp(prefix="offline-run-"))
    network_shims(shims, env.get("PATH", os.defpath))
    env["PATH"] = os.pathsep.join((str(shims), env.get("PATH", os.defpath)))
    env["KRB5CCNAME"] = f"FILE:{shims / 'no-kerberos-ticket'}"
    notes = ["Python network blocked except loopback",
             "network programs refused", "Kerberos ticket hidden", "keyring disabled",
             f"removed {', '.join(removed) or 'no credential variables'}"]
    pagsh = shutil.which("pagsh")
    if pagsh:
        command = [pagsh, "-c", 'exec "$@"', "offline_run", *command]
        notes.insert(2, "AFS tokens dropped (new PAG)")
    if args.isolate_home:
        home = tempfile.mkdtemp(prefix="offline-home-")
        env["HOME"] = home
        for var, sub_dir in (("XDG_CONFIG_HOME", ".config"), ("XDG_CACHE_HOME", ".cache"),
                             ("XDG_DATA_HOME", ".local/share"),
                             ("XDG_STATE_HOME", ".local/state")):
            env[var] = os.path.join(home, sub_dir)
        notes.append(f"HOME={home} (empty; kept afterwards)")
    print(f"offline_run: {'; '.join(notes)}", file=sys.stderr)
    try:
        return run(command, env, args.timeout)
    finally:
        shutil.rmtree(shims, ignore_errors=True)


def run(command: list[str], env: dict, timeout: float) -> int:
    process = subprocess.Popen(command, env=env, start_new_session=True)
    try:
        return process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        # SIGTERM first, so a wrapper such as mutate.py can restore the file
        # it changed; SIGKILL whatever is still running after a grace period
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=GRACE)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
        print(f"offline_run: killed after {timeout:g} s; a test is probably "
              "waiting on the network or a prompt", file=sys.stderr)
        return 124


if __name__ == "__main__":
    sys.exit(main())
