import hashlib
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

import typer

from nexy.core.config import Config
from nexy.helpers.common.console import console
from nexy.helpers.common.log_line import tagged
from nexy.helpers.fs.path import PathUtil
from nexy.helpers.imports.component import framework_from_extension, wrap_component_script
from nexy.modules.cli.init.dependencies import install_packages
from nexy.modules.cli.init.registry import COMPONENT_REGISTRY
from nexy.modules.i18n import t

_ADD_HELP_COMPONENTS = t("add.help_components", "Components to add (registry names or URLs)")
_ADD_HELP_UI = t("add.help_ui", "Force treatment as UI components")
_ADD_HELP_URL = t("add.help_url", "Force treatment as URLs")
_ADD_HELP_SHA = t("add.help_sha", "Expected SHA-256 of a remote component (aborts on mismatch)")
_ADD_HELP_ALL = t("add.help_all", "Add all available components from registry")

Resolved = tuple[str, str, str, set[str]]


_MAX_REMOTE_BYTES = 1_000_000
_REMOTE_TIMEOUT = 15
_LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


def _is_allowed_url(url: str) -> bool:
    """https only; plain http is tolerated for loopback development servers."""
    parts = urlsplit(url)
    if parts.scheme == "https":
        return bool(parts.hostname)
    return parts.scheme == "http" and parts.hostname in _LOCAL_HOSTS


class _SafeRedirect(urllib.request.HTTPRedirectHandler):
    """Refuse redirects that would leave https (or loopback http)."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        if not _is_allowed_url(newurl):
            raise urllib.error.URLError(f"redirect to a disallowed URL: {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_remote_component(url: str, expected_sha256: str | None = None) -> str | None:
    """Fetch component source from a remote URL.

    The code ends up in your project, so the download is constrained: https
    only (http for loopback), a timeout, a 1 MB cap, and an optional SHA-256
    pin. The digest of what was fetched is always printed so it can be pinned.
    """
    if not _is_allowed_url(url):
        only_https = t("add.https_only", "Only https:// URLs are supported.")
        error_msg = f"[red]{t('add.error', 'Error:')}[/red] {only_https}"
        console.print(error_msg)
        return None
    try:
        fetching = t("add.fetching", "Fetching remote component from {url}...")
        status_msg = tagged("nexy", fetching.format(url=url), "yellow")
        # Scheme and host validated by _is_allowed_url; redirects re-checked by _SafeRedirect.
        opener = urllib.request.build_opener(_SafeRedirect)
        with (
            console.status(status_msg, spinner="dots"),
            opener.open(  # nosec B310
                url, timeout=_REMOTE_TIMEOUT
            ) as response,
        ):
            raw: bytes = response.read(_MAX_REMOTE_BYTES + 1)
        if len(raw) > _MAX_REMOTE_BYTES:
            raise ValueError("component is larger than 1 MB")
        digest = hashlib.sha256(raw).hexdigest()
        if expected_sha256 and digest != expected_sha256.lower():
            raise ValueError(f"sha256 mismatch: expected {expected_sha256}, got {digest}")
        console.print(f"[dim]sha256 {digest}[/dim]")
        return raw.decode("utf-8")
    except Exception as e:
        failed = t("add.fetch_failed", "Failed to fetch component from {url}: {error}")
        error_msg = f"[red]{t('add.error', 'Error:')}[/red] {failed.format(url=url, error=e)}"
        console.print(error_msg)
        return None


def add(
    components: list[str] = typer.Argument(None, help=_ADD_HELP_COMPONENTS),
    ui: bool = typer.Option(False, "--ui", help=_ADD_HELP_UI),
    url: bool = typer.Option(False, "--url", help=_ADD_HELP_URL),
    all: bool = typer.Option(False, "--all", "-a", help=_ADD_HELP_ALL),
    sha256: str = typer.Option(None, "--sha256", help=_ADD_HELP_SHA),
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
        raise typer.Exit

    target_dir = Path("src/components/ui")
    target_dir.mkdir(parents=True, exist_ok=True)

    all_deps: set[str] = set()
    for item in components:
        resolved = _resolve_component(item, framework, url, sha256)
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
        exists = t("add.exists", "Skipping: {path} already exists.")
        skip_msg = f"[yellow]{exists.format(path=file_path)}[/yellow]"
        console.print(skip_msg)
        return

    try:
        PathUtil.write_file(file_path, wrap_component_script(content, framework))
        added = t("add.added", "Added: {path}").format(path=file_path)
        console.print(f"[green]{added}[/green]")
    except Exception as e:
        failed = t("add.write_failed", "Failed to write {path}: {error}")
        error_msg = (
            f"[red]{t('add.error', 'Error:')}[/red] {failed.format(path=file_path, error=e)}"
        )
        console.print(error_msg)
