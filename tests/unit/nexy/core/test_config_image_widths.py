"""`useImageWidths`: the widths `nx build` generates for local images (#658)."""

from __future__ import annotations

from nexy.core.config import Config


def test_image_widths_have_a_small_default(nexy_project):
    nexy_project()
    assert Config().useImageWidths == [320, 640, 960, 1280]


def test_image_widths_are_read_from_the_project_config(nexy_project):
    nexy_project("useImageWidths = [480, 960]")
    assert Config().useImageWidths == [480, 960]
