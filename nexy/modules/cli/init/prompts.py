from pathlib import Path
from typing import Any

import questionary

from nexy.modules.i18n import t

from .databases import DATABASES, default_url

BACK_VALUE = "__back__"
_STYLES = [
    ("tailwind", "Tailwind CSS"),
    ("unocss", "UnoCSS"),
    ("vanilla", "Vanilla CSS"),
    ("other", "Other"),
]
_FRAMEWORKS = ["React", "Vue", "Svelte", "Solid", "Preact"]
_DONE, _SKIP, _BACK = "done", "skip", "back"


def ask_project_name() -> str | None:
    """Prompt for a project name (None when the user cancels)."""
    name = questionary.text(
        t("cli.new.prompt", "Project name:"),
        qmark="»",
        validate=validate_project_name,
    ).ask()
    if name is None:
        return None
    return name or ask_project_name()


def validate_project_name(name: str) -> bool | str:
    """Accept a valid, available project name or return the error message."""
    if not name.strip():
        return t("cli.new.error_empty", "Project name cannot be empty.")
    if not name[0].isalpha():
        return t("cli.new.error_letter", "Project name must start with a letter.")
    if not all(c.isalnum() or c in "-_" for c in name):
        return t("cli.new.error_chars", "Use only letters, numbers, hyphens, underscores.")
    if Path(name).exists():
        return t("cli.new.error_exists", "Directory '{name}' already exists.").format(name=name)
    return True


class ProjectPrompter:
    """Handles all interactive questions for project initialization.

    Each question is a step that answers done, skip (does not apply) or back. Going back returns to
    the last question that was actually asked, so skipped ones are never shown on the way.
    """

    def __init__(self) -> None:
        self.config: dict[str, Any] = {}

    def ask_all(self) -> dict[str, Any]:
        """Runs the full questionnaire and returns the configuration dictionary."""
        steps = [
            self._router,
            self._project_type,
            self._csr,
            self._framework,
            self._style,
            self._database,
            self._orm,
            self._db_url,
        ]
        asked: list[int] = []
        position = 0
        while position < len(steps):
            outcome = steps[position]()
            if outcome == _BACK:
                position = asked.pop() if asked else position
                continue
            if outcome == _DONE:
                asked.append(position)
            position += 1
        return self.config

    def _select(self, message: str, choices: list[Any], back: bool = True, **kwargs: Any) -> Any:
        """A select that can go back; the answer is the value, or BACK_VALUE."""
        items = list(choices)
        if back:
            items.append(questionary.Choice(t("init.choice.back", "Back"), value=BACK_VALUE))
        return _required(
            questionary.select(message, choices=items, pointer="ʋ", qmark="»", **kwargs).ask()
        )

    def _router(self) -> str:
        self.config["FBRouter"] = _required(
            questionary.confirm(
                t("init.ask.router", "Use file-based router?"),
                default=True,
                qmark="»",
                instruction="(yes/no) ",
            ).ask()
        )
        return _DONE

    def _project_type(self) -> str:
        choice = self._select(
            t("init.ask.project_type", "Choose the type of project"),
            [
                questionary.Choice(t("init.choice.web", "Web (monolith web app)"), value="web"),
                questionary.Choice(t("init.choice.api", "API (RESTful API)"), value="api"),
            ],
            show_description=True,
            show_selected=True,
        )
        if choice == BACK_VALUE:
            return _BACK
        self.config["project_type"] = choice
        self.config["useCSR"] = False
        self.config["client_framework"] = "none"
        return _DONE

    def _is_web(self) -> bool:
        return self.config.get("project_type") == "web"

    def _csr(self) -> str:
        """Client routing replaces .nexy views, so it needs a renderer."""
        if not (self._is_web() and self.config.get("FBRouter")):
            return _SKIP
        self.config["useCSR"] = _required(
            questionary.confirm(
                t("init.ask.csr", "Enable client-side routing?"),
                default=False,
                qmark="»",
                instruction="(yes/no) ",
            ).ask()
        )
        return _DONE

    def _framework(self) -> str:
        """Pick the renderer; with client routing the "none" choice disappears."""
        if not self._is_web():
            return _SKIP
        if not self.config["useCSR"] and not self._wants_client_component():
            self.config["client_framework"] = "none"
            return _DONE
        framework = self._select(
            t("init.ask.framework", "Choose the client framework"), _FRAMEWORKS
        )
        if framework == BACK_VALUE:
            return _BACK
        self.config["client_framework"] = framework.lower()
        return _DONE

    def _wants_client_component(self) -> bool:
        return bool(
            _required(
                questionary.confirm(
                    t("init.ask.client_component", "Would you like to use a client component?"),
                    default=True,
                    qmark="»",
                ).ask()
            )
        )

    def _style(self) -> str:
        if not self._is_web():
            return _SKIP
        choice = self._select(
            t("init.ask.style", "Choose how to style the app"),
            [questionary.Choice(label, value=key) for key, label in _STYLES],
        )
        if choice == BACK_VALUE:
            return _BACK
        self.config["style"] = choice
        return _DONE

    def _database(self) -> str:
        choice = self._select(
            t("init.ask.database", "Choose a database"),
            [questionary.Choice(label, value=key) for key, label in DATABASES],
            default="sqlite",
        )
        if choice == BACK_VALUE:
            return _BACK
        self.config["database"] = choice
        self.config["orm"] = "None"
        self.config.pop("db_url", None)
        return _DONE

    def _orm(self) -> str:
        if self.config["database"] == "none":
            return _SKIP
        choice = self._select(
            t("init.ask.orm", "Choose an ORM"), ["SQLModel", "SQLAlchemy", "Tortoise-ORM"]
        )
        if choice == BACK_VALUE:
            return _BACK
        self.config["orm"] = choice
        return _DONE

    def _db_url(self) -> str:
        if self.config["database"] == "none":
            return _SKIP
        self.config["db_url"] = _required(
            questionary.text(
                t("init.ask.db_url", "Database URL"),
                default=default_url(self.config["database"], self.config["orm"]),
                qmark="»",
            ).ask()
        )
        return _DONE


def _required(answer: Any) -> Any:
    """questionary answers None when the user cancels (Ctrl+C)."""
    if answer is None:
        raise KeyboardInterrupt
    return answer
