"""The cards of the board, kept in SQLite. Every read and write of the board goes through here."""

import os
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

# The columns, left to right: the key in the database and the address, then the word on the page.
COLUMNS = {"todo": "To do", "doing": "In progress", "review": "Review", "done": "Done"}
TAGS = ("bug", "feature", "docs")
LONGEST_TITLE = 120

DATABASE = Path(os.environ.get("KANBAN_DB", "kanban.db"))

FIRST_CARDS = (
    ("Offline mode for the reading list", "feature", "todo"),
    ("Crash when a note has no title", "bug", "todo"),
    ("Explain sync conflicts in the help", "docs", "todo"),
    ("Share a note as a link", "feature", "doing"),
    ("Dark theme for the editor", "feature", "doing"),
    ("Search ignores accents", "bug", "review"),
    ("Export to Markdown", "feature", "done"),
    ("Write the 3.1 release notes", "docs", "done"),
)


@dataclass(frozen=True)
class Card:
    id: int
    title: str
    tag: str
    column: str
    position: int


def _connect() -> sqlite3.Connection:
    """The database, made and filled with the first cards the first time it is opened."""
    new = not DATABASE.exists()
    connection = sqlite3.connect(DATABASE)
    connection.execute(
        "create table if not exists card (id integer primary key, title text not null,"
        " tag text not null, column_key text not null, position integer not null)"
    )
    if new:
        for title, tag, column in FIRST_CARDS:
            _append(connection, title, tag, column)
        connection.commit()
    return connection


def _append(connection: sqlite3.Connection, title: str, tag: str, column: str) -> None:
    count = connection.execute("select count(*) from card where column_key = ?", (column,))
    connection.execute(
        "insert into card (title, tag, column_key, position) values (?, ?, ?, ?)",
        (title, tag, column, count.fetchone()[0]),
    )


def _column(connection: sqlite3.Connection, column: str) -> list[int]:
    rows = connection.execute(
        "select id from card where column_key = ? order by position", (column,)
    )
    return [row[0] for row in rows]


def _others(connection: sqlite3.Connection, column: str, card_id: int) -> list[int]:
    return [other for other in _column(connection, column) if other != card_id]


def _renumber(connection: sqlite3.Connection, column: str, ids: list[int]) -> None:
    for position, card_id in enumerate(ids):
        connection.execute(
            "update card set column_key = ?, position = ? where id = ?",
            (column, position, card_id),
        )


def board() -> dict[str, list[Card]]:
    """Every column, left to right, with its cards top to bottom."""
    with closing(_connect()) as connection:
        rows = connection.execute(
            "select id, title, tag, column_key, position from card order by position"
        ).fetchall()
    columns: dict[str, list[Card]] = {key: [] for key in COLUMNS}
    for row in rows:
        columns[row[3]].append(Card(*row))
    return columns


def problem(title: str) -> str:
    """What is wrong with a card title, or "" when it can be added."""
    if not title:
        return "Write what the card is about."
    if len(title) > LONGEST_TITLE:
        return f"Keep the title under {LONGEST_TITLE} characters."
    return ""


def add(title: str, tag: str = "") -> str:
    """Put a card at the bottom of To do. Returns what was wrong, or "" when it was added."""
    title = title.strip()
    if found := problem(title):
        return found
    with closing(_connect()) as connection:
        _append(connection, title, tag if tag in TAGS else "", "todo")
        connection.commit()
    return ""


def move(card_id: int, column: str, index: int | None = None) -> bool:
    """Move a card to `column`, at `index` from the top (the bottom when None or too far)."""
    with closing(_connect()) as connection:
        found = connection.execute("select column_key from card where id = ?", (card_id,))
        source = found.fetchone()
        if column not in COLUMNS or source is None:
            return False
        _renumber(connection, source[0], _others(connection, source[0], card_id))
        target = _others(connection, column, card_id)
        target.insert(len(target) if index is None else max(index, 0), card_id)
        _renumber(connection, column, target)
        connection.commit()
    return True


def remove(card_id: int) -> None:
    with closing(_connect()) as connection:
        found = connection.execute("select column_key from card where id = ?", (card_id,))
        source = found.fetchone()
        connection.execute("delete from card where id = ?", (card_id,))
        if source:
            _renumber(connection, source[0], _column(connection, source[0]))
        connection.commit()
