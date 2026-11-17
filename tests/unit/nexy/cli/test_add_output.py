"""`nx add` says what it did the way uv does: a plus per file, uv errors and warnings."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

# The package re-exports the function under the module's name: import the module by path.
add = importlib.import_module("nexy.modules.cli.commands.add")


@pytest.fixture(autouse=True)
def english(monkeypatch):
    monkeypatch.setenv("NEXY_LANG", "en")


def test_add_an_added_component_is_listed_with_a_plus(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    add._write_nexy_component(Path("ui"), "Button", "export default () => null", "react")
    assert capsys.readouterr().out == " + ui/Button.nexy\n"


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
        == "error: Failed to write ui/Button.nexy\n  cause: read-only file system\n"
    )
