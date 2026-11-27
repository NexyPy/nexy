"""The `nx.toml` file a release carries: the contract the installer must honour."""

from __future__ import annotations

import re
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

_NAME = re.compile(r"@[a-z0-9][a-z0-9-]{0,38}/[a-z0-9][a-z0-9-]{0,48}")
_VERSION = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_JSON_KEY = re.compile(r"[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*")
_UNSAFE = {";", "&", "|", "`", "$", "\n", "\r", "\\"}


class ManifestError(ValueError):
    """The manifest is not a safe Nexy module description."""


@dataclass(frozen=True)
class ModuleManifest:
    """Everything `nx add` is allowed to read from a release."""

    name: str
    version: str
    kind: Literal["source", "package"]
    nexy_version: str
    python_version: str
    python_dependencies: tuple[str, ...]
    node_dependencies: tuple[str, ...]
    files: tuple[str, ...]
    package: str | None
    config: Mapping[str, Mapping[str, Any]]
    migrations: tuple[tuple[str, ...], ...]


def parse_manifest(text: str) -> ModuleManifest:
    """Parse one `nx.toml` document, refusing anything outside the contract."""
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as problem:
        raise ManifestError("manifest is not valid TOML") from problem
    return _manifest_of(data)


def _manifest_of(data: Mapping[str, Any]) -> ModuleManifest:
    name, version = str(data.get("name", "")), str(data.get("version", ""))
    if not _NAME.fullmatch(name):
        raise ManifestError("name must be @scope/name")
    if not _VERSION.fullmatch(version):
        raise ManifestError("version must be three numbers separated by dots")
    kind = str(data.get("kind", ""))
    if kind not in ("source", "package"):
        raise ManifestError("kind must be source or package")
    compatibility = _table(data, "compatibility")
    dependencies = _table(data, "dependencies")
    files, package = _payload(_table(data, "source"), kind)
    return ModuleManifest(
        name=name,
        version=version,
        kind=kind,  # type: ignore[arg-type]
        nexy_version=str(compatibility.get("nexy", "")),
        python_version=str(compatibility.get("python", "")),
        python_dependencies=_texts(dependencies.get("python"), "dependency"),
        node_dependencies=_texts(dependencies.get("node"), "dependency"),
        files=files,
        package=package,
        config=_config(_table(data, "config")),
        migrations=_migrations(data.get("migrations", [])),
    )


def _table(data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = data.get(key, {})
    return value if isinstance(value, dict) else {}


def _texts(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ManifestError(f"{label} must be a list")
    items = tuple(str(item) for item in value)
    if any(not item or any(char in item for char in _UNSAFE) for item in items):
        raise ManifestError(f"{label} is empty or unsafe")
    return items


def _files(source: Mapping[str, Any]) -> tuple[str, ...]:
    value = source.get("files")
    if not isinstance(value, list):
        raise ManifestError("files must be a list")
    items = tuple(str(item) for item in value)
    if any(
        not item or item.startswith("/") or ".." in item.split("/") or "\\" in item
        for item in items
    ):
        raise ManifestError("a module file must be a relative path inside the module")
    return items


def _payload(source: Mapping[str, Any], kind: str) -> tuple[tuple[str, ...], str | None]:
    if kind == "source":
        files = _files(source)
        if not files:
            raise ManifestError("a source module needs at least one file")
        return files, None
    package = str(source.get("package", ""))
    if not package:
        raise ManifestError("a package module needs a package name")
    return (), package


def _config(value: Mapping[str, Any]) -> Mapping[str, Mapping[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for section, entries in value.items():
        if section not in ("nexyconfig", "package_json"):
            raise ManifestError(f"unknown config section: {section}")
        if not isinstance(entries, dict):
            raise ManifestError("a config section must be a table")
        for key, item in entries.items():
            _check_key(section, str(key))
            if not isinstance(item, (str, int, float, bool, list)):
                raise ManifestError("a config value must be a scalar or a list")
        result[section] = dict(entries)
    return result


def _check_key(section: str, key: str) -> None:
    pattern = _IDENTIFIER if section == "nexyconfig" else _JSON_KEY
    if pattern.fullmatch(key) is None or (section == "nexyconfig" and key.startswith("__")):
        raise ManifestError(f"unsafe config key: {key}")


def _migrations(value: Any) -> tuple[tuple[str, ...], ...]:
    if not isinstance(value, list):
        raise ManifestError("migrations must be a list")
    commands = []
    for entry in value:
        if not isinstance(entry, dict):
            raise ManifestError("a migration must be a table with an argv list")
        commands.append(_texts(entry.get("argv"), "migration"))
    return tuple(commands)
