from fastapi import APIRouter, HTTPException

from src.library.catalogue import BOOKS, Book, find

router = APIRouter(tags=["books"])


@router.get("/books")
async def list_books() -> list[Book]:
    return BOOKS


@router.get("/books/{book_id}")
async def get_book(book_id: int) -> Book:
    book = find(book_id)
    if book is None:
        raise HTTPException(404, "No such book.")
    return book
