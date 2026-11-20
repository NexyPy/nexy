"""Who is signed in: a password checked once, then the id of the user in the session cookie."""

from sqlmodel import Session, select

from nexy import redirect, useSession
from src.configs import db
from src.models.user import User
from src.services.passwords import password_matches


def authenticate(email: str, password: str) -> User | None:
    """The user with this email and password, or None for either one wrong."""
    with Session(db.engine) as session:
        user = session.exec(select(User).where(User.email == email.strip().lower())).first()
    if user is None or not password_matches(password, user.password_hash):
        return None
    return user


def signed_in() -> User:
    """The user of this request; a visitor who is not signed in goes to the sign-in page."""
    user_id = useSession().get("user_id")
    with Session(db.engine) as session:
        user = session.get(User, user_id) if user_id else None
    if user is None:
        redirect("/signin", 303)  # 303: a form sent while signed out lands on the page
    return user
