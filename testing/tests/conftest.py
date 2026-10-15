import gzip
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "assets"))


class FakeService:
    """A real HTTP server on localhost whose responses the test controls."""

    def __init__(self):
        self.routes = {}
        service = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                status, payload, *compress = service.routes.get(
                    self.path.split("?")[0], (404, {}))
                body = json.dumps(payload).encode()
                self.send_response(status)
                if compress and compress[0]:
                    body = gzip.compress(body)
                    self.send_header("Content-Encoding", "gzip")
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Set-Cookie", "session=s3cr3t-session-value")
                self.end_headers()
                self.wfile.write(body)

            def do_PUT(self):
                self.rfile.read(int(self.headers.get("Content-Length") or 0))
                self.do_GET()

            do_POST = do_DELETE = do_PUT

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_port}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()


@pytest.fixture
def fake_service():
    with FakeService() as service:
        yield service


# Synthetic people that the scrubber and the scan must still catch: the
# personnummer passes the checksum but is dated 2099, and uni.example.se is
# not a reserved domain, so neither belongs to anyone yet both look real.
ROSTER = [
    {"id": 101, "name": "Anna Svensson", "sortable_name": "Svensson, Anna",
     "email": "anna.svensson@uni.example.se", "login_id": "annasv",
     "avatar_url": "https://cdn.example.net/avatars/annasv.png"},
    {"id": 102, "name": "Erik Lindqvist", "sortable_name": "Lindqvist, Erik",
     "email": "erikl@uni.example.se", "login_id": "erikl", "avatar_url": None},
]
SUBMISSIONS = [
    {"id": 7, "user_id": 101, "score": 4.5, "grader": {"name": "Anna Svensson"},
     "body": "Hej! Jag heter Anna Svensson, personnummer 20990315-1018.",
     "preview_url": "https://canvas.example/courses/1/users/annasv/preview"},
]


@pytest.fixture
def roster():
    return json.loads(json.dumps(ROSTER))


@pytest.fixture
def submissions():
    return json.loads(json.dumps(SUBMISSIONS))
