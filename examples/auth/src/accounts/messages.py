"""What the pages say. The address carries a key, `?error=wrong`, and the page prints the sentence
of that key: a link can never put words of its own on the page."""

from src.accounts.store import LONGEST_PASSWORD, SHORTEST_PASSWORD
from src.accounts.throttle import LIMIT, WINDOW

ERRORS = {
    "email": "That does not look like an email address.",
    "password": f"A password has {SHORTEST_PASSWORD} to {LONGEST_PASSWORD} characters.",
    "taken": "This email already has an account. Sign in instead.",
    # Never which of the two is wrong: that would tell anyone which emails have an account.
    "wrong": "Wrong email or password.",
    "slow": f"{LIMIT} wrong passwords in a row for this email. Wait {WINDOW // 60} minutes, then try again.",
    "current": "The current password is not right.",
    "signin": "Sign in to see your account.",
}

DONE = {
    "password": "Your password is changed.",
    "out": "You are signed out.",
}
