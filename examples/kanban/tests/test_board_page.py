import re

from src.board import store


def action(client, name):
    """The address of an action, as the page's forms post to it."""
    page = client.get("/").text
    forms = re.findall(r'<form method="post" action="([^"]+)"[^>]*>', page)
    paths = {"add_card": forms[0], "move_card": forms[1], "delete_card": forms[2]}
    return paths[name]


def ids(column):
    return [card.id for card in store.board()[column]]


def test_the_board_shows_every_column(client):
    page = client.get("/").text
    assert all(re.search(rf">\s*{name}\s*<span", page) for name in store.COLUMNS.values())


def test_the_board_shows_the_cards(client):
    assert "Share a note as a link" in client.get("/").text


def test_a_column_shows_how_many_cards_it_has(client):
    assert 'data-count="doing">2<' in client.get("/").text


def test_a_card_title_is_escaped(client):
    store.add("<b>bold</b>")
    assert "<b>bold</b>" not in client.get("/").text


def test_the_add_form_adds_a_card(client):
    client.post(action(client, "add_card"), data={"title": "From the form", "tag": "docs"})
    assert store.board()["todo"][-1].title == "From the form"


def test_a_form_goes_back_to_the_board(client):
    answer = client.post(
        action(client, "add_card"), data={"title": "Back"}, headers={"referer": "/"}
    )
    assert answer.status_code == 303


def test_the_move_form_moves_a_card_to_the_bottom(client):
    card = ids("todo")[0]
    client.post(action(client, "move_card"), data={"card_id": card, "column": "review"})
    assert ids("review")[-1] == card


def test_the_delete_form_deletes_a_card(client):
    card = ids("done")[0]
    client.post(action(client, "delete_card"), data={"card_id": card})
    assert card not in ids("done")


def test_a_move_called_from_the_island_answers_the_board(client):
    card = ids("todo")[0]
    answer = client.post(
        action(client, "move_card"), json={"card_id": card, "column": "doing", "index": 0}
    )
    assert answer.json()["columns"][1]["cards"][0]["id"] == card


def test_a_move_to_a_column_that_does_not_exist_says_so(client):
    answer = client.post(
        action(client, "move_card"), json={"card_id": ids("todo")[0], "column": "x"}
    )
    assert answer.json()["note"] != ""


def test_an_unknown_page_answers_404(client):
    assert client.get("/nothing-here").status_code == 404
