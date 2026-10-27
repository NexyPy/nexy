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


def _render(live) -> str:
    console, buffer = _console()
    console.print(live)
    return buffer.getvalue()


class TestProgressBar:
    def test_a_group_shows_how_many_steps_are_finished(self):
        from nexy.helpers.common.tasks import _LiveLine

        text = _render(_LiveLine("Installing", progress=(2, 5)))
        assert "Installing" in text and "2/5" in text

    def test_a_lone_task_shows_a_pulsing_bar_without_a_count(self):
        from nexy.helpers.common.tasks import _LiveLine

        text = _render(_LiveLine("Installing"))
        assert "Installing" in text and "/" not in text

    def test_run_task_accepts_the_position_in_a_group(self):
        console, buffer = _console()
        result = run_task("x", [sys.executable, "-c", "pass"], progress=(1, 3), console=console)
        assert result.ok
