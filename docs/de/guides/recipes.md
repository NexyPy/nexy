# Rezepte

Drei Dinge, die fast jede App benötigt, nämlich vollständige Dateien, die Sie kopieren können. Jeder Codeblock unten mit a
`filename` wird in ein neues Projekt geschrieben und von der Testsuite ausgeführt, Sie lesen also, was
läuft.

Sie verwenden einfache API-Handler; Die gleichen Funktionen funktionieren hinter einer Seite in jedem [Modus](../routing/fbr/modes.md).

## Melden Sie sich mit einer Sitzung an

Ein Besucher gibt einen Namen und ein Passwort ein, der Server speichert sie in einem signierten Cookie und so weiter
unter `/api/account` ist für alle anderen geschlossen.

Schalten Sie Sitzungen ein. Sie benötigen `itsdangerous` (`uv add itsdangerous`):

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me-in-production"}
```

An- und Abmelden:

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

Schützen Sie einen ganzen Ordner mit einem [`dependencies.py`](../routing/fbr/dependencies/README.md):

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

> [!NOTE]
> Halten Sie echte Passwörter von der Quelle fern. Speichern Sie einen Hash (`argon2`, `bcrypt`) und lesen Sie ihn
> der geheime Schlüssel aus der Umgebung. Das Sitzungscookie ist signiert und nicht verschlüsselt.

## Eine JSON-API mit Erstellen, Lesen und Löschen

Ein Speicher in einem Modul, eine Sammelroute und eine Artikelroute. Ersetzen Sie das Wörterbuch durch
[eine Datenbank](databases.md), wenn die Daten einen Neustart überstehen müssen.

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

Ein Körper, der nicht zu `NewNote` passt, wird mit `422` abgelehnt, bevor Ihr Code ausgeführt wird, und die Rückgabe erfolgt
Die Anmerkung wird zur dokumentierten Antwort. Siehe
[Validierung und Fehler](../routing/fbr/handlers/validation-and-errors.md).

## Empfangen Sie eine Datei

Uploads benötigen `python-multipart` (`uv add python-multipart`). Überprüfen Sie die Größe selbst und verwenden Sie sie niemals
der Dateiname des Clients als Pfad:

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

`Path(...).name` löscht alle Ordner, die der Client in den Namen eingegeben hat, z. B. `../../etc/passwd`. Speichern Sie die
Bytes unter einem von Ihnen generierten Namen, nicht unter diesem.

## Nächste Schritte

- [Aktionen](actions.md): typisierte Serverfunktionen für Formulare und Schaltflächen
- [Middleware und Sicherheit](middleware-and-security.md): CORS, Hosts, Sitzungen
- [Testen](testing.md): Testen Sie Ihre eigenen Handler auf die gleiche Weise