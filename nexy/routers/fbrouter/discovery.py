from pathlib import Path

from nexy.core.config import Config


class RouteDiscovery:
    def __init__(self) -> None:
        self.config = Config()
        self.router_path = Path(self.config.ROUTER_PATH)

    def scan(self) -> list[Path]:
        if not self.router_path.is_dir():
            raise FileNotFoundError(f"Directory {self.router_path} not found")

        patterns = [f"**/*{ext}" for ext in self.config.ROUTE_FILE_EXTENSIONS]
        files: list[Path] = []
        for pattern in patterns:
            files.extend(self.router_path.glob(pattern))
        return sorted(f for f in files if self._is_valid_route(f))

    def _is_valid_route(self, path: Path) -> bool:
        if (
            not path.is_file()
            or path.suffix not in self.config.ROUTE_FILE_EXTENSIONS
            or path.name in self.config.ROUTE_FILE_EXCEPTIONS
        ):
            return False

        relative_parts = path.relative_to(self.router_path).parts
        return not any(part.startswith("_") or part.startswith(".") for part in relative_parts)
