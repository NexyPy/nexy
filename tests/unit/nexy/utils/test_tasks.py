"""run_task: one permanent result line, output kept on failure."""

import contextlib
import io
import re
import sys

from rich.console import Console

from nexy.helpers.common.tasks import format_duration, run_task, step


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
    def test_success_leaves_one_line_with_the_duration(self):
        console, buffer = _console()
        argv = [sys.executable, "-c", "print('hi')"]
        run_task("Installing x", argv, done="Installed x", console=console)
        assert re.fullmatch(r"Installed x in \d+(ms|\.\ds)\n", buffer.getvalue())

    def test_success_reports_the_exit_code(self):
        console, _ = _console()
        result = run_task("x", [sys.executable, "-c", "pass"], console=console)
        assert result.ok and result.returncode == 0

    def test_success_hides_the_command_output(self):
        console, buffer = _console()
        run_task("x", [sys.executable, "-c", "print('hi')"], console=console)
        assert "hi" not in buffer.getvalue()

    def test_a_task_without_done_reports_its_label(self):
        console, buffer = _console()
        run_task("uv sync", [sys.executable, "-c", "pass"], console=console)
        assert buffer.getvalue().startswith("uv sync in ")

    def test_a_failure_is_an_error_line_naming_the_task(self):
        console, buffer = _console()
        code = "import sys; sys.exit(3)"
        run_task("Installing x", [sys.executable, "-c", code], console=console)
        assert buffer.getvalue().splitlines()[0] == "error: Installing x"

    def test_a_failure_gives_the_exit_code_as_its_cause(self):
        console, buffer = _console()
        code = "import sys; sys.exit(3)"
        run_task("Installing x", [sys.executable, "-c", code], console=console)
        assert buffer.getvalue().splitlines()[1].startswith("  cause: exit 3 after ")

    def test_a_failure_keeps_the_command_output(self):
        console, buffer = _console()
        code = "import sys; print('boom: no such package'); sys.exit(3)"
        run_task("Installing x", [sys.executable, "-c", code], console=console)
        assert "  boom: no such package" in buffer.getvalue()

    def test_a_missing_executable_is_an_error_not_an_exception(self):
        console, buffer = _console()
        run_task("Running", ["definitely-not-a-binary-xyz"], console=console)
        assert buffer.getvalue().startswith("error: Running\n  cause: ")

    def test_brackets_in_output_are_not_treated_as_markup(self):
        console, buffer = _console()
        code = "import sys; print('[red]oops[/red] npm ERR!'); sys.exit(1)"
        run_task("x", [sys.executable, "-c", code], console=console)
        assert "[red]oops[/red]" in buffer.getvalue()


class TestStep:
    def test_a_finished_step_leaves_one_line_with_the_duration(self):
        console, buffer = _console()
        with step("Compiling", done="Compiled the routes", console=console):
            pass
        assert re.fullmatch(r"Compiled the routes in \d+ms\n", buffer.getvalue())

    def test_a_failed_step_is_an_error_line(self):
        console, buffer = _console()
        with contextlib.suppress(RuntimeError), step("Compiling", console=console):
            raise RuntimeError("boom")
        assert buffer.getvalue() == "error: Compiling\n"


def _render(live) -> str:
    console, buffer = _console()
    console.print(live)
    return buffer.getvalue()


class TestProgressBar:
    def test_a_group_shows_how_many_steps_are_finished(self):
        from nexy.helpers.common.tasks import _LiveLine

        text = _render(_LiveLine("Installing", progress=(2, 5)))
        assert "Installing" in text and "2/5" in text

    def test_a_lone_task_shows_no_count(self):
        from nexy.helpers.common.tasks import _LiveLine

        assert "/" not in _render(_LiveLine("Installing"))

    def test_run_task_accepts_the_position_in_a_group(self):
        console, buffer = _console()
        result = run_task("x", [sys.executable, "-c", "pass"], progress=(1, 3), console=console)
        assert result.ok
