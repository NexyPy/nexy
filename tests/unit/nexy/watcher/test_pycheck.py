"""What the dev server says about a broken Python file."""

from __future__ import annotations

from nexy.helpers.common.pycheck import describe, find_syntax_problem


def test_a_valid_file_has_no_problem(tmp_path):
    (tmp_path / "ok.py").write_text("x = 1\n", encoding="utf-8")
    assert find_syntax_problem(str(tmp_path / "ok.py"), tmp_path) is None


def test_a_syntax_error_names_the_file_and_the_line(tmp_path):
    (tmp_path / "bad.py").write_text("x = 1\ndef f(:\n", encoding="utf-8")
    problem = find_syntax_problem(str(tmp_path / "bad.py"), tmp_path)
    assert problem is not None and problem.location == "bad.py:2"


def test_a_syntax_error_has_the_kind_of_the_error(tmp_path):
    (tmp_path / "bad.py").write_text("if True:\nx = 1\n", encoding="utf-8")
    problem = find_syntax_problem(str(tmp_path / "bad.py"), tmp_path)
    assert problem is not None and problem.kind == "IndentationError"


def test_a_missing_file_has_no_problem(tmp_path):
    assert find_syntax_problem(str(tmp_path / "gone.py"), tmp_path) is None


def test_a_null_byte_is_a_problem(tmp_path):
    (tmp_path / "nul.py").write_bytes(b"x = 1\x00\n")
    assert find_syntax_problem(str(tmp_path / "nul.py"), tmp_path) is not None


def test_an_import_error_points_at_the_project_frame(tmp_path):
    source = tmp_path / "boom.py"
    source.write_text("\n\nraise KeyError('src')\n", encoding="utf-8")
    try:
        exec(compile(source.read_text(encoding="utf-8"), str(source), "exec"), {})
    except KeyError as error:
        problem = describe(error, tmp_path)
    assert problem.location == "boom.py:3"


def test_a_syntax_error_raised_by_an_import_keeps_its_line(tmp_path):
    source = tmp_path / "bad.py"
    source.write_text("def f(:\n", encoding="utf-8")
    try:
        compile(source.read_text(encoding="utf-8"), str(source), "exec")
    except SyntaxError as error:
        problem = describe(error, tmp_path)
    assert problem.location == "bad.py:1"


def test_an_error_outside_the_project_has_no_location(tmp_path):
    problem = describe(ValueError("nope"), tmp_path)
    assert problem.location == "-"
