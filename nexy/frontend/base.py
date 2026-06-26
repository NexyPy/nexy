from abc import ABC, abstractmethod
from pathlib import Path

from nexy.core.models import FrontendFramework


class BaseFrontendGenerator(ABC):
    @abstractmethod
    def generate(self) -> None:
        pass

    def _get_ff_list(self) -> list[FrontendFramework]:
        from nexy.core.config import Config

        config = Config()
        return config.useFF or []

    def _get_frameworks(self) -> set[str]:
        """Extract framework names from FFModel list."""
        ff_list = self._get_ff_list()
        return {getattr(ff, "name", "").lower() for ff in ff_list if hasattr(ff, "name")}

    def _ensure_directories(self) -> tuple[Path, Path]:
        """Create necessary directories for frontend generation."""
        dest_dir = Path("__nexy__")
        src_dir = dest_dir / "src"
        dest_dir.mkdir(parents=True, exist_ok=True)
        src_dir.mkdir(parents=True, exist_ok=True)
        return dest_dir, src_dir
