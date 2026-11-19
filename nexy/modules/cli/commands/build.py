import json
import sys
import time
from pathlib import Path
from typing import Any, NoReturn

from rich.markup import escape

from nexy.__version__ import __version__
from nexy.core.config import Config
from nexy.helpers.common import launcher
from nexy.helpers.common.console import console
from nexy.helpers.common.messages import error, took, warning
from nexy.helpers.common.summary import print_summary
from nexy.helpers.common.tasks import format_duration, run_task, step
from nexy.helpers.fs.packages import ensure_project_packages
from nexy.helpers.server.markers import write_build_marker
from nexy.helpers.server.server import Server
from nexy.modules.builder import Builder, BuildResult
from nexy.modules.cli.commands.guard import abort_on_invalid_config
from nexy.modules.cli.devtools.pycache import pycache
from nexy.modules.frontend import FrontendGenerator
from nexy.modules.i18n import t


def _announce_start() -> None:
    Server.check_nexy_prod()
    launcher.banner("build", __version__)
    console.print(f"  {t('build.creating', 'Creating an optimized production build')}...\n")


def _announce_end(started: float) -> None:
    built = t("build.built", "Built the project")
    console.print(took(built, format_duration(time.perf_counter() - started)))


def build(check: bool = False) -> None:
    pycache()
    ensure_project_packages()
    abort_on_invalid_config()
    started = time.perf_counter()
    _announce_start()
    build_result = _compile_server_components()
    _exit_on_failed_components(build_result)
    ssg_entries = _build_client_bundle() if Config().useVite else []
    if check:
        _run_checks()
    _show_summary(build_result, ssg_entries)
    write_build_marker(__version__)
    _announce_end(started)


def _compile_label() -> str:
    # A client-routed project has no server components: what compiles is its routes.
    if Config.useCSR:
        return t("build.compiling_routes", "Compiled routes")
    return t("build.compiling_server", "Compiled server components")


def _compile_server_components() -> BuildResult:
    with step(_compile_label()):
        from nexy.helpers.fs.vfs import VFS

        FrontendGenerator().generate(ssg=True)
        build_result = Builder().build(showlog=False)
        VFS().flush_to_disk()
        _write_action_client()
    return build_result


def _write_action_client() -> None:
    """Generate `@nexy/actions` before the bundle, so the client imports typed actions."""
    from nexy.modules.routers.actions.engine import ACTION_ENGINE

    ACTION_ENGINE.refresh_client()


def _exit_on_failed_components(build_result: BuildResult) -> None:
    if not build_result.failed:
        return
    failed_msg = t("build.failed_components", "{count} component(s) failed").format(
        count=len(build_result.failed)
    )
    error(failed_msg, cause=escape(", ".join(map(str, build_result.failed))))
    sys.exit(1)


def _client_failed(output: str = "") -> NoReturn:
    """A uv error for the client bundle, followed by what Vite said."""
    error(t("build.failed_client", "Failed to build the client bundle"))
    for line in output.splitlines():
        console.print(f"  {escape(line)}")
    sys.exit(1)


def _build_client_bundle() -> list[dict[str, Any]]:
    try:
        vite_proc = Server.vite(build=True, suppress_output=True, capture_stderr=True)
    except RuntimeError as problem:
        _client_failed(str(problem))
    with step(t("build.building_client", "Built client bundle")):
        out, err = vite_proc.communicate()
    if vite_proc.returncode != 0:
        _client_failed((err or out or b"").decode(errors="replace"))
    return _read_ssg_report()


def _read_ssg_report() -> list[dict[str, Any]]:
    report_path = Path("__nexy__/client/ssg-report.json")
    if not report_path.exists():
        return []
    report_data = json.loads(report_path.read_text())
    entries = report_data.get("entries", []) if isinstance(report_data, dict) else report_data
    return entries if isinstance(entries, list) else []


def _ssg_by_status(entries: list[dict[str, Any]], status: str) -> list[str]:
    return [e["file"] for e in entries if e["status"] == status]


def _show_summary(build_result: BuildResult, ssg_entries: list[dict[str, Any]]) -> None:
    more = t("build.more", "and {count} more")
    counts = [t("build.count_built", "{count} built").format(count=len(build_result.success))]
    if build_result.skipped:
        counts.append(
            t("build.count_cached", "{count} cached").format(count=len(build_result.skipped))
        )
    if Config.useCSR:
        print_summary(t("build.routes", "Routes"), counts, build_result.success, more=more)
        return
    title = t("build.server_components", "Server components")
    print_summary(title, counts, build_result.success, more=more)
    _show_client_summary(ssg_entries, more)


def _show_client_summary(entries: list[dict[str, Any]], more: str) -> None:
    rendered = _ssg_by_status(entries, "success")
    client_only = _ssg_by_status(entries, "not_supported")
    counts = [t("build.count_rendered", "{count} rendered").format(count=len(rendered))]
    if client_only:
        counts.append(
            t("build.count_client_only", "{count} client-only").format(count=len(client_only))
        )
    print_summary(t("build.client_components", "Client components"), counts, rendered, more=more)
    for path in _ssg_by_status(entries, "failed"):
        default = "{path} has no server HTML: it renders on the client only"
        warning(t("build.not_rendered", default).format(path=escape(path)))


def _run_checks() -> None:
    checks = [
        ("ruff check", [sys.executable, "-m", "ruff", "check", "."]),
        ("ruff format", [sys.executable, "-m", "ruff", "format", ".", "--check"]),
        ("mypy", [sys.executable, "-m", "mypy", "."]),
    ]
    results = [_run_single_check(name, cmd) for name, cmd in checks]
    if not all(results):
        error(t("build.checks_failed", "Some checks failed"))
        sys.exit(1)
    console.print(t("check.passed", "All checks passed"))


def _run_single_check(name: str, cmd: list[str]) -> bool:
    label = t("build.running_check", "Running {name}").format(name=name)
    done = t("build.ran_check", "Ran {name}").format(name=name)
    return run_task(label, cmd, done=done, full_output=True).ok
