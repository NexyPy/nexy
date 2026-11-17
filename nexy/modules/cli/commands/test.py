import shutil
import sys
from pathlib import Path

import typer
from rich.markup import escape

from nexy.helpers.common.console import console
from nexy.helpers.common.executables import find_tool
from nexy.helpers.common.messages import error, warning
from nexy.helpers.common.tasks import run_task
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

    if failures:
        error(t("test.failed", "{count} test run(s) failed").format(count=failures))
        sys.exit(1)
    console.print(t("test.passed", "All tests passed"))


def _run_tests(label: str, done: str, argv: list[str]) -> int:
    """uv's live row while the runner works, one line when it ends, then its own summary line."""
    result = run_task(label, argv, done=done, full_output=True)
    if result.ok and result.output:
        console.print(f"  [dim]{escape(result.output[-1])}[/dim]")
    return 0 if result.ok else 1


def _run_server(root: Path, args: list[str]) -> int:
    exe = find_tool("pytest")
    if not exe:
        warning(t("test.skip_tool", "pytest not found - skipping server tests"))
        return 0
    targets = ["tests/"] if (root / "tests").is_dir() else [str(root)]
    label = t("test.running_server", "Running the server tests with pytest")
    done = t("test.ran_server", "Ran the server tests with pytest")
    return _run_tests(label, done, [exe, *targets, *args])


def _run_client(root: Path, args: list[str]) -> int:
    if not _has_vitest(root):
        warning(t("test.skip_client", "vitest not configured - skipping client tests"))
        return 0
    npx_exe = shutil.which("npx") or sys.executable
    label = t("test.running_client", "Running the client tests with vitest")
    done = t("test.ran_client", "Ran the client tests with vitest")
    return _run_tests(label, done, [npx_exe, "vitest", "run", *args])


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
