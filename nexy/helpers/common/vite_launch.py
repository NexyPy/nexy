"""How `nexy dev` and `nexy build` start the project's Vite.

Resolution order:

1. The project's own ``node_modules/vite/bin/vite.js`` run directly, so no package-manager
   script runner (pnpm 10+ may run an implicit install first, and ``nexy dev`` must never
   mutate ``node_modules``). Node.js runs it; bun runs it when Node.js is absent.
2. Without ``node_modules`` (Yarn Plug'n'Play) or without any JS runtime on PATH, the
   package manager's ``exec`` runner.

A ``dev`` script in ``package.json`` that is more than a plain ``vite ...`` command
(``cross-env``, ``&&``, ...) keeps working: it is run through the package manager with the
port and host appended, like before.

TLS is terminated by Uvicorn and the dev proxy reaches Vite over loopback HTTP, so Vite is
never started in HTTPS mode (Vite 5 removed the ``--https`` flag anyway).
"""

from __future__ import annotations

import json
import re
import shlex
import shutil
from pathlib import Path

from nexy.helpers.common import package_manager

_SHELL_SYNTAX = re.compile(r"[&|;<>$`()]")
_RUNNERS: dict[str, tuple[str, ...]] = {
    "npm": ("npx", "--no-install", "vite"),
    "pnpm": ("pnpm", "exec", "vite"),
    "yarn": ("yarn", "vite"),
    "bun": ("bun", "x", "--bun", "vite"),
}


def local_vite() -> Path | None:
    """The project's Vite entry point, or None when it is not under ``node_modules``."""
    entry = Path("node_modules") / "vite" / "bin" / "vite.js"
    return entry if entry.is_file() else None


def vite_installed() -> bool:
    """True when `nexy dev` can start Vite without installing anything."""
    return local_vite() is not None or Path(".pnp.cjs").is_file()


def dev_script() -> str | None:
    """The ``scripts.dev`` entry of ``package.json``, if there is one."""
    try:
        data = json.loads(Path("package.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    script = data.get("scripts", {}).get("dev") if isinstance(data, dict) else None
    return script if isinstance(script, str) and script.strip() else None


def _script_words(script: str) -> list[str] | None:
    """The words of a plain ``vite ...`` script; None for shell syntax or another command."""
    if _SHELL_SYNTAX.search(script):
        return None
    try:
        words = shlex.split(script)
    except ValueError:
        return None
    return words[1:] if words and words[0] == "vite" else None


def _without_port_and_host(args: list[str]) -> list[str]:
    """*args* minus ``--port``/``--host`` and their values: Nexy chooses both."""
    kept: list[str] = []
    skip_value = False
    for arg in args:
        if skip_value:
            skip_value = False
            if not arg.startswith("-"):
                continue
        if arg in ("--port", "--host"):
            skip_value = True
        elif not arg.startswith(("--port=", "--host=")):
            kept.append(arg)
    return kept


def _plain_vite_args(script: str) -> list[str] | None:
    """Arguments of a plain ``vite ...`` script, without port/host; None for anything else."""
    words = _script_words(script)
    return None if words is None else _without_port_and_host(words)


def _js_runtime() -> str | None:
    return (
        shutil.which("node")
        or shutil.which("node.exe")
        or (package_manager.resolve("bun") if package_manager.detect() == "bun" else None)
    )


def _script_argv(manager: str, server_flags: list[str]) -> list[str]:
    """A custom dev script (env wrappers, chained commands) runs through the package manager."""
    runner = [package_manager.executable(manager), "run", "dev"]
    return [*runner, *(["--"] if manager == "npm" else []), *server_flags]


def _pnp_argv(manager: str, build: bool, server_flags: list[str]) -> list[str]:
    """Yarn Plug'n'Play has no node_modules: the package manager's own runner starts Vite."""
    runner = _RUNNERS.get(manager, _RUNNERS["npm"])
    return [package_manager.executable(runner[0]), *runner[1:], *_build_flag(build), *server_flags]


def _build_flag(build: bool) -> list[str]:
    return ["build"] if build else []


def vite_argv(build: bool, port: int) -> list[str]:
    """The argv that starts Vite for a build or a dev server on *port*.

    Raises:
        RuntimeError: No JS runtime, or Vite is not installed in the project.
    """
    manager = package_manager.detect()
    script = None if build else dev_script()
    server_flags = [] if build else ["--port", str(port), "--host"]
    if script is not None and manager is not None and _plain_vite_args(script) is None:
        return _script_argv(manager, server_flags)
    entry, runtime = local_vite(), _js_runtime()
    if entry is not None and runtime is not None:
        extra = [] if script is None else _plain_vite_args(script) or []
        return [runtime, str(entry), *_build_flag(build), *extra, *server_flags]
    if manager is not None and Path(".pnp.cjs").is_file():
        return _pnp_argv(manager, build, server_flags)
    if runtime is None:
        raise RuntimeError(
            "Node.js is not installed. Install Node.js 20 or later (or bun), then reinstall "
            "the project dependencies."
        )
    raise RuntimeError(f"Vite is not installed in this project. Run: {manager or 'npm'} install")
