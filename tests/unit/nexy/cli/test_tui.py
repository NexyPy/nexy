"""The prompts of the CLI, driven with real key presses on a scripted terminal."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from nexy.modules.cli import tui
from nexy.modules.cli.tui import render
from nexy.modules.cli.tui.theme import ASCII, UNICODE, glyphs_for

UP, DOWN, LEFT, ENTER, ESC, CTRL_C = "\x1b[A", "\x1b[B", "\x1b[D", "\r", "\x1b", "\x03"

CHOICES = [
    tui.Option("a", "Alpha", "the first"),
    tui.Option("b", "Beta", "the second"),
    tui.Option("c", "Gamma"),
]


@pytest.fixture
def keys() -> Iterator:
    """Type on the scripted terminal: ``keys("jj\\r")``."""
    with create_pipe_input() as pipe:
        saved = tui.terminal.input, tui.terminal.output
        tui.terminal.input, tui.terminal.output = pipe, DummyOutput()
        tui.transcript.clear()
        yield pipe.send_text
        tui.terminal.input, tui.terminal.output = saved


class TestSelect:
    def test_enter_picks_the_first_option(self, keys):
        keys(ENTER)
        assert tui.select("Pick", CHOICES) == "a"

    def test_down_then_enter_picks_the_next(self, keys):
        keys(DOWN + ENTER)
        assert tui.select("Pick", CHOICES) == "b"

    def test_up_from_the_first_wraps_to_the_last(self, keys):
        keys(UP + ENTER)
        assert tui.select("Pick", CHOICES) == "c"

    def test_j_and_k_move_like_the_arrows(self, keys):
        keys("jjk" + ENTER)
        assert tui.select("Pick", CHOICES) == "b"

    def test_a_digit_jumps_to_that_option(self, keys):
        keys("3" + ENTER)
        assert tui.select("Pick", CHOICES) == "c"

    def test_the_default_is_where_the_cursor_starts(self, keys):
        keys(ENTER)
        assert tui.select("Pick", CHOICES, default="b") == "b"

    def test_left_goes_back(self, keys):
        keys(LEFT)
        assert tui.select("Pick", CHOICES) is tui.BACK

    def test_escape_goes_back(self, keys):
        keys(ESC)
        assert tui.select("Pick", CHOICES) is tui.BACK

    def test_back_is_ignored_when_the_prompt_cannot_go_back(self, keys):
        keys(LEFT + ENTER)
        assert tui.select("Pick", CHOICES, back=False) == "a"

    def test_ctrl_c_cancels(self, keys):
        keys(CTRL_C)
        with pytest.raises(KeyboardInterrupt):
            tui.select("Pick", CHOICES)

    def test_an_answered_prompt_stays_in_the_transcript(self, keys):
        keys(ENTER)
        tui.select("Pick", CHOICES)
        assert tui.transcript._heights == [3]

    def test_going_back_leaves_nothing_in_the_transcript(self, keys):
        keys(LEFT)
        tui.select("Pick", CHOICES)
        assert tui.transcript._heights == []


class TestConfirm:
    def test_yes_is_the_default(self, keys):
        keys(ENTER)
        assert tui.confirm("Sure?") is True

    def test_down_answers_no(self, keys):
        keys(DOWN + ENTER)
        assert tui.confirm("Sure?") is False

    def test_the_default_can_be_no(self, keys):
        keys(ENTER)
        assert tui.confirm("Sure?", default=False) is False

    def test_left_goes_back(self, keys):
        keys(LEFT)
        assert tui.confirm("Sure?") is tui.BACK


class TestText:
    def test_what_is_typed_is_the_answer(self, keys):
        keys("demo" + ENTER)
        assert tui.text("Name") == "demo"

    def test_the_default_is_prefilled(self, keys):
        keys(ENTER)
        assert tui.text("Name", default="shop") == "shop"

    def test_typing_after_the_default_extends_it(self, keys):
        keys("-2" + ENTER)
        assert tui.text("Name", default="shop") == "shop-2"

    def test_an_invalid_answer_is_not_accepted_until_it_is_fixed(self, keys):
        def at_least_two(value: str) -> bool | str:
            return True if len(value) >= 2 else "too short"

        keys("a" + ENTER + "b" + ENTER)
        assert tui.text("Name", validate=at_least_two) == "ab"

    def test_escape_goes_back_when_allowed(self, keys):
        keys(ESC)
        assert tui.text("Name", back=True) is tui.BACK

    def test_ctrl_c_cancels(self, keys):
        keys(CTRL_C)
        with pytest.raises(KeyboardInterrupt):
            tui.text("Name")


class TestTranscript:
    def test_erasing_with_nothing_shown_is_harmless(self):
        tui.transcript.erase_last()

    def test_erasing_removes_the_last_block(self, keys):
        keys(ENTER + ENTER)
        tui.select("One", CHOICES)
        tui.select("Two", CHOICES)
        tui.transcript.erase_last()
        assert len(tui.transcript._heights) == 1


class TestRender:
    @staticmethod
    def _plain(fragments) -> str:
        return "".join(text for _style, text in fragments)

    def test_the_current_option_has_the_selected_style(self):
        fragments = render.options(CHOICES, 1, UNICODE)
        styles = {text.strip(): style for style, text in fragments}
        assert styles["Beta"] == "class:label.selected" and styles["Alpha"] == "class:label"

    def test_every_option_shows_its_description(self):
        plain = self._plain(render.options(CHOICES, 0, UNICODE))
        assert "the first" in plain and "the second" in plain

    def test_the_labels_line_up(self):
        lines = self._plain(render.options(CHOICES, 0, UNICODE)).splitlines()
        assert lines[0].index("the first") == lines[1].index("the second")

    def test_the_footer_lists_the_keys(self):
        plain = self._plain(render.footer(UNICODE, back=True))
        assert "enter" in plain and "←" in plain and "ctrl+c" in plain

    def test_without_back_the_footer_has_no_back_key(self):
        assert "←" not in self._plain(render.footer(UNICODE, back=False))

    def test_an_answered_question_shows_the_answer_on_its_own_line(self):
        plain = self._plain(render.answered("Style", "Tailwind CSS", UNICODE))
        assert plain.splitlines()[1].endswith("Tailwind CSS")


class TestGlyphs:
    def test_a_utf8_terminal_gets_unicode(self):
        assert glyphs_for("utf-8") is UNICODE

    def test_another_encoding_gets_ascii(self):
        assert glyphs_for("cp1252") is ASCII

    def test_an_unknown_encoding_gets_ascii(self):
        assert glyphs_for(None) is ASCII
