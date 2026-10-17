from abc import ABC, abstractmethod
from pathlib import Path

from nexy.core.models import FrontendFramework


class BaseFrontendGenerator(ABC):
    @abstractmethod
    def generate(self) -> None:
        pass

    def _get_ff(self) -> FrontendFramework | None:
        from nexy.core.config import Config

        config = Config()
        use_ff = config.useFF
        if isinstance(use_ff, list):
            return use_ff[0] if use_ff else None
        return use_ff

    def _get_frameworks(self) -> set[str]:
        """Extract the active framework name."""
        ff = self._get_ff()
        return {ff.name.lower()} if ff else set()

    def _ensure_directories(self) -> tuple[Path, Path]:
        """Create necessary directories for frontend generation."""
        dest_dir = Path("__nexy__")
        src_dir = dest_dir / "src"
        dest_dir.mkdir(parents=True, exist_ok=True)
        src_dir.mkdir(parents=True, exist_ok=True)
        return dest_dir, src_dir
