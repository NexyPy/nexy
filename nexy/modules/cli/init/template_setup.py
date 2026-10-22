"""Template initialization: clone/render, shared overlays and the post-init pipeline."""

import re
import shutil
import subprocess  # nosec B404
import sys
from contextlib import suppress
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from nexy.helpers.common.console import console
from nexy.modules.cli.constants import TEMPLATES_DIR
from nexy.modules.i18n import t

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
    project_name = project_dir_name or dest.resolve().name

    try:
        with console.status(
            "[yellow]nexy[/yellow] » "
            + t("init.initializing", "Initializing {name}...").format(name=template_name),
            spinner="dots",
        ):
            if use_github:
                _clone_from_github(dest, subdir)
            else:
                _render_local_template(template_name, dest, config, project_name)

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


def _render_local_template(
    template_name: str, dest: Path, config: dict[str, Any], project_name: str
) -> None:
    from nexy.modules.i18n import _detect_locale

    context = {
        "orm": config.get("orm", "None"),
        "db_url": config.get("db_url"),
        "project_name": project_name,
        "project_type": config.get("project_type", "web"),
        "FBRouter": config.get("FBRouter", False),
        "client_framework": config.get("client_framework", "none"),
        "locale": _detect_locale(),
    }
    TemplateRenderer(TEMPLATES_DIR / template_name, dest, context).render()
    _render_shared_files(template_name, dest, context)

    generate_init_files(dest / "src")


def _render_shared_files(template_name: str, dest: Path, context: dict[str, Any]) -> None:
    """Render the _shared overlays that apply to this template type."""
    shared_dir = TEMPLATES_DIR / "_shared"
    if template_name.startswith("web-"):
        for sub_dir, rel_dest in [
            ("web-components", "src/components"),
            ("web", "."),
        ]:
            src = shared_dir / sub_dir
            if src.is_dir():
                tgt = dest / rel_dest if rel_dest != "." else dest
                TemplateRenderer(src, tgt, context).render()
        _place_web_assets(dest, template_name)
    elif template_name.startswith("api-"):
        src = shared_dir / "api"
        if src.is_dir():
            TemplateRenderer(src, dest, context).render()

    _render_overlays(template_name, dest, context)


def _render_overlays(template_name: str, dest: Path, context: dict[str, Any]) -> None:
    """Render configs/ for every template type and fbr/ for *-fbr ones."""
    shared_dir = TEMPLATES_DIR / "_shared"
    cfg_src = shared_dir / "configs"
    if cfg_src.is_dir():
        TemplateRenderer(cfg_src, dest / "src" / "configs", context).render()

    if template_name.endswith("-fbr"):
        fbr_src = shared_dir / "fbr"
        if fbr_src.is_dir():
            TemplateRenderer(fbr_src, dest / "src", context).render()


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
    dirs_to_check = [base]
    dirs_to_check.extend(sorted(base.rglob("*")))
    for dir_path in dirs_to_check:
        if dir_path.is_dir() and not (dir_path / "__init__.py").exists():
            is_top_src = dir_path == base
            has_py = any(f.suffix == ".py" for f in dir_path.iterdir())
            has_nexy = any(f.suffix == ".nexy" for f in dir_path.iterdir())
            if is_top_src or has_py or has_nexy:
                (dir_path / "__init__.py").write_text("")


def _run_post_init_pipeline(
    dest: Path, config: dict[str, Any], project_dir_name: str | None
) -> None:
    """Install dependencies and run every post-render setup step."""
    orm = config.get("orm", "None")
    db_url = config.get("db_url")

    installer = DependencyInstaller(dest, orm=orm)
    installer.install_all()

    generate_post_init_files(dest, orm, db_url)

    init_migration(orm, dest, db_url)

    init_git(dest)

    cleanup_build_artifacts(dest)

    print_success_message(project_dir_name)


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


def init_migration(orm: str, dest: Path, db_url: str | None) -> None:
    """Scaffold alembic/aerich when the config picked an ORM."""
    tool = ""
    if orm in ("SQLModel", "SQLAlchemy"):
        tool = "alembic"
    elif orm == "Tortoise-ORM":
        tool = "aerich"
    if not tool:
        return

    with console.status(
        f"[yellow]nexy[/yellow] » Initializing {tool}...",
        spinner="dots",
    ):
        if tool == "aerich":
            uv_exe = shutil.which("uv") or "uv"
            subprocess.run(
                [uv_exe, "run", tool, "init", "-t", "src.configs.db.TORTOISE_ORM"],
                cwd=dest,
                capture_output=True,
            )  # nosec B603/B607
            return
        uv_exe = shutil.which("uv") or "uv"
        subprocess.run(
            [uv_exe, "run", tool, "init", tool],
            cwd=dest,
            capture_output=True,
        )  # nosec B603/B607
        alembic_dir = dest / "alembic"
        if alembic_dir.exists():
            _render_alembic_env(alembic_dir, orm)
            if db_url:
                write_alembic_ini_url(dest, db_url)


def _render_alembic_env(alembic_dir: Path, orm: str) -> None:
    loader = FileSystemLoader(str(TEMPLATES_DIR / "alembic"))
    # Renders a Python code template (env.py), not HTML; autoescaping
    # here would corrupt the generated Python. See SECURITY.md.
    env = Environment(loader=loader)  # nosec B701
    env_path = alembic_dir / "env.py"
    env_path.write_text(env.get_template("env.py.jinja2").render(orm=orm))


def write_alembic_ini_url(dest: Path, db_url: str) -> None:
    alembic_ini = dest / "alembic.ini"
    if not alembic_ini.exists():
        return
    content = alembic_ini.read_text(encoding="utf-8")
    content = re.sub(
        r"^sqlalchemy\.url\s*=.*",
        f"sqlalchemy.url = {db_url}",
        content,
        flags=re.MULTILINE,
    )
    alembic_ini.write_text(content, encoding="utf-8")


def cleanup_build_artifacts(dest: Path) -> None:
    for folder_name in ["build", "dist"]:
        folder_path = dest / folder_name
        if folder_path.exists() and folder_path.is_dir():
            shutil.rmtree(folder_path, ignore_errors=True)


def print_success_message(project_dir_name: str | None = None) -> None:
    console.print(
        "\n[green]nexy[/green] \u00bb "
        + t("init.success_title", "Project initialized successfully!")
    )
    _print_next_steps(project_dir_name)


def _print_next_steps(project_dir_name: str | None) -> None:
    console.print("\n" + t("init.next_steps", "Next steps:"))

    step = 1
    if project_dir_name:
        console.print(f"  {step}. [cyan]cd {project_dir_name}[/cyan]")
        step += 1
        activate_msg = t("init.step_activate_venv", "Activate the virtual environment")
        console.print(f"  {step}. [cyan]{_activate_command()}[/cyan] {activate_msg}")
        step += 1

    dev_msg = t("init.step_run_dev", "Start the development server")
    console.print(f"  {step}. [cyan]nexy dev[/cyan] - {dev_msg}")
    help_msg = t("init.step_help", "Explore available commands")
    console.print(f"  {step + 1}. [cyan]nexy --help[/cyan] - {help_msg}")


def _activate_command() -> str:
    if sys.platform == "win32":
        return ".venv\\Scripts\\activate"
    return "source .venv/bin/activate"
