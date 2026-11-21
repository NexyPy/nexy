"""The library service: a FastAPI app written before Nexy, kept as it is.

Its routes are plugged into Nexy with `useRouter = service.router` in `nexyconfig.py`. Nothing in
this folder imports Nexy.
"""

from fastapi import FastAPI

from src.library.books import router as books
from src.library.loans import router as loans

service = FastAPI(title="Library")
service.include_router(books, prefix="/api/v1")
service.include_router(loans, prefix="/api/v1")
