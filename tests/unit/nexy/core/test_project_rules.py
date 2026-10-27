"""A project is either server-rendered (.nexy) or client-routed (framework files), never both."""

from pathlib import Path

from nexy.core.project_rules import project_problems

_REACT = "from nexy.frontend import react"


def _write(root: Path, rel: str, content: str = "x") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestServerMode:
    def test_nexy_pages_and_islands_are_fine(self, nexy_project, tmp_path):
        nexy_project("useFF = react()", imports=_REACT)
        _write(tmp_path, "src/routes/index.nexy")
        _write(tmp_path, "src/routes/layout.nexy")
        _write(tmp_path, "src/routes/api/x.py")
        _write(tmp_path, "src/components/Counter.tsx")
        assert project_problems(tmp_path) == []

    def test_a_client_route_is_rejected(self, nexy_project, tmp_path):
        nexy_project("useFF = react()", imports=_REACT)
        _write(tmp_path, "src/routes/index.nexy")
        _write(tmp_path, "src/routes/users.tsx")
        (problem,) = project_problems(tmp_path)
        assert "users.tsx" in problem and "useCSR = False" in problem

    def test_a_framework_layout_is_rejected(self, nexy_project, tmp_path):
        nexy_project("useFF = react()", imports=_REACT)
        _write(tmp_path, "src/routes/layout.nexy")
        _write(tmp_path, "src/routes/blog/layout.tsx")
        (problem,) = project_problems(tmp_path)
        assert "blog/layout.tsx" in problem

    def test_hidden_files_are_not_routes(self, nexy_project, tmp_path):
        nexy_project("useFF = react()", imports=_REACT)
        _write(tmp_path, "src/routes/_partials/Card.tsx")
        assert project_problems(tmp_path) == []


class TestClientMode:
    def test_client_routes_and_api_are_fine(self, nexy_project, tmp_path):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        _write(tmp_path, "src/routes/layout.tsx")
        _write(tmp_path, "src/routes/users.tsx")
        _write(tmp_path, "src/routes/api/users.py")
        assert project_problems(tmp_path) == []

    def test_a_nexy_page_is_rejected(self, nexy_project, tmp_path):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        _write(tmp_path, "src/routes/users.tsx")
        _write(tmp_path, "src/routes/blog.nexy")
        (problem,) = project_problems(tmp_path)
        assert "blog.nexy" in problem and "useCSR = True" in problem

    def test_layout_nexy_is_rejected(self, nexy_project, tmp_path):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        _write(tmp_path, "src/routes/layout.nexy")
        (problem,) = project_problems(tmp_path)
        assert "layout.nexy" in problem

    def test_many_files_are_summarised(self, nexy_project, tmp_path):
        nexy_project("useCSR = True\nuseFF = react()", imports=_REACT)
        for index in range(8):
            _write(tmp_path, f"src/routes/p{index}.nexy")
        (problem,) = project_problems(tmp_path)
        assert "and 3 more" in problem


def test_no_routes_directory_means_no_problem(nexy_project, tmp_path):
    nexy_project("")
    assert project_problems(tmp_path) == []
