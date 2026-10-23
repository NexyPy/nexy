"""Scaffold every Nexy project type into examples/ using the `nexy new` pipeline.

Two sources are used:

* the pre-rendered templates published on GitHub, cloned by `nexy new -t`;
* the templates bundled with the package, rendered with the same configuration
  the interactive questionnaire produces (CSR and ORM variants).

Dependencies are deliberately not installed: examples are committed source
snapshots, not ready-to-run environments. Run `uv sync` and `pnpm install`
(or `bun install`) inside an example before `nexy dev`.

Usage:
    python scripts/scaffold_examples.py [--force]
"""

import argparse
import os
import shutil
from pathlib import Path
from typing import Any

from nexy.modules.cli.init import dependencies, template_setup
from nexy.modules.cli.init.project import InitProject

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"

# (template name on GitHub, destination relative to examples/)
GITHUB_TEMPLATES: tuple[tuple[str, str], ...] = (
    ("api-fbr", "FBR/api/minimal"),
    ("api-modular", "Modular/api/minimal"),
    ("web-fbr-none", "FBR/web/basics/none"),
    ("web-fbr-react", "FBR/web/basics/react"),
    ("web-fbr-vue", "FBR/web/basics/vue"),
    ("web-fbr-svelte", "FBR/web/basics/svelte"),
    ("web-fbr-solid", "FBR/web/basics/solid"),
    ("web-fbr-preact", "FBR/web/basics/preact"),
    ("web-modular-none", "Modular/web/basics/none"),
    ("web-modular-react", "Modular/web/basics/react"),
    ("web-modular-vue", "Modular/web/basics/vue"),
    ("web-modular-svelte", "Modular/web/basics/svelte"),
    ("web-modular-solid", "Modular/web/basics/solid"),
    ("web-modular-preact", "Modular/web/basics/preact"),
)

_DB_URLS = {
    "SQLModel": "sqlite:///dev.db",
    "SQLAlchemy": "sqlite:///dev.db",
    "Tortoise-ORM": "sqlite://dev.db",
}

_ORM_DEPENDENCIES: dict[str, tuple[str, ...]] = {
    "SQLModel": ("sqlmodel", "alembic", "python-dotenv"),
    "SQLAlchemy": ("sqlalchemy", "alembic", "python-dotenv"),
    "Tortoise-ORM": ("tortoise-orm", "aiosqlite", "aerich", "python-dotenv"),
}


def _web(
    *,
    framework: str,
    csr: bool = False,
    orm: str = "None",
    fbr: bool = True,
) -> dict[str, Any]:
    """Configuration for a web project, matching the interactive prompt keys."""
    return {
        "project_type": "web",
        "FBRouter": fbr,
        "useCSR": csr,
        "client_framework": framework,
        "orm": orm,
        "db_url": _DB_URLS.get(orm),
    }


def _api(*, fbr: bool, orm: str) -> dict[str, Any]:
    """Configuration for an API project with an ORM."""
    return {
        "project_type": "api",
        "FBRouter": fbr,
        "useCSR": False,
        "client_framework": "none",
        "orm": orm,
        "db_url": _DB_URLS[orm],
    }


# (label, bundled template, destination relative to examples/, config)
LOCAL_VARIANTS: tuple[tuple[str, str, str, dict[str, Any]], ...] = (
    ("web-fbr-react-csr", "web-fbr", "FBR/web/CSR/react", _web(framework="react", csr=True)),
    ("web-fbr-vue-csr", "web-fbr", "FBR/web/CSR/vue", _web(framework="vue", csr=True)),
    ("web-fbr-svelte-csr", "web-fbr", "FBR/web/CSR/svelte", _web(framework="svelte", csr=True)),
    ("web-fbr-solid-csr", "web-fbr", "FBR/web/CSR/solid", _web(framework="solid", csr=True)),
    ("web-fbr-preact-csr", "web-fbr", "FBR/web/CSR/preact", _web(framework="preact", csr=True)),
    ("api-fbr-sqlmodel", "api-fbr", "FBR/api/sqlmodel", _api(fbr=True, orm="SQLModel")),
    ("api-fbr-sqlalchemy", "api-fbr", "FBR/api/sqlalchemy", _api(fbr=True, orm="SQLAlchemy")),
    ("api-fbr-tortoise", "api-fbr", "FBR/api/tortoise", _api(fbr=True, orm="Tortoise-ORM")),
    (
        "api-modular-sqlmodel",
        "api-modular",
        "Modular/api/sqlmodel",
        _api(fbr=False, orm="SQLModel"),
    ),
    (
        "api-modular-sqlalchemy",
        "api-modular",
        "Modular/api/sqlalchemy",
        _api(fbr=False, orm="SQLAlchemy"),
    ),
    (
        "api-modular-tortoise",
        "api-modular",
        "Modular/api/tortoise",
        _api(fbr=False, orm="Tortoise-ORM"),
    ),
    (
        "web-fbr-react-sqlmodel",
        "web-fbr",
        "FBR/web/basics/react-sqlmodel",
        _web(framework="react", orm="SQLModel"),
    ),
    (
        "web-modular-react-sqlalchemy",
        "web-modular",
        "Modular/web/basics/react-sqlalchemy",
        _web(framework="react", orm="SQLAlchemy", fbr=False),
    ),
)


def _skip_dependency_install(_installer: object) -> None:
    """Keep examples source-only: no .venv or node_modules in the repository."""


def _skip_migration(_orm: str, _dest: Path, _db_url: str | None) -> None:
    """Examples ship without generated Alembic/Aerich directories."""


def _add_python_dependencies(dest: Path, packages: tuple[str, ...]) -> None:
    """Declare ORM dependencies without running `uv add`."""
    pyproject = dest / "pyproject.toml"
    text = pyproject.read_text(encoding="utf-8")
    marker = "dependencies = ["
    start = text.index(marker)
    end = text.index("]", start)
    declared = text[start:end]
    missing = tuple(package for package in packages if f'"{package}"' not in declared)
    if not missing:
        return

    before = text[:end]
    if not before.endswith("\n"):
        before += "\n"
    added = "".join(f'    "{package}",\n' for package in missing)
    pyproject.write_text(before + added + text[end:], encoding="utf-8")


def _finalize_orm_example(dest: Path, config: dict[str, Any]) -> None:
    """Add ORM dependencies, an .env.example and a database section to the README."""
    orm = str(config.get("orm", "None"))
    if orm == "None":
        return

    db_url = str(config["db_url"])
    _add_python_dependencies(dest, _ORM_DEPENDENCIES[orm])
    (dest / ".env.example").write_text(f"DATABASE_URL={db_url}\n", encoding="utf-8")
    (dest / ".env").unlink(missing_ok=True)

    readme = dest / "README.md"
    if not readme.exists():
        return
    text = readme.read_text(encoding="utf-8").rstrip()
    readme.write_text(
        f"{text}\n\n## Database\n\n"
        f"This example uses **{orm}**. `.env.example` defaults to\n"
        f"`DATABASE_URL={db_url}`; copy it to `.env` and change the URL for\n"
        "PostgreSQL or MySQL (add the matching driver to `pyproject.toml`).\n\n"
        "Migration directories are not included: initialize Alembic or Aerich\n"
        "before the first schema change.\n",
        encoding="utf-8",
    )


def _remove_nested_repository(dest: Path) -> None:
    shutil.rmtree(dest / ".git", ignore_errors=True)


def scaffold_github_template(template: str, dest_rel: str, force: bool) -> bool:
    dest = EXAMPLES / dest_rel
    if dest.exists():
        if not force:
            print(f"[examples] skip {dest_rel}: already exists (use --force to regenerate)")
            return False
        shutil.rmtree(dest)

    InitProject().run(
        template=template,
        project_dir=dest_rel,
        command="new",
        show_title=False,
    )
    _remove_nested_repository(dest)
    print(f"[examples] {template} -> {dest_rel}: ok")
    return True


def scaffold_local_variant(
    name: str,
    template: str,
    dest_rel: str,
    config: dict[str, Any],
    force: bool,
) -> bool:
    dest = EXAMPLES / dest_rel
    if dest.exists():
        if not force:
            print(f"[examples] skip {dest_rel}: already exists (use --force to regenerate)")
            return False
        shutil.rmtree(dest)

    template_setup.initialize_from_template(template, dest, config)
    _remove_nested_repository(dest)
    _finalize_orm_example(dest, config)
    print(f"[examples] {name} -> {dest_rel}: ok")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Regenerate existing examples")
    args = parser.parse_args()

    dependencies.DependencyInstaller.install_all = _skip_dependency_install  # type: ignore[method-assign]
    template_setup.init_migration = _skip_migration  # type: ignore[assignment]

    EXAMPLES.mkdir(exist_ok=True)
    previous = Path.cwd()
    # Run from examples/: GitClone stashes the surrounding repository's .git
    # when the process runs at a repo root, which examples must never trigger.
    os.chdir(EXAMPLES)
    try:
        created = [
            scaffold_github_template(template, dest_rel, args.force)
            for template, dest_rel in GITHUB_TEMPLATES
        ]
        created.extend(
            scaffold_local_variant(name, template, dest_rel, config, args.force)
            for name, template, dest_rel, config in LOCAL_VARIANTS
        )
    finally:
        os.chdir(previous)

    total = len(GITHUB_TEMPLATES) + len(LOCAL_VARIANTS)
    print(f"[examples] {sum(created)}/{total} generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
