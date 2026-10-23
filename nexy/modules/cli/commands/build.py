import json
import subprocess  # nosec B404
import sys
import time
from pathlib import Path
from typing import Any

from nexy.__version__ import __version__
from nexy.core.config import Config
from nexy.helpers.common.console import console
from nexy.helpers.common.report import print_cmd_result, print_tree_section
from nexy.helpers.server.server import Server
from nexy.modules.builder import Builder, BuildResult
from nexy.modules.cli.commands.guard import abort_on_invalid_config
from nexy.modules.cli.devtools.pycache import pycache
from nexy.modules.frontend import FrontendGenerator
from nexy.modules.i18n import t


def build(check: bool = False) -> None:
    pycache()
    abort_on_invalid_config()
    build_start = time.perf_counter()
    config = Config()
    version = __version__
    Server.check_nexy_prod()
    console.print(f"nexy@{version} {t('build.label', 'build')}\n")
    console.print(f"{t('build.creating', 'Creating an optimized production build')}\n")

    build_result = _compile_server_components()
    _exit_on_failed_components(build_result)

    ssg_entries: list[dict[str, Any]] = []
    if config.useVite:
        ssg_entries = _build_client_bundle()

    if check:
        _run_checks()

    _show_summary(build_result, ssg_entries)

    build_elapsed = time.perf_counter() - build_start
    success_msg = t("build.success_build", "build in {time}").format(time=f"{build_elapsed:.2f}s")
    console.print(f"\n  [green]\u2713[/green] {success_msg}")


def _compile_server_components() -> BuildResult:
    with console.status(f"  {t('build.compiling_server', 'compiling server components')} ..."):
        from nexy.helpers.fs.vfs import VFS

        FrontendGenerator().generate(ssg=True)
        build_result = Builder().build(showlog=False)
        VFS().flush_to_disk()
    return build_result


def _exit_on_failed_components(build_result: BuildResult) -> None:
    if not build_result.failed:
        return
    failed_msg = t("build.failed_components", "{count} component(s) failed").format(
        count=len(build_result.failed)
    )
    console.print(f"  [red]\u2718[/red] {failed_msg}")
    for path in build_result.failed:
        console.print(f"     {path}")
    sys.exit(1)


def _build_client_bundle() -> list[dict[str, Any]]:
    with console.status(f"  {t('build.building_client', 'building client bundle')} ..."):
        vite_proc = Server.vite(build=True, suppress_output=True, capture_stderr=True)
        out, err = vite_proc.communicate()
        if vite_proc.returncode != 0:
            console.print(f"  [red]\u2718[/red] {t('build.failed_client', 'client build failed')}")
            error_output = err or out
            if error_output:
                console.print(f"[red]{error_output.decode()}[/red]")
            sys.exit(1)
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
    labels = {
        "skipped": t("build.skipped_label", "Skipped (cached)"),
        "success": t("build.success_label", "Build success"),
        "failed": t("build.failed_label", "Build Failed"),
    }
    print_tree_section(
        t("build.server_components", "server components"),
        build_result.success,
        build_result.failed,
        "green",
        "red",
        build_result.skipped,
        labels,
    )
    print_tree_section(
        t("build.client_components", "client components"),
        _ssg_by_status(ssg_entries, "success"),
        _ssg_by_status(ssg_entries, "failed"),
        "cyan",
        "red",
        _ssg_by_status(ssg_entries, "not_supported"),
        labels,
    )


def _run_checks() -> None:
    console.print()
    checks = [
        ("ruff check", ["ruff", "check", "."]),
        ("ruff format", ["ruff", "format", ".", "--check"]),
        ("mypy", [sys.executable, "-m", "mypy", "."]),
    ]
    results = [_run_single_check(name, cmd) for name, cmd in checks]
    if not all(results):
        console.print(f"\n  [red]{t('build.checks_failed', 'checks failed')}[/red]")
        sys.exit(1)
    console.print(f"\n  [green]\u2713[/green] {t('build.checks_passed', 'all checks passed')}")


def _run_single_check(name: str, cmd: list[str]) -> bool:
    with console.status(f"  {name} ..."):
        r = subprocess.run(cmd, capture_output=True, text=True)  # nosec B603 - trusted internal command construction
    print_cmd_result(name, r)
    return r.returncode == 0
