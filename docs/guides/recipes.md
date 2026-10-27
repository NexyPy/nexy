# Recipes

Three things almost every app needs, as complete files you can copy. Every code block below with a
`filename` is written into a fresh project and exercised by the test suite, so what you read is what
runs.

They use plain API handlers; the same functions work behind a page in either [mode](../routing/fbr/modes.md).

## Sign in with a session

A visitor posts a name and a password, the server remembers them in a signed cookie, and everything
under `/api/account` is closed to anyone else.

Turn sessions on. They need `itsdangerous` (`uv add itsdangerous`):

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me-in-production"}
```

Sign in and out:

```python filename="src/routes/api/login.py"
from pydantic import BaseModel

from nexy.http import HTTPException, Request

USERS = {"ada": "lovelace"}


class Credentials(BaseModel):
    name: str
    password: str


async def POST(request: Request, body: Credentials):
    if USERS.get(body.name) != body.password:
        raise HTTPException(status_code=401, detail="Wrong name or password")
    request.session["user"] = body.name
    return {"user": body.name}
```

```python filename="src/routes/api/logout.py"
from nexy.http import Request


async def POST(request: Request):
    request.session.clear()
    return {"signed_out": True}
```

Guard a whole folder with one [`dependencies.py`](../routing/fbr/dependencies/README.md):

```python filename="src/routes/api/account/dependencies.py"
from nexy.http import HTTPException, Request


def current_user(request: Request) -> str:
    if not request.session.get("user"):
        raise HTTPException(status_code=401, detail="Sign in first")
    return request.session["user"]


dependencies = [current_user]
```

```python filename="src/routes/api/account/index.py"
from nexy.http import Request


async def GET(request: Request):
    return {"user": request.session["user"]}
```

> **Good to know**: keep real passwords out of the source. Store a hash (`argon2`, `bcrypt`) and read
> the secret key from the environment. The session cookie is signed, not encrypted.

## A JSON API with create, read and delete

A store in a module, a collection route and an item route. Replace the dictionary with
[a database](databases.md) when the data must survive a restart.

```python filename="src/notes.py"
from pydantic import BaseModel


class Note(BaseModel):
    id: int
    title: str


NOTES: dict[int, Note] = {}
```

```python filename="src/routes/api/notes/index.py"
from pydantic import BaseModel

from src.notes import NOTES, Note


class NewNote(BaseModel):
    title: str


async def GET() -> list[Note]:
    return list(NOTES.values())


async def POST(body: NewNote) -> Note:
    note = Note(id=max(NOTES, default=0) + 1, title=body.title)
    NOTES[note.id] = note
    return note
```

```python filename="src/routes/api/notes/[id].py"
from nexy.http import HTTPException

from src.notes import NOTES, Note


async def GET(id: int) -> Note:
    if id not in NOTES:
        raise HTTPException(status_code=404, detail="No such note")
    return NOTES[id]


async def DELETE(id: int) -> dict[str, bool]:
    if NOTES.pop(id, None) is None:
        raise HTTPException(status_code=404, detail="No such note")
    return {"deleted": True}
```

A body that does not fit `NewNote` is refused with `422` before your code runs, and the return
annotation becomes the documented response. See
[validation and errors](../routing/fbr/handlers/validation-and-errors.md).

## Receive a file

Uploads need `python-multipart` (`uv add python-multipart`). Check the size yourself, and never use
the client's file name as a path:

```python filename="src/routes/api/upload.py"
from pathlib import Path

from nexy.http import HTTPException, UploadFile

MAX_BYTES = 1_000_000


async def POST(file: UploadFile) -> dict[str, int | str]:
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large")
    name = Path(file.filename or "upload").name
    return {"name": name, "size": len(data)}
```

`Path(...).name` drops any folder the client put in the name, such as `../../etc/passwd`. Save the
bytes under a name you generate, not under this one.

## Next steps

- [Actions](actions.md): typed server functions for forms and buttons
- [Middleware and security](middleware-and-security.md): CORS, hosts, sessions
- [Testing](testing.md): test your own handlers the same way
