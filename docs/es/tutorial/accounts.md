# Cree una aplicación de notas con Nexy, parte 10: cree una cuenta e inicie sesión

La Parte 10 permite a un visitante crear una cuenta con un correo electrónico y una contraseña, iniciar sesión y cerrar sesión, y recuerda quién inició sesión con una cookie de sesión.

**Antes de comenzar:** la aplicación de la [parte 9](paginate-the-notes.md).

## Activar sesiones

Una sesión es una cookie firmada: el servidor coloca en ella la identificación del usuario que inició sesión y la lee en cada solicitud. Starlette lo firma con `itsdangerous`:

```bash
uv add itsdangerous
```

El secreto con el que firma se guarda en `.env`, al lado de la dirección de la base de datos:

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
SESSION_SECRET=change-me-to-a-long-random-string
```

Haz un verdadero secreto con `python -c "import secrets; print(secrets.token_urlsafe(32))"`. Cualquiera que lo sepa puede firmar una cookie como cualquier usuario.

`useSession` activa las sesiones, con el secreto leído del entorno:

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

`os.environ[...]` y no `os.getenv(...)`: sin un secreto, la aplicación se detiene al iniciarse en lugar de ejecutarse sin ninguno.

## Describir un usuario

<!-- router:fbr,custom -->
```python filename="src/modelos/user_model.py"
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
```
<!-- /router -->

<!-- router:modular -->
Un usuario es una característica propia, en `src/apps/users/`:

```python filename="src/apps/users/user_model.py"
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
```
<!-- /router -->

La tabla mantiene un hash de la contraseña, nunca la contraseña: una base de datos robada no revela las contraseñas. `unique=True` hace que la base de datos rechace una segunda cuenta con el mismo correo electrónico.

```bash
nx migrate -m "create users"
nx migrate --upgrade
```

La migración encuentra el nuevo modelo por sí sola: lee cada `*_model.py` de `src/`.

## Hash y verificar una contraseña

`hashlib.scrypt`, de la biblioteca estándar, es un hash lento intencionalmente, por lo que adivinar las contraseñas una por una le cuesta años al atacante. Cada contraseña obtiene su propia sal aleatoria:

<!-- router:fbr,custom -->
```python filename="src/cuentas.py"
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
```python filename="src/cuentas.py"
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

`hmac.compare_digest` se compara en un tiempo que no depende de dónde difieren los dos hashes, por lo que el tiempo de respuesta no le dice nada al atacante.

## Registrarse, iniciar sesión, cerrar sesión

Tres acciones. Cada uno que lo logra escribe la sesión, o la vacía:

```python filename="src/acciones/cuentas.py"
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

*Correo electrónico o contraseña incorrectos*, nunca cuál: un mensaje que dijera "no hay cuenta con este correo electrónico" le diría a cualquiera qué correos electrónicos tienen una cuenta.

## las dos formas

<!-- router:fbr,custom -->
```nexy filename="src/rutas/signup.nexy"
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

```nexy filename="src/rutas/signin.nexy"
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

`autocomplete="new-password"` permite que un administrador de contraseñas ofrezca una contraseña segura y `current-password` le permite completar la que guardó.

## Mostrar quién ha iniciado sesión

La página de notas saluda al usuario y muestra el botón de cerrar sesión; en su lugar, un visitante ve los enlaces a los dos formularios:

<!-- router:fbr,custom -->
```nexy filename="src/rutas/notas/index.nexy"
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

Abra <http://localhost:3000/signup>, cree una cuenta: accederá a las notas con un botón **Cerrar sesión**. Cierra sesión y luego inicia sesión nuevamente en <http://localhost:3000/signin>.

## lo que aprendiste

- `useSession` en `nexyconfig.py` activa una cookie de sesión firmada; su secreto vive en `.env`.
- La base de datos mantiene un hash lento y salado de la contraseña, verificado con `hmac.compare_digest`.
- Una Acción escribe la sesión con `useSession()`; una página lo lee de la misma manera.

## Próximos pasos

- [Parte 11: dale a cada usuario sus propias notas](own-notes.md)
- [Middleware y seguridad](../guides/middleware-and-security.md): sesiones, CORS y hosts confiables
