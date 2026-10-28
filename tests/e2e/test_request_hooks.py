"""The request hooks read the real request of a real page."""

from __future__ import annotations

from pathlib import Path

from tests.e2e.project import request, scaffold, write

PAGE = (
    "---\n"
    "from nexy import useHeaders, useIsActive, useParams, useUrl\n\n"
    "slug: prop[str]\n"
    "---\n"
    '<p id="out">{{ useParams().slug }}|{{ useUrl().path }}|'
    "{{ useIsActive('/post') }}|{{ useIsActive('/about') }}|"
    "{{ useIsActive('/post/hello', exact=True) }}|{{ useHeaders()['x-demo'] }}</p>\n"
)


def test_a_page_reads_its_parameters_url_headers_and_active_links(tmp_path: Path):
    scaffold(tmp_path, "web-fbr", "none")
    write(tmp_path, "src/routes/post/[slug].nexy", PAGE)
    _, _, body = request(tmp_path, ("/post/hello", {"x-demo": "yes"}))[0]
    assert "hello|/post/hello|True|False|True|yes" in body
