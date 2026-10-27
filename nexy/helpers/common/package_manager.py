"""Node.js package manager detection and command construction.

A committed lockfile wins so an existing project keeps its package manager.
New projects use the project-wide priority: bun, then pnpm, then npm. Yarn is
only selected when its lockfile is present.
"""

from __future__ import annotations

import shutil
import subprocess  # nosec B404
from pathlib import Path

PRIORITY: tuple[str, ...] = ("bun", "pnpm", "npm")

_LOCKFILES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("bun", ("bun.lock", "bun.lockb")),
    ("pnpm", ("pnpm-lock.yaml",)),
    ("yarn", ("yarn.lock",)),
    ("npm", ("package-lock.json",)),
)


def resolve(name: str) -> str | None:
    """Return the executable path for *name*, including Windows shims."""
    return (
        shutil.which(name)
        or shutil.which(f"{name}.cmd")
        or shutil.which(f"{name}.exe")
        or shutil.which(f"{name}.bat")
    )


def manager_from_lockfile(directory: Path) -> str | None:
    """Return the package manager implied by a lockfile in *directory*."""
    for manager, lockfiles in _LOCKFILES:
        if any((directory / lockfile).exists() for lockfile in lockfiles):
            return manager
    return None


def detect(directory: Path | None = None) -> str | None:
    """Detect the package manager for *directory*.

    A lockfile takes precedence over the binary priority so an existing
    project does not switch managers on the next install. Without a lockfile,
    the first installed manager in :data:`PRIORITY` wins.
    """
    root = Path(directory or ".")
    locked = manager_from_lockfile(root)
    if locked is not None and resolve(locked) is not None:
        return locked
    for manager in PRIORITY:
        if resolve(manager) is not None:
            return manager
    return None


def executable(manager: str) -> str:
    """Return the absolute executable path for *manager*.

    Raises:
        FileNotFoundError: The manager is not installed or not on PATH.
    """
    found = resolve(manager)
    if found is None:
        raise FileNotFoundError(f"{manager} is not installed or not on PATH")
    return found


def version(manager: str) -> tuple[int, ...] | None:
    """Return *manager*'s version as a numeric tuple, or None if unknown."""
    try:
        result = subprocess.run(  # nosec B603 - resolved executable, fixed argv
            [executable(manager), "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    parts: list[int] = []
    for part in result.stdout.strip().split("."):
        digits = "".join(character for character in part if character.isdigit())
        if not digits:
            break
        parts.append(int(digits))
    return tuple(parts) or None


def install_argv(manager: str, allow_builds: tuple[str, ...] = ()) -> list[str]:
    """Return the install argv for *manager*.

    pnpm 11 and later fail the install when a dependency's build script is not
    approved (``ERR_PNPM_IGNORED_BUILDS``). The *allow_builds* names are
    approved for this install only, so no project configuration is generated.
    """
    argv = [executable(manager), "install"]
    if manager == "pnpm" and allow_builds:
        current = version(manager)
        if current is not None and current[0] >= 11:
            argv.extend(f"--allow-build={name}" for name in allow_builds)
    return argv


def add_argv(manager: str, packages: list[str]) -> list[str]:
    """Return the argv that installs runtime *packages* with *manager*."""
    executable_path = executable(manager)
    if manager == "npm":
        return [executable_path, "install", *packages]
    return [executable_path, "add", *packages]
