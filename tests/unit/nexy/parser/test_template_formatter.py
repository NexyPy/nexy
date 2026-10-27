"""How the attributes of a component tag become the arguments of a Jinja call."""

from __future__ import annotations

import pytest

from nexy.modules.compiler.parser.template import TemplateFormatter, TemplateParser

format_dict = TemplateFormatter.format_dict


@pytest.mark.parametrize(
    ("attrs", "expected"),
    [
        ({}, ""),
        ({"title": "Hello"}, 'title="Hello"'),
        ({"count": "3"}, "count=3"),
        ({"ratio": "1.5"}, "ratio=1.5"),
        ({"open": "true"}, "open=true"),
        ({"x": "None"}, "x=None"),
        ({"name": "{{ user }}"}, "name=(user)"),
        ({"name": "Hi {{ user }}!"}, 'name="Hi " ~ (user) ~ "!"'),
        ({"{{ user }}": ""}, "user=user"),
        ({"{{ ...props }}": ""}, "**props"),
        ({"{{ **extra }}": ""}, "**extra"),
        ({"a": "1", "b": "{{ c }}"}, "a=1, b=(c)"),
    ],
)
def test_an_attribute_becomes_an_argument(attrs, expected):
    assert format_dict(attrs) == expected


def test_a_call_in_the_name_is_not_a_shorthand():
    assert "=" in format_dict({"{{ f(x) }}": ""}) and "**" not in format_dict({"{{ f(x) }}": ""})


def test_two_expressions_in_one_value_are_joined():
    assert format_dict({"v": "{{ a }}{{ b }}"}) == "v=(a) ~ (b)"


class TestPlainTags:
    @staticmethod
    def _render(html: str) -> str:
        return TemplateParser().parse(html)

    def test_attributes_are_kept(self):
        assert self._render('<div class="a" id="b">x</div>') == '<div class="a" id="b">x</div>'

    def test_a_quote_in_a_value_is_escaped(self):
        assert "&quot;" in self._render("<p title='say \"hi\"'>x</p>")

    def test_an_attribute_without_a_value_stays_bare(self):
        assert self._render("<input disabled />") == "<input disabled />"

    def test_a_jinja_expression_in_the_tag_is_kept_as_it_is(self):
        assert "{{ attrs }}" in self._render("<p {{ attrs }}>x</p>")

    def test_a_tag_without_attributes_has_no_stray_space(self):
        assert self._render("<p>x</p>") == "<p>x</p>"

    def test_a_self_closing_tag_stays_self_closing(self):
        assert self._render('<img src="a.png" />') == '<img src="a.png" />'
