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


class TestLinkEscaping:
    def test_href_cannot_break_out_of_the_attribute(self):
        from nexy.link import link

        html = link('/a"><script>alert(1)</script>', "x")
        assert "<script>" not in html
        assert "&quot;" in html or "&#x27;" in html

    def test_href_cannot_break_out_of_the_prefetch_call(self):
        from nexy.link import link

        html = link("/a');alert(1);('", "x")
        assert "alert(1)" in html
        # The quote is inside a JSON string literal, never a bare statement boundary.
        assert "__nexy_prefetch(&quot;/a&#x27;);alert(1);(&#x27;&quot;)" in html

    def test_extra_attributes_are_escaped(self):
        from nexy.link import link

        html = link("/a", "x", title='"><b>')
        assert "<b>" not in html


class TestMediaEscaping:
    def test_image_attributes_are_escaped(self):
        from nexy.image import image

        html = image('/a.png" onerror="alert(1)', alt='x" onload="y')
        assert 'onerror="alert(1)' not in html
        assert 'onload="y' not in html
        assert "&quot;" in html

    def test_audio_and_video_sources_are_escaped(self):
        from nexy.audio import audio
        from nexy.video import video

        for html in (audio('/a.mp3"><script>x</script>'), video('/v.mp4"><script>x</script>')):
            assert "<script>" not in html

    def test_media_extra_attributes_are_escaped(self):
        from nexy.audio import audio

        assert "<b>" not in audio("/a.mp3", title='"><b>')

    def test_normal_media_markup_is_unchanged(self):
        from nexy.audio import audio

        html = audio("/media/song.mp3")
        assert '<source src="/media/song.mp3" type="audio/mp3" />' in html


class TestMarkdownTocEscaping:
    def test_heading_ids_are_escaped_in_the_toc(self):
        from nexy.modules.runtime.markdown import build_toc_html

        toc = build_toc_html('<h2 id="x&quot;><script>y</script>">Title</h2>')
        assert "<script>" not in toc
        assert "toc-link" in toc
