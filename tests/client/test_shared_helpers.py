"""Link and Image behave alike in every framework because they share these helpers."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
NODE = shutil.which("node")


@pytest.fixture(scope="module")
def seen() -> dict:
    done = subprocess.run(
        [NODE, str(HERE / "shared_scenarios.mjs")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
        cwd=HERE,
    )
    assert "@@" in done.stdout, (done.stdout + done.stderr)[-1500:]
    return json.loads(done.stdout.split("@@")[1])


def test_a_path_loses_its_query_fragment_and_trailing_slash(seen):
    assert seen["paths"] == ["/", "/about", "/about", "/about", "/", "/a/b"]


class TestActiveLink:
    @pytest.mark.parametrize("case", ["same", "trailing", "query", "parent", "rootSelf"])
    def test_these_links_are_active(self, seen, case):
        assert seen["active"][case] is True

    @pytest.mark.parametrize("case", ["parentExact", "sibling", "root"])
    def test_these_are_not(self, seen, case):
        assert seen["active"][case] is False


class TestImage:
    def test_it_is_lazy_and_decoded_off_the_main_thread_by_default(self, seen):
        basic = seen["image"]["basic"]
        assert basic["loading"] == "lazy" and basic["decoding"] == "async"
        assert "fetchpriority" not in basic

    def test_both_dimensions_keep_the_aspect_ratio_when_css_resizes_it(self, seen):
        sized = seen["image"]["sized"]
        assert sized["width"] == 800 and sized["height"] == 600
        assert sized["style"] == {"height": "auto", "maxWidth": "100%"}

    def test_a_single_dimension_adds_no_style(self, seen):
        assert "style" not in seen["image"]["widthOnly"]

    def test_a_priority_image_loads_now_at_high_priority(self, seen):
        priority = seen["image"]["priority"]
        assert priority["loading"] == "eager" and priority["fetchpriority"] == "high"

    def test_a_filling_image_covers_its_parent_and_ignores_dimensions(self, seen):
        fill = seen["image"]["fill"]
        assert fill["style"]["position"] == "absolute" and fill["style"]["objectFit"] == "cover"
        assert "width" not in fill and "height" not in fill

    def test_an_explicit_loading_wins(self, seen):
        assert seen["image"]["explicitLoading"]["loading"] == "eager"

    def test_responsive_sources_are_passed_through(self, seen):
        responsive = seen["image"]["responsive"]
        assert responsive["sizes"] == "100vw" and responsive["srcset"].startswith("/a.png 1x")


def test_style_objects_become_css_text(seen):
    assert seen["css"] == {"camel": "max-width:100%;object-fit:cover", "empty": ""}
