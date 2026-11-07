# Nexy کے ساتھ ایک نوٹس ایپ بنائیں، حصہ 10: ایک اکاؤنٹ بنائیں اور سائن ان کریں۔

حصہ 10 وزیٹر کو ایک ای میل اور پاس ورڈ کے ساتھ ایک اکاؤنٹ بنانے، سائن ان اور سائن آؤٹ کرنے، اور یاد رکھنے دیتا ہے کہ سیشن کوکی کے ساتھ کون سائن ان ہوا ہے۔

**شروع کرنے سے پہلے:** [حصہ 9](paginate-the-notes.md) کی ایپ۔

## سیشنز آن کریں۔

سیشن ایک دستخط شدہ کوکی ہے: سرور اس میں سائن ان صارف کی شناخت رکھتا ہے، اور ہر درخواست پر اسے واپس پڑھتا ہے۔ Starlette اس پر `itsdangerous` کے ساتھ دستخط کرتا ہے:

```bash
uv add itsdangerous
```

اس نے جس راز سے دستخط کیے ہیں وہ ڈیٹا بیس ایڈریس کے آگے `.env` میں رکھا گیا ہے:

```bash filename="env"
DATABASE_URL=sqlite:///dev.db
SESSION_SECRET=change-me-to-a-long-random-string
```

`python -c "import secrets; print(secrets.token_urlsafe(32))"` کے ساتھ ایک حقیقی راز بنائیں۔ کوئی بھی جو اسے جانتا ہے وہ کسی بھی صارف کے بطور کوکی پر دستخط کر سکتا ہے۔

`useSession` ماحول سے خفیہ پڑھے جانے کے ساتھ سیشن آن کرتا ہے:

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

`os.environ[...]` اور نہیں `os.getenv(...)`: بغیر کسی راز کے، ایپ بغیر کسی کے چلنے کے بجائے اسٹارٹ اپ پر رک جاتی ہے۔

## صارف کی وضاحت کریں۔

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
صارف اس کی اپنی ایک خصوصیت ہے، `src/apps/users/` میں:

```python filename="src/apps/users/user_model.py"
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
```
<!-- /router -->

ٹیبل پاس ورڈ کا ایک ہیش رکھتا ہے، پاس ورڈ کبھی نہیں: چوری شدہ ڈیٹا بیس پاس ورڈ نہیں دیتا۔ `unique=True` ڈیٹا بیس اسی ای میل کے ساتھ دوسرے اکاؤنٹ سے انکار کرتا ہے۔

```bash
nx migrate -m "create users"
nx migrate --upgrade
```

ہجرت اپنے طور پر نیا ماڈل تلاش کرتی ہے: یہ ہر `*_model.py` کو `src/` پڑھتی ہے۔

## ہیش کریں اور پاس ورڈ چیک کریں۔

`hashlib.scrypt`، معیاری لائبریری سے، ایک ہیش ہے جسے مقصد کے مطابق سست بنایا گیا ہے، اس لیے ایک ایک کرکے پاس ورڈ کا اندازہ لگانا حملہ آور کو برسوں کا خرچہ دیتا ہے۔ ہر پاس ورڈ کو اپنا بے ترتیب نمک ملتا ہے:

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

`hmac.compare_digest` ایک ایسے وقت میں موازنہ کرتا ہے جو اس بات پر منحصر نہیں ہوتا ہے کہ دونوں ہیشوں میں کہاں فرق ہے، لہذا جواب کا وقت حملہ آور کو کچھ نہیں بتاتا ہے۔

## سائن اپ کریں، سائن ان کریں، سائن آؤٹ کریں۔

تین اعمال۔ ہر ایک جو کامیاب ہوتا ہے وہ سیشن لکھتا ہے، یا اسے خالی کرتا ہے:

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

*غلط ای میل یا پاس ورڈ*، جو کبھی نہیں: ایک پیغام جس میں کہا گیا تھا کہ "اس ای میل کے ساتھ کوئی اکاؤنٹ نہیں" کسی کو بھی بتائے گا کہ کون سے ای میلز کا اکاؤنٹ ہے۔

## دو شکلیں۔

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

`autocomplete="new-password"` پاس ورڈ مینیجر کو ایک مضبوط پاس ورڈ پیش کرنے دیتا ہے، اور `current-password` اسے محفوظ کردہ پاس ورڈ کو بھرنے دیتا ہے۔

## دکھائیں کہ کون سائن ان ہے۔

نوٹس کا صفحہ صارف کو سلام کرتا ہے اور سائن آؤٹ بٹن دکھاتا ہے۔ ایک وزیٹر اس کے بجائے دو فارموں کے لنکس دیکھتا ہے:

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

کھولیں <http://localhost:3000/signup>، ایک اکاؤنٹ بنائیں: آپ **سائن آؤٹ** بٹن کے ساتھ نوٹوں پر اترتے ہیں۔ سائن آؤٹ کریں، پھر <http://localhost:3000/signin> پر دوبارہ سائن ان کریں۔

## جو آپ نے سیکھا۔

- `useSession` `nexyconfig.py` میں دستخط شدہ سیشن کوکی کو آن کرتا ہے۔ اس کا راز `.env` میں رہتا ہے۔
- ڈیٹا بیس پاس ورڈ کی نمکین، سست ہیش رکھتا ہے، جس کی جانچ `hmac.compare_digest` سے کی جاتی ہے۔
- ایک ایکشن سیشن کو `useSession()` کے ساتھ لکھتا ہے؛ ایک صفحہ اسے اسی طرح پڑھتا ہے۔

## اگلے اقدامات

- [حصہ 11: ہر صارف کو ان کے اپنے نوٹس دیں](own-notes.md)
- [مڈل ویئر اور سیکیورٹی](../guides/middleware-and-security.md): سیشنز، CORS اور قابل اعتماد میزبان
