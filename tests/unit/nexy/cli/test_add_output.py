"""`nx add` says what it did the way uv does: a plus per file, uv errors and warnings."""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from nexy.modules.cli import CLI

# The package re-exports the function under the module's name: import the module by path.
add = importlib.import_module("nexy.modules.cli.commands.add")


def run_add(*arguments):
    return CliRunner().invoke(CLI, ["add", *arguments])


@pytest.fixture(autouse=True)
def english(monkeypatch):
    monkeypatch.setenv("NEXY_LANG", "en")


# The path as the system writes it: `ui\Button.nexy` on Windows, `ui/Button.nexy` elsewhere.
BUTTON = Path("ui", "Button.nexy")


def test_add_an_added_component_is_listed_with_a_plus(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    add._write_nexy_component(Path("ui"), "Button", "export default () => null", "react")
    assert capsys.readouterr().out == f" + {BUTTON}\n"


def test_add_a_component_that_exists_is_a_uv_warning(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    Path("Button.nexy").write_text("kept")
    add._write_nexy_component(Path(), "Button", "x", "react")
    expected = "warning: Skipping: Button.nexy already exists.\n"
    assert capsys.readouterr().out == expected


def test_add_an_unknown_component_is_a_uv_error(capsys):
    add._resolve_registry_component("definitely-not-a-component", "react")
    expected = "error: Component 'definitely-not-a-component' not found in registry.\n"
    assert capsys.readouterr().out == expected


def test_add_a_plain_http_url_is_a_uv_error(capsys):
    add.fetch_remote_component("http://example.com/c.tsx")
    assert capsys.readouterr().out == "error: Only https:// URLs are supported.\n"


def test_add_a_failed_download_is_a_uv_error_with_its_cause(monkeypatch, capsys):
    def offline(_url):
        raise OSError("no route to host")

    monkeypatch.setattr(add, "_download", offline)
    add.fetch_remote_component("https://example.com/c.tsx")
    error, cause = capsys.readouterr().out.splitlines()
    assert (error, cause) == (
        "error: Failed to fetch component from https://example.com/c.tsx",
        "  cause: no route to host",
    )


def test_add_a_component_that_cannot_be_written_is_a_uv_error(tmp_path, monkeypatch, capsys):
    def refuse(*_args):
        raise OSError("read-only file system")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(add.PathUtil, "write_file", refuse)
    add._write_nexy_component(Path("ui"), "Button", "x", "react")
    assert (
        capsys.readouterr().out
        == f"error: Failed to write {BUTTON}\n  cause: read-only file system\n"
    )


class TestAddVercel:
    def test_entry_point_imports_the_application(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        run_add("vercel")
        assert "import_module" in Path("src/server.py").read_text()

    def test_entry_point_copies_the_project_into_a_writable_root(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        run_add("vercel")
        body = Path("src/server.py").read_text()
        assert all(name in body for name in ('"src"', '"__nexy__"', '"public"', '"nexyconfig.py"'))

    def test_host_config_caches_hashed_assets_forever(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        run_add("vercel")
        config = json.loads(Path("vercel.json").read_text())
        assert config["headers"][0]["headers"][0]["value"] == (
            "public, max-age=31536000, immutable"
        )

    def test_host_config_caches_images_for_one_day(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        run_add("vercel")
        config = json.loads(Path("vercel.json").read_text())
        assert config["headers"][1]["headers"][0]["value"] == (
            "public, max-age=86400, stale-while-revalidate=604800"
        )

    def test_generated_files_are_ignored_once(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        Path(".gitignore").write_text("*.log\n")
        run_add("vercel")
        run_add("vercel")
        assert Path(".gitignore").read_text().count("__nexy__/build-cache.json") == 1

    def test_an_existing_entry_point_is_kept(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        Path("src/server.py").parent.mkdir(parents=True)
        Path("src/server.py").write_text("kept")
        run_add("vercel")
        assert Path("src/server.py").read_text() == "kept"

    def test_an_unknown_platform_is_an_error(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = run_add("netlify")
        assert "error:" in result.stdout

    def test_mixing_a_platform_with_a_component_is_an_error(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = run_add("vercel", "button")
        assert "error:" in result.stdout

    def test_a_platform_with_flags_is_an_error(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = run_add("vercel", "--all")
        assert "error:" in result.stdout

    def test_a_platform_is_not_installed_as_a_component(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(add, "install_packages", lambda _names: pytest.fail("install called"))
        run_add("vercel")
        assert not Path("src/components/ui/vercel.nexy").exists()
