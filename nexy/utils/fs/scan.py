from pathlib import Path

SKIP_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    "__nexy__",
    ".pytest_cache",
    "dist",
    "build",
    ".vscode-test",
}


def has_files(root: Path, exts: tuple[str, ...]) -> bool:
    """Return True when at least one file ending in *exts* exists under *root*."""
    for _dirpath, dirnames, filenames in root.walk():
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith(exts):
                return True
    return False


def collect_files(root: Path, exts: tuple[str, ...]) -> list[str]:
    """List every file ending in *exts* under *root*, sorted, skipping SKIP_DIRS."""
    files: list[str] = []
    for dirpath, dirnames, filenames in root.walk():
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith(exts):
                files.append(str(Path(dirpath) / name))
    return sorted(files)
