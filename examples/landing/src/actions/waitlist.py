"""The action the waitlist form calls when the browser runs JavaScript."""

from nexy.decorators import Action
from pydantic import BaseModel

from src.services.waitlist import MESSAGES, join


class Answer(BaseModel):
    joined: bool
    message: str


@Action
def join_waitlist(email: str) -> Answer:
    outcome = join(email)
    return Answer(joined=outcome == "joined", message=MESSAGES[outcome])
