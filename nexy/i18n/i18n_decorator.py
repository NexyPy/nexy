from __future__ import annotations

from typing import Any

_I18N_REGISTRY: dict[str, type] = {}


def i18n():
    def wrapper(cls: type) -> type:
        qual = f"{cls.__module__}.{cls.__qualname__}"
        _I18N_REGISTRY[qual] = cls
        cls.__i18n_defaults__ = {
            k: v for k, v in cls.__dict__.items() if not k.startswith("_") and isinstance(v, str)
        }

        orig_getattr = cls.__getattribute__

        def __getattribute__(self: Any, name: str) -> Any:
            if name.startswith("_"):
                return orig_getattr(self, name)
            from nexy.i18n.core import trans

            key = f"{cls.__qualname__}.{name}"
            val = trans(key)
            if val != key:
                return val
            return orig_getattr(self, name)

        cls.__getattribute__ = __getattribute__
        return cls

    return wrapper
