from nexy.vite import Vite


class TestViteErrorOverlay:
    """Dev client WS must render a browser overlay on nexy:error."""

    def test_hmr_script_handles_nexy_error(self):
        script = Vite()
        assert "nexy:error" in script
        assert "nexyErrorOverlay" in script

    def test_overlay_renders_error_file_and_message(self):
        script = Vite()
        assert "data.errors" in script
        assert "e.file" in script
        assert "e.message" in script

    def test_overlay_has_styled_container(self):
        script = Vite()
        assert "nexy-error-overlay" in script
