from src.configs.db import run
from src.services.note_service import NoteService


def write(title: str, body: str = "", pinned: bool = False) -> int:
    note = run(NoteService.create())
    run(NoteService.save(note.id, title, body))
    if pinned:
        run(NoteService.pin(note.id, True))
    return note.id


def titles(search: str = "") -> list[str]:
    return [note.title for note in run(NoteService.all(search))]


def test_a_new_note_is_empty():
    assert run(NoteService.create()).body == ""


def test_the_latest_changed_note_comes_first():
    write("older")
    write("newer")
    assert titles() == ["newer", "older"]


def test_a_pinned_note_comes_before_the_others():
    write("pinned", pinned=True)
    write("newer")
    assert titles() == ["pinned", "newer"]


def test_editing_a_note_brings_it_to_the_top():
    first = write("first")
    write("second")
    run(NoteService.save(first, "first, edited", ""))
    assert titles()[0] == "first, edited"


def test_a_search_finds_a_word_of_the_title():
    write("Groceries")
    write("Ideas")
    assert titles("grocer") == ["Groceries"]


def test_a_search_finds_a_word_of_the_body():
    write("Monday", "call the plumber")
    write("Tuesday", "nothing")
    assert titles("plumber") == ["Monday"]


def test_a_search_of_spaces_finds_every_note():
    write("one")
    write("two")
    assert len(titles("   ")) == 2


def test_saving_a_missing_note_stores_nothing():
    assert run(NoteService.save(999, "title", "")) is None


def test_pinning_a_missing_note_stores_nothing():
    assert run(NoteService.pin(999, True)) is None


def test_a_deleted_note_is_gone():
    note = write("gone")
    run(NoteService.remove(note))
    assert run(NoteService.find(note)) is None


def test_deleting_a_missing_note_says_so():
    assert run(NoteService.remove(999)) is False
