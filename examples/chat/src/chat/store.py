"""The messages of every room, kept in SQLite. Every read and write of the chat goes through here."""

import os
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

# The rooms: the word in the address, then what the room is for.
ROOMS = {
    "general": "Anything for the whole team",
    "design": "Screens, icons and reviews",
    "releases": "What ships, and when",
}
LONGEST_NAME = 40
LONGEST_TEXT = 500
SHOWN = 50  # a room shows its latest messages; older ones stay in the database

DATABASE = Path(os.environ.get("CHAT_DB", "chat.db"))

FIRST_MESSAGES = (
    ("general", "Ama", "Morning all. Stand-up moves to 10:30 today."),
    ("general", "Lucas", "Works for me. I will bring the numbers from last week."),
    ("general", "Mei", "Coffee machine on the third floor is fixed, by the way."),
    ("design", "Mei", "New empty states for the inbox are in the file."),
    ("design", "Ama", "Love the illustration. Can the text be one line shorter?"),
    ("releases", "Lucas", "3.2 is frozen. Release notes by Thursday."),
    ("releases", "Ama", "Store screenshots are ready for review."),
)


@dataclass(frozen=True)
class Message:
    id: int
    room: str
    author: str
    text: str
    sent_at: str  # ISO 8601, in UTC


def _connect() -> sqlite3.Connection:
    """The database, made and filled with the first messages the first time it is opened."""
    new = not DATABASE.exists()
    connection = sqlite3.connect(DATABASE)
    connection.execute(
        "create table if not exists message (id integer primary key, room text not null,"
        " author text not null, text text not null, sent_at text not null)"
    )
    if new:
        start = datetime.now(UTC) - timedelta(hours=2)
        for minutes, (room, author, text) in enumerate(FIRST_MESSAGES):
            _insert(connection, room, author, text, start + timedelta(minutes=7 * minutes))
        connection.commit()
    return connection


def _insert(
    connection: sqlite3.Connection, room: str, author: str, text: str, at: datetime
) -> None:
    connection.execute(
        "insert into message (room, author, text, sent_at) values (?, ?, ?, ?)",
        (room, author, text, at.isoformat(timespec="seconds")),
    )


def message_id(text: str) -> int | None:
    """The id written in an address or a form, or None when it is not one SQLite can hold."""
    return int(text) if text.isdigit() and len(text) <= 18 else None


def messages(room: str, after: int = 0) -> list[Message]:
    """The latest messages of a room, oldest first; with `after`, only the ones newer than it."""
    with closing(_connect()) as connection:
        rows = connection.execute(
            "select id, room, author, text, sent_at from message"
            " where room = ? and id > ? order by id desc limit ?",
            (room, after, SHOWN),
        ).fetchall()
    return [Message(*row) for row in reversed(rows)]


# What the room says after a refused message. The address carries the key only, never the words,
# so nobody can put a sentence of their own on the page with a link.
NOTES = {
    "room": "This room does not exist.",
    "name": f"Write your name, in {LONGEST_NAME} characters or fewer.",
    "text": f"Write a message, in {LONGEST_TEXT} characters or fewer.",
}


def problem(room: str, author: str, text: str) -> str:
    """The key in NOTES of what is wrong with a message, or "" when it can be sent."""
    if room not in ROOMS:
        return "room"
    if not author or len(author) > LONGEST_NAME:
        return "name"
    if not text or len(text) > LONGEST_TEXT:
        return "text"
    return ""


def send(room: str, author: str, text: str) -> str:
    """Store a message. Returns the key of what was wrong, or "" when it was sent."""
    author, text = author.strip(), text.strip()
    if found := problem(room, author, text):
        return found
    with closing(_connect()) as connection:
        _insert(connection, room, author, text, datetime.now(UTC))
        connection.commit()
    return ""
