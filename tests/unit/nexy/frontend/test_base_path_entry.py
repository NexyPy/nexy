"""The generated TypeScript modules publish `useBasePath` to the router and to Vite."""

from __future__ import annotations

import json
from pathlib import Path

from nexy.modules.frontend.vite_entry import write_base_file, write_mode_file


def test_the_generated_constant_carries_the_prefix(nexy_project, tmp_path: Path) -> None:
    nexy_project('useBasePath = "/app"')

    write_base_file(tmp_path)

    assert "export const BASE_PATH = '/app'" in (tmp_path / "base-path.auto.ts").read_text(
        encoding="utf-8"
    )


def test_the_generated_constant_is_empty_without_a_prefix(nexy_project, tmp_path: Path) -> None:
    nexy_project("")

    write_base_file(tmp_path)

    assert "export const BASE_PATH = ''" in (tmp_path / "base-path.auto.ts").read_text(
        encoding="utf-8"
    )


def test_the_mode_file_publishes_the_prefix(nexy_project, tmp_path: Path) -> None:
    nexy_project('useBasePath = "/app/"')

    write_mode_file(tmp_path, [])

    mode = json.loads((tmp_path / "mode.auto.json").read_text(encoding="utf-8"))
    assert mode == {"csr": False, "framework": "", "basePath": "/app"}
