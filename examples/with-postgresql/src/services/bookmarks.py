"""Every query of the sample. Pages and actions call these functions, never the engine."""

from urllib.parse import urlsplit

from sqlmodel import Session, col, select

from src.configs.db import create_tables, engine
from src.models import Bookmark

LONGEST_TITLE = 200
LONGEST_URL = 2000

create_tables()


def problem(title: str, url: str) -> str:
    """The key of what is wrong with a new bookmark, or "" when it can be saved."""
    if not title.strip() or len(title) > LONGEST_TITLE:
        return "title"
    parts = urlsplit(url.strip())
    # http and https only: a `javascript:` address in a link runs code when it is clicked.
    if parts.scheme not in ("http", "https") or not parts.netloc or len(url) > LONGEST_URL:
        return "url"
    return ""


def add(title: str, url: str) -> Bookmark:
    with Session(engine) as session:
        bookmark = Bookmark(title=title.strip(), url=url.strip())
        session.add(bookmark)
        session.commit()
        session.refresh(bookmark)
        return bookmark


def search(words: str = "") -> list[Bookmark]:
    """The bookmarks whose title holds `words`, any case, newest first. ILIKE on PostgreSQL;
    SQLAlchemy writes the same search for SQLite with lower()."""
    query = select(Bookmark).order_by(col(Bookmark.created_at).desc(), col(Bookmark.id).desc())
    if words.strip():
        pattern = (
            "%" + words.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        )
        query = query.where(col(Bookmark.title).ilike(pattern, escape="\\"))
    with Session(engine) as session:
        return list(session.exec(query.limit(100)))
