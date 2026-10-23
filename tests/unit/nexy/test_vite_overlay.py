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

    @pytest.mark.usefixtures("dev_project")
    def test_hmr_script_handles_nexy_error(self):
        script = Vite()
        assert "nexy:error" in script
        assert "nexyErrorOverlay" in script

    @pytest.mark.usefixtures("dev_project")
    def test_overlay_renders_error_file_and_message(self):
        script = Vite()
        assert "data.errors" in script
        assert "e.file" in script
        assert "e.message" in script

    @pytest.mark.usefixtures("dev_project")
    def test_overlay_has_styled_container(self):
        script = Vite()
        assert "nexy-error-overlay" in script


class TestViteTagsAreSameOrigin:
    """Vite tags must be relative: the dev server exposes a single origin.

    Absolute URLs pointed at the internal Vite port, which leaked that port and
    only worked for a browser on the machine running the dev server.
    """

    @pytest.mark.usefixtures("dev_project")
    def test_client_tag_is_relative(self):
        assert 'src="/@vite/client"' in Vite()

    @pytest.mark.usefixtures("dev_project")
    def test_entry_tag_is_relative(self):
        assert 'src="/__nexy__/main.ts"' in Vite()

    @pytest.mark.usefixtures("dev_project")
    def test_no_hardcoded_localhost(self):
        assert "localhost" not in Vite()
