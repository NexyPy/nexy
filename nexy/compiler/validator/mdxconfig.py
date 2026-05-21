from pathlib import Path

from nexy.core.config import Config
from nexy.runtime.mdxconfig import MdxCompConfig


class MdxConfigValidationError(Exception):
    pass


class MdxConfigValidator:
    @staticmethod
    def validate() -> list[str]:
        warnings: list[str] = []

        root = Path(Config.PROJECT_ROOT or ".").resolve()
        config_path = root / "src" / "mdxconfig"

        if not config_path.exists():
            return warnings

        content = config_path.read_text(encoding="utf-8")

        for line_num, line in enumerate(content.splitlines(), 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if "use {" not in line or '} from "' not in line:
                msg = (
                    f"Line {line_num}: malformed syntax, expected "
                    "'<element>: use { Symbol } from \"<glob>\"'"
                )
                warnings.append(msg)
                continue

            element = line.split(":")[0].strip()
            if not element.isidentifier():
                warnings.append(f"Line {line_num}: '{element}' is not a valid HTML element name")

        for element, mapping in MdxCompConfig.mappings().items():
            resolved = MdxCompConfig.resolve_source(mapping.source, root)
            if resolved is None:
                warnings.append(f"Mapping for <{element}>: no file matching '{mapping.source}'")

        return warnings
