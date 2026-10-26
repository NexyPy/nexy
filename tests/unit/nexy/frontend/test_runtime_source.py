"""runtime.ts is a real TypeScript template with the navigable extensions filled in."""

from __future__ import annotations

from nexy.modules.frontend.constants import NAVIGABLE_EXTS, navigable_glob
from nexy.modules.frontend.vite_entry import runtime_source, write_runtime_file


def test_no_placeholder_is_left():
    assert "__NAVIGABLE" not in runtime_source()


def test_the_glob_covers_every_navigable_extension():
    assert f"'/src/**/*.{navigable_glob()}'" in runtime_source()


def test_the_extension_list_is_the_constant():
    listed = ", ".join(f"'{ext}'" for ext in NAVIGABLE_EXTS)
    assert f"const NAVIGABLE_EXTS = [{listed}];" in runtime_source()


def test_the_runtime_and_its_router_are_written(tmp_path):
    write_runtime_file(tmp_path)
    assert (tmp_path / "runtime.ts").is_file() and (tmp_path / "router.ts").is_file()
