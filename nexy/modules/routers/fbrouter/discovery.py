from pathlib import Path

from nexy.core.config import Config
from nexy.helpers.common.console import console

KNOWN_ROUTE_EXTENSIONS = [".nexy", ".md", ".mdx", ".py", ".tsx", ".jsx", ".vue", ".svelte"]
_FRAMEWORK_ROUTE_EXTENSIONS = {".tsx", ".jsx", ".vue", ".svelte"}


class RouteDiscovery:
    def __init__(self) -> None:
        self.config = Config()
        self.router_path = Path(self.config.ROUTER_PATH)

    def scan(self) -> list[Path]:
        if not self.router_path.is_dir():
            raise FileNotFoundError(f"Directory {self.router_path} not found")

        active = set(self.config.ROUTE_FILE_EXTENSIONS)
        files: list[Path] = []
        for pattern in [f"**/*{ext}" for ext in KNOWN_ROUTE_EXTENSIONS]:
            files.extend(self.router_path.glob(pattern))
        valid: list[Path] = []
        for f in files:
            if not self._is_valid_route(f):
                continue
            if self.config.useCSR and f.suffix == ".nexy":
                self._warn_csr_ignored(f)
                continue
            if f.suffix not in active:
                self._warn_out_of_set(f)
                continue
            valid.append(f)
        return sorted(valid)

    def _warn_csr_ignored(self, path: Path) -> None:
        rel = path.relative_to(self.router_path)
        console.print(
            f"  [yellow]WARN[/yellow] {rel}: .nexy is disabled (useCSR=True) - "
            f"client routing owns the views, use a framework route file instead"
        )

    def _warn_out_of_set(self, path: Path) -> None:
        ff = self.config.useFF
        name = getattr(ff, "name", "none") if ff else "none"
        rel = path.relative_to(self.router_path)
        console.print(
            f"  [yellow]WARN[/yellow] {rel}: extension '{path.suffix}' is not active "
            f"(useFF={name}) - skipped"
        )

    def _is_valid_route(self, path: Path) -> bool:
        if (
            not path.is_file()
            or path.suffix not in KNOWN_ROUTE_EXTENSIONS
            or path.name in self.config.ROUTE_FILE_EXCEPTIONS
        ):
            return False

        relative_parts = path.relative_to(self.router_path).parts
        return not any(part.startswith("_") or part.startswith(".") for part in relative_parts)
