from pathlib import Path

import pytest

from nexy.vite import Vite

MINIMAL_VITE_CONFIG = "export default {};\n"


@pytest.fixture
def dev_project(nexy_project, tmp_path: Path) -> None:
    """A dev project where Vite() emits the client HMR/overlay script.

    Replaces the dependency on the repo-root vite.config.ts removed by
    cleanup: the script is only emitted for a project that enables Vite.
    """
    nexy_project("useVite = True")
    (tmp_path / "vite.config.ts").write_text(MINIMAL_VITE_CONFIG, encoding="utf-8")


class TestViteErrorOverlay:
    """Dev client WS must render a browser overlay on nexy:error."""

    def test_hmr_script_handles_nexy_error(self, dev_project: None):
        script = Vite()
        assert "nexy:error" in script
        assert "nexyErrorOverlay" in script

    def test_overlay_renders_error_file_and_message(self, dev_project: None):
        script = Vite()
        assert "data.errors" in script
        assert "e.file" in script
        assert "e.message" in script

    def test_overlay_has_styled_container(self, dev_project: None):
        script = Vite()
        assert "nexy-error-overlay" in script
