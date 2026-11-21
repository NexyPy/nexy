"""The actions of the board. A form posts to them without JavaScript, and the Solid island calls
them as functions from `@nexy/actions`. Each one answers with the whole board, as the server holds
it: the page puts its cards in that order, never in the order it guessed."""

from nexy.decorators import Action
from pydantic import BaseModel

from src.board import store


class CardView(BaseModel):
    id: int
    title: str
    tag: str


class ColumnView(BaseModel):
    key: str
    title: str
    cards: list[CardView]


class BoardView(BaseModel):
    columns: list[ColumnView]
    note: str = ""  # why the last change was refused; empty when it was made


def view(note: str = "") -> BoardView:
    columns = [
        ColumnView(
            key=key,
            title=store.COLUMNS[key],
            cards=[CardView(id=card.id, title=card.title, tag=card.tag) for card in cards],
        )
        for key, cards in store.board().items()
    ]
    return BoardView(columns=columns, note=note)


@Action
def add_card(title: str, tag: str = "") -> BoardView:
    """A new card at the bottom of To do."""
    return view(store.add(title, tag))


@Action
def move_card(card_id: int, column: str, index: int | None = None) -> BoardView:
    """Move a card to a column, at `index` from the top, or at the bottom without one."""
    moved = store.move(card_id, column, index)
    return view("" if moved else "That card or column no longer exists. The board is reloaded.")


@Action
def delete_card(card_id: int) -> BoardView:
    store.remove(card_id)
    return view()
