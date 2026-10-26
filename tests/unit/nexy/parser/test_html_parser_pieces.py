"""Reading a start tag: its real spelling, its attributes, and whether it closes itself."""

from __future__ import annotations

import pytest

from nexy.modules.compiler.parser.html_parser import (
    NexyHTMLParser,
    _read_start_tag,
    _tag_attributes,
)


class TestReadStartTag:
    def test_a_component_keeps_its_capitals(self):
        name, _, _ = _read_start_tag("usercard", [], "<UserCard />")
        assert name == "UserCard"

    def test_the_attributes_keep_their_spelling(self):
        _, attributes, _ = _read_start_tag("a", [], "<a data-Id=\"1\" href='/x' target=_blank>")
        assert attributes == {"data-Id": "1", "href": "/x", "target": "_blank"}

    def test_an_attribute_without_a_value_is_empty(self):
        assert _tag_attributes("<input disabled>", 6) == {"disabled": ""}

    def test_a_slash_before_the_end_is_self_closing(self):
        assert _read_start_tag("br", [], "<br />")[2] is True

    def test_a_plain_tag_is_not_self_closing(self):
        assert _read_start_tag("p", [], "<p>")[2] is False

    def test_without_the_raw_text_the_parser_result_is_used(self):
        assert _read_start_tag("p", [("class", "a"), ("hidden", None)], None) == (
            "p",
            {"class": "a", "hidden": ""},
            False,
        )


class TestTree:
    @staticmethod
    def _parse(html: str):
        return NexyHTMLParser().parse(html)

    def test_children_nest_under_their_parent(self):
        (root,) = self._parse("<div><p>x</p></div>")
        assert root.tag_name == "div" and root.children[0].tag_name == "p"

    @pytest.mark.parametrize("tag", ["br", "img", "input", "hr", "meta"])
    def test_a_void_element_has_no_children(self, tag):
        nodes = self._parse(f"<{tag}>text")
        assert nodes[0].is_self_closing and len(nodes) == 2

    def test_a_component_named_like_a_void_element_can_have_children(self):
        (node,) = self._parse("<Input>x</Input>")
        assert not node.is_self_closing and node.children

    def test_an_end_tag_closes_what_it_matches_case_insensitively(self):
        (node,) = self._parse("<Card>x</card>")
        assert node.children[0].content == "x"

    def test_the_doctype_is_kept(self):
        assert self._parse("<!DOCTYPE html><p>x</p>")[0].content == "<!DOCTYPE html>"

    def test_parsing_twice_starts_clean(self):
        parser = NexyHTMLParser()
        parser.parse("<div>")
        assert len(parser.parse("<p>x</p>")) == 1
