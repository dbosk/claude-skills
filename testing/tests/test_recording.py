"""Recording a real local service through vcrpy leaves nothing personal behind."""

import json
import urllib.request

import pytest
import vcr

import vcr_support
from vcr_support import Pseudonymizer


def fetch(url, token="real-secret-token-value"):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())


def test_record_scrub_and_replay_offline(tmp_path, fake_service, roster, submissions):
    fake_service.routes["/api/v1/users"] = (200, roster)
    fake_service.routes["/api/v1/submissions"] = (200, submissions)
    originals = tmp_path / "originals.txt"
    config = Pseudonymizer(b"test-key", originals).vcr_config()
    cassette = tmp_path / "cassettes" / "test_users.yaml"

    with vcr.VCR(record_mode="once", **config).use_cassette(str(cassette)):
        live_users = fetch(fake_service.url + "/api/v1/users")
        fetch(fake_service.url + "/api/v1/submissions")
    assert live_users[0]["name"] == "Anna Svensson"  # the code saw real data

    text = cassette.read_text()
    assert "real-secret-token-value" not in text and "s3cr3t" not in text
    leaks = list(vcr_support.scan_text(text, vcr_support.read_list(originals)))
    assert leaks == []

    fake_service.__exit__(None, None, None)  # the service is gone: replay only
    with vcr.VCR(record_mode="none", **config).use_cassette(str(cassette)):
        replayed = fetch(fake_service.url + "/api/v1/users", token="other")
    assert replayed[0]["name"].startswith("Person-")
    assert replayed[0]["name"] == replayed[0]["sortable_name"]


def test_template_scan_fails_on_unlisted_field(tmp_path, fake_service):
    fake_service.routes["/x"] = (200, [{"name": "Anna Svensson", "login_id": "annasv"},
                                        {"nickname": "Svensson"}])
    originals = tmp_path / "originals.txt"
    config = Pseudonymizer(b"k", originals).vcr_config()
    cassette = tmp_path / "c.yaml"
    with vcr.VCR(record_mode="once", **config).use_cassette(str(cassette)):
        fetch(fake_service.url + "/x")
    # "Svensson" alone in an unlisted field is not replaced (only full names
    # are), but the originals scan catches the surname part.
    kinds = {kind for _, kind, _ in vcr_support.scan_text(
        cassette.read_text(), vcr_support.read_list(originals))}
    assert "original" in kinds


def test_gzip_bodies_are_scrubbed_too(tmp_path, fake_service, roster):
    fake_service.routes["/gz"] = (200, roster, "gzip")
    originals = tmp_path / "originals.txt"
    config = Pseudonymizer(b"k", originals).vcr_config()
    cassette = tmp_path / "c.yaml"
    with vcr.VCR(record_mode="once", **config).use_cassette(str(cassette)):
        fetch(fake_service.url + "/gz")
    text = cassette.read_text()
    assert "!!binary" not in text  # stored decoded, so it was scrubbed and is reviewable
    assert list(vcr_support.scan_text(text, vcr_support.read_list(originals))) == []
