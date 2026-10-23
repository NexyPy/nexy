"""The public ``nexy.frontend`` module is the documented framework import path.

Every template, example and docs page ships ``from nexy.frontend import react``
(and the other framework helpers). That module must exist and re-export the
implementations from ``nexy.modules.frontend``.
"""

import importlib

import pytest

from nexy.core.models import FrontendFramework

FRAMEWORKS = ("react", "preact", "solid", "svelte", "vue")


@pytest.mark.parametrize("name", FRAMEWORKS)
def test_public_module_exposes_framework(name: str) -> None:
    module = importlib.import_module("nexy.frontend")

    assert callable(getattr(module, name))


@pytest.mark.parametrize("name", FRAMEWORKS)
def test_public_framework_returns_framework(name: str) -> None:
    module = importlib.import_module("nexy.frontend")

    assert isinstance(getattr(module, name)(), FrontendFramework)


def test_public_module_reexports_same_object() -> None:
    public = importlib.import_module("nexy.frontend")
    internal = importlib.import_module("nexy.modules.frontend")

    assert public.react is internal.react
