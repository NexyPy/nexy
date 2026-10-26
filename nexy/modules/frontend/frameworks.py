"""The frontend frameworks Nexy can mount: a name, the files they own and their browser script."""

from __future__ import annotations

from nexy.core.models import FrontendFramework
from nexy.modules.frontend.islands import ISLANDS_RUNTIME, script

_EXTENSIONS: dict[str, tuple[str, ...]] = {
    "react": ("jsx", "tsx"),
    "vue": ("vue",),
    "solid": ("jsx", "tsx"),
    "svelte": ("svelte",),
    "preact": ("jsx", "tsx"),
}


def framework(name: str) -> FrontendFramework:
    """The framework called *name*; its script is the shared islands runtime plus its own."""
    extension = list(_EXTENSIONS[name])
    return FrontendFramework(name=name, render=ISLANDS_RUNTIME + script(name), extension=extension)


def react() -> FrontendFramework:
    return framework("react")


def vue() -> FrontendFramework:
    return framework("vue")


def solid() -> FrontendFramework:
    return framework("solid")


def svelte() -> FrontendFramework:
    return framework("svelte")


def preact() -> FrontendFramework:
    return framework("preact")
