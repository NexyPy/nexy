# Nexy এর সাথে একটি নোট অ্যাপ তৈরি করুন, পার্ট 10: একটি অ্যাকাউন্ট তৈরি করুন এবং সাইন ইন করুন৷

পার্ট 10 একজন দর্শককে একটি ইমেল এবং একটি পাসওয়ার্ড দিয়ে একটি অ্যাকাউন্ট তৈরি করতে, সাইন ইন এবং সাইন আউট করতে দেয় এবং সেশন কুকি দিয়ে কে সাইন ইন করেছে তা মনে রাখতে দেয়৷

**আপনি শুরু করার আগে:** [পার্ট 9](paginate-the-notes.md) এর অ্যাপ।

## সেশন চালু করুন

একটি সেশন হল একটি স্বাক্ষরিত কুকি: সার্ভার এতে সাইন-ইন করা ব্যবহারকারীর আইডি রাখে এবং প্রতিটি অনুরোধে এটি আবার পড়ে। Starlette এটিকে `itsdangerous` দিয়ে স্বাক্ষর করে:

```bash
uv add itsdangerous
```

এটি যে গোপনীয়তার সাথে স্বাক্ষর করে তা ডাটাবেস ঠিকানার পাশে `.env` এ রাখা হয়েছে:

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
SESSION_SECRET=change-me-to-a-long-random-string
```

সঙ্গে একটি বাস্তব গোপন করুন `python -c "import secrets; print(secrets.token_urlsafe(32))"`. যে কেউ এটি জানেন যে কোনও ব্যবহারকারী হিসাবে একটি কুকিতে স্বাক্ষর করতে পারেন৷

`useSession` পরিবেশ থেকে গোপন পাঠ সহ সেশন চালু করে:

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

`os.environ[...]` এবং নয় `os.getenv(...)`: গোপনীয়তা ছাড়া, অ্যাপটি কোনোটির সাথে না চলার পরিবর্তে স্টার্টআপে থামে।

## একজন ব্যবহারকারীর বর্ণনা দিন

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
একজন ব্যবহারকারী তার নিজস্ব একটি বৈশিষ্ট্য, `src/apps/users/`:

```python filename="src/apps/users/user_model.py"
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
```
<!-- /router -->

টেবিলটি পাসওয়ার্ডের একটি হ্যাশ রাখে, পাসওয়ার্ড কখনই না: একটি চুরি করা ডাটাবেস পাসওয়ার্ড দেয় না। `unique=True` ডাটাবেস একই ইমেল সহ একটি দ্বিতীয় অ্যাকাউন্ট প্রত্যাখ্যান করে।

```bash
nx migrate -m "create users"
nx migrate --upgrade
```

মাইগ্রেশন নিজেই নতুন মডেল খুঁজে পায়: এটি প্রতিটি `*_model.py` `src/` পড়ে।

## হ্যাশ করুন এবং একটি পাসওয়ার্ড চেক করুন

`hashlib.scrypt`, স্ট্যান্ডার্ড লাইব্রেরি থেকে, উদ্দেশ্যমূলকভাবে ধীরগতির তৈরি একটি হ্যাশ, তাই একের পর এক পাসওয়ার্ড অনুমান করা আক্রমণকারীর বছর খরচ করে। প্রতিটি পাসওয়ার্ড তার নিজস্ব এলোমেলো লবণ পায়:

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

`hmac.compare_digest` এমন একটি সময়ের মধ্যে তুলনা করে যা দুটি হ্যাশের পার্থক্যের উপর নির্ভর করে না, তাই উত্তরের সময় আক্রমণকারীকে কিছুই বলে না।

## সাইন আপ করুন, সাইন ইন করুন, সাইন আউট করুন

তিনটি অ্যাকশন। সফল হওয়া প্রত্যেকেই সেশন লেখেন বা খালি করে:

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

*ভুল ইমেল বা পাসওয়ার্ড*, কোনটি নয়: একটি বার্তা যা বলে যে "এই ইমেলের সাথে কোন অ্যাকাউন্ট নেই" যে ইমেলগুলির একটি অ্যাকাউন্ট আছে তা কাউকে বলে দেবে৷

## দুটি রূপ

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

`autocomplete="new-password"` একটি পাসওয়ার্ড ম্যানেজারকে একটি শক্তিশালী পাসওয়ার্ড অফার করতে দেয় এবং `current-password` এটি সংরক্ষিত পাসওয়ার্ডটি পূরণ করতে দেয়।

## কে সাইন ইন করেছেন তা দেখান৷

নোট পৃষ্ঠা ব্যবহারকারীকে অভিবাদন জানায় এবং সাইন-আউট বোতাম দেখায়; একজন দর্শক পরিবর্তে দুটি ফর্মের লিঙ্কগুলি দেখেন:

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

খুলুন <http://localhost:3000/signup>, একটি অ্যাকাউন্ট তৈরি করুন: আপনি একটি **সাইন আউট** বোতাম দিয়ে নোটগুলিতে ল্যান্ড করেন৷ সাইন আউট করুন, তারপর <http://localhost:3000/signin> এ আবার সাইন ইন করুন।

## আপনি যা শিখেছেন

- `useSession` `nexyconfig.py` একটি স্বাক্ষরিত সেশন কুকি চালু করে; এর গোপন বসবাস `.env`।
- ডাটাবেস পাসওয়ার্ডের একটি লবণাক্ত, ধীর হ্যাশ রাখে, `hmac.compare_digest` দিয়ে চেক করা হয়।
- একটি অ্যাকশন `useSession()` দিয়ে অধিবেশন লেখে; একটি পৃষ্ঠা একই ভাবে এটি পড়ে।

## পরবর্তী পদক্ষেপ

- [পার্ট 11: প্রত্যেক ব্যবহারকারীকে তাদের নিজস্ব নোট দিন](own-notes.md)
- [মিডলওয়্যার এবং নিরাপত্তা ](../guides/middleware-and-security.md): সেশন, CORS এবং বিশ্বস্ত হোস্ট
