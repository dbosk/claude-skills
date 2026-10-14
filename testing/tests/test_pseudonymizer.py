"""The pseudonymizer replaces identities consistently and remembers originals."""

import json
import stat

import vcr_support
from vcr_support import Pseudonymizer


def everything_text(obj):
    return json.dumps(obj, ensure_ascii=False)


def test_identity_fields_are_replaced(roster):
    scrubbed = Pseudonymizer(b"k").scrub_json(roster)
    text = everything_text(scrubbed)
    for original in ("Anna", "Svensson", "Lindqvist", "uni.example.se", "annasv", "erikl"):
        assert original not in text
    assert scrubbed[0]["avatar_url"] == vcr_support.URL_PLACEHOLDER
    assert scrubbed[0]["id"] == 101  # plain ids are kept: replay matching needs them


def test_same_person_gets_same_pseudonym_in_every_form(roster):
    p = Pseudonymizer(b"k")
    first = p.scrub_json(roster)[0]
    assert first["name"] == first["sortable_name"]  # "Svensson, Anna" == "Anna Svensson"
    later = p.scrub_json({"grader": {"display_name": "Anna Svensson"}})
    assert later["grader"]["display_name"] == first["name"]


def test_pseudonyms_depend_on_the_key(roster):
    a = Pseudonymizer(b"one").scrub_json(roster)[0]["name"]
    b = Pseudonymizer(b"two").scrub_json(roster)[0]["name"]
    assert a != b and a.startswith("Person-") and b.startswith("Person-")


def test_free_text_is_redacted_wholesale(submissions):
    scrubbed = Pseudonymizer(b"k").scrub_json(submissions)
    assert scrubbed[0]["body"] == vcr_support.FREE_TEXT_PLACEHOLDER


def test_known_names_are_replaced_in_unlisted_fields(roster):
    p = Pseudonymizer(b"k")
    p.scrub_json(roster)  # learns the roster
    later = p.scrub_json({"title": "Feedback for Anna Svensson",
                          "url": "https://lms.example/users/annasv/files"})
    assert "Anna" not in later["title"] and "annasv" not in later["url"]


def test_personnummer_and_emails_in_free_strings():
    p = Pseudonymizer(b"k")
    out = p.scrub_text("ID 20990315-1018, mail someone@uni.example.se, ts 1700000000")
    assert "20990315-1018" not in out and "uni.example.se" not in out
    assert "1700000000" in out  # an epoch timestamp is not a personnummer


def test_originals_are_logged_privately(tmp_path, roster):
    log = tmp_path / "originals.txt"
    Pseudonymizer(b"k", log).scrub_json(roster)
    logged = log.read_text().splitlines()
    assert {"Anna Svensson", "Svensson", "anna.svensson@uni.example.se", "annasv"} <= set(logged)
    assert stat.S_IMODE(log.stat().st_mode) == 0o600


def test_body_scrubbing_keeps_non_json_and_binary():
    p = Pseudonymizer(b"k")
    assert b"someone@uni.example.se" not in p.scrub_body(b"<p>someone@uni.example.se</p>")
    assert p.scrub_body(b"\xff\xfe\x00binary") == b"\xff\xfe\x00binary"


def test_opt_in_id_keys_keep_type_and_rewrite_urls():
    p = Pseudonymizer(b"k", id_keys={"id"})
    out = p.scrub_json([{"id": 2894642, "url": "https://api.example/users/2894642"},
                        {"id": 7, "title": "Lab 7"}])
    new_id = out[0]["id"]
    assert isinstance(new_id, int) and new_id != 2894642 and len(str(new_id)) == 7
    assert out[0]["url"] == f"https://api.example/users/{new_id}"
    assert out[1]["title"] == "Lab 7"  # short ids are not replaced inside text
    assert Pseudonymizer(b"k").scrub_json({"id": 2894642}) == {"id": 2894642}  # off by default


def test_only_person_shaped_names_are_pseudonymized():
    p = Pseudonymizer(b"k")
    out = p.scrub_json({
        "course": {"id": 1, "name": "KTH Programming Lab", "description": "Labs"},
        "teachers": [{"id": 5, "name": "Anna Svensson"}],  # parent key says person
        "user": {"name": "Erik Lindqvist", "login_id": "erikl"},
        "owner": {"login": "kth-org", "type": "Organization"},
    })
    assert out["course"]["name"] == "KTH Programming Lab"  # not a person
    assert out["teachers"][0]["name"].startswith("Person-")
    assert out["user"]["name"].startswith("Person-")
    assert out["owner"]["login"] == "kth-org"  # an organization is not a person
    assert "kth" not in {v.lower() for v in p._recorded}  # course words never logged


def test_keep_text_records_synthetic_prose_verbatim():
    p = Pseudonymizer(b"k")
    p.keep_text = {"body"}
    assert p.scrub_json({"body": "Synthetic page text"})["body"] == "Synthetic page text"
    p.keep_text = set()
    assert p.scrub_json({"body": "Synthetic page text"})["body"] == vcr_support.FREE_TEXT_PLACEHOLDER


def test_json_inside_a_string_is_scrubbed():
    p = Pseudonymizer(b"k")
    inner = json.dumps({"user": {"name": "Anna Svensson", "email": "anna@uni.example.se"}})
    out = p.scrub_json({"payload": inner})
    assert "Anna" not in out["payload"] and "uni.example.se" not in out["payload"]
    assert json.loads(out["payload"])["user"]["name"].startswith("Person-")


def test_url_encoded_email_in_a_request_is_scrubbed():
    class Request:  # the two attributes vcrpy's hook touches
        uri = "https://lms.example/api/v1/users?search_term=anna.svensson%40uni.example.se&per_page=10"
        body = None
    p = Pseudonymizer(b"k")
    uri = p.before_record_request(Request()).uri
    assert "anna.svensson" not in uri and "uni.example.se" not in uri and "per_page=10" in uri
    plain = Request()
    plain.uri = "https://lms.example/api/v1/courses?per_page=10&include%5B%5D=term"
    assert p.before_record_request(plain).uri == plain.uri  # untouched when clean


def test_large_rosters_scrub_in_linear_time():
    import time
    roster = [{"name": f"Förnamn{i} Efternamn{i}", "email": f"student{i}@uni.example.se",
               "login_id": f"stud{i}"} for i in range(300)]
    p = Pseudonymizer(b"k")
    start = time.perf_counter()
    p.scrub_json(roster)
    p.scrub_json([{"title": f"Feedback {i}"} for i in range(500)])
    assert time.perf_counter() - start < 3


def test_placeholder_domains_match_whole_domains():
    p = Pseudonymizer(b"k")
    assert p.email("anna@notexample.com") != "anna@notexample.com"
    assert p.email("someone@example.com") == "someone@example.com"
    assert p.email("someone@lms.test") == "someone@lms.test"


def test_originals_file_refuses_symlinks_and_shared_files(tmp_path):
    import os
    import pytest
    target = tmp_path / "elsewhere.txt"
    link = tmp_path / "originals.txt"
    link.symlink_to(target)
    with pytest.raises(OSError):
        Pseudonymizer(b"k", link).name("Anna Svensson")
    assert not target.exists()
    shared = tmp_path / "shared.txt"
    shared.write_text("")
    shared.chmod(0o644)
    with pytest.raises(PermissionError):
        Pseudonymizer(b"k", shared).name("Anna Svensson")


def test_default_originals_path_is_in_a_private_directory(tmp_path):
    import os
    path = vcr_support.default_originals_path(tmp_path)
    assert stat.S_IMODE(path.parent.stat().st_mode) == 0o700
    assert path.parent.stat().st_uid == os.getuid()


def test_ladok_record_is_scrubbed_by_key():
    # LADOK's Swedish keys: names, personnummer, contact data, the staff
    # member in SenastAndradAv, the decision maker (Beslutsfattare) and
    # free-text notes (Anteckning).
    record = {"Student": {
        "Uid": "6f1c2d3e-0a1b-11ee-8c2d-0242ac120002",
        "Fornamn": "Anna", "Efternamn": "Svensson",
        "Personnummer": "209903151018", "Epostadress": "anna.svensson@uni.example.se",
        "Anvandarnamn": "annasv", "Utdelningsadress": "Storgatan 1",
        "Postnummer": "11122", "Postort": "Ankeborg", "Telefonnummer": "0701112233"},
        "SenastAndradAv": "larare@uni.example.se",
        "Beslutsfattare": "Bertil Beslutsson",
        "Anteckning": "Anna missade tentan på grund av sjukdom."}
    p = Pseudonymizer(b"k")
    out = p.scrub_json(record)
    text = everything_text(out)
    for original in ("Anna", "Svensson", "209903151018", "annasv", "Storgatan",
                     "11122", "Ankeborg", "0701112233", "larare", "sjukdom",
                     "Bertil", "Beslutsson"):
        assert original not in text
    assert out["Student"]["Postort"] == vcr_support.CONTACT_PLACEHOLDER
    assert out["Anteckning"] == vcr_support.FREE_TEXT_PLACEHOLDER


def test_personnummer_field_is_replaced_even_when_the_checksum_fails():
    out = Pseudonymizer(b"k").scrub_json({"Personnummer": "199001011234"})
    assert "199001011234" not in everything_text(out)


def test_uuid_identities_keep_their_shape():
    import re
    uuid = "6f1c2d3e-0a1b-11ee-8c2d-0242ac120002"
    p = Pseudonymizer(b"k", id_keys={"course_uid"})
    out = p.scrub_json({"Uid": uuid, "Fornamn": "Anna", "course_uid": uuid.upper()})
    shape = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)
    for key in ("Uid", "course_uid"):
        assert shape.fullmatch(out[key]) and out[key].lower() != uuid


def test_saml_responses_and_form_secrets_are_redacted():
    blob = "PHNhbWxwOlJlc3BvbnNlIHhtbG5zOnNhbWxwPSJ1cm46b2FzaXM" * 3
    html = f'<form><input type="hidden" name="SAMLResponse" value="{blob}"/></form>'
    assert blob not in Pseudonymizer(b"k").scrub_body(html)
    form = f"SAMLResponse={blob}&RelayState=abc"
    assert blob not in Pseudonymizer(b"k").scrub_body(form.encode()).decode()
