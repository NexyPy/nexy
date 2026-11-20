"""The actions the page calls, against a real SQLite database."""

from src.actions.todos import (
    add_todo,
    clear_completed,
    delete_todo,
    list_todos,
    rename_todo,
    toggle_todo,
)


def _titles(board) -> list[str]:
    return [item.title for item in board.items]


def _first_id() -> int:
    return list_todos().items[0].id


def test_a_new_list_is_empty():
    assert list_todos().items == []


def test_adding_a_todo_saves_it():
    add_todo("Buy bread")
    assert _titles(list_todos()) == ["Buy bread"]


def test_adding_trims_the_title():
    assert _titles(add_todo("  Buy bread  ")) == ["Buy bread"]


def test_an_empty_title_is_refused():
    assert add_todo("   ").note == "Write what there is to do."


def test_a_refused_title_saves_nothing():
    add_todo("")
    assert list_todos().items == []


def test_a_title_over_200_characters_is_refused():
    assert add_todo("x" * 201).note == "Keep it under 200 characters."


def test_the_list_keeps_the_order_of_adding():
    add_todo("First")
    assert _titles(add_todo("Second")) == ["First", "Second"]


def test_toggling_marks_a_todo_done():
    add_todo("Buy bread")
    assert toggle_todo(_first_id()).items[0].done is True


def test_toggling_twice_marks_it_not_done():
    add_todo("Buy bread")
    toggle_todo(_first_id())
    assert toggle_todo(_first_id()).items[0].done is False


def test_renaming_changes_the_title():
    add_todo("Buy bred")
    assert _titles(rename_todo(_first_id(), "Buy bread")) == ["Buy bread"]


def test_renaming_to_nothing_keeps_the_old_title():
    add_todo("Buy bread")
    assert _titles(rename_todo(_first_id(), " ")) == ["Buy bread"]


def test_deleting_removes_the_todo():
    add_todo("Buy bread")
    assert delete_todo(_first_id()).items == []


def test_clearing_removes_only_the_done_ones():
    add_todo("Done")
    add_todo("Not done")
    toggle_todo(_first_id())
    assert _titles(clear_completed()) == ["Not done"]


def test_an_unknown_id_changes_nothing():
    add_todo("Buy bread")
    assert _titles(toggle_todo(999)) == ["Buy bread"]
