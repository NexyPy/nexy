"""The header and the aligned lines of `nx dev`, `nx start` and `nx new`, with no arrow."""

import io

import pytest
from rich.console import Console

from nexy.helpers.common import launcher


@pytest.fixture
def printed(monkeypatch) -> io.StringIO:
    buffer = io.StringIO()
    monkeypatch.setattr(launcher, "console", Console(file=buffer, force_terminal=False, width=100))
    return buffer


def test_an_entry_is_its_label_then_its_value(printed):
    launcher.entry("Local:", "http://localhost:8000")
    assert printed.getvalue() == "  Local:     http://localhost:8000\n"


def test_an_entry_label_gets_its_colon(printed):
    launcher.entry("Ready", "0.73s")
    assert printed.getvalue() == "  Ready:     0.73s\n"


def test_a_next_step_is_the_command_then_what_it_does(printed):
    launcher.step("nexy dev", "Start the development server")
    assert printed.getvalue() == "  nexy dev  Start the development server\n"


def test_a_next_step_can_be_a_command_alone(printed):
    launcher.step("cd demo")
    assert printed.getvalue() == "  cd demo\n"


def test_the_header_names_the_brand_the_version_and_the_command(printed):
    launcher.banner("new", "2.5.0")
    assert printed.getvalue() == "\nnexy 2.5.0  new\n\n"


def test_next_steps_line_up_on_the_longest_command(printed):
    launcher.step("cd demo", "Go in", 12)
    assert printed.getvalue() == "  cd demo       Go in\n"


def test_a_padded_command_alone_has_no_trailing_spaces(printed):
    launcher.step("cd demo", "", 12)
    assert printed.getvalue() == "  cd demo\n"
