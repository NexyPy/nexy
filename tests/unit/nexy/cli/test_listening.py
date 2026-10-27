"""What the server prints once it is ready: where it listens and how long it took."""

from __future__ import annotations

import pytest

from nexy.helpers.common import launcher
from nexy.helpers.server.listening import Endpoint, print_listening


class TestEndpoint:
    def test_protocol_follows_the_certificates(self):
        plain = Endpoint("127.0.0.1", 3000)
        secure = Endpoint("127.0.0.1", 3000, "key.pem", "cert.pem")
        assert (plain.protocol, secure.protocol) == ("http", "https")

    def test_a_key_without_a_certificate_stays_http(self):
        assert Endpoint("h", 1, ssl_keyfile="key.pem").protocol == "http"

    def test_the_url_names_the_host_and_port(self):
        assert Endpoint("h", 8000).url("example.test") == "http://example.test:8000"


@pytest.fixture
def entries(monkeypatch) -> list[str]:
    seen: list[str] = []
    monkeypatch.setattr(launcher, "entry", lambda _label, value: seen.append(value))
    return seen


class TestPrintListening:
    def test_the_network_address_is_shown_when_listening_on_all_interfaces(self, entries):
        print_listening("dev", "1", Endpoint("0.0.0.0", 3000), 1.5, lambda: "192.168.1.2")  # noqa: S104
        assert "http://localhost:3000" in entries and "http://192.168.1.2:3000" in entries

    def test_loopback_shows_no_network_line(self, entries):
        print_listening("dev", "1", Endpoint("127.0.0.1", 3000), 0.2, lambda: "192.168.1.2")
        assert entries == ["http://localhost:3000", "0.20s"]

    def test_a_machine_without_a_network_shows_none_either(self, entries):
        print_listening("start", "1", Endpoint("0.0.0.0", 3000), 0.1, lambda: "127.0.0.1")  # noqa: S104
        assert entries == ["http://localhost:3000", "0.10s"]

    def test_the_command_is_in_the_header(self, capsys):
        print_listening("start", "9.9", Endpoint("127.0.0.1", 3000), 0.1, lambda: "127.0.0.1")
        out = capsys.readouterr().out
        assert "start" in out and "9.9" in out and "Ctrl+C" in out

    def test_a_secure_endpoint_is_announced_as_https(self, entries):
        endpoint = Endpoint("127.0.0.1", 3443, "k.pem", "c.pem")
        print_listening("dev", "1", endpoint, 0.1, lambda: "127.0.0.1")
        assert entries[0] == "https://localhost:3443"
