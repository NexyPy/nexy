import hashlib
import urllib.error
import urllib.request
from pathlib import Path
from typing import cast

import typer
from rich.markup import escape

from nexy.core.config import Config
from nexy.core.framework_rules import as_list
from nexy.helpers.common.console import console
from nexy.helpers.common.messages import error, warning
from nexy.helpers.common.tasks import waiting
from nexy.helpers.fs.path import PathUtil
from nexy.helpers.imports.component import framework_from_extension, wrap_component_script
from nexy.modules.cli.add.client import RegistryModuleClient
from nexy.modules.cli.add.installer import InstallError, ModuleInstaller
from nexy.modules.cli.add.reference import ModuleReference, parse_reference
from nexy.modules.cli.add.urls import is_allowed_url
from nexy.modules.cli.deployment import GITIGNORE_LINES, PLATFORM_FILES
from nexy.modules.cli.init.dependencies import install_packages
from nexy.modules.cli.init.registry import COMPONENT_REGISTRY
from nexy.modules.i18n import t

_ADD_HELP_COMPONENTS = t("add.help_components", "Components to add (registry names or URLs)")
_ADD_HELP_UI = t("add.help_ui", "Force treatment as UI components")
_ADD_HELP_URL = t("add.help_url", "Force treatment as URLs")
_ADD_HELP_SHA = t("add.help_sha", "Expected SHA-256 of a remote component (aborts on mismatch)")
_ADD_HELP_ALL = t("add.help_all", "Add all available components from registry")
_ADD_HELP_MIGRATE = t("add.help_migrate", "Run declared migrations after the install")

Resolved = tuple[str, str, str, set[str]]


_MAX_REMOTE_BYTES = 1_000_000
_REMOTE_TIMEOUT = 15


class _SafeRedirect(urllib.request.HTTPRedirectHandler):
    """Refuse redirects that would leave https (or loopback http)."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        if not is_allowed_url(newurl):
            raise urllib.error.URLError(f"redirect to a disallowed URL: {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _download(url: str) -> bytes:
    """The body of *url*, at most `_MAX_REMOTE_BYTES`; redirects are re-checked."""
    fetching = t("add.fetching", "Fetching remote component from {url}...")
    # Scheme and host validated by _is_allowed_url; redirects re-checked by _SafeRedirect.
    opener = urllib.request.build_opener(_SafeRedirect)
    with (
        waiting(fetching.format(url=url)),
        opener.open(url, timeout=_REMOTE_TIMEOUT) as response,  # nosec B310
    ):
        raw: bytes = response.read(_MAX_REMOTE_BYTES + 1)
    if len(raw) > _MAX_REMOTE_BYTES:
        raise ValueError("component is larger than 1 MB")
    return raw


def _check_digest(raw: bytes, expected_sha256: str | None) -> str:
    """The SHA-256 of *raw*; a different one than *expected_sha256* is an error."""
    digest = hashlib.sha256(raw).hexdigest()
    if expected_sha256 and digest != expected_sha256.lower():
        raise ValueError(f"sha256 mismatch: expected {expected_sha256}, got {digest}")
    return digest


def fetch_remote_component(url: str, expected_sha256: str | None = None) -> str | None:
    """Fetch component source from a remote URL.

    The code ends up in your project, so the download is constrained: https
    only (http for loopback), a timeout, a 1 MB cap, and an optional SHA-256
    pin. The digest of what was fetched is always printed so it can be pinned.
    """
    if not is_allowed_url(url):
        error(t("add.https_only", "Only https:// URLs are supported."))
        return None
    try:
        raw = _download(url)
        console.print(f"[dim]sha256 {_check_digest(raw, expected_sha256)}[/dim]")
        return raw.decode("utf-8")
    except Exception as failure:
        failed = t("add.fetch_failed", "Failed to fetch component from {url}")
        error(failed.format(url=escape(url)), cause=escape(str(failure)))
        return None


def _configured_framework() -> str:
    """The framework of the project (the first when several are listed); React by default."""
    frameworks = as_list(Config().useFF)
    return frameworks[0].name.lower() if frameworks else "react"


def _add_components(components: list[str], is_url: bool, sha256: str | None) -> set[str]:
    """Write each component into `src/components/ui`; the packages they need are returned."""
    target_dir = Path("src/components/ui")
    target_dir.mkdir(parents=True, exist_ok=True)
    needed: set[str] = set()
    framework = _configured_framework()
    for item in components:
        resolved = _resolve_component(item, framework, is_url, sha256)
        if resolved is not None:
            name, content, fw, deps = resolved
            needed.update(deps)
            _write_nexy_component(target_dir, name, content, fw)
    return needed


def add(
    components: list[str] = typer.Argument(None, help=_ADD_HELP_COMPONENTS),
    ui: bool = typer.Option(False, "--ui", help=_ADD_HELP_UI),
    url: bool = typer.Option(False, "--url", help=_ADD_HELP_URL),
    all: bool = typer.Option(False, "--all", "-a", help=_ADD_HELP_ALL),
    sha256: str = typer.Option(None, "--sha256", help=_ADD_HELP_SHA),
    migrate: bool = typer.Option(False, "--migrate", help=_ADD_HELP_MIGRATE),
) -> None:
    if _add_module_arguments(components, ui, url, all, sha256, migrate):
        return
    if components and components[0].lower() in PLATFORM_FILES:
        if ui or url or all or sha256:
            error(t("add.usage_text", "nexy add [COMPONENT_NAME or URL]..."))
        else:
            _add_platform(components)
        return
    if all:
        components = list(COMPONENT_REGISTRY.keys())
    if not components:
        _print_available_components()
        raise typer.Exit
    needed = _add_components(components, url, sha256)
    if needed:
        install_packages(list(needed))


def _add_module_arguments(
    components: list[str] | None,
    ui: bool,
    url: bool,
    all: bool,
    sha256: str | None,
    migrate: bool,
) -> bool:
    """Install namespaced modules; say whether the arguments named modules."""
    if not components or not any(item.startswith("@") for item in components):
        return False
    if ui or url or all or sha256:
        error(t("add.usage_text", "nexy add [COMPONENT_NAME or URL]..."))
        return True
    _add_modules(components, migrate)
    return True


def _add_modules(components: list[str], migrate: bool) -> None:
    """Install each module, reporting a bad reference or a failed install."""
    if any(not item.startswith("@") for item in components):
        error(t("add.usage_text", "nexy add [COMPONENT_NAME or URL]..."))
        return
    try:
        references = [cast(ModuleReference, parse_reference(item)) for item in components]
    except ValueError as problem:
        error(str(problem))
        return
    installer = _module_installer()
    for reference in references:
        try:
            installer.install(reference, migrate=migrate)
        except InstallError as problem:
            error(str(problem))
            return


def _module_installer() -> ModuleInstaller:
    """Build an installer for the registry of the current project."""
    client = RegistryModuleClient(Config().useModuleRegistry)
    return ModuleInstaller(client)


def _add_platform(names: list[str]) -> None:
    """Write the files of one deployment platform; never mix it with components."""
    if len(names) != 1:
        error(t("add.usage_text", "nexy add [COMPONENT_NAME or URL]..."))
        return
    files = PLATFORM_FILES[names[0].lower()]
    for path, content in files.items():
        _write_platform_file(path, content)
    _add_gitignore_lines(GITIGNORE_LINES)


def _write_platform_file(path: Path, content: str) -> None:
    """Write a platform file, keeping an existing one and reporting each new file."""
    if path.exists():
        warning(t("add.exists", "Skipping: {path} already exists.").format(path=path))
        return
    PathUtil.write_file(path, content)
    console.print(f" [green]+[/green] {escape(str(path))}")


def _add_gitignore_lines(lines: tuple[str, ...]) -> None:
    """Append the missing ignore lines, once each, keeping the rest of the file."""
    ignore = Path(".gitignore")
    existing = ignore.read_text(encoding="utf-8").splitlines() if ignore.exists() else []
    missing = [line for line in lines if line not in existing]
    if missing:
        PathUtil.write_file(ignore, "\n".join([*existing, *missing]) + "\n")


def _print_available_components() -> None:
    usage_msg = (
        f"[yellow]{t('add.usage', 'Usage:')}[/yellow] "
        f"{t('add.usage_text', 'nexy add [COMPONENT_NAME or URL]...')}"
    )
    console.print(usage_msg)
    names = f"[cyan]{', '.join(COMPONENT_REGISTRY.keys())}[/cyan]"
    available_msg = t("add.available", "Available UI components: {names}").format(names=names)
    console.print(available_msg)


def _resolve_component(
    item: str, framework: str, force_url: bool, sha256: str | None = None
) -> Resolved | None:
    """Resolve one CLI entry into (name, content, framework, dependencies)."""
    is_url = item.startswith(("http://", "https://")) or force_url
    if is_url:
        return _resolve_remote_component(item, sha256)
    return _resolve_registry_component(item, framework)


def _resolve_remote_component(url: str, sha256: str | None = None) -> Resolved | None:
    content = fetch_remote_component(url, sha256)
    if not content:
        return None
    url_path = Path(url)
    return url_path.stem, content, framework_from_extension(url_path.suffix), set()


def _resolve_registry_component(item: str, framework: str) -> Resolved | None:
    entry = COMPONENT_REGISTRY.get(item.lower())
    if entry is None:
        not_found = t("add.not_found", "Component '{name}' not found in registry.")
        error(not_found.format(name=escape(item)))
        return None

    fw = framework if framework in entry.framework_code else next(iter(entry.framework_code))
    return entry.name, entry.framework_code[fw], fw, set(entry.dependencies)


def _write_nexy_component(target_dir: Path, name: str, content: str, framework: str) -> None:
    """Write a .nexy component file, skipping when it already exists."""
    file_path = target_dir / f"{name}.nexy"

    if file_path.exists():
        warning(t("add.exists", "Skipping: {path} already exists.").format(path=file_path))
        return

    try:
        PathUtil.write_file(file_path, wrap_component_script(content, framework))
        console.print(f" [green]+[/green] {escape(str(file_path))}")
    except Exception as problem:
        failed = t("add.write_failed", "Failed to write {path}")
        error(failed.format(path=file_path), cause=escape(str(problem)))
