"""`nx info`: print environment and project versions in one plain block."""

from __future__ import annotations

import json
import platform
import subprocess  # nosec B404
from pathlib import Path

from nexy.__version__ import __version__
from nexy.helpers.common import package_manager
from nexy.helpers.common.console import console
from nexy.modules.cli.agents import detect_profile
from nexy.modules.i18n import t

_FRAMEWORKS: tuple[tuple[str, str], ...] = (
    ("react", "react"),
    ("preact", "preact"),
    ("vue", "vue"),
    ("svelte", "svelte"),
    ("solid-js", "solid"),
)


def _node_version() -> str:
    not_found = t("info.not_found", "not found")
    node_exe = package_manager.resolve("node")
    if node_exe is None:
        return not_found
    try:
        result = subprocess.run(  # nosec B603 - resolved executable, fixed argv
            [node_exe, "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return not_found
    if result.returncode != 0:
        return not_found
    raw = result.stdout.strip().lstrip("vV")
    return raw or not_found


def _package_manager_info(root: Path) -> str:
    not_found = t("info.not_found", "not found")
    manager = package_manager.detect(root)
    if manager is None:
        return not_found
    ver = package_manager.version(manager)
    if ver is None:
        return manager
    return f"{manager} {'.'.join(str(part) for part in ver)}"


def _router_info(root: Path) -> str:
    not_found = t("info.not_found", "not found")
    if not (root / "nexyconfig.py").is_file():
        return not_found
    profile = detect_profile(root)
    if profile.router == "fbr":
        return t("info.router_file_based", "file-based")
    return profile.router


def _frameworks_info(root: Path) -> str:
    not_found = t("info.not_found", "not found")
    pkg_file = root / "package.json"
    if not pkg_file.is_file():
        return not_found
    try:
        data = json.loads(pkg_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return not_found
    deps: dict[str, object] = {
        **(data.get("dependencies") or {}),
        **(data.get("devDependencies") or {}),
    }
    found: list[str] = []
    for pkg_name, label in _FRAMEWORKS:
        if pkg_name in deps:
            raw_ver = str(deps[pkg_name]).strip().lstrip("^~>=< ")
            found.append(f"{label} {raw_ver}" if raw_ver else label)
    return ", ".join(found) if found else not_found


def info() -> None:
    """Print Nexy, Python, OS, Node, package manager, router, and framework versions."""
    root = Path.cwd()
    python_ver = f"{platform.python_version()} ({platform.python_implementation()})"
    os_ver = f"{platform.system()} {platform.release()} {platform.machine()}".strip()

    rows: list[tuple[str, str]] = [
        (t("info.label.nexy", "Nexy"), __version__),
        (t("info.label.python", "Python"), python_ver),
        (t("info.label.os", "OS"), os_ver),
        (t("info.label.node", "Node"), _node_version()),
        (t("info.label.package", "Package"), _package_manager_info(root)),
        (t("info.label.router", "Router"), _router_info(root)),
        (t("info.label.frameworks", "Frameworks"), _frameworks_info(root)),
    ]

    for label, value in rows:
        console.print(f"{label:<12}{value}", highlight=False, markup=False)
