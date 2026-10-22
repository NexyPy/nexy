from nexy.i18n._cli import FALLBACK_LOCALE, _deep_merge, _detect_locale, _load_locale, _normalize
from nexy.i18n._cli import t as t_cli
from nexy.i18n.core import L, LocaleManager, current_locale, t, trans, useLocale
from nexy.i18n.i18n_decorator import _I18N_REGISTRY, i18n

__all__ = [
    "L",
    "LocaleManager",
    "current_locale",
    "trans",
    "t",
    "useLocale",
    "i18n",
    "_I18N_REGISTRY",
    "t_cli",
    "_detect_locale",
    "_normalize",
    "_load_locale",
    "_deep_merge",
    "FALLBACK_LOCALE",
]
