import pytest

from nexy.errors import NexyCompileError
from nexy.modules.compiler.parser import Parser
from nexy.modules.compiler.parser.validator import ImportValidator

SOURCE = "---\nx = 1\n---\n<p>{{ x }}</p>"


def _boom(*_args, **_kwargs):
    raise ValueError("phase failed")


def test_parser_aggregates_import_and_template_errors(nexy_project, monkeypatch) -> None:
    nexy_project()
    parser = Parser()
    monkeypatch.setattr(ImportValidator, "validate_imports", _boom)
    monkeypatch.setattr(parser.template_parser, "parse", _boom)
    with pytest.raises(NexyCompileError) as exc:
        parser.process(SOURCE, "page.nexy")
    assert "2 errors found" in exc.value.message
    assert exc.value.hint is not None


def test_parser_reports_logic_error_without_template_noise(nexy_project, monkeypatch) -> None:
    nexy_project()
    parser = Parser()
    template_calls: list[str] = []
    monkeypatch.setattr(parser.logic_parser, "process", _boom)
    monkeypatch.setattr(
        parser.template_parser, "parse", lambda *_a, **_k: template_calls.append("called")
    )
    with pytest.raises(NexyCompileError, match="phase failed"):
        parser.process(SOURCE, "page.nexy")
    assert template_calls == []


def test_parser_single_phase_error_has_no_aggregate_header(nexy_project, monkeypatch) -> None:
    nexy_project()
    parser = Parser()
    monkeypatch.setattr(ImportValidator, "validate_imports", _boom)
    with pytest.raises(NexyCompileError) as exc:
        parser.process(SOURCE, "page.nexy")
    assert "errors found" not in exc.value.message
    assert exc.value.hint is not None
