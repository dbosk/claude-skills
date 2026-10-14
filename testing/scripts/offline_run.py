#!/usr/bin/env python3
"""Run a test command so that it cannot reach a real service.

    offline_run.py -- COMMAND [ARG ...]
    offline_run.py -- make test
    offline_run.py -- uv run pytest

For the first run of an unfamiliar suite ("first run the tests"), when
some tests may log in to a service or write to it.  Every Python process
the command starts (and their Python subprocesses) gets:

- network connections refused, except to loopback (local instances still
  work); non-Python programs such as curl are NOT covered;
- the keyring disabled (PYTHON_KEYRING_BACKEND=fail), so no stored
  credential is used and no unlock prompt appears;
- no .pyc files and no .pytest_cache (PYTHONDONTWRITEBYTECODE,
  -p no:cacheprovider), and --continue-on-collection-errors, so that a
  module that logs in at import time does not hide the other tests' results;
- UV_OFFLINE=1, so `uv run` does not try to download.

Tests that need the service then fail or skip, which is the baseline.
The exit status is the command's.
"""

import os
import subprocess
import sys
from pathlib import Path

OFFLINE_DIR = Path(__file__).resolve().parent / "offline"


def offline_env(env: dict) -> dict:
    env = dict(env)
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
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    print("offline_run: Python network blocked except loopback; keyring disabled",
          file=sys.stderr)
    return subprocess.run(argv, env=offline_env(os.environ)).returncode


if __name__ == "__main__":
    sys.exit(main())
