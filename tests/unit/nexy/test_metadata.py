"""A page names its title and its head tags; the layout writes them, escaped, once."""

from __future__ import annotations

import pytest
from starlette.requests import Request

import nexy
from nexy.core.config import Config
from nexy.metadata import Metadata, setMetadata, useMetadata
from nexy.modules.routers.context import current_request


@pytest.fixture
def in_request():
    scope = {"type": "http", "method": "GET", "path": "/", "headers": [], "query_string": b""}
    token = current_request.set(Request(scope))
    yield
    current_request.reset(token)


class TestHtml:
    def test_a_title_becomes_the_title_tag(self):
        assert "<title>Blog</title>" in Metadata(title="Blog").html()

    def test_a_template_wraps_the_title(self):
        page = Metadata(title="Blog", title_template="%s | Nexy")
        assert "<title>Blog | Nexy</title>" in page.html()

    def test_without_a_title_the_site_title_is_used(self, monkeypatch):
        monkeypatch.setattr(Config, "useTitle", "My site")
        assert "<title>My site</title>" in Metadata().html()

    def test_a_description_a_canonical_and_robots(self):
        html = Metadata(description="Posts", canonical="/blog", robots="noindex").html()
        assert 'name="description" content="Posts"' in html
        assert 'rel="canonical" href="/blog"' in html
        assert 'name="robots" content="noindex"' in html

    def test_open_graph_keys_get_their_prefix(self):
        html = Metadata(og={"title": "Blog", "image": "/a.png"}).html()
        assert 'property="og:title" content="Blog"' in html
        assert 'property="og:image" content="/a.png"' in html

    def test_twitter_keys_get_their_prefix(self):
        html = Metadata(twitter={"card": "summary"}).html()
        assert 'name="twitter:card" content="summary"' in html

    def test_an_icon_and_extra_tags(self):
        html = Metadata(icon="/f.svg", extra=[{"name": "theme-color", "content": "#fff"}]).html()
        assert 'rel="icon" href="/f.svg"' in html
        assert 'name="theme-color" content="#fff"' in html

    def test_nothing_unset_is_written(self):
        html = Metadata(title="x").html()
        assert "description" not in html and "canonical" not in html and "og:" not in html


class TestEscaping:
    def test_a_title_cannot_close_the_tag_and_inject_a_script(self):
        html = Metadata(title="</title><script>alert(1)</script>").html()
        assert "<script>" not in html and "&lt;/title&gt;" in html

    def test_an_attribute_cannot_break_out_of_its_quotes(self):
        html = Metadata(description='x" onload="alert(1)').html()
        assert 'onload="alert' not in html and "&quot;" in html

    def test_open_graph_values_are_escaped_too(self):
        assert "<img" not in Metadata(og={"title": "<img src=x>"}).html()


@pytest.mark.usefixtures("in_request")
class TestSetMetadata:
    def test_it_sets_the_fields_of_the_request(self):
        setMetadata(title="Blog", description="Posts")
        assert (useMetadata().title, useMetadata().description) == ("Blog", "Posts")

    def test_a_later_call_wins_and_keeps_the_rest(self):
        setMetadata(title="A", description="d")
        setMetadata(title="B")
        assert (useMetadata().title, useMetadata().description) == ("B", "d")

    def test_open_graph_keys_are_merged(self):
        setMetadata(og={"title": "A"})
        setMetadata(og={"image": "/i.png"})
        assert useMetadata().og == {"title": "A", "image": "/i.png"}

    def test_a_field_that_does_not_exist_is_refused(self):
        with pytest.raises(TypeError, match="titel"):
            setMetadata(titel="typo")


class TestOutsideARequest:
    def test_it_refuses_to_run_outside_a_request(self):
        with pytest.raises(RuntimeError, match="request"):
            setMetadata(title="x")

    def test_nexy_exports_both(self):
        assert nexy.setMetadata is setMetadata and nexy.useMetadata is useMetadata
