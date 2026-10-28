"""What `nx new` tells the developer to do next: a project with an ORM has tables to create."""

from __future__ import annotations

import pytest

from nexy.modules.cli.init import template_setup


@pytest.fixture
def commands(monkeypatch):
    shown: list[str] = []
    monkeypatch.setattr(template_setup.launcher, "step", lambda command, *_: shown.append(command))
    return shown


def test_a_project_with_an_orm_is_told_to_create_its_tables(commands):
    template_setup.print_success_message("demo", orm="SQLModel")
    assert 'nexy migrate -m "create tables"' in commands and "nexy migrate --upgrade" in commands


def test_the_tables_come_before_the_dev_server(commands):
    template_setup.print_success_message("demo", orm="Tortoise-ORM")
    assert commands.index("nexy migrate --upgrade") < commands.index("nexy dev")


def test_a_project_without_an_orm_has_nothing_to_migrate(commands):
    template_setup.print_success_message("demo", orm="None")
    assert not any("migrate" in command for command in commands)


def test_the_old_call_without_an_orm_still_works(commands):
    template_setup.print_success_message("demo")
    assert "nexy dev" in commands
