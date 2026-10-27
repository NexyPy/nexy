"""The build cache and the outcome of compiling one file."""

from __future__ import annotations

from pathlib import Path

from nexy.errors import NexyCompileError
from nexy.modules.builder import BuildError, BuildResult, Outcome, _error_of, _record
from nexy.modules.builder.cache import BuildCache


class TestCache:
    def test_an_unknown_file_is_not_current(self, tmp_path):
        cache = BuildCache(tmp_path / "c.json", persistent=True)
        assert not cache.is_current("a.nexy", "1")

    def test_a_remembered_file_is_current_until_it_changes(self, tmp_path):
        cache = BuildCache(tmp_path / "c.json", persistent=True)
        cache.remember("a.nexy", "1")
        assert cache.is_current("a.nexy", "1") and not cache.is_current("a.nexy", "2")

    def test_the_cache_survives_a_restart(self, tmp_path):
        first = BuildCache(tmp_path / "c.json", persistent=True)
        first.remember("a.nexy", "1")
        first.save()
        assert BuildCache(tmp_path / "c.json", persistent=True).is_current("a.nexy", "1")

    def test_a_dev_cache_is_empty_and_never_written(self, tmp_path):
        file = tmp_path / "c.json"
        file.write_text('{"a.nexy": "1"}', encoding="utf-8")
        cache = BuildCache(file, persistent=False)
        cache.remember("b.nexy", "2")
        cache.save()
        assert not cache.is_current("a.nexy", "1")
        assert file.read_text(encoding="utf-8") == '{"a.nexy": "1"}'

    def test_a_corrupt_file_is_an_empty_cache(self, tmp_path):
        file = tmp_path / "c.json"
        file.write_text("{not json", encoding="utf-8")
        assert BuildCache(file, persistent=True).entries == {}

    def test_a_cache_that_is_not_an_object_is_empty(self, tmp_path):
        file = tmp_path / "c.json"
        file.write_text("[1, 2]", encoding="utf-8")
        assert BuildCache(file, persistent=True).entries == {}

    def test_a_new_configuration_forgets_every_file(self, tmp_path):
        cache = BuildCache(tmp_path / "c.json", persistent=True)
        cache.start("old", incremental=True)
        cache.remember("a.nexy", "1")
        cache.start("new", incremental=True)
        assert not cache.is_current("a.nexy", "1")

    def test_the_same_configuration_keeps_them(self, tmp_path):
        cache = BuildCache(tmp_path / "c.json", persistent=True)
        cache.start("same", incremental=True)
        cache.remember("a.nexy", "1")
        cache.start("same", incremental=True)
        assert cache.is_current("a.nexy", "1")

    def test_a_full_build_keeps_the_entries_it_is_given(self, tmp_path):
        cache = BuildCache(tmp_path / "c.json", persistent=True)
        cache.remember("a.nexy", "1")
        cache.start("new", incremental=False)
        assert cache.is_current("a.nexy", "1")

    def test_saving_creates_the_folder(self, tmp_path):
        cache = BuildCache(tmp_path / "deep" / "c.json", persistent=True)
        cache.save()
        assert (tmp_path / "deep" / "c.json").is_file()


class TestErrors:
    def test_a_compile_error_keeps_its_position_and_hint(self):
        failure = NexyCompileError("a.nexy", "bad", line=3, column=4, hint="fix it")
        error = _error_of("a.nexy", failure)
        assert (error.line, error.column, error.hint) == (3, 4, "fix it")

    def test_another_error_is_named_after_its_type(self):
        error = _error_of("a.nexy", ValueError("boom"))
        assert (error.type, error.message, error.path) == ("ValueError", "boom", "a.nexy")


class TestRecord:
    def test_a_skipped_file_is_counted_as_skipped(self):
        result = BuildResult()
        _record(Outcome("a.nexy", skipped=True), result, showlog=False)
        assert result.skipped == ["a.nexy"] and result.success == []

    def test_a_compiled_file_is_a_success(self):
        result = BuildResult()
        _record(Outcome("a.nexy"), result, showlog=False)
        assert result.success == ["a.nexy"]

    def test_a_failure_keeps_its_error(self, capsys):
        result = BuildResult()
        error = BuildError(path="a.nexy", message="bad")
        _record(Outcome("a.nexy", error=error), result, showlog=False)
        assert result.failed == ["a.nexy"] and result.errors["a.nexy"] is error
        assert "bad" in capsys.readouterr().out

    def test_the_log_names_each_file_when_asked(self, capsys):
        _record(Outcome("a.nexy"), BuildResult(), showlog=True)
        assert "compiled" in capsys.readouterr().out


def test_the_cache_path_is_inside_the_generated_folder():
    from nexy.modules.builder import Builder

    assert Builder().cache_file == Path("__nexy__") / "build-cache.json"
