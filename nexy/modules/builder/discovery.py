import traceback
from collections.abc import Generator
from pathlib import Path

from nexy.core.config import Config


class Discovery:
    """Scans files to find .nexy, .md, .mdx, and framework route files."""

    TARGET_EXTENSIONS = Config.TARGET_EXTENSIONS
    DEFAULT_EXCLUDED_DIRS = {
        "__pycache__",
        ".git",
        ".venv",
        "node_modules",
        "dist",
        "build",
        "__nexy__",
        ".pytest_cache",
        ".mypy_cache",
        ".uvcache",
        ".github",
        ".cursor",
        ".vscode",
        ".nexy-virt",
    }

    def __init__(self) -> None:
        self.excluded_dirs = self.DEFAULT_EXCLUDED_DIRS.copy()

    def scan(self, root_path: Path | str) -> list[Path]:
        root = Path(root_path)
        if not root.is_dir():
            raise FileNotFoundError(f"not found {root} folder")

        return list(self._walk(root))

    def _walk(self, current_path: Path) -> Generator[Path, None, None]:
        try:
            for item in current_path.iterdir():
                if item.is_dir():
                    if item.name not in self.excluded_dirs:
                        yield from self._walk(item)
                elif item.suffix in self.TARGET_EXTENSIONS:
                    yield item
        except PermissionError:
            traceback.print_exc()

    def add_excluded_dir(self, dir_name: str) -> None:
        self.excluded_dirs.add(dir_name)

    def remove_excluded_dir(self, dir_name: str) -> None:
        self.excluded_dirs.discard(dir_name)
