"""The document of a client-routed React route: rendered by Node, completed by Python."""

import json
import re
from pathlib import Path

import httpx
import pytest

from nexy.modules.runtime import csr_document
from nexy.modules.runtime.csr_document import render_document

DOC = (
    '<!DOCTYPE html><html lang="fr"><head><title>T</title></head>'
    "<body><main>Hi</main></body></html>"
)


def _render(**overrides):
    args = {
        "page_file": "/src/routes/index.tsx",
        "page_key": "pagekey",
        "layouts": ["/src/routes/layout.tsx"],
        "layout_keys": ["layoutkey"],
        "props": {},
        "static_stem": "/src/routes/index",
        "dynamic": False,
    }
    args.update(overrides)
    return render_document(**args)


def _boot(html: str) -> dict:
    match = re.search(
        r'<script id="__nexy_page" type="application/json">(.*?)</script>', html, re.S
    )
    assert match, html
    return json.loads(match.group(1))


@pytest.fixture(autouse=True)
def _project(tmp_path, monkeypatch, nexy_project):
    nexy_project("")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(csr_document, "Vite", lambda: "<script src='/assets/app.js'></script>")
    monkeypatch.setattr(csr_document, "vite_proxy_port", lambda: None)


def _production(tmp_path: Path, suffix: str, html: str = DOC) -> None:
    (tmp_path / "__nexy__").mkdir(exist_ok=True)
    (tmp_path / "__nexy__" / "nexy.prod").write_text("", encoding="utf-8")
    target = tmp_path / "__nexy__" / "client" / "static" / "src" / "routes" / f"index.{suffix}.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")


class TestProduction:
    def test_serves_the_prerendered_document(self, tmp_path):
        _production(tmp_path, "document")
        html = _render()
        assert html.startswith('<!DOCTYPE html><html lang="fr">')
        assert "<main>Hi</main>" in html
        assert _boot(html)["mode"] == "document"

    def test_assets_go_in_the_head_and_the_page_description_before_body_end(self, tmp_path):
        _production(tmp_path, "document")
        html = _render()
        assert html.index("/assets/app.js") < html.index("</head>")
        assert html.index("__nexy_page") < html.index("</body>")

    def test_dynamic_routes_serve_the_shell(self, tmp_path):
        _production(tmp_path, "shell", DOC.replace("Hi", ""))
        html = _render(dynamic=True)
        assert _boot(html)["mode"] == "shell"

    def test_missing_file_falls_back_to_a_client_rendered_document(self, tmp_path):
        (tmp_path / "__nexy__").mkdir()
        (tmp_path / "__nexy__" / "nexy.prod").write_text("", encoding="utf-8")
        html = _render()
        assert html.lstrip().startswith("<!DOCTYPE html>")
        assert _boot(html)["mode"] == "client"

    def test_description_carries_the_page_layouts_and_props(self, tmp_path):
        _production(tmp_path, "document")
        boot = _boot(_render(props={"slug": "x"}))
        assert boot["page"] == "pagekey" and boot["layouts"] == ["layoutkey"]
        assert boot["props"] == {"slug": "x"}


class TestDevelopment:
    def test_asks_the_vite_dev_server(self, monkeypatch):
        calls = {}

        def fake_post(url, **kwargs):
            calls.update(url=url, body=kwargs["json"])
            return httpx.Response(200, text=DOC, request=httpx.Request("POST", url))

        monkeypatch.setattr(csr_document, "vite_proxy_port", lambda: 5173)
        monkeypatch.setattr(csr_document.httpx, "post", fake_post)
        html = _render(props={"slug": "x"})
        assert calls["url"] == "http://127.0.0.1:5173/__nexy__/render"
        assert calls["body"] == {
            "page": "/src/routes/index.tsx",
            "layouts": ["/src/routes/layout.tsx"],
            "props": {"slug": "x"},
        }
        assert _boot(html)["mode"] == "document"

    def test_large_props_travel_in_the_body_not_the_url(self, monkeypatch):
        seen = {}

        def fake_post(url, **kwargs):
            seen.update(url=url, size=len(json.dumps(kwargs["json"])))
            return httpx.Response(200, text=DOC, request=httpx.Request("POST", url))

        monkeypatch.setattr(csr_document, "vite_proxy_port", lambda: 5173)
        monkeypatch.setattr(csr_document.httpx, "post", fake_post)
        _render(props={"blob": "x" * 100_000})
        assert "?" not in seen["url"] and seen["size"] > 100_000

    def test_a_render_error_falls_back_instead_of_breaking_the_request(self, monkeypatch):
        def failing_post(url, **_kwargs):
            return httpx.Response(500, text="Error: boom", request=httpx.Request("POST", url))

        monkeypatch.setattr(csr_document, "vite_proxy_port", lambda: 5173)
        monkeypatch.setattr(csr_document.httpx, "post", failing_post)
        assert _boot(_render())["mode"] == "client"

    def test_vite_not_reachable_falls_back(self, monkeypatch):
        def unreachable(_url, **_kwargs):
            raise httpx.ConnectError("down")

        monkeypatch.setattr(csr_document, "vite_proxy_port", lambda: 5173)
        monkeypatch.setattr(csr_document.httpx, "post", unreachable)
        assert _boot(_render())["mode"] == "client"


class TestSafety:
    def test_props_cannot_close_the_script_tag(self, tmp_path):
        _production(tmp_path, "document")
        html = _render(props={"x": "</script><script>alert(1)</script>"})
        assert "</script><script>alert(1)" not in html
        assert _boot(html)["props"]["x"] == "</script><script>alert(1)</script>"

    def test_a_fragment_response_is_replaced_by_the_fallback_document(self, tmp_path):
        _production(tmp_path, "document", "<div>no html element here</div>")
        assert _boot(_render())["mode"] == "client"
