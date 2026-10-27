import shutil
import subprocess  # nosec B404
import sys
from pathlib import Path

import typer

from nexy.helpers.common.console import console
from nexy.helpers.common.executables import find_tool
from nexy.modules.i18n import t


def test(
    server: bool = typer.Option(
        True, "--server", help=t("test.help_server", "Run server tests (pytest)")
    ),
    client: bool = typer.Option(
        False, "--client", help=t("test.help_client", "Run client tests (vitest)")
    ),
    args: list[str] | None = typer.Argument(  # noqa: B008
        None, help=t("test.help_args", "Extra arguments forwarded to the test runner")
    ),
) -> None:
    """Run server (pytest) and/or client (vitest) tests."""
    failures = 0
    root = Path.cwd()

    if server:
        failures += _run_server(root, args or [])
    if client:
        failures += _run_client(root, args or [])

    console.print()
    if failures:
        msg = t("test.failed", "{count} test run(s) failed").format(count=failures)
        console.print(f"  [red]\u2718[/red] {msg}")
        sys.exit(1)
    console.print(f"  [green]\u2713[/green] {t('test.passed', 'all tests passed')}")


def _run_server(root: Path, args: list[str]) -> int:
    exe = find_tool("pytest")
    if not exe:
        msg = t("test.skip_tool", "pytest not found - skipping server tests")
        console.print(f"  [yellow]\u26a0[/yellow] {msg}")
        return 0
    targets = ["tests/"] if (root / "tests").is_dir() else [str(root)]
    with console.status("  pytest ..."):
        r = subprocess.run([exe, *targets, *args], capture_output=True, text=True)  # nosec B603
    _print_result("pytest", r)
    return 0 if r.returncode == 0 else 1


def _run_client(root: Path, args: list[str]) -> int:
    if not _has_vitest(root):
        msg = t("test.skip_client", "vitest not configured - skipping client tests")
        console.print(f"  [yellow]\u26a0[/yellow] {msg}")
        return 0
    npx_exe = shutil.which("npx") or sys.executable
    with console.status("  vitest ..."):
        r = subprocess.run([npx_exe, "vitest", "run", *args], capture_output=True, text=True)  # nosec B603/B607
    _print_result("vitest", r)
    return 0 if r.returncode == 0 else 1


def _has_vitest(root: Path) -> bool:
    if (root / "vitest.config.ts").is_file():
        return True
    pkg = root / "package.json"
    if pkg.is_file():
        try:
            import json

            data = json.loads(pkg.read_text(encoding="utf-8"))
            scripts = data.get("scripts", {})
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            return "vitest" in scripts or "vitest" in deps
        except Exception:
            return False
    return False


def _print_result(name: str, r: subprocess.CompletedProcess[str]) -> None:
    if r.returncode == 0:
        console.print(f"  [green]\u2713[/green] {name}")
    else:
        console.print(f"  [red]\u2718[/red] {name}")
        if r.stdout:
            console.print(r.stdout)
        if r.stderr:
            console.print(f"[red]{r.stderr}[/red]")
