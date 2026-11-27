"""Apply the config hooks a module declares, without rewriting unrelated settings."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from nexy.helpers.fs.path import PathUtil

_NEW_CONFIG = (
    "from nexy.core.models import NexyConfigModel\n\n\n"
    "class NexyConfig(NexyConfigModel):\n    pass\n"
)


def apply_config_hooks(hooks: Mapping[str, Mapping[str, Any]], root: Path = Path(".")) -> list[str]:
    """Write each declared setting and return one line per change for the terminal."""
    changes: list[str] = []
    if "nexyconfig" in hooks:
        changes.extend(_apply_nexyconfig(root, hooks["nexyconfig"]))
    if "package_json" in hooks:
        changes.extend(_apply_package_json(root, hooks["package_json"]))
    return changes


def _apply_nexyconfig(root: Path, entries: Mapping[str, Any]) -> list[str]:
    path = root / "nexyconfig.py"
    text = path.read_text(encoding="utf-8") if path.exists() else _NEW_CONFIG
    for key, value in entries.items():
        text = _set_python_value(text, key, value)
    PathUtil.write_file(path, text.rstrip() + "\n")
    return [f"nexyconfig.py: {key}" for key in entries]


def _set_python_value(text: str, key: str, value: Any) -> str:
    assignment = f"{key} = {_python_literal(value)}"
    pattern = re.compile(rf"(?m)^(\s*){re.escape(key)}\s*=.*$")
    if pattern.search(text):
        return pattern.sub(lambda match: f"{match.group(1)}{assignment}", text, count=1)
    marker = "class NexyConfig(NexyConfigModel):"
    return text.replace(marker, f"{marker}\n    {assignment}", 1)


def _python_literal(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False) if isinstance(value, str) else repr(value)


def _apply_package_json(root: Path, entries: Mapping[str, Any]) -> list[str]:
    path = root / "package.json"
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    for key, value in entries.items():
        _set_json_value(data, key.split("."), value)
    PathUtil.write_file(path, json.dumps(data, indent=2) + "\n")
    return [f"package.json: {key}" for key in entries]


def _set_json_value(data: dict[str, Any], parts: list[str], value: Any) -> None:
    for part in parts[:-1]:
        data = data.setdefault(part, {})
    data[parts[-1]] = value
