"""The questions of `nx new`: one function each. A question answers done, skipped or back."""

from __future__ import annotations

from typing import Any

import questionary

from nexy.modules.i18n import t

from .databases import DATABASES, default_url

BACK_VALUE = "__back__"
DONE, SKIP, BACK = "done", "skip", "back"

_STYLES = [
    ("tailwind", "Tailwind CSS"),
    ("unocss", "UnoCSS"),
    ("vanilla", "Vanilla CSS"),
    ("other", "Other"),
]
_FRAMEWORKS = ["React", "Vue", "Svelte", "Solid", "Preact"]
_ORMS = ["SQLModel", "SQLAlchemy", "Tortoise-ORM"]

Config = dict[str, Any]


def required(answer: Any) -> Any:
    """questionary answers None when the user cancels (Ctrl+C)."""
    if answer is None:
        raise KeyboardInterrupt
    return answer


def _select(message: str, choices: list[Any], **kwargs: Any) -> Any:
    """A select that can go back; the answer is the value, or BACK_VALUE."""
    items = [*choices, questionary.Choice(t("init.choice.back", "Back"), value=BACK_VALUE)]
    return required(
        questionary.select(message, choices=items, pointer="ʋ", qmark="»", **kwargs).ask()
    )


def _confirm(message: str, default: bool, **kwargs: Any) -> bool:
    return bool(required(questionary.confirm(message, default=default, qmark="»", **kwargs).ask()))


def _is_web(config: Config) -> bool:
    return config.get("project_type") == "web"


def ask_router(config: Config) -> str:
    config["FBRouter"] = _confirm(
        t("init.ask.router", "Use file-based router?"), True, instruction="(yes/no) "
    )
    return DONE


def ask_project_type(config: Config) -> str:
    choice = _select(
        t("init.ask.project_type", "Choose the type of project"),
        [
            questionary.Choice(t("init.choice.web", "Web (monolith web app)"), value="web"),
            questionary.Choice(t("init.choice.api", "API (RESTful API)"), value="api"),
        ],
        show_description=True,
        show_selected=True,
    )
    if choice == BACK_VALUE:
        return BACK
    config.update(project_type=choice, useCSR=False, client_framework="none")
    return DONE


def ask_csr(config: Config) -> str:
    """Client routing replaces .nexy views, so it needs a renderer."""
    if not (_is_web(config) and config.get("FBRouter")):
        return SKIP
    config["useCSR"] = _confirm(
        t("init.ask.csr", "Enable client-side routing?"), False, instruction="(yes/no) "
    )
    return DONE


def _wants_client_component() -> bool:
    return _confirm(
        t("init.ask.client_component", "Would you like to use a client component?"), True
    )


def ask_framework(config: Config) -> str:
    """Pick the renderer; with client routing the "none" choice disappears."""
    if not _is_web(config):
        return SKIP
    if not config["useCSR"] and not _wants_client_component():
        config["client_framework"] = "none"
        return DONE
    framework = _select(t("init.ask.framework", "Choose the client framework"), _FRAMEWORKS)
    if framework == BACK_VALUE:
        return BACK
    config["client_framework"] = framework.lower()
    return DONE


def ask_style(config: Config) -> str:
    if not _is_web(config):
        return SKIP
    choice = _select(
        t("init.ask.style", "Choose how to style the app"),
        [questionary.Choice(label, value=key) for key, label in _STYLES],
    )
    if choice == BACK_VALUE:
        return BACK
    config["style"] = choice
    return DONE


def ask_database(config: Config) -> str:
    choice = _select(
        t("init.ask.database", "Choose a database"),
        [questionary.Choice(label, value=key) for key, label in DATABASES],
        default="sqlite",
    )
    if choice == BACK_VALUE:
        return BACK
    config.update(database=choice, orm="None")
    config.pop("db_url", None)
    return DONE


def ask_orm(config: Config) -> str:
    if config["database"] == "none":
        return SKIP
    choice = _select(t("init.ask.orm", "Choose an ORM"), _ORMS)
    if choice == BACK_VALUE:
        return BACK
    config["orm"] = choice
    return DONE


def ask_db_url(config: Config) -> str:
    if config["database"] == "none":
        return SKIP
    config["db_url"] = required(
        questionary.text(
            t("init.ask.db_url", "Database URL"),
            default=default_url(config["database"], config["orm"]),
            qmark="»",
        ).ask()
    )
    return DONE


STEPS = (
    ask_router,
    ask_project_type,
    ask_csr,
    ask_framework,
    ask_style,
    ask_database,
    ask_orm,
    ask_db_url,
)
