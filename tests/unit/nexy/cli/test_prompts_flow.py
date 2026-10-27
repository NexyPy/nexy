"""The questions of `nx new`: their order, what they set, and going back to the one before."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from nexy.modules.cli import tui
from nexy.modules.cli.init import questions
from nexy.modules.cli.init.prompts import ProjectPrompter

BACK = tui.BACK


class Script:
    """Stands in for the terminal: answers in order and remembers what was asked."""

    def __init__(self, answers):
        self.answers = list(answers)
        self.asked: list[str] = []
        self.choices: dict[str, list] = {}
        self.backs: dict[str, bool] = {}

    def _answer(self, message, back=True):
        self.asked.append(message)
        self.backs[message] = back
        answer = self.answers.pop(0)
        if answer is None:
            raise KeyboardInterrupt
        return answer

    def select(self, message, choices, *, default=None, back=True):
        self.choices[message] = [choice.value for choice in choices]
        return self._answer(message, back)

    def confirm(self, message, *, back=True, **_kwargs):
        return self._answer(message, back)

    def text(self, message, *, back=False, **_kwargs):
        return self._answer(message, back)

    def install(self, monkeypatch):
        fake = SimpleNamespace(select=self.select, confirm=self.confirm, text=self.text)
        monkeypatch.setattr(questions, "tui", fake)


def _run(monkeypatch, answers) -> tuple[dict, Script]:
    script = Script(answers)
    script.install(monkeypatch)
    return ProjectPrompter().ask_all(), script


WEB = [True, "web", True, "react", "tailwind", False]


def test_the_client_routing_question_is_short(monkeypatch):
    _, script = _run(monkeypatch, [*WEB, "None"])
    assert "Enable client-side routing?" in script.asked


def test_full_client_routed_web_project(monkeypatch):
    config, _ = _run(
        monkeypatch, [True, "web", True, "react", "unocss", False, "SQLModel", "sqlite", "x"]
    )
    assert (config["useCSR"], config["client_framework"], config["style"]) == (
        True,
        "react",
        "unocss",
    )
    assert (config["database"], config["orm"], config["db_url"]) == ("sqlite", "SQLModel", "x")


def test_no_orm_means_no_database_and_no_url(monkeypatch):
    config, script = _run(monkeypatch, [True, "web", False, True, "vue", "tailwind", False, "None"])
    assert (config["database"], config["orm"]) == ("none", "None") and "db_url" not in config
    assert "Choose a database" not in script.asked


def test_the_orm_is_asked_before_the_database(monkeypatch):
    _, script = _run(monkeypatch, [*WEB, "SQLAlchemy", "postgresql", "x"])
    assert script.asked.index("Choose an ORM") < script.asked.index("Choose a database")


def test_an_api_project_is_not_asked_about_styles_or_client_routing(monkeypatch):
    _, script = _run(monkeypatch, [False, "api", "None"])
    assert "Choose how to style the app" not in script.asked
    assert "Enable client-side routing?" not in script.asked


def test_the_style_choices(monkeypatch):
    _, script = _run(monkeypatch, [*WEB, "None"])
    assert script.choices["Choose how to style the app"] == [
        "tailwind",
        "unocss",
        "vanilla",
        "other",
    ]


def test_the_orm_choices_end_with_no_database(monkeypatch):
    _, script = _run(monkeypatch, [*WEB, "None"])
    assert script.choices["Choose an ORM"] == ["SQLModel", "SQLAlchemy", "Tortoise-ORM", "None"]


def test_the_database_choices_have_no_none(monkeypatch):
    _, script = _run(monkeypatch, [*WEB, "SQLModel", "sqlite", "x"])
    assert script.choices["Choose a database"] == [
        "sqlite",
        "postgresql",
        "neon",
        "mysql",
        "other",
    ]


class TestAlias:
    def test_the_default_alias_is_kept_when_not_customized(self, monkeypatch):
        config, _ = _run(monkeypatch, [*WEB, "None"])
        assert config["alias"] == "@"

    def test_a_custom_alias_is_asked_for_and_stored(self, monkeypatch):
        config, _ = _run(monkeypatch, [True, "web", True, "react", "tailwind", True, " ~ ", "None"])
        assert config["alias"] == "~"

    def test_an_api_project_has_no_alias_question(self, monkeypatch):
        _, script = _run(monkeypatch, [False, "api", "None"])
        assert "Customize the import alias?" not in script.asked


class TestGoingBack:
    def test_the_first_question_cannot_go_back(self, monkeypatch):
        _, script = _run(monkeypatch, [*WEB, "None"])
        assert script.backs["Use file-based router?"] is False

    def test_back_from_the_framework_asks_client_routing_again(self, monkeypatch):
        answers = [True, "web", True, BACK, False, True, "svelte", "tailwind", False, "None"]
        config, script = _run(monkeypatch, answers)
        assert script.asked.count("Enable client-side routing?") == 2
        assert (config["useCSR"], config["client_framework"]) == (False, "svelte")

    def test_back_from_the_first_selects_goes_to_the_question_before(self, monkeypatch):
        answers = [True, "web", True, "vue", BACK, "solid", "tailwind", False, "None"]
        config, _ = _run(monkeypatch, answers)
        assert config["client_framework"] == "solid"

    def test_back_from_the_orm_goes_to_the_alias(self, monkeypatch):
        answers = [*WEB, BACK, True, "~", "None"]
        config, _ = _run(monkeypatch, answers)
        assert config["alias"] == "~"

    def test_back_from_the_database_goes_to_the_orm(self, monkeypatch):
        answers = [*WEB, "SQLModel", BACK, "None"]
        config, _ = _run(monkeypatch, answers)
        assert config["orm"] == "None"

    def test_back_from_the_url_goes_to_the_database(self, monkeypatch):
        answers = [*WEB, "SQLModel", "sqlite", BACK, "mysql", "x"]
        config, _ = _run(monkeypatch, answers)
        assert config["database"] == "mysql"

    def test_back_over_a_question_that_was_skipped_goes_further_back(self, monkeypatch):
        # An API project skips client routing: back from the ORM lands on the project type.
        answers = [True, "api", BACK, "api", "None"]
        _, script = _run(monkeypatch, answers)
        assert script.asked.count("Choose the type of project") == 2


def test_cancelling_a_question_stops_the_questionnaire(monkeypatch):
    script = Script([True, None])
    script.install(monkeypatch)
    with pytest.raises(KeyboardInterrupt):
        ProjectPrompter().ask_all()
