"""The questions of `nx new`: one function each. A question answers done, skipped or back."""

from __future__ import annotations

from typing import Any

from nexy.modules.cli import tui
from nexy.modules.cli.tui import BACK as GO_BACK
from nexy.modules.cli.tui import Option
from nexy.modules.i18n import t

from .databases import DATABASES, default_url

DONE, SKIP, BACK = "done", "skip", "back"

Config = dict[str, Any]

NO_ORM = "None"


def _styles() -> list[Option]:
    return [
        Option(
            "tailwind", "Tailwind CSS", t("init.hint.tailwind", "utility classes in your markup")
        ),
        Option("unocss", "UnoCSS", t("init.hint.unocss", "on-demand atomic CSS, very fast")),
        Option(
            "vanilla", "Vanilla CSS", t("init.hint.vanilla", "plain stylesheets, nothing to learn")
        ),
        Option(
            "other",
            t("init.choice.other", "Other"),
            t("init.hint.other_style", "set it up yourself"),
        ),
    ]


def _frameworks() -> list[Option]:
    return [
        Option("react", "React", t("init.hint.react", "the most widely used UI library")),
        Option("vue", "Vue", t("init.hint.vue", "approachable and well documented")),
        Option("svelte", "Svelte", t("init.hint.svelte", "compiled, very little runtime")),
        Option("solid", "Solid", t("init.hint.solid", "fine-grained reactivity, no virtual DOM")),
        Option("preact", "Preact", t("init.hint.preact", "React API in 3 kB")),
    ]


def _orms() -> list[Option]:
    return [
        Option(
            "SQLModel", "SQLModel", t("init.hint.sqlmodel", "Pydantic models that are also tables")
        ),
        Option("SQLAlchemy", "SQLAlchemy", t("init.hint.sqlalchemy", "the reference Python ORM")),
        Option(
            "Tortoise-ORM", "Tortoise-ORM", t("init.hint.tortoise", "async-first, Django-like API")
        ),
        Option(
            NO_ORM,
            t("init.choice.no_database", "No database"),
            t("init.hint.no_orm", "no database layer, add one later"),
        ),
    ]


def _databases() -> list[Option]:
    hints = {
        "sqlite": t("init.hint.sqlite", "a file, nothing to install"),
        "postgresql": t("init.hint.postgresql", "the robust open-source standard"),
        "neon": t("init.hint.neon", "serverless PostgreSQL in the cloud"),
        "mysql": t("init.hint.mysql", "widely hosted, MariaDB compatible"),
        "other": t("init.hint.other_db", "type your own connection URL"),
    }
    other = t("init.choice.other", "Other")
    return [Option(key, other if key == "other" else label, hints[key]) for key, label in DATABASES]


def _yes_no(message: str, yes_hint: str, no_hint: str, default: bool, back: bool = True) -> Any:
    """A yes/no question whose two answers are described."""
    return tui.confirm(
        message,
        yes=t("init.choice.yes", "Yes"),
        no=t("init.choice.no", "No"),
        yes_hint=yes_hint,
        no_hint=no_hint,
        default=default,
        back=back,
    )


def _is_web(config: Config) -> bool:
    return config.get("project_type") == "web"


def ask_router(config: Config) -> str:
    answer = _yes_no(
        t("init.ask.router", "Use file-based router?"),
        t("init.hint.router_yes", "pages are the files of src/routes"),
        t("init.hint.router_no", "register routes in code, with modules"),
        True,
        back=False,
    )
    if answer is GO_BACK:
        return BACK
    config["FBRouter"] = answer
    return DONE


def ask_project_type(config: Config) -> str:
    choice = tui.select(
        t("init.ask.project_type", "Choose the type of project"),
        [
            Option(
                "web",
                t("init.choice.web", "Web"),
                t("init.hint.web", "pages, layouts and components in one app"),
            ),
            Option(
                "api",
                t("init.choice.api", "API"),
                t("init.hint.api", "JSON endpoints only, no pages"),
            ),
        ],
    )
    if choice is GO_BACK:
        return BACK
    config.update(project_type=choice, useCSR=False, client_framework="none")
    return DONE


def ask_csr(config: Config) -> str:
    """Client routing replaces .nexy views, so it needs a renderer."""
    if not (_is_web(config) and config.get("FBRouter")):
        return SKIP
    answer = _yes_no(
        t("init.ask.csr", "Enable client-side routing?"),
        t("init.hint.csr_yes", "the browser navigates without reloading"),
        t("init.hint.csr_no", "every page is rendered by the server"),
        False,
    )
    if answer is GO_BACK:
        return BACK
    config["useCSR"] = answer
    return DONE


def _wants_client_component() -> Any:
    return _yes_no(
        t("init.ask.client_component", "Would you like to use a client component?"),
        t("init.hint.component_yes", "interactive parts written in a UI framework"),
        t("init.hint.component_no", "server-rendered .nexy pages only"),
        True,
    )


def ask_framework(config: Config) -> str:
    """Pick the renderer; with client routing the "none" choice disappears."""
    if not _is_web(config):
        return SKIP
    if not config["useCSR"]:
        wanted = _wants_client_component()
        if wanted is GO_BACK:
            return BACK
        if not wanted:
            config["client_framework"] = "none"
            return DONE
    framework = tui.select(t("init.ask.framework", "Choose the client framework"), _frameworks())
    if framework is GO_BACK:
        return BACK
    config["client_framework"] = framework
    return DONE


def ask_style(config: Config) -> str:
    if not _is_web(config):
        return SKIP
    choice = tui.select(t("init.ask.style", "Choose how to style the app"), _styles())
    if choice is GO_BACK:
        return BACK
    config["style"] = choice
    return DONE


def ask_orm(config: Config) -> str:
    """The ORM comes first: a database only makes sense once something talks to it."""
    choice = tui.select(t("init.ask.orm", "Choose an ORM"), _orms())
    if choice is GO_BACK:
        return BACK
    config["orm"] = choice
    config.pop("db_url", None)
    config["database"] = "none" if choice == NO_ORM else config.get("database", "sqlite")
    return DONE


def ask_database(config: Config) -> str:
    if config["orm"] == NO_ORM:
        return SKIP
    choice = tui.select(
        t("init.ask.database", "Choose a database"),
        _databases(),
        default=config.get("database", "sqlite"),
    )
    if choice is GO_BACK:
        return BACK
    config["database"] = choice
    return DONE


def ask_db_url(config: Config) -> str:
    if config["orm"] == NO_ORM:
        return SKIP
    answer = tui.text(
        t("init.ask.db_url", "Database URL"),
        default=default_url(config["database"], config["orm"]),
        back=True,
    )
    if answer is GO_BACK:
        return BACK
    config["db_url"] = answer
    return DONE


STEPS = (
    ask_router,
    ask_project_type,
    ask_csr,
    ask_framework,
    ask_style,
    ask_orm,
    ask_database,
    ask_db_url,
)
