# Nexy এর সাথে একটি নোট অ্যাপ তৈরি করুন, পার্ট 12: ইমেলের মাধ্যমে একটি ভুলে যাওয়া পাসওয়ার্ড রিসেট করুন

পার্ট 12 একজন ব্যবহারকারীকে ইমেলের মাধ্যমে একটি লিঙ্ক পাঠায় যারা তাদের পাসওয়ার্ড ভুলে গেছে। লিঙ্কটি একটি নতুন পাসওয়ার্ডের জন্য একটি ফর্ম খোলে, এক ঘন্টা কাজ করে এবং শুধুমাত্র একবার।

**আপনি শুরু করার আগে:** [পার্ট 11](own-notes.md) এর অ্যাপ।

## একটি ইমেইল পাঠান

`smtplib`, স্ট্যান্ডার্ড লাইব্রেরি থেকে, যেকোন মেল সার্ভারের সাথে কথা বলে: আপনার প্রদানকারীর, অথবা পোস্টমার্ক, রিসেন্ড বা অ্যামাজন এসইএস-এর মতো একটি পরিষেবা, যা সকলেই SMTP গ্রহণ করে। একটি সার্ভার ছাড়া, ইমেলটি `nexy dev` এর টার্মিনালে মুদ্রিত হয়, যা আপনার কম্পিউটারে আপনার প্রয়োজন:

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

বাস্তবে পাঠাতে, সার্ভার যোগ করুন `.env`:

```text
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=notes@example.com
SMTP_PASSWORD=the-password-of-the-mailbox
MAIL_FROM=notes@example.com
APP_URL=https://notes.example.com
```

`starttls()` পাসওয়ার্ড পাঠানোর আগে সংযোগটি এনক্রিপ্ট করে।

## একটি লিঙ্ক তৈরি করুন যা একবার কাজ করে, এক ঘন্টার জন্য

লিঙ্কটি সেশন সিক্রেট সহ স্বাক্ষরিত একটি টোকেন বহন করে, তাই কেউ হাতে একটি তৈরি করতে পারে না। `itsdangerous` এটিতে সময় লেখেন, এবং `max_age` এক ঘণ্টা পর তা প্রত্যাখ্যান করেন। টোকেনটি পাসওয়ার্ড হ্যাশের শেষটিও ধারণ করে: একবার পাসওয়ার্ড পরিবর্তন হলে, হ্যাশ পরিবর্তিত হয় এবং লিঙ্কটি কাজ করা বন্ধ করে দেয়।

<!-- router:fbr,custom -->
```python filename="src/password_reset.py"
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
```python filename="src/password_reset.py"
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

## লিঙ্কের জন্য জিজ্ঞাসা করুন, তারপর এটি ব্যবহার করুন

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

`request_reset` একইভাবে উত্তর দেয় যে ইমেলের একটি অ্যাকাউন্ট আছে কি না: পৃষ্ঠাটি বলছে একটি লিঙ্ক *সম্ভবত* তার পথে রয়েছে, তাই এটি কাউকে জানায় না কোন ইমেলগুলি নিবন্ধিত হয়েছে৷

## দুটি পৃষ্ঠা, এবং তাদের একটি লিঙ্ক

<!-- router:fbr,custom -->
```nexy filename="src/routes/forgot.nexy"
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

`role="status"` একজন স্ক্রিন রিডারকে বাধা না দিয়ে বার্তা পড়তে বাধ্য করে, যেখানে `role="alert"` বাধা দেয়: একটি নিশ্চিতকরণ একটি ত্রুটি নয়।

খুলুন <http://localhost:3000/forgot>, আপনার অ্যাকাউন্টের ইমেল টাইপ করুন এবং পাঠান। `nexy dev`-এর টার্মিনাল ইমেলটি প্রিন্ট করে: এর লিঙ্কটি খুলুন, একটি নতুন পাসওয়ার্ড চয়ন করুন এবং এটি দিয়ে সাইন ইন করুন। লিঙ্কটি দ্বিতীয়বার খুলুন: এটি প্রত্যাখ্যান করা হয়েছে।

## আপনি যা শিখেছেন

- `smtplib` যেকোনো SMTP সার্ভারের মাধ্যমে একটি ইমেল পাঠায়; উন্নয়নে, এটি মুদ্রণ যথেষ্ট।
- `itsdangerous` থেকে একটি স্বাক্ষরিত, টাইমড টোকেন এমন একটি লিঙ্ক তৈরি করে যা কেউ জাল করতে পারে না, এক ঘন্টার জন্য বৈধ।
- টোকেনে পাসওয়ার্ড হ্যাশের কিছু অংশ রাখলে লিঙ্কটি একবারই কাজ করে।

## পরবর্তী পদক্ষেপ

- [ইউনিট 4, অংশ 13: আপনি টাইপ করার সাথে সাথে নোটগুলি অনুসন্ধান করুন](search-the-notes.md)
- [মিডলওয়্যার এবং নিরাপত্তা ](../guides/middleware-and-security.md): সেশন, CORS এবং বিশ্বস্ত হোস্ট
