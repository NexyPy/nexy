"""Messages of the command line in the shape uv gives them: a bold keyword, then the message."""

import io

from rich.console import Console

from nexy.helpers.common import messages


def _printed(say, *args) -> str:
    buffer = io.StringIO()
    say(*args, console=Console(file=buffer, force_terminal=False, width=100))
    return buffer.getvalue()


def _coloured(say, *args) -> str:
    buffer = io.StringIO()
    console = Console(file=buffer, force_terminal=True, color_system="standard", width=100)
    say(*args, console=console)
    return buffer.getvalue()


class TestError:
    def test_an_error_starts_with_the_error_keyword(self):
        assert _printed(messages.error, "No such template") == "error: No such template\n"

    def test_a_cause_goes_on_its_own_indented_line(self):
        text = _printed(messages.error, "Could not create the project", "git failed")
        assert text.splitlines()[1] == "  cause: git failed"

    def test_the_error_keyword_is_bold_red(self):
        assert "\x1b[1;31merror" in _coloured(messages.error, "boom")


class TestWarning:
    def test_a_warning_starts_with_the_warning_keyword(self):
        assert _printed(messages.warning, "Slow connection") == "warning: Slow connection\n"

    def test_the_warning_keyword_is_bold_yellow(self):
        assert "\x1b[1;33mwarning" in _coloured(messages.warning, "slow")


class TestHint:
    def test_a_hint_starts_with_the_hint_keyword(self):
        assert _printed(messages.hint, "Run nx build") == "hint: Run nx build\n"


class TestTook:
    def test_the_duration_follows_the_message(self):
        assert messages.took("Installed zod", "1.2s") == "Installed zod [dim]in 1.2s[/dim]"
