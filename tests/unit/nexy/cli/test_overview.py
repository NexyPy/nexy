"""`nx` without a command shows the version and every command; each command has its alias."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from nexy.modules.cli import CLI
from nexy.modules.cli.overview import _commands

runner = CliRunner()


def test_running_nx_alone_lists_the_commands():
    out = runner.invoke(CLI, []).output
    assert all(name in out for name in ("dev", "start", "build", "migrate"))


def test_the_version_flag_prints_the_version():
    result = runner.invoke(CLI, ["--version"])
    assert result.exit_code == 0 and "nexy" in result.output


def test_every_overview_command_exists():
    names = {usage.split()[0] for usage, _ in _commands()}
    registered = {command.name or command.callback.__name__ for command in CLI.registered_commands}
    assert names <= registered


def test_each_command_has_a_one_letter_alias():
    aliases = {c.name for c in CLI.registered_commands if c.hidden}
    assert aliases == {"d", "s", "b", "c", "f", "i", "n", "m"}


@pytest.mark.parametrize("alias", ["d", "s", "b", "c", "f", "i", "n", "m"])
def test_an_alias_answers_to_help(alias):
    assert runner.invoke(CLI, [alias, "--help"]).exit_code == 0
