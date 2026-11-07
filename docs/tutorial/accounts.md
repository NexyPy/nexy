# Build a notes app with Nexy, part 10: create an account and sign in

Part 10 lets a visitor create an account with an email and a password, sign in and sign out, and
remembers who is signed in with a session cookie.

**Before you start:** the app of [part 9](paginate-the-notes.md).

## Turn sessions on

A session is a signed cookie: the server puts the id of the signed-in user in it, and reads it back
on every request. Starlette signs it with `itsdangerous`:

```bash
uv add itsdangerous
```

The secret it signs with is kept in `.env`, next to the database address:

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
SESSION_SECRET=change-me-to-a-long-random-string
```

Make a real secret with `python -c "import secrets; print(secrets.token_urlsafe(32))"`. Anyone who
knows it can sign a cookie as any user.

`useSession` turns sessions on, with the secret read from the environment:

<!-- router:fbr,custom -->
```python filename="nexyconfig.py"
import os

from dotenv import load_dotenv

from nexy.core.models import NexyConfigModel
from nexy.frontend import react

load_dotenv()


class NexyConfig(NexyConfigModel):
    useFF = react()
    useTitle = "Nexy Web (FBR + React)"
    useAliases = {"@": "src"}
    useVite = True
    useDevTools = True
    useSession = {"secret_key": os.environ["SESSION_SECRET"]}
```
<!-- /router -->

<!-- router:modular -->
```python filename="nexyconfig.py"
import os

from dotenv import load_dotenv

from nexy.core.models import NexyConfigModel
from nexy.frontend import react
from src.apps.app_module import AppModule

load_dotenv()


class NexyConfig(NexyConfigModel):
    useFF = react()
    useTitle = "Nexy Web (Modular + React)"
    useRouter = AppModule
    useAliases = {"@": "src"}
    useVite = True
    useDevTools = True
    useSession = {"secret_key": os.environ["SESSION_SECRET"]}
```
<!-- /router -->

`os.environ[...]` and not `os.getenv(...)`: without a secret, the app stops at startup instead of
running with none.

## Describe a user

<!-- router:fbr,custom -->
```python filename="src/models/user_model.py"
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
```
<!-- /router -->

<!-- router:modular -->
A user is a feature of its own, in `src/apps/users/`:

```python filename="src/apps/users/user_model.py"
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
```
<!-- /router -->

The table keeps a hash of the password, never the password: a stolen database does not give the
passwords away. `unique=True` makes the database refuse a second account with the same email.

```bash
nx migrate -m "create users"
nx migrate --upgrade
```

The migration finds the new model on its own: it reads every `*_model.py` of `src/`.

## Hash and check a password

`hashlib.scrypt`, from the standard library, is a hash made slow on purpose, so guessing passwords
one by one costs an attacker years. Each password gets its own random salt:

<!-- router:fbr,custom -->
```python filename="src/accounts.py"
import hashlib
import hmac
import secrets

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.user_model import User


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"{salt.hex()}:{digest.hex()}"


def password_matches(password: str, stored: str) -> bool:
    salt, digest = stored.split(":")
    found = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=2**14, r=8, p=1)
    return hmac.compare_digest(found.hex(), digest)


def create_user(email: str, password: str) -> User | None:
    """The new user, or None when the email already has an account."""
    user = User(email=email, password_hash=hash_password(password))
    with Session(engine) as session:
        session.add(user)
        try:
            session.commit()
        except IntegrityError:
            return None
        session.refresh(user)
    return user


def authenticate(email: str, password: str) -> User | None:
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
    if user is None or not password_matches(password, user.password_hash):
        return None
    return user
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/accounts.py"
import hashlib
import hmac
import secrets

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from src.apps.users.user_model import User
from src.configs.db import engine


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"{salt.hex()}:{digest.hex()}"


def password_matches(password: str, stored: str) -> bool:
    salt, digest = stored.split(":")
    found = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=2**14, r=8, p=1)
    return hmac.compare_digest(found.hex(), digest)


def create_user(email: str, password: str) -> User | None:
    """The new user, or None when the email already has an account."""
    user = User(email=email, password_hash=hash_password(password))
    with Session(engine) as session:
        session.add(user)
        try:
            session.commit()
        except IntegrityError:
            return None
        session.refresh(user)
    return user


def authenticate(email: str, password: str) -> User | None:
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
    if user is None or not password_matches(password, user.password_hash):
        return None
    return user
```
<!-- /router -->

`hmac.compare_digest` compares in a time that does not depend on where the two hashes differ, so the
answer time tells an attacker nothing.

## Sign up, sign in, sign out

Three Actions. Each one that succeeds writes the session, or empties it:

```python filename="src/actions/accounts.py"
from urllib.parse import urlencode

from nexy import useSession
from nexy.decorators import Action
from nexy.http import RedirectResponse
from src.accounts import authenticate, create_user

MIN_PASSWORD = 8


def go(path: str, error: str = "") -> RedirectResponse:
    query = f"?{urlencode({'error': error})}" if error else ""
    return RedirectResponse(f"{path}{query}", status_code=303)


@Action
async def sign_up(email: str, password: str) -> RedirectResponse:
    email = email.strip().lower()
    if len(password) < MIN_PASSWORD:
        return go("/signup", f"A password has at least {MIN_PASSWORD} characters.")
    user = create_user(email, password)
    if user is None:
        return go("/signup", "This email already has an account.")
    useSession()["user_id"] = user.id
    return go("/notes")


@Action
async def sign_in(email: str, password: str) -> RedirectResponse:
    user = authenticate(email.strip().lower(), password)
    if user is None:
        return go("/signin", "Wrong email or password.")
    useSession()["user_id"] = user.id
    return go("/notes")


@Action
async def sign_out() -> RedirectResponse:
    useSession().clear()
    return go("/")
```

*Wrong email or password*, never which one: a message that said "no account with this email" would
tell anyone which emails have an account.

## The two forms

<!-- router:fbr,custom -->
```nexy filename="src/routes/signup.nexy"
---
from nexy import useSearchParams

error = useSearchParams().get("error", "")
---
<section class="app-page">
  <h1>Create an account</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['sign_up'] }}">
    <label>Email <input type="email" name="email" autocomplete="email" required></label>
    <label>Password <input type="password" name="password" autocomplete="new-password" minlength="8" required></label>
    <button type="submit">Create the account</button>
  </form>

  <a href="/signin">I already have an account</a>
</section>
```

```nexy filename="src/routes/signin.nexy"
---
from nexy import useSearchParams

error = useSearchParams().get("error", "")
---
<section class="app-page">
  <h1>Sign in</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['sign_in'] }}">
    <label>Email <input type="email" name="email" autocomplete="email" required></label>
    <label>Password <input type="password" name="password" autocomplete="current-password" required></label>
    <button type="submit">Sign in</button>
  </form>

  <a href="/signup">Create an account</a>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/users/signup_view.nexy"
---
from nexy import useSearchParams

error = useSearchParams().get("error", "")
---
<section class="app-page">
  <h1>Create an account</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['sign_up'] }}">
    <label>Email <input type="email" name="email" autocomplete="email" required></label>
    <label>Password <input type="password" name="password" autocomplete="new-password" minlength="8" required></label>
    <button type="submit">Create the account</button>
  </form>

  <a href="/signin">I already have an account</a>
</section>
```

```nexy filename="src/apps/users/signin_view.nexy"
---
from nexy import useSearchParams

error = useSearchParams().get("error", "")
---
<section class="app-page">
  <h1>Sign in</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['sign_in'] }}">
    <label>Email <input type="email" name="email" autocomplete="email" required></label>
    <label>Password <input type="password" name="password" autocomplete="current-password" required></label>
    <button type="submit">Sign in</button>
  </form>

  <a href="/signup">Create an account</a>
</section>
```

```python filename="src/apps/users/users_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


def page(view: str):
    return useViews(LAYOUT, context={"children": useViews(view)})


@Controller("/signup")
class SignUpController:
    async def get(self):
        return page("src/apps/users/signup_view.nexy")


@Controller("/signin")
class SignInController:
    async def get(self):
        return page("src/apps/users/signin_view.nexy")
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AboutController, AppController
from .notes.notes_controller import NoteController, NotesApiController, NotesController
from .users.users_controller import SignInController, SignUpController


@Module()
class AppModule:
    controllers = [
        AppController,
        AboutController,
        NotesController,
        NoteController,
        NotesApiController,
        SignUpController,
        SignInController,
    ]
```
<!-- /router -->

`autocomplete="new-password"` lets a password manager offer a strong password, and
`current-password` lets it fill the one it saved.

## Show who is signed in

The notes page greets the user and shows the sign-out button; a visitor sees the links to the two
forms instead:

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams, useSession
from src.notes import notes_page

params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(number)
notes = found[0]
more = found[1]
signed_in = "user_id" in useSession()
---
<section class="app-page">
  <h1>Notes</h1>

  {% if signed_in %}
  <form method="post" action="{{ __actions_path['sign_out'] }}">
    <button type="submit">Sign out</button>
  </form>
  {% else %}
  <p><a href="/signin">Sign in</a> or <a href="/signup">create an account</a>.</p>
  {% endif %}

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams, useSession
from src.notes import notes_page

params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(number)
notes = found[0]
more = found[1]
signed_in = "user_id" in useSession()
---
<section class="app-page">
  <h1>Notes</h1>

  {% if signed_in %}
  <form method="post" action="{{ __actions_path['sign_out'] }}">
    <button type="submit">Sign out</button>
  </form>
  {% else %}
  <p><a href="/signin">Sign in</a> or <a href="/signup">create an account</a>.</p>
  {% endif %}

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>
</section>
```
<!-- /router -->

Open <http://localhost:3000/signup>, create an account: you land on the notes with a **Sign out**
button. Sign out, then sign in again at <http://localhost:3000/signin>.

## What you learned

- `useSession` in `nexyconfig.py` turns on a signed session cookie; its secret lives in `.env`.
- The database keeps a salted, slow hash of the password, checked with `hmac.compare_digest`.
- An Action writes the session with `useSession()`; a page reads it the same way.

## Next steps

- [Part 11: give each user their own notes](own-notes.md)
- [Middleware and security](../guides/middleware-and-security.md): sessions, CORS and trusted hosts
