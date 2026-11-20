"""Every web starter ships a /todos page and the six server actions it calls."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

from nexy.modules.cli.init.template_setup import _render_local_template

PAGES = {
    "none": "todos.nexy",
    "react": "todos.tsx",
    "preact": "todos.tsx",
    "solid": "todos.tsx",
    "vue": "todos.vue",
    "svelte": "todos.svelte",
}
STARTERS = [(style, fw) for style in ("tailwind", "vanilla") for fw in PAGES]
ACTIONS = ["todos", "add_todo", "toggle_todo", "rename_todo", "delete_todo", "clear_done"]


def _scaffold(dest: Path, style: str, framework: str, orm: str = "None", fbr: bool = True) -> Path:
    config = {
        "client_framework": framework,
        "FBRouter": fbr,
        "project_type": "web",
        "orm": orm,
        "useCSR": framework != "none",
        "style": style,
    }
    _render_local_template("web-fbr" if fbr else "web-modular", dest, config, "demo")
    return dest


def _page(tmp_path: Path, style: str, framework: str) -> str:
    _scaffold(tmp_path, style, framework)
    return (tmp_path / "src" / "routes" / PAGES[framework]).read_text("utf-8")


def _actions(tmp_path: Path, orm: str = "None") -> str:
    _scaffold(tmp_path, "vanilla", "react", orm)
    return (tmp_path / "src/actions/todos.py").read_text("utf-8")


def _memory_service(tmp_path: Path) -> ModuleType:
    _scaffold(tmp_path, "vanilla", "react")
    path = tmp_path / "src/services/todo_service.py"
    spec = importlib.util.spec_from_file_location("todo_service_under_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(("style", "framework"), STARTERS)
class TestTheTodosPage:
    def test_the_page_has_a_field_for_a_new_task(self, tmp_path, style, framework):
        assert 'placeholder="What needs to be done?"' in _page(tmp_path, style, framework)

    def test_a_refused_change_is_announced_to_a_screen_reader(self, tmp_path, style, framework):
        assert 'aria-live="polite"' in _page(tmp_path, style, framework)

    def test_the_filters_say_which_one_is_on(self, tmp_path, style, framework):
        assert "aria-pressed" in _page(tmp_path, style, framework)

    def test_no_build_time_jinja_is_left(self, tmp_path, style, framework):
        assert "{%" not in _page(tmp_path, style, framework)


@pytest.mark.parametrize("framework", [fw for fw in PAGES if fw != "none"])
def test_a_client_routed_page_calls_the_shared_module(tmp_path, framework):
    assert 'from "../lib/todos";' in _page(tmp_path, "vanilla", framework)


def test_the_shared_module_calls_the_typed_actions(tmp_path):
    _scaffold(tmp_path, "vanilla", "react")
    text = (tmp_path / "src/lib/todos.ts").read_text("utf-8")
    assert f'import {{ {", ".join(sorted(ACTIONS))} }} from "@nexy/actions";' in text


def test_a_server_page_has_no_shared_module(tmp_path):
    _scaffold(tmp_path, "vanilla", "none")
    assert not (tmp_path / "src/lib").exists()


@pytest.mark.parametrize("action", ACTIONS)
def test_a_server_page_reaches_each_action(tmp_path, action):
    attribute = f"data-{action.replace('_', '-')}=\"{{{{ __actions_path['{action}'] }}}}\""
    assert attribute in _page(tmp_path, "vanilla", "none")


def test_a_server_page_writes_a_title_as_text(tmp_path):
    assert "title.textContent = todo.title;" in _page(tmp_path, "vanilla", "none")


def test_a_utility_page_has_no_class_of_the_plain_stylesheet(tmp_path):
    assert "nx-todo" not in _page(tmp_path, "tailwind", "react")


def test_a_modular_project_shows_the_page_from_its_todos_app(tmp_path):
    _scaffold(tmp_path, "vanilla", "none", fbr=False)
    assert "todos/todo_view.nexy" in (tmp_path / "src/apps/app_controller.py").read_text("utf-8")


def test_a_modular_project_has_the_actions_in_its_todos_app(tmp_path):
    _scaffold(tmp_path, "vanilla", "none", fbr=False)
    assert "def add_todo(" in (tmp_path / "src/apps/todos/todo_actions.py").read_text("utf-8")


def test_a_web_project_has_no_users_page(tmp_path):
    _scaffold(tmp_path, "vanilla", "none", "SQLModel")
    assert not (tmp_path / "src/routes/users").exists()


@pytest.mark.parametrize("orm", ["SQLModel", "SQLAlchemy"])
def test_with_a_database_the_tasks_are_the_todos_table(tmp_path, orm):
    _scaffold(tmp_path, "vanilla", "react", orm)
    model = (tmp_path / "src/models/todo_model.py").read_text("utf-8")
    assert '__tablename__ = "todos"' in model


def test_with_tortoise_the_tasks_are_the_todos_table(tmp_path):
    _scaffold(tmp_path, "vanilla", "react", "Tortoise-ORM")
    assert 'table = "todos"' in (tmp_path / "src/models/todo_model.py").read_text("utf-8")


def test_with_tortoise_the_actions_wait_on_its_own_loop(tmp_path):
    assert "await arun(TodoService.add(title))" in _actions(tmp_path, "Tortoise-ORM")


def test_with_tortoise_the_config_registers_the_todo_model(tmp_path):
    _scaffold(tmp_path, "vanilla", "react", "Tortoise-ORM")
    assert '"src.models.todo_model"' in (tmp_path / "src/configs/db.py").read_text("utf-8")


@pytest.mark.parametrize("orm", ["None", "SQLModel", "SQLAlchemy", "Tortoise-ORM"])
def test_the_actions_are_valid_python(tmp_path, orm):
    compile(_actions(tmp_path, orm), "todos.py", "exec")


@pytest.mark.parametrize("orm", ["None", "SQLModel", "SQLAlchemy", "Tortoise-ORM"])
def test_the_service_is_valid_python(tmp_path, orm):
    _scaffold(tmp_path, "vanilla", "react", orm)
    source = (tmp_path / "src/services/todo_service.py").read_text("utf-8")
    compile(source, "todo_service.py", "exec")


class TestTheMemoryService:
    def test_it_starts_with_three_tasks(self, tmp_path):
        assert len(_memory_service(tmp_path).TodoService.all()) == 3

    def test_add_gives_the_next_id(self, tmp_path):
        service = _memory_service(tmp_path).TodoService
        service.add("Write a test")
        assert service.all()[-1].id == 4

    def test_toggle_marks_a_task_done(self, tmp_path):
        service = _memory_service(tmp_path).TodoService
        service.toggle(1)
        assert service.all()[0].done is True

    def test_rename_changes_the_title(self, tmp_path):
        service = _memory_service(tmp_path).TodoService
        service.rename(2, "Renamed")
        assert service.all()[1].title == "Renamed"

    def test_remove_drops_the_task(self, tmp_path):
        service = _memory_service(tmp_path).TodoService
        service.remove(1)
        assert [todo.id for todo in service.all()] == [2, 3]

    def test_clear_done_keeps_what_is_left_to_do(self, tmp_path):
        service = _memory_service(tmp_path).TodoService
        service.clear_done()
        assert [todo.id for todo in service.all()] == [1, 2]

    def test_an_unknown_id_changes_nothing(self, tmp_path):
        service = _memory_service(tmp_path).TodoService
        service.toggle(99)
        assert [todo.done for todo in service.all()] == [False, False, True]
