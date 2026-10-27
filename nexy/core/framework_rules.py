"""What a frontend framework implies: which files are routes and which names are special."""

from __future__ import annotations

from typing import Any

from nexy.core.models import FrontendFramework

FrameworkChoice = FrontendFramework | list[FrontendFramework] | None

ALWAYS_ACTIVE_EXTENSIONS = (".nexy", ".md", ".mdx", ".py")
_SPECIAL_WITH_NEXY = ("layout", "errors", "loading")


def dotted(extension: str) -> str:
    """``tsx`` and ``.tsx`` both become ``.tsx``."""
    return extension if extension.startswith(".") else f".{extension}"


def as_list(choice: FrameworkChoice) -> list[FrontendFramework]:
    """The configured frameworks as a list, empty when there are none."""
    if choice is None:
        return []
    return choice if isinstance(choice, list) else [choice]


def require_one_framework(choice: FrameworkChoice) -> None:
    if isinstance(choice, list) and len(choice) != 1:
        raise ValueError("useFF must configure exactly one frontend framework")


def require_csr_prerequisites(csr: bool, choice: FrameworkChoice, router: Any = None) -> None:
    """Reject client routing that cannot work, instead of building an empty application.

    * no ``useFF``: the client router only renders framework components, and without a framework
      no route file is active at all;
    * ``useRouter`` (modular): module routing never reads the route directory, so ``useCSR``
      would have nothing to route.
    """
    if not csr:
        return
    if router is not None:
        raise ValueError(
            "useCSR requires file-based routing: remove useRouter from "
            "nexyconfig.py or set useCSR = False"
        )
    if not as_list(choice):
        raise ValueError(
            "useCSR requires a client framework: set useFF = react() "
            "(or vue/svelte/solid/preact), or set useCSR = False to keep "
            ".nexy server-rendered views"
        )


def route_extensions(framework: FrontendFramework | None, csr: bool = False) -> list[str]:
    """The extensions that make a file a route: Nexy's own, then the framework's."""
    exts = [ext for ext in ALWAYS_ACTIVE_EXTENSIONS if not (csr and ext == ".nexy")]
    for ext in (framework.extension if framework else None) or []:
        if dotted(ext) not in exts:
            exts.append(dotted(ext))
    return exts


def extension_map(known: dict[str, str], frameworks: list[FrontendFramework]) -> dict[str, str]:
    """*known* plus one entry per extension a framework owns, pointing at its lowercase name."""
    mapping = dict(known)
    for framework in frameworks:
        for ext in framework.extension or []:
            mapping[dotted(ext).lower()] = framework.name.lower()
    return mapping


def special_names(
    prefix: str,
    registry: dict[str, Any],
    user_exts: list[str] | None = None,
    include_nexy: bool = True,
) -> list[str]:
    """The file names that play a special role (``layout.tsx``, ``notfound.nexy``, ...)."""
    names = [f"{prefix}.nexy"] if include_nexy and prefix in _SPECIAL_WITH_NEXY else []
    extensions = {dotted(ext) for ext in user_exts or []}
    for framework in registry.values():
        extensions.update(dotted(ext) for ext in getattr(framework, "extension", []) or [])
    return [*names, *(f"{prefix}{ext.lower()}" for ext in sorted(extensions))]
