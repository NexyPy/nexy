# Créer une application de notes avec Nexy, partie 12 : réinitialiser un mot de passe oublié par e-mail

La partie 12 envoie un lien par email à un utilisateur qui a oublié son mot de passe. Le lien ouvre un formulaire pour un nouveau mot de passe, fonctionne pendant une heure et une seule fois.

**Avant de commencer :** l'application de la [partie 11](own-notes.md).

## Envoyer un email

`smtplib`, de la bibliothèque standard, communique avec n'importe quel serveur de messagerie : celui de votre fournisseur ou un service tel que Postmark, Resend ou Amazon SES, qui acceptent tous SMTP. Sans serveur, l'email est imprimé dans le terminal de `nexy dev`, c'est tout ce dont vous avez besoin sur votre ordinateur :

```python filename="src/mail.py"
import os
import smtplib
from email.message import EmailMessage


def send_email(to: str, subject: str, body: str) -> None:
    """Send through the SMTP server named in `.env`; without one, print the email instead."""
    host = os.getenv("SMTP_HOST")
    if not host:
        print(f"To: {to}\nSubject: {subject}\n\n{body}", flush=True)
        return
    message = EmailMessage()
    message["From"] = os.getenv("MAIL_FROM", "notes@localhost")
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587"))) as smtp:
        smtp.starttls()
        smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        smtp.send_message(message)
```

Pour envoyer pour de vrai, ajoutez le serveur à `.env` :

```text
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=notes@example.com
SMTP_PASSWORD=the-password-of-the-mailbox
MAIL_FROM=notes@example.com
APP_URL=https://notes.example.com
```

`starttls()` crypte la connexion avant l'envoi du mot de passe.

## Faire un lien qui fonctionne une fois, pendant une heure

Le lien contient un jeton signé avec le secret de session, donc personne ne peut en créer un à la main. `itsdangerous` y écrit l'heure et `max_age` la refuse au bout d'une heure. Le jeton contient également la fin du hachage du mot de passe : une fois le mot de passe modifié, le hachage change et le lien cesse de fonctionner.

<!-- router:fbr,custom -->
```python filename="src/mot de passe_reset.py"
import os

from itsdangerous import BadSignature, URLSafeTimedSerializer
from sqlmodel import Session, select

from src.accounts import hash_password
from src.configs.db import engine
from src.models.user_model import User

ONE_HOUR = 3600


def signer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(os.environ["SESSION_SECRET"], salt="password-reset")


def find_by_email(email: str) -> User | None:
    with Session(engine) as session:
        return session.exec(select(User).where(User.email == email)).first()


def reset_token(user: User) -> str:
    """A token that names the user and the end of their current password hash."""
    return signer().dumps([user.id, user.password_hash[-16:]])


def user_of(token: str) -> User | None:
    """The user of a token less than an hour old, whose password has not changed since."""
    try:
        user_id, fingerprint = signer().loads(token, max_age=ONE_HOUR)
    except BadSignature:
        return None
    with Session(engine) as session:
        user = session.get(User, user_id)
    if user is None or user.password_hash[-16:] != fingerprint:
        return None
    return user


def set_password(user_id: int, password: str) -> None:
    with Session(engine) as session:
        user = session.get(User, user_id)
        user.password_hash = hash_password(password)
        session.commit()
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/mot de passe_reset.py"
import os

from itsdangerous import BadSignature, URLSafeTimedSerializer
from sqlmodel import Session, select

from src.accounts import hash_password
from src.apps.users.user_model import User
from src.configs.db import engine

ONE_HOUR = 3600


def signer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(os.environ["SESSION_SECRET"], salt="password-reset")


def find_by_email(email: str) -> User | None:
    with Session(engine) as session:
        return session.exec(select(User).where(User.email == email)).first()


def reset_token(user: User) -> str:
    """A token that names the user and the end of their current password hash."""
    return signer().dumps([user.id, user.password_hash[-16:]])


def user_of(token: str) -> User | None:
    """The user of a token less than an hour old, whose password has not changed since."""
    try:
        user_id, fingerprint = signer().loads(token, max_age=ONE_HOUR)
    except BadSignature:
        return None
    with Session(engine) as session:
        user = session.get(User, user_id)
    if user is None or user.password_hash[-16:] != fingerprint:
        return None
    return user


def set_password(user_id: int, password: str) -> None:
    with Session(engine) as session:
        user = session.get(User, user_id)
        user.password_hash = hash_password(password)
        session.commit()
```
<!-- /router -->

## Demandez le lien, puis utilisez-le

```python filename="src/actions/password_reset.py"
import os
from urllib.parse import urlencode

from nexy.decorators import Action
from nexy.http import RedirectResponse
from src.mail import send_email
from src.password_reset import find_by_email, reset_token, set_password, user_of

MIN_PASSWORD = 8


def go(path: str, **query: str) -> RedirectResponse:
    return RedirectResponse(f"{path}?{urlencode(query)}" if query else path, status_code=303)


@Action
async def request_reset(email: str) -> RedirectResponse:
    user = find_by_email(email.strip().lower())
    if user is not None:
        link = f"{os.getenv('APP_URL', 'http://localhost:3000')}/reset?token={reset_token(user)}"
        body = f"Open this link within an hour to choose a new password:\n\n{link}\n"
        send_email(user.email, "Reset your password", body)
    return go("/forgot", sent="1")


@Action
async def reset_password(token: str, password: str) -> RedirectResponse:
    user = user_of(token)
    if user is None:
        return go("/forgot", error="This link has expired or was used. Ask for a new one.")
    if len(password) < MIN_PASSWORD:
        return go("/reset", token=token, error=f"A password has at least {MIN_PASSWORD} characters.")
    set_password(user.id, password)
    return go("/signin", reset="1")
```

`request_reset` répond de la même manière, que l'e-mail ait un compte ou non : la page indique qu'un lien *peut* être en route, donc elle n'indique à personne quels e-mails sont enregistrés.

## Les deux pages et un lien vers elles

<!-- router:fbr,custom -->
```nexy filename="src/routes/oublié.nexy"
---
from nexy import useSearchParams

params = useSearchParams()
sent = params.get("sent") == "1"
error = params.get("error", "")
---
<section class="app-page">
  <h1>Forgot your password?</h1>

  {% if sent %}
  <p role="status">If an account uses this email, a link to reset its password is on its way.</p>
  {% endif %}
  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['request_reset'] }}">
    <label>Email <input type="email" name="email" autocomplete="email" required></label>
    <button type="submit">Send the link</button>
  </form>
</section>
```

```nexy filename="src/routes/reset.nexy"
---
from nexy import useSearchParams

params = useSearchParams()
token = params.get("token", "")
error = params.get("error", "")
---
<section class="app-page">
  <h1>Choose a new password</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['reset_password'] }}">
    <input type="hidden" name="token" value="{{ token | e }}">
    <label>New password <input type="password" name="password" autocomplete="new-password" minlength="8" required></label>
    <button type="submit">Save the password</button>
  </form>
</section>
```

```nexy filename="src/routes/signin.nexy"
---
from nexy import useSearchParams

params = useSearchParams()
error = params.get("error", "")
reset = params.get("reset") == "1"
---
<section class="app-page">
  <h1>Sign in</h1>

  {% if reset %}
  <p role="status">Your password is changed: sign in with the new one.</p>
  {% endif %}
  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['sign_in'] }}">
    <label>Email <input type="email" name="email" autocomplete="email" required></label>
    <label>Password <input type="password" name="password" autocomplete="current-password" required></label>
    <button type="submit">Sign in</button>
  </form>

  <a href="/forgot">Forgot your password?</a>
  <a href="/signup">Create an account</a>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/users/forgot_view.nexy"
---
from nexy import useSearchParams

params = useSearchParams()
sent = params.get("sent") == "1"
error = params.get("error", "")
---
<section class="app-page">
  <h1>Forgot your password?</h1>

  {% if sent %}
  <p role="status">If an account uses this email, a link to reset its password is on its way.</p>
  {% endif %}
  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['request_reset'] }}">
    <label>Email <input type="email" name="email" autocomplete="email" required></label>
    <button type="submit">Send the link</button>
  </form>
</section>
```

```nexy filename="src/apps/users/reset_view.nexy"
---
from nexy import useSearchParams

params = useSearchParams()
token = params.get("token", "")
error = params.get("error", "")
---
<section class="app-page">
  <h1>Choose a new password</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['reset_password'] }}">
    <input type="hidden" name="token" value="{{ token | e }}">
    <label>New password <input type="password" name="password" autocomplete="new-password" minlength="8" required></label>
    <button type="submit">Save the password</button>
  </form>
</section>
```

```nexy filename="src/apps/users/signin_view.nexy"
---
from nexy import useSearchParams

params = useSearchParams()
error = params.get("error", "")
reset = params.get("reset") == "1"
---
<section class="app-page">
  <h1>Sign in</h1>

  {% if reset %}
  <p role="status">Your password is changed: sign in with the new one.</p>
  {% endif %}
  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['sign_in'] }}">
    <label>Email <input type="email" name="email" autocomplete="email" required></label>
    <label>Password <input type="password" name="password" autocomplete="current-password" required></label>
    <button type="submit">Sign in</button>
  </form>

  <a href="/forgot">Forgot your password?</a>
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


@Controller("/forgot")
class ForgotController:
    async def get(self):
        return page("src/apps/users/forgot_view.nexy")


@Controller("/reset")
class ResetController:
    async def get(self):
        return page("src/apps/users/reset_view.nexy")
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AboutController, AppController
from .notes.notes_controller import NoteController, NotesApiController, NotesController
from .users.users_controller import (
    ForgotController,
    ResetController,
    SignInController,
    SignUpController,
)


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
        ForgotController,
        ResetController,
    ]
```
<!-- /router -->

`role="status"` fait lire le message à un lecteur d'écran sans l'interrompre, où `role="alert"` interrompt : une confirmation n'est pas une erreur.

Ouvrez <http://localhost:3000/forgot>, saisissez l'email de votre compte et envoyez. Le terminal de `nexy dev` imprime l'e-mail : ouvrez son lien, choisissez un nouveau mot de passe et connectez-vous avec celui-ci. Ouvrez une seconde fois le lien : il est refusé.

## Ce que tu as appris

- `smtplib` envoie un e-mail via n'importe quel serveur SMTP ; en développement, l’imprimer suffit.
- Un jeton signé et chronométré de `itsdangerous` crée un lien que personne ne peut forger, valable une heure.
- Mettre une partie du hachage du mot de passe dans le jeton fait que le lien ne fonctionne qu'une seule fois.

## Prochaines étapes

- [Unité 4, partie 13 : recherchez les notes au fur et à mesure que vous tapez](search-the-notes.md)
- [Middleware et sécurité](../guides/middleware-and-security.md) : sessions, CORS et hôtes de confiance
