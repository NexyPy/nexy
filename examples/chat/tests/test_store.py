import pytest

from src.chat import store


def test_every_room_starts_with_messages():
    assert all(store.messages(room) for room in store.ROOMS)


def test_messages_come_oldest_first():
    ids = [message.id for message in store.messages("general")]
    assert ids == sorted(ids)


def test_a_sent_message_comes_last_in_its_room():
    store.send("general", "Ines", "Lunch at noon?")
    assert store.messages("general")[-1].text == "Lunch at noon?"


def test_a_sent_message_stays_in_its_room():
    store.send("design", "Ines", "New icons are up")
    assert "New icons are up" not in [m.text for m in store.messages("general")]


def test_the_name_and_the_text_are_trimmed():
    store.send("general", "  Ines ", "  hello  ")
    assert (store.messages("general")[-1].author, store.messages("general")[-1].text) == (
        "Ines",
        "hello",
    )


@pytest.mark.parametrize(
    ("name", "text"),
    [("", "hi"), ("Ines", " "), ("x" * (store.LONGEST_NAME + 1), "hi"), ("Ines", "x" * 501)],
)
def test_a_message_without_a_name_or_text_or_too_long_is_refused(name, text):
    assert store.send("general", name, text) != ""


def test_a_message_to_a_room_that_does_not_exist_is_refused():
    assert store.send("nowhere", "Ines", "hi") != ""


def test_a_refused_message_is_not_stored():
    before = len(store.messages("general"))
    store.send("general", "", "hi")
    assert len(store.messages("general")) == before


def test_the_messages_after_one_are_only_the_newer_ones():
    last = store.messages("general")[-1].id
    store.send("general", "Ines", "newer")
    assert [m.text for m in store.messages("general", after=last)] == ["newer"]


def test_a_room_shows_its_latest_messages_only():
    for n in range(store.SHOWN + 5):
        store.send("general", "Ines", f"message {n}")
    assert len(store.messages("general")) == store.SHOWN


def test_a_message_keeps_the_time_it_was_sent_in_utc():
    store.send("general", "Ines", "when?")
    assert store.messages("general")[-1].sent_at.endswith("+00:00")


@pytest.mark.parametrize("text", ["", "-1", "1.5", "9" * 19])
def test_an_id_sqlite_cannot_hold_is_none(text):
    assert store.message_id(text) is None


def test_an_id_is_read_from_its_digits():
    assert store.message_id("42") == 42
