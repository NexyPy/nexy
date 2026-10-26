"""The line with the error, and a few lines around it, as the dev server prints them."""

from __future__ import annotations

from nexy.helpers.common.code_frame import format_frame, rows_around
from nexy.helpers.common.pycheck import find_syntax_problem, report

SOURCE = [f"line {n}" for n in range(1, 11)]


def test_rows_around_a_line_cover_three_lines_each_side():
    assert [n for n, _ in rows_around(SOURCE, 5)] == [2, 3, 4, 5, 6, 7, 8]


def test_rows_stop_at_the_first_line():
    assert [n for n, _ in rows_around(SOURCE, 1)] == [1, 2, 3, 4]


def test_rows_stop_at_the_last_line():
    assert [n for n, _ in rows_around(SOURCE, 10)] == [7, 8, 9, 10]


def test_the_faulty_line_is_marked_and_the_others_are_not():
    lines = format_frame(rows_around(SOURCE, 5), hit=5)
    marked = [line for line in lines if "> " in line]
    assert len(marked) == 1 and "line 5" in marked[0]


def test_a_caret_sits_under_the_column():
    code, caret = format_frame(((4, "def GET(:"),), hit=4, column=9)
    assert caret.index("^") == code.index("def GET(:") + 8


def test_the_numbers_line_up():
    lines = format_frame(((9, "a"), (10, "b")), hit=10)
    assert lines[0].index("|") == lines[1].index("|")


def test_markup_in_the_code_is_not_interpreted():
    assert "[bold]" in format_frame(((1, "x = '[bold]'"),), hit=1)[0].replace("\\[", "[")


def test_a_syntax_problem_carries_the_lines_around_it(tmp_path):
    path = tmp_path / "users.py"
    path.write_text("a = 1\nb = 2\ndef GET(:\n    pass\nc = 3\n", encoding="utf-8")
    problem = find_syntax_problem(str(path), tmp_path)
    assert problem is not None
    assert (problem.line, [n for n, _ in problem.rows]) == (3, [1, 2, 3, 4, 5])


def test_a_syntax_problem_knows_its_column(tmp_path):
    path = tmp_path / "users.py"
    path.write_text("def GET(:\n    pass\n", encoding="utf-8")
    problem = find_syntax_problem(str(path), tmp_path)
    assert problem is not None and problem.column == 9


def test_the_report_names_the_file_the_error_and_the_code(tmp_path, capsys):
    path = tmp_path / "users.py"
    path.write_text("a = 1\ndef GET(:\n    pass\n", encoding="utf-8")
    problem = find_syntax_problem(str(path), tmp_path)
    assert problem is not None
    report(problem, "Fix it and save.")
    out = capsys.readouterr().out
    assert "nexy » error" in out and "SyntaxError" in out and "def GET(:" in out
    assert "Fix it and save." in out


class TestStrayMarkdown:
    def test_a_readme_at_the_root_is_not_a_page(self):
        from nexy.modules.cli.devtools.watcher import is_stray_markdown

        assert is_stray_markdown("README.md") is True

    def test_a_markdown_route_is_a_page(self):
        from nexy.modules.cli.devtools.watcher import is_stray_markdown

        assert is_stray_markdown("src/routes/blog/post.md") is False

    def test_a_python_file_is_never_stray(self):
        from nexy.modules.cli.devtools.watcher import is_stray_markdown

        assert is_stray_markdown("src/routes/users.py") is False
