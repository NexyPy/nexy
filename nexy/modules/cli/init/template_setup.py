"""Template initialization: clone/render, shared overlays and the post-init pipeline."""

import shutil
import subprocess  # nosec B404
import sys
from contextlib import suppress
from pathlib import Path
from typing import Any

from nexy.__version__ import __version__
from nexy.helpers.common import launcher
from nexy.helpers.common.console import console
from nexy.helpers.common.log_line import tagged
from nexy.helpers.fs.packages import ensure_packages
from nexy.modules.cli.agents import install_agent_files, profile_from_context
from nexy.modules.cli.constants import TEMPLATES_DIR
from nexy.modules.cli.migrations import alembic
from nexy.modules.cli.migrations.first import FirstMigration, Runner, run_first_migration
from nexy.modules.i18n import t

from .alias import DEFAULT_ALIAS, apply_alias
from .clone import GitClone
from .dependencies import DependencyInstaller
from .renderer import TemplateRenderer

_GITIGNORE_CONTENT = """__pycache__/
*.pyc
.env
.nexy/
nexy.db
*.db
node_modules/
dist/
.venv/
venv/
"""


def _fetch_template(
    template_name: str, dest: Path, config: dict[str, Any], use_github: bool, subdir: str
) -> None:
    with console.status(
        "[yellow]nexy[/yellow] » "
        + t("init.initializing", "Initializing {name}...").format(name=template_name),
        spinner="dots",
    ):
        if use_github:
            _clone_from_github(dest, subdir)
        else:
            _render_local_template(template_name, dest, config, dest.resolve().name)


def initialize_from_template(
    template_name: str,
    dest: Path,
    config: dict[str, Any] | None = None,
    use_github: bool = False,
    subdir: str = "",
) -> None:
    """Clone/render the template into *dest*, then run the post-init pipeline."""
    config = config or {}
    project_dir_name = dest.name if dest != Path(".") else None
    try:
        _fetch_template(template_name, dest, config, use_github, subdir)
        _run_post_init_pipeline(dest, config, project_dir_name)
    except Exception as e:
        console.print(
            "\n[red]nexy[/red] » "
            + t("init.error", "Initialization failed: {error}").format(error=str(e))
        )
        raise


def _clone_from_github(dest: Path, subdir: str) -> None:
    cloner = GitClone()
    cloner.clone(cloner.repo, cloner.branch, dest, subdir=subdir)


def _template_context(config: dict[str, Any], project_name: str) -> dict[str, Any]:
    """Everything the templates of one project are rendered with."""
    context = {
        "orm": config.get("orm", "None"),
        "db_url": config.get("db_url"),
        "database": config.get("database", "none"),
        "style": config.get("style", "tailwind"),
        "project_name": project_name,
        "project_type": config.get("project_type", "web"),
        "FBRouter": config.get("FBRouter", False),
        "useCSR": config.get("useCSR", False),
        "client_framework": config.get("client_framework", "none"),
        "nexy_version": __version__,
    }
    context.update(_markup_context(context["client_framework"], context["useCSR"]))
    context["utility_ui"] = _utility_ui(context)
    return context


def _render_local_template(
    template_name: str, dest: Path, config: dict[str, Any], project_name: str
) -> None:
    context = _template_context(config, project_name)
    exclude = _excluded_suffixes(context)
    TemplateRenderer(TEMPLATES_DIR / template_name, dest, context, exclude).render()
    _render_shared_files(template_name, dest, context)
    if config.get("agents", True):
        install_agent_files(dest, profile_from_context(context))

    generate_init_files(dest / "src")
    apply_alias(dest, config.get("alias", DEFAULT_ALIAS))


_FRAMEWORK_LABELS = {
    "none": "HTML",
    "react": "React",
    "preact": "Preact",
    "solid": "Solid",
    "vue": "Vue",
    "svelte": "Svelte",
}


def _markup_context(framework: str, client_routed: bool) -> dict[str, str]:
    """Names the shared markup needs: the class attribute of the syntax and the framework label."""
    return {
        # Only JSX in React spells it className. A server-rendered project writes HTML (.nexy)
        # even when React runs in its islands.
        "cls": "className" if framework == "react" and client_routed else "class",
        "fw_label": _FRAMEWORK_LABELS.get(framework, "HTML"),
    }


_UTILITY_STYLES = ("tailwind", "unocss")


def _utility_ui(context: dict[str, Any]) -> bool:
    """True for the utility-class starter: file-based routing with Tailwind or UnoCSS."""
    return bool(context["FBRouter"]) and context["style"] in _UTILITY_STYLES


def _excluded_suffixes(context: dict[str, Any]) -> set[str]:
    """Client routing owns the views, so no .nexy file is scaffolded."""
    return {".nexy"} if context.get("useCSR") else set()


def _render_shared_files(template_name: str, dest: Path, context: dict[str, Any]) -> None:
    """Render the _shared overlays that apply to this template type."""
    shared_dir = TEMPLATES_DIR / "_shared"
    exclude = _excluded_suffixes(context)
    if template_name.startswith("web-"):
        overlays = [("web-components", "src/components"), ("web", ".")]
        if context.get("utility_ui"):
            overlays.append(("web-ui", "."))
        for sub_dir, rel_dest in overlays:
            src = shared_dir / sub_dir
            if src.is_dir():
                tgt = dest / rel_dest if rel_dest != "." else dest
                TemplateRenderer(src, tgt, context, exclude).render()
        _place_web_assets(dest, template_name)
        _drop_unused_style_files(dest, context.get("style", "tailwind"))
    elif template_name.startswith("api-"):
        src = shared_dir / "api"
        if src.is_dir():
            TemplateRenderer(src, dest, context, exclude).render()

    _render_overlays(template_name, dest, context)


def _render_overlays(template_name: str, dest: Path, context: dict[str, Any]) -> None:
    """Render configs/ for every template type and fbr/ for *-fbr ones."""
    shared_dir = TEMPLATES_DIR / "_shared"
    exclude = _excluded_suffixes(context)
    cfg_src = shared_dir / "configs"
    if cfg_src.is_dir():
        # `src/configs/db.py` is rendered for every template, even when orm is None:
        # the file is conditionally written inside the Jinja2 by the template itself,
        # so without an ORM it is either a negligible file or a fragile empty route.
        TemplateRenderer(cfg_src, dest / "src" / "configs", context, exclude).render()

    if template_name.endswith("-fbr"):
        fbr_src = shared_dir / "fbr"
        if fbr_src.is_dir():
            TemplateRenderer(fbr_src, dest / "src", context, exclude).render()


def _drop_unused_style_files(dest: Path, style: str) -> None:
    """The UnoCSS config is rendered with the other web files; only UnoCSS projects keep it."""
    if style != "unocss":
        (dest / "uno.config.ts").unlink(missing_ok=True)


def _place_web_assets(dest: Path, template_name: str) -> None:
    """Move favicon.ico and globale.css to their final locations."""
    favicon = dest / "favicon.ico"
    if favicon.exists():
        if template_name.endswith("-fbr"):
            (dest / "src" / "routes").mkdir(parents=True, exist_ok=True)
            shutil.move(str(favicon), str(dest / "src" / "routes" / "favicon.ico"))
        else:
            (dest / "public").mkdir(parents=True, exist_ok=True)
            shutil.move(str(favicon), str(dest / "public" / "favicon.ico"))

    root_globale = dest / "globale.css"
    if root_globale.exists():
        (dest / "src").mkdir(parents=True, exist_ok=True)
        shutil.move(str(root_globale), str(dest / "src" / "globale.css"))


def generate_init_files(base: Path) -> None:
    """Auto-generate empty __init__.py in Python package dirs."""
    ensure_packages(base)


def _run_post_init_pipeline(
    dest: Path, config: dict[str, Any], project_dir_name: str | None
) -> None:
    """Install dependencies and run every post-render setup step."""
    orm = config.get("orm", "None")
    db_url = config.get("db_url")

    installer = DependencyInstaller(dest, orm=orm, database=config.get("database", "none"))
    installer.install_all()

    generate_post_init_files(dest, orm, db_url)

    migration = init_migration(orm, dest, db_url)
    _report_migration(migration)

    init_git(dest)

    cleanup_build_artifacts(dest)

    print_success_message(project_dir_name, orm, migrated=migration.done)


def generate_post_init_files(dest: Path, orm: str, db_url: str | None) -> None:
    """Create package __init__.py files and the .env after template rendering."""
    if orm != "None":
        for model_dir in [
            dest / "src" / "models",
            dest / "src" / "apps",
            dest / "src" / "apps" / "users",
        ]:
            if model_dir.exists() and any(f.suffix == ".py" for f in model_dir.iterdir()):
                (model_dir / "__init__.py").write_text("")
        for cfg_dir in [dest / "src" / "configs"]:
            if cfg_dir.exists():
                (cfg_dir / "__init__.py").write_text("")

    write_env_file(dest, db_url)


def write_env_file(dest: Path, db_url: str | None) -> None:
    """Create .env with DATABASE_URL when the config provides one."""
    if not db_url:
        return
    env_file = dest / ".env"
    if not env_file.exists():
        env_file.write_text(f"DATABASE_URL={db_url}\n")


def init_git(dest: Path) -> None:
    gitignore = dest / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(_GITIGNORE_CONTENT)
    git_exe = shutil.which("git")
    if not git_exe:
        return
    with suppress(OSError, subprocess.SubprocessError):
        subprocess.run(
            [git_exe, "init"],
            cwd=dest,
            check=True,
            capture_output=True,
        )  # nosec B603/B607 - resolved via shutil.which, fixed argv


_MIGRATION_TOOLS = {"SQLModel": "alembic", "SQLAlchemy": "alembic", "Tortoise-ORM": "aerich"}


def uv_run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run a tool of the new project's environment through uv, keeping what it printed."""
    uv = shutil.which("uv") or "uv"
    return subprocess.run(  # nosec B603 B607
        [uv, "run", *args], cwd=cwd, capture_output=True, text=True, check=False
    )


def _scaffold_migration_tool(
    tool: str, orm: str, dest: Path, db_url: str | None, run: Runner
) -> bool:
    """Initialize the migration tool in *dest*; Alembic also gets Nexy's `env.py` and the URL.

    Returns whether the tool left its files behind: without them there is nothing to migrate.
    """
    if tool == "aerich":
        run(["aerich", "init", "-t", "src.configs.db.TORTOISE_ORM"], dest)
        return (dest / "migrations").exists()
    run(["alembic", "init", "alembic"], dest)
    if not (dest / "alembic").exists():
        return False
    alembic.render_env(dest / "alembic", orm, alembic.models_module(dest))
    if db_url:
        alembic.write_ini_url(dest, db_url)
    return True


def init_migration(
    orm: str, dest: Path, db_url: str | None, run: Runner = uv_run
) -> FirstMigration:
    """Set alembic/aerich up when the config picked an ORM, then create the first migration.

    The tables are created when the database URL is known and answers; otherwise the result says
    why not, and `nx new` tells the developer to run `nexy migrate`.
    """
    tool = _MIGRATION_TOOLS.get(orm)
    if tool is None:
        return FirstMigration(False)
    message = t("init.migration_tool", "Initializing {tool}...").format(tool=tool)
    with console.status(tagged("nexy", message, "yellow"), spinner="dots"):
        if not _scaffold_migration_tool(tool, orm, dest, db_url, run):
            return FirstMigration(False, f"{tool} was not initialised")
        return run_first_migration(tool, dest, db_url, run)


def _report_migration(migration: FirstMigration) -> None:
    """Say that the tables exist, or why they were not created; nothing when it was not tried."""
    if migration.done:
        done = t("init.migrated", "Created the first migration and the tables")
        console.print(tagged("nexy", done, "green"))
    elif migration.problem:
        skipped = t("init.migration_skipped", "The tables were not created: {problem}")
        console.print(tagged("nexy", skipped.format(problem=migration.problem), "yellow"))


def cleanup_build_artifacts(dest: Path) -> None:
    for folder_name in ["build", "dist"]:
        folder_path = dest / folder_name
        if folder_path.exists() and folder_path.is_dir():
            shutil.rmtree(folder_path, ignore_errors=True)


def print_success_message(
    project_dir_name: str | None = None, orm: str = "None", migrated: bool = False
) -> None:
    _print_next_steps(project_dir_name, orm, migrated)


def _print_next_steps(project_dir_name: str | None, orm: str, migrated: bool) -> None:
    console.print("\n" + t("init.next_steps", "Next steps"))

    if project_dir_name:
        launcher.step(f"cd {project_dir_name}")

    launcher.step(
        _activate_command(), t("init.step_activate_venv", "Activate the virtual environment")
    )
    if orm != "None" and not migrated:
        _print_migration_steps()
    launcher.step("nexy dev", t("init.step_run_dev", "Start the development server"))
    launcher.step("nexy --help", t("init.step_help", "Explore available commands"))


def _print_migration_steps() -> None:
    """A new project has models but no tables: the users page fails until they exist."""
    create = t("init.step_migrate_create", "Create the first migration")
    apply = t("init.step_migrate_apply", "Create the tables in the database")
    launcher.step('nexy migrate -m "create tables"', create)
    launcher.step("nexy migrate --upgrade", apply)


def _activate_command() -> str:
    if sys.platform == "win32":
        return ".venv\\Scripts\\activate"
    return "source .venv/bin/activate"
