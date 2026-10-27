"""Translations of the Nexy command line: the messages, prompts and help texts of ``nx``.

Nexy itself ships no runtime i18n; an application picks the i18n library it likes.
"""

from nexy.modules.i18n._cli import (
    FALLBACK_LOCALE,
    SUPPORTED_LOCALES,
    _detect_locale,
    _load_locale,
    _normalize,
)
from nexy.modules.i18n._cli import t as t

__all__ = [
    "FALLBACK_LOCALE",
    "SUPPORTED_LOCALES",
    "_detect_locale",
    "_load_locale",
    "_normalize",
    "t",
]
