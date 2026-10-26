"""The shared part of audio and video."""

from __future__ import annotations

from nexy.helpers.html.media import media_element, playback_attributes, render_attributes
from nexy.video import video


def _flags(**changes):
    base = {
        "preload": "metadata",
        "class_name": None,
        "controls": False,
        "autoplay": False,
        "loop": False,
        "muted": False,
    }
    return playback_attributes(**{**base, **changes})


def test_a_flag_that_is_on_becomes_a_bare_attribute():
    assert render_attributes(_flags(loop=True)) == 'preload="metadata" loop'


def test_a_flag_that_is_off_is_left_out():
    assert "loop" not in render_attributes(_flags())


def test_a_value_is_escaped():
    assert render_attributes({"title": 'a"b'}) == 'title="a&quot;b"'


def test_the_sources_replace_the_single_src():
    markup = media_element("audio", {}, "x.mp3", ["a.mp3", "b.ogg"])
    assert "x.mp3" not in markup and "b.ogg" in markup


def test_a_path_cannot_break_out_of_its_attribute():
    markup = media_element("video", {}, '"><script>.mp4', None)
    assert "<script>" not in markup


def test_the_size_comes_right_after_preload():
    markup = video("c.mp4", width=1, class_name="x", controls=False)
    assert markup.startswith('<video preload="metadata" width="1" class="x">')
