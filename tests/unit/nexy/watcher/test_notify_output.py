"""The lines the dev log prints for a recompiled page: no check mark, uv errors."""

from __future__ import annotations

import pytest

from nexy.modules.cli.devtools.watch import notify


@pytest.fixture(autouse=True)
def english(monkeypatch):
    monkeypatch.setenv("NEXY_LANG", "en")


class _Compiler:
    def compile(self, _path: str) -> None:
        return None


def test_a_recompiled_page_is_one_line_with_its_duration(capsys):
    notify.compile_page(_Compiler(), "src/routes/a.nexy")
    assert capsys.readouterr().out.startswith("Compiled src/routes/a.nexy in ")


def test_a_recompiled_page_has_no_check_mark(capsys):
    notify.compile_page(_Compiler(), "src/routes/a.nexy")
    assert "✓" not in capsys.readouterr().out


def test_a_compile_error_is_a_uv_error_with_its_cause(monkeypatch, capsys):
    monkeypatch.setattr(notify.HMR_MANAGER, "loop", None)
    notify.report_compile_error("src/routes/a.nexy", ValueError("bad tag"))
    expected = "error: Failed to compile src/routes/a.nexy\n  cause: ValueError: bad tag\n"
    assert capsys.readouterr().out == expected


def test_the_hmr_timing_line_has_no_arrow(monkeypatch, capsys):
    monkeypatch.setenv("NEXY_HMR_DEBUG", "1")
    notify._log_hmr_timing("src/routes/a.nexy", 0.0)
    assert "→" not in capsys.readouterr().out
