"""Recorded-service tests: offline replay by default, `--live` to detect drift.

Copy this file and vcr_support.py into the project's tests/ directory.
Requires pytest and pytest-recording (which brings vcrpy and PyYAML).
In pyproject.toml:

    [tool.pytest.ini_options]
    # Replay must never touch the network; local instances (rung 2) may.
    addopts = ["--block-network", "--allowed-hosts=127.0.0.1,::1,localhost"]

Modes:

    pytest                                   replay committed cassettes, offline
    pytest --live                            run against the real service, re-record
                                             into a temp dir, compare shapes with the
                                             committed cassettes (values never shown)
    pytest --live --live-writes              also run tests marked `mutates`
    pytest --record-mode=once -k test_new    record a new test's cassette
    pytest --record-mode=rewrite -k test_x   deliberately re-record after drift

Recording (any mode but replay) needs TEST_PSEUDONYM_KEY set to a secret
that stays out of the repo (e.g. in the keyring or a password manager).
Keep it stable: the same key gives the same pseudonyms, so re-recordings
produce small, reviewable diffs.

Markers:

    live                  needs the real service; skipped unless --live
    mutates               changes state on the service (POST, PUT, DELETE);
                          replayed normally, skipped under --live unless
                          --live-writes, and then only against a sandbox
    synthetic_text(*keys) these free-text fields hold synthetic sandbox prose;
                          record them verbatim instead of redacting them
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

import pytest

# Import the helper next to this file, also when tests/ is a package or
# pytest runs with --import-mode=importlib.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import vcr_support  # noqa: E402

SERVICE_TOKEN_ENV = "SERVICE_TOKEN"  # TODO: the project's credential variable
LIVE_MARKER_FILE = ".pytest-live-cassettes"  # only directories holding it are wiped


def record_mode_of(config):
    return config.getoption("--record-mode") or "none"


def pytest_addoption(parser):
    group = parser.getgroup("live", "live service checks")
    group.addoption("--live", action="store_true",
                    help="run recorded tests against the real service and "
                         "report cassette drift")
    group.addoption("--live-dir", default=None,
                    help="where --live writes fresh cassettes; give it as "
                         "--live-dir=PATH (default: a private directory under the temp dir)")
    group.addoption("--live-writes", action="store_true",
                    help="under --live, also run tests marked `mutates`")


def pytest_configure(config):
    for line in ("live: needs the real service; skipped unless --live",
                 "mutates: changes state on the service; skipped under --live "
                 "unless --live-writes",
                 "synthetic_text(*keys): record these free-text fields verbatim"):
        config.addinivalue_line("markers", line)
    config._recorded_dirs = set()
    if config.getoption("--live"):
        # Set the options themselves, not only the fixtures: the network
        # block of pytest-recording reads the options, and live tests
        # without a cassette must reach the service too.
        config.option.record_mode = "all"
        config.option.block_network = False
        root = Path(str(config.rootpath))
        tag = hashlib.sha256(str(root.resolve()).encode()).hexdigest()[:10]
        config._live_dir = Path(config.getoption("--live-dir") or vcr_support.private_dir()
                                / f"{root.name}-{tag}-live-cassettes").resolve()
        prepare_live_dir(config._live_dir, root.resolve())
    if record_mode_of(config) != "none" and not os.environ.get(vcr_support.KEY_ENV):
        pytest.exit(f"refusing to record: set {vcr_support.KEY_ENV} so that "
                    "personal data is pseudonymized", returncode=2)


def prepare_live_dir(live_dir: Path, root: Path):
    """Empty the live directory, but only one that an earlier live run made.

    A stale run must not mask drift, yet a mistyped --live-dir must never
    delete a project: refuse anything that is not empty and not ours.
    """
    if live_dir == root or live_dir in root.parents:
        pytest.exit(f"refusing --live-dir={live_dir}: it contains the project", returncode=2)
    if live_dir.exists() and any(live_dir.iterdir()):
        if not (live_dir / LIVE_MARKER_FILE).exists():
            pytest.exit(f"refusing to empty --live-dir={live_dir}: it has files that "
                        "an earlier live run did not write", returncode=2)
        shutil.rmtree(live_dir)
    live_dir.mkdir(parents=True, exist_ok=True)
    (live_dir / LIVE_MARKER_FILE).write_text("written by pytest --live; safe to delete\n")


def pytest_collection_modifyitems(config, items):
    live = config.getoption("--live")
    skip_live = pytest.mark.skip(reason="live-only test; run with --live")
    skip_write = pytest.mark.skip(
        reason="changes the service; run with --live --live-writes against a sandbox")
    for item in items:
        if not live and "live" in item.keywords:
            item.add_marker(skip_live)
        if live and "mutates" in item.keywords and not config.getoption("--live-writes"):
            item.add_marker(skip_write)


@pytest.fixture(scope="session")
def recording(record_mode):
    return record_mode != "none"


@pytest.fixture(scope="module")
def vcr_cassette_dir(request):
    module = Path(request.node.path)
    committed = module.parent / "cassettes" / module.stem
    config = request.config
    if config.getoption("--live"):
        relative = committed.relative_to(config.rootpath)
        target = config._live_dir / relative
        config._recorded_dirs.add((committed, target))
        return str(target)
    if record_mode_of(config) != "none":
        config._recorded_dirs.add((committed, committed))
    return str(committed)


@pytest.fixture(scope="session")
def pseudonymizer(request, recording):
    key = os.environ.get(vcr_support.KEY_ENV, "")  # checked in pytest_configure
    originals = Path(os.environ.get(vcr_support.ORIGINALS_ENV)
                     or vcr_support.default_originals_path(request.config.rootpath))
    request.config._originals_path = originals
    # Replay never writes a cassette, so its key only has to be non-empty.
    return vcr_support.Pseudonymizer((key or "replay-only").encode(),
                                     originals if recording else None)


@pytest.fixture
def vcr_config(request, pseudonymizer):
    marker = request.node.get_closest_marker("synthetic_text")
    pseudonymizer.keep_text = {k.lower() for k in marker.args} if marker else set()
    yield pseudonymizer.vcr_config()
    pseudonymizer.keep_text = set()


@pytest.fixture(autouse=True)
def cassette_fully_played(vcr, recording):
    """In replay, every recorded request must be made again.

    Otherwise a test that skips a DELETE or its cleanup still passes.
    """
    yield
    if vcr is not None and not recording and not vcr.all_played:
        unplayed = [f"{r.method} {r.path}" for i, r in enumerate(vcr.requests)
                    if not vcr.play_counts[i]]
        pytest.fail(f"{len(unplayed)} recorded request(s) not made in replay: "
                    + ", ".join(unplayed), pytrace=False)


@pytest.fixture(scope="session")
def service_token(recording):
    """The real credential when talking to the service, a dummy in replay.

    Authorization headers are filtered from cassettes and not used for
    matching, so replay works without any secret on the machine.
    """
    if not recording:
        return "replay-token"
    token = os.environ.get(SERVICE_TOKEN_ENV)
    if not token:
        pytest.skip(f"{SERVICE_TOKEN_ENV} not set; cannot reach the service")
    return token


def pytest_sessionfinish(session, exitstatus):
    config = session.config
    pairs = getattr(config, "_recorded_dirs", set())
    if not pairs:
        return
    reporter = config.pluginmanager.get_plugin("terminalreporter")

    def write(message, **markup):
        if reporter:
            reporter.write_line(message, **markup)
        else:
            print(message)

    originals = vcr_support.Needles(
        vcr_support.read_list(getattr(config, "_originals_path", None)))

    leaks = []
    for _, written in sorted(pairs):
        for f in vcr_support.iter_files([written]):
            if f.name != LIVE_MARKER_FILE:
                leaks += [(f, where, kind, hit)
                          for where, kind, hit in vcr_support.scan_file(f, originals)]
    if leaks:
        write("PRIVACY: recorded cassettes contain personal data or secrets "
              "(values redacted below). Extend the key lists in vcr_support.py "
              "or the scrubbing, delete the cassettes, and record again.", red=True)
        for f, where, kind, hit in leaks:
            write(f"  {f}:{where}: {kind} {hit}")
        session.exitstatus = 1

    if config.getoption("--live"):
        drift = []
        for committed, live in sorted(pairs):
            if committed.exists() and live.exists():
                drift += vcr_support.compare_directories(committed, live)
        hard = [f for f in drift if f[0] == "drift"]
        for sev, name, key, msg in drift:
            if msg != "not re-recorded in the live run":
                write(f"  {sev}: {name} {key}: {msg}", red=sev == "drift")
        if hard:
            write("DRIFT: the service no longer matches the committed cassettes. "
                  "Fix the code if needed, then re-record the affected tests with "
                  "--record-mode=rewrite -k <test> and review the diff.", red=True)
            session.exitstatus = 1
        else:
            write(f"live: no structural drift ({config._live_dir})", green=True)
