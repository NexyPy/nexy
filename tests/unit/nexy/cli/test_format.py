from pathlib import Path

from nexy.utils.fs.frontmatter import (
    reassemble_frontmatter as _reassemble,
    split_frontmatter as _split_frontmatter,
)
from nexy.utils.fs.scan import collect_files as _collect_files


def test_split_frontmatter_extracts_logic_and_template() -> None:
    source = "---\nx=1\n---\n<div>hello</div>"
    logic, template = _split_frontmatter(source)
    assert logic == "x=1"
    assert "<div>hello</div>" in template


def test_split_frontmatter_no_delimiter_returns_template_only() -> None:
    source = "<div>plain template</div>"
    logic, template = _split_frontmatter(source)
    assert logic == ""
    assert template == source


def test_reassemble_roundtrip_with_logic() -> None:
    logic, template = "x = 1", "<div>hi</div>"
    result = _reassemble(logic, template)
    assert result.startswith("---\n")
    assert "x = 1" in result
    assert result.rstrip().endswith("</div>")


def test_reassemble_without_logic_returns_template() -> None:
    assert _reassemble("", "<p>hi</p>") == "<p>hi</p>"


def test_collect_files_filters_extensions(tmp_path: Path) -> None:
    (tmp_path / "a.nexy").write_text("", encoding="utf-8")
    (tmp_path / "b.py").write_text("", encoding="utf-8")
    (tmp_path / "c.tsx").write_text("", encoding="utf-8")
    files = _collect_files(tmp_path, (".nexy",))
    assert files == [str(tmp_path / "a.nexy")]


def test_collect_files_skips_node_modules(tmp_path: Path) -> None:
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "x.nexy").write_text("", encoding="utf-8")
    (tmp_path / "a.nexy").write_text("", encoding="utf-8")
    files = _collect_files(tmp_path, (".nexy",))
    assert files == [str(tmp_path / "a.nexy")]
