"""run_task: one permanent result line, output kept on failure."""

import io
import sys

from rich.console import Console

from nexy.helpers.common.tasks import format_duration, run_task


def _console() -> tuple[Console, io.StringIO]:
    buffer = io.StringIO()
    return Console(file=buffer, force_terminal=False, width=100), buffer


class TestFormatDuration:
    def test_milliseconds(self):
        assert format_duration(0.042) == "42ms"

    def test_seconds(self):
        assert format_duration(1.24) == "1.2s"

    def test_minutes(self):
        assert format_duration(65) == "1m 05s"


class TestRunTask:
    def test_success_prints_one_check_line(self):
        console, buffer = _console()
        result = run_task(
            "Installing x",
            [sys.executable, "-c", "print('hi')"],
            done="Installed x",
            console=console,
        )
        assert result.ok and result.returncode == 0
        text = buffer.getvalue()
        assert "✔ Installed x" in text
        assert "hi" not in text

    def test_failure_keeps_the_command_output(self):
        console, buffer = _console()
        code = "import sys; print('boom: no such package'); sys.exit(3)"
        result = run_task("Installing x", [sys.executable, "-c", code], console=console)
        assert not result.ok and result.returncode == 3
        text = buffer.getvalue()
        assert "✘ Installing x" in text and "exit 3" in text
        assert "boom: no such package" in text

    def test_missing_executable_is_reported_not_raised(self):
        console, buffer = _console()
        result = run_task("Running", ["definitely-not-a-binary-xyz"], console=console)
        assert not result.ok
        assert "✘ Running" in buffer.getvalue()

    def test_brackets_in_output_are_not_treated_as_markup(self):
        console, buffer = _console()
        code = "import sys; print('[red]oops[/red] npm ERR!'); sys.exit(1)"
        run_task("x", [sys.executable, "-c", code], console=console)
        assert "[red]oops[/red]" in buffer.getvalue()
