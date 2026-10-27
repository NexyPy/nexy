"""Translation of the Nexy command line.

One JSON catalog per language sits next to this file (``fr.json``, ``ja.json``...). The language is
the first of these that is supported: ``NEXY_LANG``, the locale variables of the shell, the language
of the operating system. Anything else is English, which is also what a missing message falls back
to, so a catalog that lags behind never shows a bare key.
"""

import json
import locale as _py_locale
import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

FALLBACK_LOCALE = "en"

# The most spoken languages among developers: the countries with the most accounts on GitHub, and
# the languages the documentation of Vite, Nuxt and Next.js is community-translated into.
SUPPORTED_LOCALES: tuple[str, ...] = (
    "en", "zh", "hi", "es", "pt", "fr", "de", "ja", "ru", "ko", "id", "ar",
)  # fmt: skip

# Old or regional codes that name a language the catalogs do have.
_ALIASES = {"in": "id"}

_ROOT = Path(__file__).parent


def _normalize(tag: str) -> str:
    """The supported language a locale tag such as ``pt_BR.UTF-8`` stands for, or English."""
    primary = (
        (tag or "").strip().lower().replace("_", "-").split(".")[0].split("@")[0].split("-")[0]
    )
    primary = _ALIASES.get(primary, primary)
    return primary if primary in SUPPORTED_LOCALES else FALLBACK_LOCALE


def _supported(tag: str | None) -> str | None:
    """The language of a tag when it is supported, else None (so the next source is tried)."""
    if not tag:
        return None
    normalized = _normalize(tag)
    primary = tag.strip().lower().replace("_", "-").split(".")[0].split("@")[0].split("-")[0]
    return normalized if normalized != FALLBACK_LOCALE or primary in ("en", "in") else None


def _operating_system_locale() -> str | None:
    """The user interface language of the operating system, when it can be read."""
    if sys.platform == "win32":
        try:
            import ctypes

            identifier = ctypes.windll.kernel32.GetUserDefaultUILanguage()  # type: ignore[attr-defined,unused-ignore]
            return _py_locale.windows_locale.get(identifier)
        except (AttributeError, OSError):
            return None
    try:
        return _py_locale.getlocale()[0]
    except (OSError, ValueError):
        return None


@lru_cache(maxsize=1)
def _detect_locale() -> str:
    for name in ("NEXY_LANG", "LC_ALL", "LC_MESSAGES", "LANG"):
        language = _supported(os.environ.get(name))
        if language:
            return language
    # LANGUAGE is a colon-separated list in order of preference ("tr:es:fr").
    for tag in os.environ.get("LANGUAGE", "").split(":"):
        language = _supported(tag)
        if language:
            return language
    return _normalize(_operating_system_locale() or "")


@lru_cache(maxsize=len(SUPPORTED_LOCALES))
def _load_locale(locale: str) -> dict[str, Any]:
    path = _ROOT / f"{locale}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _lookup(data: dict[str, Any], key: str) -> str | None:
    value: Any = data
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value if isinstance(value, str) else None


def t(key: str, default: str | None = None, *, locale: str | None = None) -> str:
    """The message of `key` in the user's language.

    Falls back to English, then to `default`, then to the key itself.
    """
    language = locale or _detect_locale()
    message = _lookup(_load_locale(language), key)
    if message is None and language != FALLBACK_LOCALE:
        message = _lookup(_load_locale(FALLBACK_LOCALE), key)
    if message is not None:
        return message
    return default if default is not None else key
