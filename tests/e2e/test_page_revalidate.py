"""A `.nexy` page with `revalidate` is cached by the router, as the ISR docs say."""

from __future__ import annotations

from pathlib import Path

from tests.e2e.project import request, scaffold, write

PAGE = "---\nrevalidate = 60\n---\n<p>cached page</p>\n"


def test_a_page_with_revalidate_answers_with_cache_headers(tmp_path: Path):
    scaffold(tmp_path)
    write(tmp_path, "src/routes/cached.nexy", PAGE)
    status, headers, _ = request(tmp_path, ("/cached", {}))[0]
    assert status == 200 and "s-maxage=60" in headers.get("cache-control", "")


def test_a_page_without_revalidate_is_not_cached(tmp_path: Path):
    scaffold(tmp_path)
    write(tmp_path, "src/routes/plain.nexy", "<p>plain page</p>\n")
    _, headers, _ = request(tmp_path, ("/plain", {}))[0]
    assert "s-maxage" not in headers.get("cache-control", "")


DYNAMIC = "---\nslug: prop[str]\nrevalidate = 60\n---\n<p>post {{ slug }}</p>\n"


def test_a_dynamic_page_with_revalidate_shows_its_own_parameter(tmp_path: Path):
    scaffold(tmp_path)
    write(tmp_path, "src/routes/post/[slug].nexy", DYNAMIC)
    first, second = request(tmp_path, ("/post/alpha", {}), ("/post/beta", {}))
    assert ("post alpha" in first[2], "post beta" in second[2]) == (True, True)


def test_two_pages_of_one_dynamic_route_are_cached_apart(tmp_path: Path):
    scaffold(tmp_path)
    write(tmp_path, "src/routes/post/[slug].nexy", DYNAMIC)
    pages = request(tmp_path, ("/post/alpha", {}), ("/post/beta", {}), ("/post/alpha", {}))
    assert ("post beta" in pages[1][2], "post alpha" in pages[2][2]) == (True, True)
