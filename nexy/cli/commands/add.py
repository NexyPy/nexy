import urllib.request
from pathlib import Path

import typer

from nexy.core.config import Config
from nexy.helpers.common.console import console
from nexy.helpers.fs.path import PathUtil
from nexy.helpers.imports.component import framework_from_extension, wrap_component_script
from nexy.helpers.init.dependencies import install_packages
from nexy.helpers.init.registry import COMPONENT_REGISTRY
from nexy.i18n import t

_ADD_HELP_COMPONENTS = t("add.help_components", "Components to add (registry names or URLs)")
_ADD_HELP_UI = t("add.help_ui", "Force treatment as UI components")
_ADD_HELP_URL = t("add.help_url", "Force treatment as URLs")
_ADD_HELP_ALL = t("add.help_all", "Add all available components from registry")

Resolved = tuple[str, str, str, set[str]]


def fetch_remote_component(url: str) -> str | None:
    """Fetches component source from a remote URL.

    Only http(s) is accepted: urlopen would otherwise happily follow
    file:// or custom schemes and read local files.
    """
    if not url.startswith(("http://", "https://")):
        error_msg = f"[red]{t('add.error', 'Error:')}[/red] Only http(s) URLs are supported."
        console.print(error_msg)
        return None
    try:
        status_msg = (
            f"[yellow]nexy[/yellow] \u00bb "
            f"{t('add.fetching', 'Fetching remote component from')} {url}..."
        )
        # Scheme already restricted to http(s) by the guard above.
        status_ctx = console.status(status_msg, spinner="dots")
        with status_ctx, urllib.request.urlopen(url) as response:  # nosec B310
            text: str = response.read().decode("utf-8")
            return text
    except Exception as e:
        error_msg = (
            f"[red]{t('add.error', 'Error:')}[/red] "
            f"{t('add.fetch_failed', 'Failed to fetch component from')} {url}: {e}"
        )
        console.print(error_msg)
        return None


def add(
    components: list[str] = typer.Argument(None, help=_ADD_HELP_COMPONENTS),
    ui: bool = typer.Option(False, "--ui", help=_ADD_HELP_UI),
    url: bool = typer.Option(False, "--url", help=_ADD_HELP_URL),
    all: bool = typer.Option(False, "--all", "-a", help=_ADD_HELP_ALL),
) -> None:
    config = Config()

    framework = "react"
    use_ff = config.useFF
    if use_ff:
        # A list config selects the first framework (same convention as _normalize_ff).
        framework = (use_ff[0] if isinstance(use_ff, list) else use_ff).name.lower()

    if all:
        components = list(COMPONENT_REGISTRY.keys())

    if not components:
        _print_available_components()
        raise typer.Exit()

    target_dir = Path("src/components/ui")
    target_dir.mkdir(parents=True, exist_ok=True)

    all_deps: set[str] = set()
    for item in components:
        resolved = _resolve_component(item, framework, url)
        if resolved is None:
            continue
        name, content, fw, deps = resolved
        all_deps.update(deps)
        _write_nexy_component(target_dir, name, content, fw)

    if all_deps:
        install_packages(list(all_deps))


def _print_available_components() -> None:
    usage_msg = (
        f"[yellow]{t('add.usage', 'Usage:')}[/yellow] "
        f"{t('add.usage_text', 'nexy add [COMPONENT_NAME or URL]...')}"
    )
    console.print(usage_msg)
    available_msg = (
        f"{t('add.available', 'Available UI components:')} "
        f"[cyan]{', '.join(COMPONENT_REGISTRY.keys())}[/cyan]"
    )
    console.print(available_msg)


def _resolve_component(item: str, framework: str, force_url: bool) -> Resolved | None:
    """Resolve one CLI entry into (name, content, framework, dependencies)."""
    is_url = item.startswith(("http://", "https://")) or force_url
    if is_url:
        return _resolve_remote_component(item)
    return _resolve_registry_component(item, framework)


def _resolve_remote_component(url: str) -> Resolved | None:
    content = fetch_remote_component(url)
    if not content:
        return None
    url_path = Path(url)
    return url_path.stem, content, framework_from_extension(url_path.suffix), set()


def _resolve_registry_component(item: str, framework: str) -> Resolved | None:
    entry = COMPONENT_REGISTRY.get(item.lower())
    if entry is None:
        not_found_template = t("add.not_found", "Component '{name}' not found in registry.")
        not_found_msg = (
            f"[red]{t('add.error', 'Error:')}[/red] {not_found_template.format(name=item)}"
        )
        console.print(not_found_msg)
        return None

    fw = framework if framework in entry.framework_code else next(iter(entry.framework_code))
    return entry.name, entry.framework_code[fw], fw, set(entry.dependencies)


def _write_nexy_component(target_dir: Path, name: str, content: str, framework: str) -> None:
    """Write a .nexy component file, skipping when it already exists."""
    file_path = target_dir / f"{name}.nexy"

    if file_path.exists():
        skip_msg = (
            f"[yellow]{t('add.skipping', 'Skipping:')}[/yellow] "
            f"{file_path} {t('add.exists', 'already exists.')}"
        )
        console.print(skip_msg)
        return

    try:
        PathUtil.write_file(file_path, wrap_component_script(content, framework))
        console.print(f"[green]{t('add.added', 'Added:')}[/green] {file_path}")
    except Exception as e:
        error_msg = (
            f"[red]{t('add.error', 'Error:')}[/red] "
            f"{t('add.write_failed', 'Failed to write')} {file_path}: {e}"
        )
        console.print(error_msg)
