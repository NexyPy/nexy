import re
from dataclasses import dataclass
from pathlib import Path

from nexy.core.config import Config

_MAPPING_PATTERN = re.compile(r"^\s*(\w+):\s*use\s+\{\s*(\w*)\s*\}\s+from\s+\"([^\"]*)\"\s*$")


@dataclass
class MdxComponentMapping:
    element: str
    symbol: str
    source: str


class MdxCompConfig:
    _mappings: dict[str, MdxComponentMapping] = {}
    _loaded = False
    _load_error: str | None = None

    @classmethod
    def load(cls) -> None:
        if cls._loaded:
            return

        cls._mappings.clear()

        root = Path(Config.PROJECT_ROOT or ".").resolve()
        config_path = root / "src" / "mdxconfig"

        if not config_path.exists():
            cls._loaded = True
            cls._load_error = None
            return

        content = config_path.read_text(encoding="utf-8")

        for _line_num, line in enumerate(content.splitlines(), 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            m = _MAPPING_PATTERN.match(line)
            if not m:
                continue

            element = m.group(1)
            symbol = m.group(2).strip()
            pattern = m.group(3).strip()

            if not pattern:
                continue

            if not symbol:
                cls._mappings[element] = MdxComponentMapping(
                    element=element,
                    symbol="",
                    source=pattern,
                )
            else:
                cls._mappings[element] = MdxComponentMapping(
                    element=element,
                    symbol=symbol,
                    source=pattern,
                )

        cls._loaded = True

    @classmethod
    def resolve_source(cls, pattern: str, root: Path) -> Path | None:
        resolved = cls._resolve_alias(pattern) or pattern

        matches = sorted(Path(root).glob(resolved))
        if not matches:
            return None

        return matches[0]

    @classmethod
    def _resolve_alias(cls, pattern: str) -> str | None:
        if not pattern.startswith("@"):
            return None
        for alias_key, alias_val in Config.ALIASES.items():
            if alias_key and pattern.startswith(f"@{alias_key}"):
                rest = pattern[len(alias_key) + 1 :]
                return alias_val.rstrip("/") + "/" + rest.lstrip("/")
        rest = pattern[1:].lstrip("/")
        return "src/" + rest

    @classmethod
    def has_mappings(cls) -> bool:
        return len(cls._mappings) > 0

    @classmethod
    def get_mapping(cls, element: str) -> MdxComponentMapping | None:
        return cls._mappings.get(element)

    @classmethod
    def mappings(cls) -> dict[str, MdxComponentMapping]:
        return dict(cls._mappings)
