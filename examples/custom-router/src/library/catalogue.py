"""The books of the library. The FastAPI routes and the Nexy pages read the same list."""

from pydantic import BaseModel


class Book(BaseModel):
    id: int
    title: str
    author: str
    on_loan: bool = False


BOOKS = [
    Book(id=1, title="The Left Hand of Darkness", author="Ursula K. Le Guin"),
    Book(id=2, title="Kindred", author="Octavia E. Butler", on_loan=True),
    Book(id=3, title="Piranesi", author="Susanna Clarke"),
]


def find(book_id: int) -> Book | None:
    return next((book for book in BOOKS if book.id == book_id), None)
