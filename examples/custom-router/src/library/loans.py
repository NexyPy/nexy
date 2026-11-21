import hmac
import os

from fastapi import APIRouter, Depends, Header, HTTPException

from src.library.catalogue import Book, find


def require_staff(x_staff_token: str = Header("")) -> None:
    """The dependency the service always had: Nexy runs it as FastAPI does."""
    token = os.environ.get("LIBRARY_STAFF_TOKEN", "demo-staff-token")
    if not hmac.compare_digest(token, x_staff_token):
        raise HTTPException(401, "Send a valid X-Staff-Token header.")


router = APIRouter(tags=["loans"], dependencies=[Depends(require_staff)])


@router.post("/books/{book_id}/loan")
async def lend(book_id: int) -> Book:
    book = find(book_id)
    if book is None:
        raise HTTPException(404, "No such book.")
    if book.on_loan:
        raise HTTPException(409, "This book is already on loan.")
    book.on_loan = True
    return book
