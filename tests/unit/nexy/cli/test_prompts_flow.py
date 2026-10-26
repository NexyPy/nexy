"""The questions of `nx new`: their order, what they set, and going back to the one before."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from nexy.modules.cli.init import questions
from nexy.modules.cli.init.prompts import BACK_VALUE, ProjectPrompter


class Script:
    """Stands in for questionary: answers in order and remembers what was asked."""

    def __init__(self, answers):
        self.answers = list(answers)
        self.asked: list[str] = []
        self.choices: dict[str, list] = {}

    def _ask(self, kind):
        def build(message, *args, choices=None, **kwargs):
            self.asked.append(message)
            if choices is not None:
                self.choices[message] = [getattr(c, "value", c) for c in choices]
            return SimpleNamespace(ask=lambda: self.answers.pop(0))

        return build

    def install(self, monkeypatch):
        fake = SimpleNamespace(
            confirm=self._ask("confirm"),
            select=self._ask("select"),
            text=self._ask("text"),
            Choice=lambda title, value=None, **kw: SimpleNamespace(title=title, value=value),
        )
        monkeypatch.setattr(questions, "questionary", fake)


def _run(monkeypatch, answers) -> tuple[dict, Script]:
    script = Script(answers)
    script.install(monkeypatch)
    return ProjectPrompter().ask_all(), script


def _without_back(choices):
    return [c for c in choices if c != BACK_VALUE]


def test_the_client_routing_question_is_short(monkeypatch):
    _, script = _run(monkeypatch, [True, "web", True, "React", "tailwind", "none"])
    assert "Enable client-side routing?" in script.asked


def test_full_client_routed_web_project(monkeypatch):
    config, _ = _run(monkeypatch, [True, "web", True, "React", "unocss", "sqlite", "SQLModel", "x"])
    assert (config["useCSR"], config["client_framework"], config["style"]) == (
        True,
        "react",
        "unocss",
    )
    assert (config["database"], config["orm"], config["db_url"]) == ("sqlite", "SQLModel", "x")


def test_no_database_means_no_orm_and_no_url(monkeypatch):
    config, script = _run(monkeypatch, [True, "web", False, True, "Vue", "tailwind", "none"])
    assert config["orm"] == "None" and "db_url" not in config
    assert "Choose an ORM" not in script.asked


def test_an_api_project_is_not_asked_about_styles_or_client_routing(monkeypatch):
    _, script = _run(monkeypatch, [False, "api", "none"])
    assert "Choose a style system" not in script.asked
    assert "Enable client-side routing?" not in script.asked


def test_the_style_choices(monkeypatch):
    _, script = _run(monkeypatch, [True, "web", True, "React", "tailwind", "none"])
    assert _without_back(script.choices["Choose how to style the app"]) == [
        "tailwind",
        "unocss",
        "vanilla",
        "other",
    ]


def test_the_database_choices_end_with_none(monkeypatch):
    _, script = _run(monkeypatch, [True, "web", True, "React", "tailwind", "none"])
    assert _without_back(script.choices["Choose a database"]) == [
        "sqlite",
        "postgresql",
        "neon",
        "mysql",
        "other",
        "none",
    ]


class TestGoingBack:
    def test_the_framework_question_offers_a_way_back(self, monkeypatch):
        _, script = _run(monkeypatch, [True, "web", True, "React", "tailwind", "none"])
        assert script.choices["Choose the client framework"][-1] == BACK_VALUE

    def test_back_from_the_framework_asks_client_routing_again(self, monkeypatch):
        answers = [True, "web", True, BACK_VALUE, False, True, "Svelte", "tailwind", "none"]
        config, script = _run(monkeypatch, answers)
        assert script.asked.count("Enable client-side routing?") == 2
        assert (config["useCSR"], config["client_framework"]) == (False, "svelte")

    def test_back_from_the_first_selects_goes_to_the_question_before(self, monkeypatch):
        answers = [True, "web", True, "Vue", BACK_VALUE, "Solid", "tailwind", "none"]
        config, _ = _run(monkeypatch, answers)
        assert config["client_framework"] == "solid"

    def test_back_from_the_database_goes_to_the_style(self, monkeypatch):
        answers = [True, "web", True, "Vue", "tailwind", BACK_VALUE, "vanilla", "none"]
        config, _ = _run(monkeypatch, answers)
        assert config["style"] == "vanilla"

    def test_back_over_a_question_that_was_skipped_goes_further_back(self, monkeypatch):
        # An API project skips client routing: back from the database lands on the project type.
        answers = [True, "api", BACK_VALUE, "api", "none"]
        _, script = _run(monkeypatch, answers)
        assert script.asked.count("Choose the type of project") == 2


def test_cancelling_a_question_stops_the_questionnaire(monkeypatch):
    script = Script([True, None])
    script.install(monkeypatch)
    with pytest.raises(KeyboardInterrupt):
        ProjectPrompter().ask_all()
