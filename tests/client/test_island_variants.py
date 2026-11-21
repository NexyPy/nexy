"""The client build renders an island once per set of literal props a page gives it (#554)."""

from __future__ import annotations

import json
import shutil
import subprocess
from functools import cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
NODE = shutil.which("node")
PROPS = {
    "src/components/spike.tsx": {
        "Spike": {"k1": {"label": "clicks"}, "k2": {"label": "boom"}},
        "Badge": {"k3": {"label": "new"}},
    }
}


@cache
def _checked(root: str) -> dict:
    done = subprocess.run(
        [NODE, str(HERE / "island_variants.mjs"), root],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
        cwd=HERE,
    )
    assert done.stdout.startswith("{"), (done.stdout + done.stderr)[-1500:]
    return json.loads(done.stdout)


def _result(tmp_path_factory) -> dict:
    root = tmp_path_factory.getbasetemp() / "island-variants"
    manifest = root / "__nexy__" / "client" / "island-props.json"
    if not manifest.is_file():
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps(PROPS), encoding="utf-8")
    return _checked(str(root))


def test_a_build_without_the_list_has_no_props(tmp_path_factory):
    assert _result(tmp_path_factory)["missing"] == {}


def test_a_symbol_the_file_does_not_export_is_its_default_export(tmp_path_factory):
    assert list(_result(tmp_path_factory)["defaultExport"]) == ["k1", "k2"]


def test_a_symbol_the_file_exports_is_that_export(tmp_path_factory):
    assert _result(tmp_path_factory)["namedExport"] == {"k3": {"label": "new"}}


def test_a_file_no_page_gives_props_has_none(tmp_path_factory):
    assert _result(tmp_path_factory)["otherFile"] == {}


def test_each_set_of_props_is_rendered_under_its_key(tmp_path_factory):
    assert _result(tmp_path_factory)["rendered"] == [["k1", "<b>clicks</b>"]]


def test_a_set_of_props_that_fails_to_render_is_reported(tmp_path_factory):
    assert "it broke" in _result(tmp_path_factory)["warnings"][0]
