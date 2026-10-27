"""Every dev log line starts the same way: a label, then », then the message."""

from __future__ import annotations

from rich.text import Text

from nexy.helpers.common.log_line import tag, tagged


def _plain(markup: str) -> str:
    return Text.from_markup(markup).plain


def test_a_tag_is_the_label_and_an_arrow():
    assert _plain(tag("vite")) == "vite »"


def test_a_tag_takes_the_colour_asked_for():
    assert tag("GET", "green").startswith("[green]GET[/green]")


def test_a_line_is_the_tag_and_the_message():
    assert _plain(tagged("nexy", "update src/a.py")) == "nexy » update src/a.py"


def test_a_line_does_not_start_with_spaces():
    assert not _plain(tagged("nexy", "x")).startswith(" ")
