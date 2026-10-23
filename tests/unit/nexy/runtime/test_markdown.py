from nexy.modules.runtime.markdown import (
    _slugify,
    build_toc_html,
    inject_heading_ids,
    render_markdown,
)


def test_render_markdown_converts_heading() -> None:
    assert "<h1>" in render_markdown("# Title")


def test_slugify_strips_punctuation_and_spaces() -> None:
    assert _slugify("Hello, World!") == "hello-world"


def test_inject_heading_ids_adds_slug() -> None:
    assert 'id="hello-world"' in inject_heading_ids("<h2>Hello World</h2>")


def test_inject_heading_ids_keeps_existing_id() -> None:
    html = '<h2 id="custom">Hi</h2>'
    assert inject_heading_ids(html) == html


def test_inject_heading_ids_ignores_unclosed_heading() -> None:
    assert inject_heading_ids("<h2>dangling") == "<h2>dangling"


def test_inject_heading_ids_ignores_empty_heading() -> None:
    assert inject_heading_ids("<h2></h2>") == "<h2></h2>"


def test_build_toc_returns_empty_without_headings() -> None:
    assert build_toc_html("<p>text</p>") == ""


def test_build_toc_nests_subsections() -> None:
    assert build_toc_html("<h2>One</h2><h3>Two</h3>").count("<ul>") == 2


def test_build_toc_filters_depth_range() -> None:
    toc = build_toc_html("<h1>Skip</h1><h2>Keep</h2>", "2-3")
    assert "Keep" in toc and "Skip" not in toc


def test_build_toc_falls_back_on_invalid_range() -> None:
    assert "Keep" in build_toc_html("<h2>Keep</h2>", "bogus")


def test_build_toc_escapes_heading_text() -> None:
    assert "<script>" not in build_toc_html("<h2>A <script>alert(1)</script></h2>")


def test_build_toc_skips_unclosed_heading() -> None:
    assert build_toc_html("<h2>dangling") == ""


def test_build_toc_skips_empty_heading() -> None:
    toc = build_toc_html("<h2></h2><h2>Real</h2>")
    assert "Real" in toc and toc.count("<li>") == 1


def test_build_toc_closes_descending_levels() -> None:
    toc = build_toc_html("<h3>Deep</h3><h2>Shallow</h2>")
    assert "Shallow" in toc and "Deep" in toc
