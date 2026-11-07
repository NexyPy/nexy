# Créez une application de notes avec Nexy, partie 10 : créez un compte et connectez-vous

La partie 10 permet à un visiteur de créer un compte avec un e-mail et un mot de passe, de se connecter et de se déconnecter, et de se souvenir de qui est connecté avec un cookie de session.

**Avant de commencer :** l'application de la [partie 9](paginate-the-notes.md).

## Activer les sessions

Une session est un cookie signé : le serveur y met l'identifiant de l'utilisateur connecté et le relit à chaque demande. Starlette le signe avec `itsdangerous` :

```bash
uv add itsdangerous
```

Le secret avec lequel il signe est conservé dans `.env`, à côté de l'adresse de la base de données :

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
SESSION_SECRET=change-me-to-a-long-random-string
```

Faites un vrai secret avec `python -c "import secrets; print(secrets.token_urlsafe(32))"`. Quiconque le connaît peut signer un cookie comme n'importe quel utilisateur.

`useSession` active les sessions, avec le secret lu depuis l'environnement :

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

`os.environ[...]` et non `os.getenv(...)` : sans secret, l'application s'arrête au démarrage au lieu de s'exécuter sans aucun secret.

## Décrire un utilisateur

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
Un utilisateur est une fonctionnalité à part entière, dans `src/apps/users/` :

```python filename="src/apps/users/user_model.py"
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
```
<!-- /router -->

La table conserve un hachage du mot de passe, jamais le mot de passe : une base de données volée ne donne pas les mots de passe. `unique=True` fait que la base de données refuse un deuxième compte avec le même email.

```bash
nx migrate -m "create users"
nx migrate --upgrade
```

La migration trouve le nouveau modèle d'elle-même : elle lit tous les `*_model.py` de `src/`.

## Hachez et vérifiez un mot de passe

`hashlib.scrypt`, de la bibliothèque standard, est un hachage volontairement lent, donc deviner les mots de passe un par un coûte des années à l'attaquant. Chaque mot de passe reçoit son propre sel aléatoire :

<!-- router:fbr,custom -->
```python filename="src/comptes.py"
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
```python filename="src/comptes.py"
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

`hmac.compare_digest` compare dans un temps qui ne dépend pas de la différence entre les deux hachages, donc le temps de réponse ne dit rien à un attaquant.

## S'inscrire, se connecter, se déconnecter

Trois actions. Chacun qui réussit écrit la session, ou la vide :

```python filename="src/actions/comptes.py"
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

*Email ou mot de passe erroné*, jamais lequel : un message indiquant "aucun compte avec cet e-mail" indiquerait à quiconque quels e-mails ont un compte.

## Les deux formes

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

`autocomplete="new-password"` permet à un gestionnaire de mots de passe de proposer un mot de passe fort, et `current-password` lui permet de remplir celui qu'il a enregistré.

## Afficher qui est connecté

La page de notes accueille l'utilisateur et affiche le bouton de déconnexion ; un visiteur voit à la place les liens vers les deux formulaires :

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

Ouvrez <http://localhost:3000/signup>, créez un compte : vous atterrissez sur les notes avec un bouton **Déconnexion**. Déconnectez-vous, puis reconnectez-vous à <http://localhost:3000/signin>.

## Ce que tu as appris

- `useSession` dans `nexyconfig.py` active un cookie de session signé ; son secret réside dans `.env`.
- La base de données conserve un hachage lent et salé du mot de passe, vérifié avec `hmac.compare_digest`.
- Une action écrit la session avec `useSession()` ; une page le lit de la même manière.

## Prochaines étapes

- [Partie 11 : donnez à chaque utilisateur ses propres notes](own-notes.md)
- [Middleware et sécurité](../guides/middleware-and-security.md) : sessions, CORS et hôtes de confiance
