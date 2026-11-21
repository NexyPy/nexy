import pytest

from src.board import store
from src.board.store import COLUMNS


def titles(column):
    return [card.title for card in store.board()[column]]


def test_a_new_board_starts_with_the_first_cards():
    assert sum(len(cards) for cards in store.board().values()) == len(store.FIRST_CARDS)


def test_the_board_has_every_column_in_order():
    assert list(store.board()) == list(COLUMNS)


def test_a_new_card_goes_to_the_bottom_of_to_do():
    store.add("Write the release notes")
    assert titles("todo")[-1] == "Write the release notes"


def test_a_title_is_trimmed():
    store.add("  Spaces around  ")
    assert titles("todo")[-1] == "Spaces around"


@pytest.mark.parametrize("title", ["", "   ", "x" * (store.LONGEST_TITLE + 1)])
def test_a_title_empty_or_too_long_is_refused(title):
    assert store.add(title) != ""


def test_a_refused_title_adds_nothing():
    before = titles("todo")
    store.add("")
    assert titles("todo") == before


def test_an_unknown_tag_is_dropped():
    store.add("Tagged", tag="<script>")
    assert store.board()["todo"][-1].tag == ""


def test_a_card_moves_to_the_bottom_of_a_column():
    card = store.board()["todo"][0]
    store.move(card.id, "done")
    assert store.board()["done"][-1].id == card.id


def test_a_card_moves_to_a_place_in_a_column():
    card = store.board()["todo"][0]
    store.move(card.id, "review", 0)
    assert store.board()["review"][0].id == card.id


def test_a_card_moved_down_its_own_column_lands_where_asked():
    first = store.board()["todo"][0]
    store.move(first.id, "todo", 2)
    assert [card.id for card in store.board()["todo"]].index(first.id) == 2


def test_a_move_leaves_the_positions_without_gaps():
    store.move(store.board()["todo"][0].id, "doing", 1)
    assert [card.position for card in store.board()["todo"]] == list(range(len(titles("todo"))))


def test_a_move_to_an_unknown_column_is_refused():
    card = store.board()["todo"][0]
    assert store.move(card.id, "nowhere") is False


def test_a_move_of_an_unknown_card_is_refused():
    assert store.move(999, "done") is False


def test_a_place_past_the_end_puts_the_card_last():
    card = store.board()["todo"][0]
    store.move(card.id, "doing", 99)
    assert store.board()["doing"][-1].id == card.id


def test_a_removed_card_is_gone():
    card = store.board()["done"][0]
    store.remove(card.id)
    assert card.id not in [c.id for cards in store.board().values() for c in cards]
