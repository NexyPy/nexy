import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from nexy.core.config import Config


def to_json_literal(value: object) -> str:
    """Serialize *value* as a JSON literal (Python bools/None mapped to JS)."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(to_json_literal(item) for item in value) + "]"
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


class Json:
    @staticmethod
    def create(path: str) -> Callable[[], Any]:
        try:
            p = Path(path)
            if not p.is_absolute():
                p = Path(Config.PROJECT_ROOT).joinpath(path)

            with p.open("r", encoding="utf-8") as f:
                result = json.load(f)
                return lambda: result
        except Exception:
            return lambda: {}
