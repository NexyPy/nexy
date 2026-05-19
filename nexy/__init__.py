from __future__ import annotations

import importlib
from types import ModuleType

_LAZY_MODULES: dict[str, tuple[str, str]] = {
    "Audio": ("nexy.audio", "Audio"),
    "Video": ("nexy.video", "Video"),
    "Form": ("nexy.form", "Form"),
    "Import": ("nexy._import", "Import"),
    "Template": ("nexy.template", "Template"),
    "Vite": ("nexy.vite", "Vite"),
    "useViews": ("nexy.hooks", "useViews"),
    "usePathname": ("nexy.hooks", "usePathname"),
    "useSearchParams": ("nexy.hooks", "useSearchParams"),
    "useRouter": ("nexy.hooks", "useRouter"),
    "useQuery": ("nexy.hooks", "useQuery"),
    "useSession": ("nexy.hooks", "useSession"),
    "useCookies": ("nexy.hooks", "useCookies"),
}

_CACHE: dict[str, object] = {}


def __getattr__(name: str) -> object:
    if name in _CACHE:
        return _CACHE[name]
    if name in _LAZY_MODULES:
        mod_path, attr = _LAZY_MODULES[name]
        mod: ModuleType = importlib.import_module(mod_path)
        val = getattr(mod, attr)
        _CACHE[name] = val
        return val
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return [*_LAZY_MODULES.keys(), "app"]


__all__ = [
    "Audio",
    "Video",
    "Form",
    "Import",
    "Template",
    "Vite",
    "app",
    "useViews",
    "usePathname",
    "useSearchParams",
    "useRouter",
    "useQuery",
    "useSession",
    "useCookies",
]
