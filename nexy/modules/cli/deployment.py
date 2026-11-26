"""Data-only registry of the files that `nx add <platform>` writes in a project."""

import json
from pathlib import Path

VERCEL_ENTRY_POINT = '''"""Entry point for hosts that run this app as a Python ASGI application."""

import os
import shutil
import sys
import tempfile
from importlib import import_module
from pathlib import Path

PROJECT_ITEMS = (
    "src",
    "__nexy__",
    "public",
    "nexyconfig.py",
    "pyproject.toml",
    "vite.config.ts",
)


def copy_item(source: Path, target: Path) -> None:
    """Copy a file or a folder as new, writable files, whatever the source permissions."""
    if source.is_file():
        shutil.copyfile(source, target)
        return
    target.mkdir(parents=True, exist_ok=True)
    for child in sorted(source.iterdir()):
        if child.name != "__pycache__":
            copy_item(child, target / child.name)


def copy_project(root: Path, target: Path) -> None:
    """Copy what Nexy needs at runtime, so it can rewrite its build folder."""
    for name in PROJECT_ITEMS:
        if (root / name).exists():
            copy_item(root / name, target / name)


def writable_root(root: Path) -> Path:
    """Return the project folder, or a writable copy when the host mounts it read-only."""
    if os.access(root, os.W_OK):
        return root
    target = Path(tempfile.mkdtemp(prefix="nexy-"))
    copy_project(root, target)
    return target


def enter(root: Path) -> None:
    """Make a relocated copy the working folder and the first import location."""
    os.chdir(root)
    sys.path.insert(0, str(root))


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = writable_root(ROOT)
if RUNTIME_ROOT != ROOT:
    enter(RUNTIME_ROOT)

app = import_module("nexy.app").app
'''

VERCEL_HEADERS = [
    {
        "source": "/assets/(.*)",
        "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}],
    },
    {
        "source": "/(.*)\\.(svg|webp|avif|png|jpg|jpeg|gif|ico|woff2)",
        "headers": [
            {
                "key": "Cache-Control",
                "value": "public, max-age=86400, stale-while-revalidate=604800",
            }
        ],
    },
]

PLATFORM_FILES: dict[str, dict[Path, str]] = {
    "vercel": {
        Path("src", "server.py"): VERCEL_ENTRY_POINT,
        Path("vercel.json"): json.dumps({"headers": VERCEL_HEADERS}, indent=2) + "\n",
    }
}

GITIGNORE_LINES: tuple[str, ...] = (
    "__nexy__/build-cache.json",
    "__nexy__/server.port",
    "__nexy__/.temp/",
    "__pycache__/",
)
