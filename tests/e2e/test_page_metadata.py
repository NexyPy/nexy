"""A page names its title and head tags; the root layout writes them, escaped."""

from __future__ import annotations

from pathlib import Path

from tests.e2e.project import request, scaffold, write

NO_HEADERS: dict[str, str] = {}

LAYOUT = (
    "---\n"
    "from nexy import useMetadata\n\n"
    "children: prop[NexyElement]\n"
    "---\n"
    "<!DOCTYPE html>\n"
    "<html><head>{{ useMetadata().html() }}</head><body>{{ children }}</body></html>\n"
)
STATIC = '---\nmetadata = {"title": "Blog", "description": "Posts"}\n---\n<h1>Blog</h1>\n'
DYNAMIC = (
    "---\nfrom nexy import setMetadata\n\nslug: prop[str]\n"
    'setMetadata(title=slug.title(), og={"image": "/cover.png"})\n---\n<h1>{{ slug }}</h1>\n'
)
UNSAFE = (
    "---\nfrom nexy import setMetadata\n\nslug: prop[str]\nsetMetadata(title=slug)\n---\n<p>x</p>\n"
)


def _site(tmp_path: Path) -> Path:
    scaffold(tmp_path, "web-fbr", "none")
    write(tmp_path, "src/routes/layout.nexy", LAYOUT)
    write(tmp_path, "src/routes/blog.nexy", STATIC)
    write(tmp_path, "src/routes/post/[slug].nexy", DYNAMIC)
    write(tmp_path, "src/routes/evil/[slug].nexy", UNSAFE)
    write(tmp_path, "src/routes/plain.nexy", "<p>plain</p>\n")
    return tmp_path


def _body(tmp_path: Path, path: str) -> str:
    return request(_site(tmp_path), (path, NO_HEADERS))[0][2]


def test_a_static_metadata_reaches_the_head(tmp_path: Path):
    body = _body(tmp_path, "/blog")
    assert "<title>Blog</title>" in body and 'name="description" content="Posts"' in body


def test_a_dynamic_metadata_reaches_the_head(tmp_path: Path):
    body = _body(tmp_path, "/post/hello")
    assert "<title>Hello</title>" in body and 'property="og:image" content="/cover.png"' in body


def test_a_page_without_metadata_gets_the_title_of_the_site(tmp_path: Path):
    body = _body(tmp_path, "/plain")
    assert "<title>" in body and 'name="description"' not in body


def test_a_title_built_from_the_url_cannot_inject_markup(tmp_path: Path):
    body = _body(tmp_path, "/evil/%3Cimg%20src%3Dx%20onerror%3Dalert(1)%3E")
    head = body.split("</head>")[0]
    assert "<img src=x" not in head and "&lt;img src=x" in head


def test_the_metadata_of_one_request_does_not_reach_the_next(tmp_path: Path):
    first, second = request(_site(tmp_path), ("/blog", NO_HEADERS), ("/plain", NO_HEADERS))
    assert "<title>Blog</title>" in first[2] and "<title>Blog</title>" not in second[2]
