"""run_task: one permanent result line, output kept on failure."""

import contextlib
import io
import re
import sys

from rich.console import Console

from nexy.helpers.common.tasks import _LiveLine, format_duration, run_task, step, waiting


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

    def test_a_failure_keeps_only_the_end_of_a_long_output(self):
        console, buffer = _console()
        code = "import sys; [print(f'line {n}') for n in range(40)]; sys.exit(1)"
        run_task("x", [sys.executable, "-c", code], console=console)
        assert "line 0\n" not in buffer.getvalue()

    def test_full_output_keeps_every_line_of_a_failure(self):
        console, buffer = _console()
        code = "import sys; [print(f'line {n}') for n in range(40)]; sys.exit(1)"
        run_task("x", [sys.executable, "-c", code], console=console, full_output=True)
        assert "  line 0\n" in buffer.getvalue()

    def test_full_output_is_not_dimmed(self):
        console = Console(file=io.StringIO(), force_terminal=True, width=80)
        code = "import sys; print('src/app.py:3: error'); sys.exit(1)"
        run_task("x", [sys.executable, "-c", code], console=console, full_output=True)
        assert "\x1b[2m  src/app.py" not in console.file.getvalue()

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


class TestWaiting:
    def test_waiting_leaves_no_line(self):
        console, buffer = _console()
        with waiting("Starting the dev server", console=console):
            pass
        assert buffer.getvalue() == ""

    def test_waiting_draws_uv_live_row_on_a_terminal(self):
        console = Console(file=io.StringIO(), force_terminal=True, width=80)
        with waiting("Starting the dev server", console=console):
            console.file.write("")
        assert "Starting the dev server" in console.file.getvalue()


def _render(live) -> str:
    console, buffer = _console()
    console.print(live)
    return buffer.getvalue()


class TestLiveRow:
    """The row shown while a task runs is uv's: a spinner and a dim message, or a bar."""

    def test_a_lone_task_is_a_spinner_then_its_label(self):
        assert re.fullmatch(r"[⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏] Installing\n", _render(_LiveLine("Installing")))

    def test_a_lone_task_shows_the_last_line_of_its_output(self):
        live = _LiveLine("pnpm install")
        live.last = "Progress: resolved 42"
        assert _render(live)[2:] == "pnpm install  Progress: resolved 42\n"

    def test_a_lone_task_shows_no_elapsed_time(self):
        assert "ms" not in _render(_LiveLine("Installing"))

    def test_a_group_is_a_bar_of_twenty_cells_then_the_count(self):
        text = _render(_LiveLine("uv sync", progress=(2, 5)))
        assert text == "████████░░░░░░░░░░░░ [2/5] uv sync\n"

    def test_an_empty_group_bar_has_no_full_cell(self):
        assert _render(_LiveLine("x", progress=(0, 3))).startswith("░" * 20 + " [0/3]")

    def test_the_message_is_dim(self):
        console = Console(file=io.StringIO(), force_terminal=True, color_system="standard")
        console.print(_LiveLine("Installing"))
        assert "\x1b[2mInstalling" in console.file.getvalue()

    def test_a_long_message_is_cut_to_the_width(self):
        live = _LiveLine("x" * 300)
        assert max(len(line) for line in _render(live).splitlines()) <= 100

    def test_run_task_accepts_the_position_in_a_group(self):
        console, _ = _console()
        result = run_task("x", [sys.executable, "-c", "pass"], progress=(1, 3), console=console)
        assert result.ok
