from pathlib import Path

from nexy.core.config import Config
from nexy.helpers.fs.scan import SKIP_DIRS, walk_paths


class Discovery:
    """Scans files to find .nexy, .md, .mdx, and framework route files."""

    TARGET_EXTENSIONS = Config.TARGET_EXTENSIONS
    DEFAULT_EXCLUDED_DIRS = SKIP_DIRS

    def __init__(self) -> None:
        self.excluded_dirs = self.DEFAULT_EXCLUDED_DIRS.copy()

    def scan(self, root_path: Path | str) -> list[Path]:
        root = Path(root_path)
        if not root.is_dir():
            raise FileNotFoundError(f"not found {root} folder")

        return list(walk_paths(root, self.TARGET_EXTENSIONS, excluded=self.excluded_dirs))

    def add_excluded_dir(self, dir_name: str) -> None:
        self.excluded_dirs.add(dir_name)

    def remove_excluded_dir(self, dir_name: str) -> None:
        self.excluded_dirs.discard(dir_name)
