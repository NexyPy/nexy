from nexy.frontend import preact, react, solid, svelte, vue


class TestFrameworkIslands:
    """Every framework entry must honor client: directives via nexyIslands."""

    def test_react_embeds_islands_runtime(self):
        render = react().render
        assert "nexyIslands" in render
        assert "nexyIslands.init" in render

    def test_vue_embeds_islands_runtime(self):
        render = vue().render
        assert "nexyIslands" in render
        assert "nexyIslands.init" in render

    def test_svelte_embeds_islands_runtime(self):
        render = svelte().render
        assert "nexyIslands" in render
        assert "nexyIslands.init" in render

    def test_solid_embeds_islands_runtime(self):
        render = solid().render
        assert "nexyIslands" in render
        assert "nexyIslands.init" in render

    def test_preact_embeds_islands_runtime(self):
        render = preact().render
        assert "nexyIslands" in render
        assert "nexyIslands.init" in render

    def test_every_framework_skips_client_only(self):
        for fw in (react, vue, svelte, solid, preact):
            assert "client:only" in fw().render
