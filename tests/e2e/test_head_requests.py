"""HEAD answers a page and an API route of a real project like GET, without the body (#80)."""

from __future__ import annotations

from pathlib import Path

from tests.e2e.project import request, scaffold, write

NO_HEADERS: dict[str, str] = {}


def _head(tmp_path: Path, path: str) -> tuple[int, dict[str, str], str]:
    scaffold(tmp_path, "web-fbr", "none")
    write(tmp_path, "src/routes/about.nexy", "<h1>About</h1>\n")
    write(tmp_path, "src/routes/api/ping.py", 'async def GET():\n    return {"ok": True}\n')
    return request(tmp_path, (path, NO_HEADERS, "HEAD"))[0]


def test_head_on_a_page_answers_200(tmp_path):
    assert _head(tmp_path, "/about")[0] == 200


def test_head_on_a_page_has_no_body(tmp_path):
    assert _head(tmp_path, "/about")[2] == ""


def test_head_on_an_api_route_answers_200(tmp_path):
    assert _head(tmp_path, "/api/ping")[0] == 200
