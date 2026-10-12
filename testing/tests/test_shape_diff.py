"""cassette_shape_diff.py reports structural drift and never values."""

import json
import subprocess
import sys
from pathlib import Path

import yaml

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "cassette_shape_diff.py"


def cassette(directory, payload, status=200, path="/api/v1/users/101"):
    directory.mkdir(parents=True, exist_ok=True)
    data = {"version": 1, "interactions": [{
        "request": {"method": "GET", "uri": f"https://lms.example{path}",
                    "body": None, "headers": {}},
        "response": {"status": {"code": status, "message": "OK"},
                     "headers": {"Content-Type": ["application/json"]},
                     "body": {"string": json.dumps(payload)}}}]}
    (directory / "test_x.yaml").write_text(yaml.safe_dump(data))


def diff(a, b, *flags):
    return subprocess.run([sys.executable, str(SCRIPT), str(a), str(b), *flags],
                          capture_output=True, text=True)


def test_value_changes_are_not_drift(tmp_path):
    cassette(tmp_path / "old", {"id": 1, "name": "Person-aaaaaa", "tags": ["a"]})
    cassette(tmp_path / "new", {"id": 2, "name": "Person-bbbbbb", "tags": ["b", "c"]},
             path="/api/v1/users/202")
    result = diff(tmp_path / "old", tmp_path / "new")
    assert result.returncode == 0, result.stdout


def test_renamed_key_is_drift_and_values_stay_hidden(tmp_path):
    cassette(tmp_path / "old", {"id": 1, "login_id": "user-aaaaaa"})
    cassette(tmp_path / "new", {"id": 1, "login": "user-aaaaaa"})
    result = diff(tmp_path / "old", tmp_path / "new")
    assert result.returncode == 1
    assert "removed $.login_id" in result.stdout
    assert "user-aaaaaa" not in result.stdout


def test_type_and_status_changes_are_drift(tmp_path):
    cassette(tmp_path / "old", {"score": 4.5})
    cassette(tmp_path / "new", {"score": "4.5"}, status=203)
    out = diff(tmp_path / "old", tmp_path / "new").stdout
    assert "type of $.score" in out and "status" in out


def test_null_is_compatible_and_additions_need_strict(tmp_path):
    cassette(tmp_path / "old", {"avatar": None})
    cassette(tmp_path / "new", {"avatar": "https://example.invalid/x", "extra": 1})
    assert diff(tmp_path / "old", tmp_path / "new").returncode == 0
    assert diff(tmp_path / "old", tmp_path / "new", "--strict").returncode == 1


def test_empty_or_smaller_live_arrays_are_not_drift(tmp_path):
    cassette(tmp_path / "old", [{"id": 1, "grade": "A"}, {"id": 2}])
    cassette(tmp_path / "new", [])
    assert diff(tmp_path / "old", tmp_path / "new").returncode == 0
    cassette(tmp_path / "new2", [{"id": 3}])  # the one live item lacks the optional key
    assert diff(tmp_path / "old", tmp_path / "new2").returncode == 0


def test_cassettes_with_python_tags_load():
    import vcr_support
    text = ("interactions:\n- request: {uri: 'https://x.example/', method: GET}\n"
            "  response:\n    status: !!python/tuple [200, OK]\n    body: {string: ''}\n")
    path = Path(__file__).parent / "_tuple.yaml"
    path.write_text(text)
    try:
        assert len(vcr_support.load_cassette(path)) == 1
    finally:
        path.unlink()


def test_optional_keys_are_not_drift_but_required_ones_are(tmp_path):
    cassette(tmp_path / "old", [{"id": 1, "grade": "A"}, {"id": 2}])
    cassette(tmp_path / "new", [{"id": 3}, {"id": 4}])  # nobody graded yet
    assert diff(tmp_path / "old", tmp_path / "new").returncode == 0
    cassette(tmp_path / "old2", [{"id": 1, "login_id": "a"}, {"id": 2, "login_id": "b"}])
    cassette(tmp_path / "new2", [{"id": 1, "login": "a"}, {"id": 2, "login": "b"}])
    assert diff(tmp_path / "old2", tmp_path / "new2").returncode == 1
