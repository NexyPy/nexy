from nexy.audio import audio
from nexy.image import image
from nexy.link import link
from nexy.video import video


class TestAudio:
    def test_renders_source_tag_from_single_src(self) -> None:
        html = audio("track.mp3")

        assert "<audio" in html
        assert '<source src="track.mp3" type="audio/mp3" />' in html

    def test_sources_override_single_src(self) -> None:
        html = audio("fallback.mp3", sources=["a.mp3", "b.ogg"])

        assert '<source src="a.mp3" type="audio/mp3" />' in html
        assert '<source src="b.ogg" type="audio/ogg" />' in html
        assert "fallback.mp3" not in html

    def test_default_flags_render_controls_and_preload(self) -> None:
        html = audio("t.mp3")

        assert "controls" in html
        assert 'preload="metadata"' in html

    def test_disabled_flags_are_omitted(self) -> None:
        html = audio("t.mp3", controls=False)

        assert "controls" not in html

    def test_kwargs_and_class_name_are_merged(self) -> None:
        html = audio("t.mp3", class_name="player", **{"data-x": "1"})

        assert 'class="player"' in html
        assert 'data-x="1"' in html


class TestVideo:
    def test_renders_source_tag_from_single_src(self) -> None:
        html = video("clip.mp4")

        assert "<video" in html
        assert '<source src="clip.mp4" type="video/mp4" />' in html

    def test_width_height_render_as_strings(self) -> None:
        html = video("c.mp4", width=640, height=360)

        assert 'width="640"' in html
        assert 'height="360"' in html

    def test_disabled_controls_are_omitted(self) -> None:
        html = video("c.mp4", controls=False)

        assert "controls" not in html

    def test_loop_and_muted_render_bare_attributes(self) -> None:
        html = video("c.mp4", loop=True, muted=True)

        assert "loop" in html
        assert "muted" in html


class TestImage:
    def test_renders_img_tag_with_lazy_default(self) -> None:
        html = image("pic.png")

        assert "<img" in html
        assert 'loading="lazy"' in html

    def test_width_height_render_when_provided(self) -> None:
        html = image("p.png", width=100, height=50)

        assert 'width="100"' in html
        assert 'height="50"' in html

    def test_width_height_omitted_when_none(self) -> None:
        html = image("p.png")

        assert "width" not in html
        assert "height" not in html

    def test_class_and_kwargs_merged(self) -> None:
        html = image("p.png", class_name="thumb", **{"data-id": "7"})

        assert 'class="thumb"' in html
        assert 'data-id="7"' in html


class TestLink:
    def test_renders_anchor_with_nexy_marker(self) -> None:
        html = link("/about", "About")

        assert "<a " in html
        assert 'data-nexy-link="true"' in html
        assert ">About</a>" in html

    def test_prefetch_handlers_when_enabled(self) -> None:
        html = link("/a", prefetch=True)

        assert "onmouseenter" in html
        assert "ontouchstart" in html

    def test_no_prefetch_handlers_when_disabled(self) -> None:
        html = link("/a", prefetch=False)

        assert "onmouseenter" not in html
