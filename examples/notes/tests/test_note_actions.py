import pytest


@pytest.fixture
def note_id(call):
    return call("create_note").json()["id"]


def test_no_note_yet_answers_an_empty_list(call):
    assert call("notes").json() == []


def test_a_new_note_answers_its_id(call):
    assert isinstance(call("create_note").json()["id"], int)


def test_a_saved_note_is_read_back(call, note_id):
    call("save_note", note_id=note_id, title="Groceries", body="- milk")
    assert call("note", note_id=note_id).json()["body"] == "- milk"


def test_a_title_is_saved_without_its_spaces(call, note_id):
    saved = call("save_note", note_id=note_id, title="  Groceries  ", body="")
    assert saved.json()["note"]["title"] == "Groceries"


def test_a_list_shows_the_excerpt_of_each_note(call, note_id):
    call("save_note", note_id=note_id, title="Groceries", body="# Monday\n- milk")
    assert call("notes").json()[0]["excerpt"] == "Monday"


def test_a_search_answers_the_notes_that_hold_it(call, note_id):
    call("save_note", note_id=note_id, title="Groceries", body="")
    call("create_note")
    assert len(call("notes", search="groc").json()) == 1


def test_a_title_too_long_is_refused(call, note_id):
    saved = call("save_note", note_id=note_id, title="x" * 121, body="")
    assert saved.json() == {"note": None, "problem": "Keep the title under 120 characters."}


def test_a_body_too_long_is_refused(call, note_id):
    saved = call("save_note", note_id=note_id, title="", body="x" * 20_001)
    assert saved.json()["problem"] == "Keep a note under 20,000 characters: split it in two."


def test_a_note_can_be_pinned(call, note_id):
    assert call("pin_note", note_id=note_id, pinned=True).json()["pinned"] is True


def test_a_deleted_note_answers_404(call, note_id):
    call("delete_note", note_id=note_id)
    assert call("note", note_id=note_id).status_code == 404


def test_saving_a_deleted_note_answers_404(call, note_id):
    call("delete_note", note_id=note_id)
    assert call("save_note", note_id=note_id, title="", body="").status_code == 404


def test_deleting_a_note_answers_true(call, note_id):
    assert call("delete_note", note_id=note_id).json() is True


def test_the_preview_answers_html(call):
    assert call("preview", body="**bold**").json() == "<p><strong>bold</strong></p>\n"


def test_a_note_says_when_it_changed_in_utc(call, note_id):
    assert call("note", note_id=note_id).json()["updated_at"].endswith("Z")
