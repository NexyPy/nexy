"""`nx add <url>` downloads code into the project: constrain and verify it."""

import hashlib
import http.server
import threading
from collections.abc import Iterator

import pytest

from nexy.modules.cli.commands.add import fetch_remote_component

BODY = b"export default function Button() { return null }\n"


class _Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path == "/big":
            payload = b"x" * 1_100_000
        elif self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "ftp://example.com/x.tsx")
            self.end_headers()
            return
        else:
            payload = BODY
        self.send_response(200)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *_args):
        pass


@pytest.fixture
def base_url() -> Iterator[str]:
    server = http.server.HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


class TestUrlPolicy:
    @pytest.mark.parametrize("url", ["http://example.com/x.tsx", "file:///etc/passwd", "ftp://a/b"])
    def test_non_https_remote_is_rejected(self, url):
        assert fetch_remote_component(url) is None


class TestFetch:
    def test_loopback_http_is_allowed(self, base_url):
        assert fetch_remote_component(base_url + "/button.tsx") == BODY.decode()

    def test_matching_digest_is_accepted(self, base_url):
        digest = hashlib.sha256(BODY).hexdigest()
        assert fetch_remote_component(base_url + "/b.tsx", digest) == BODY.decode()

    def test_wrong_digest_is_rejected(self, base_url):
        assert fetch_remote_component(base_url + "/b.tsx", "0" * 64) is None

    def test_oversized_component_is_rejected(self, base_url):
        assert fetch_remote_component(base_url + "/big") is None

    def test_redirect_out_of_policy_is_rejected(self, base_url):
        assert fetch_remote_component(base_url + "/redirect") is None
