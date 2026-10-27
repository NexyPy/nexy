"""Imports of files are checked before compiling: a missing one is reported with what was meant."""

from __future__ import annotations

from pathlib import Path

import pytest

from nexy.core.config import Config
from nexy.core.models import NexyImport
from nexy.modules.compiler.parser.validator import ImportValidationError, ImportValidator


@pytest.fixture
def project(tmp_path, monkeypatch) -> Path:
    monkeypatch.setattr(Config, "PROJECT_ROOT", tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "page.nexy").write_text("", encoding="utf-8")
    (tmp_path / "src" / "card.nexy").write_text("", encoding="utf-8")
    return tmp_path


def _validate(project: Path, *imports: NexyImport) -> None:
    ImportValidator.validate_imports(list(imports), str(project / "src" / "page.nexy"))


def test_a_relative_import_is_resolved_from_the_importing_file(project):
    _validate(project, NexyImport(path="./card.nexy", symbol="Card"))


def test_a_parent_relative_import_is_resolved(project):
    (project / "shared.nexy").write_text("", encoding="utf-8")
    _validate(project, NexyImport(path="../shared.nexy", symbol="Shared"))


def test_a_project_relative_import_is_resolved_from_the_root(project):
    _validate(project, NexyImport(path="src/card.nexy", symbol="Card"))


def test_an_absolute_import_is_resolved_as_is(project):
    _validate(project, NexyImport(path=str(project / "src" / "card.nexy"), symbol="Card"))


def test_a_missing_file_is_an_error(project):
    with pytest.raises(ImportValidationError):
        _validate(project, NexyImport(path="./nope.nexy", symbol="Nope"))


def test_the_error_names_the_import_and_the_resolved_path(project):
    with pytest.raises(ImportValidationError) as caught:
        _validate(project, NexyImport(path="./nope.nexy", symbol="Nope", alias="N"))
    message = str(caught.value)
    assert "./nope.nexy" in message and "symbol='Nope'" in message and "alias='N'" in message


def test_files_with_the_same_stem_are_suggested(project):
    (project / "src" / "card.tsx").write_text("", encoding="utf-8")
    with pytest.raises(ImportValidationError) as caught:
        _validate(project, NexyImport(path="./card.vue", symbol="Card"))
    assert "card.tsx" in str(caught.value) and "card.nexy" in str(caught.value)


def test_no_suggestion_is_made_when_the_folder_does_not_exist(project):
    with pytest.raises(ImportValidationError) as caught:
        _validate(project, NexyImport(path="./ghost/card.nexy", symbol="Card"))
    assert "suggestions" not in str(caught.value)


def test_the_first_missing_import_stops_the_check(project):
    with pytest.raises(ImportValidationError) as caught:
        _validate(
            project,
            NexyImport(path="./a-missing.nexy", symbol="A"),
            NexyImport(path="./b-missing.nexy", symbol="B"),
        )
    assert "a-missing" in str(caught.value) and "b-missing" not in str(caught.value)


def test_no_imports_is_fine(project):
    _validate(project)
