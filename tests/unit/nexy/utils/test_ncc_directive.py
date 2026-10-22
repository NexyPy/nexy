from nexy.utils.imports.ncc import NexyClientComponent


class TestNccDirective:
    """<ncc directive="client:idle"> defers hydration via island attributes."""

    def test_default_tag_has_no_island_attrs(self):
        comp = NexyClientComponent("src/components/card.tsx", "react", "Card")
        html = comp.generate({})
        assert "data-nexy-island" not in html
        assert "data-nexy-directive" not in html

    def test_directive_emits_island_attrs(self):
        comp = NexyClientComponent("src/components/card.tsx", "react", "Card")
        html = comp.generate({"directive": "client:idle"})
        assert 'data-nexy-island=""' in html
        assert 'data-nexy-directive="client:idle"' in html

    def test_directive_removed_from_props(self):
        comp = NexyClientComponent("src/components/card.tsx", "react", "Card")
        html = comp.generate({"title": "Hi", "directive": "client:visible"})
        assert 'data-nexy-directive="client:visible"' in html
        assert "client:visible" not in html.split("data-nexy-props")[1].split('"')[1]

    def test_client_only_passes_through(self):
        comp = NexyClientComponent("src/components/card.tsx", "react", "Card")
        html = comp.generate({"directive": "client:only"})
        assert 'data-nexy-directive="client:only"' in html

    def test_client_media_emits_query(self):
        comp = NexyClientComponent("src/components/card.tsx", "react", "Card")
        html = comp.generate({"directive": "client:media", "media": "(min-width: 640px)"})
        assert 'data-nexy-directive="client:media"' in html
        assert 'data-nexy-media="(min-width: 640px)"' in html

    def test_client_media_without_query_omits_attr(self):
        comp = NexyClientComponent("src/components/card.tsx", "react", "Card")
        html = comp.generate({"directive": "client:media"})
        assert 'data-nexy-directive="client:media"' in html
        assert "data-nexy-media" not in html

    def test_media_removed_from_props(self):
        comp = NexyClientComponent("src/components/card.tsx", "react", "Card")
        html = comp.generate(
            {"title": "Hi", "directive": "client:media", "media": "(min-width: 640px)"}
        )
        assert "(min-width: 640px)" in html.split("data-nexy-props")[0]
