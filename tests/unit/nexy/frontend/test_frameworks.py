"""Each framework ships its browser script as a .js file, after the shared islands runtime."""

from __future__ import annotations

import pytest

from nexy.modules.frontend.frameworks import framework
from nexy.modules.frontend.islands import ISLANDS_RUNTIME

NAMES = ["react", "vue", "solid", "svelte", "preact"]


@pytest.mark.parametrize("name", NAMES)
def test_the_script_starts_with_the_islands_runtime(name):
    assert framework(name).render.startswith(ISLANDS_RUNTIME)


@pytest.mark.parametrize("name", NAMES)
def test_the_script_mounts_its_own_framework(name):
    render = framework(name).render
    assert "data-nexy-fw" in render and name in render


@pytest.mark.parametrize(
    ("name", "extensions"),
    [
        ("react", ["jsx", "tsx"]),
        ("vue", ["vue"]),
        ("svelte", ["svelte"]),
        ("solid", ["jsx", "tsx"]),
    ],
)
def test_a_framework_owns_its_file_extensions(name, extensions):
    assert framework(name).extension == extensions


def test_an_unknown_framework_is_an_error():
    with pytest.raises(KeyError):
        framework("angular")
