from __future__ import annotations

import importlib
import importlib.util
import json
from contextvars import ContextVar
from pathlib import Path
from threading import RLock
from typing import Any

_RTL_LOCALES = frozenset({"ar", "he", "fa", "ur", "ps", "ku"})


def _is_rtl(locale: str) -> bool:
    return locale.split("-")[0].split("_")[0].lower() in _RTL_LOCALES


current_locale: ContextVar[str] = ContextVar("current_locale", default="en")


class LocaleManager:
    _instance: LocaleManager | None = None
    _lock: RLock = RLock()
    _translations: dict[str, dict[str, Any]] = {}
    _loaded: bool = False
    _project_dir: Path | None = None
    _available: list[str] = ["en"]
    _default: str = "en"

    def __new__(cls) -> LocaleManager:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def configure(
        self,
        available: list[str] | None = None,
        default: str = "en",
        project_locales_dir: str | None = None,
    ) -> None:
        self._available = available or ["en"]
        self._default = default
        if project_locales_dir is not None:
            self._project_dir = Path(project_locales_dir)
        self._loaded = False
        self._load()

    def _load_py_module(self, path: Path) -> dict[str, Any] | None:
        import sys

        try:
            parent = path.parent
            name = path.stem
            for key in list(sys.modules):
                if key == name or key.startswith(f"{name}."):
                    del sys.modules[key]
            sys.path.insert(0, str(parent))
            mod = importlib.import_module(name)
            sys.path.remove(str(parent))
            return getattr(mod, "translations", None)
        except Exception:
            return None

    def _load(self) -> None:
        if self._loaded:
            return
        with self._lock:
            if self._loaded:
                return
            merged: dict[str, dict[str, Any]] = {}
            if self._project_dir:
                i18n_py = self._project_dir / "i18n.py"
            for locale in self._available:
                data: dict[str, Any] = {}
                if self._project_dir:
                    json_file = self._project_dir / f"{locale}.json"
                    if json_file.exists():
                        with json_file.open("r", encoding="utf-8") as f:
                            data = json.load(f)
                    else:
                        py_file = self._project_dir / f"{locale}.py"
                        if py_file.exists():
                            loaded = self._load_py_module(py_file)
                            if loaded:
                                data = loaded
                        elif locale == self._default and i18n_py.exists():
                            loaded = self._load_py_module(i18n_py)
                            if loaded:
                                data = loaded
                merged[locale] = data
            # Merge generated __nexy__/i18n/ files on top
            # Format: {class_name: {locale: {attr: value, ...}, ...}, ...}
            gen_dir = Path.cwd() / "__nexy__" / "i18n"
            if gen_dir.exists():
                for gen_file in sorted(gen_dir.glob("*.json")):
                    gen_data = json.loads(gen_file.read_text(encoding="utf-8"))
                    for cls_name, locales in gen_data.items():
                        for locale, cls_data in locales.items():
                            if locale not in merged:
                                continue
                            if cls_name in merged[locale]:
                                merged[locale][cls_name].update(cls_data)
                            else:
                                merged[locale][cls_name] = cls_data
            self._translations = merged
            self._loaded = True

    def available_locales(self) -> list[str]:
        self._load()
        return list(self._available)

    def default_locale(self) -> str:
        return self._default

    def translate(self, key: str, default: str | None = None, locale: str | None = None) -> str:
        self._load()
        loc = locale or current_locale.get() or self._default
        if loc not in self._translations:
            loc = self._default
        data = self._translations.get(loc, {})
        value: Any = data
        for part in key.split("."):
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default if default is not None else key
        if isinstance(value, str):
            return value
        return default if default is not None else key

    def reload(self) -> None:
        with self._lock:
            self._loaded = False


L = LocaleManager()


def trans(key: str, default: str | None = None, *, locale: str | None = None) -> str:
    return L.translate(key, default=default, locale=locale)


t = trans


def useLocale() -> dict[str, Any]:
    loc = current_locale.get()
    return {
        "locale": loc,
        "is_rtl": _is_rtl(loc),
        "available": L.available_locales(),
        "default": L.default_locale(),
        "trans": trans,
    }
