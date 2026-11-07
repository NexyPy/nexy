# Verwenden Sie SQLite mit Nexy

SQLite ist die Datenbank, die ein neues Nexy-Projekt verwendet, wenn `DATABASE_URL` nicht festgelegt ist: eine Datei, kein Server und Pythons eigener Treiber, über SQLModel, SQLAlchemy oder Tortoise-ORM.

## Wenn SQLite passt

- Entwicklung, Tests und Demos: nichts zu installieren oder zu starten.
- Eine Site mit einem Server und bescheidenen Schreibvorgängen: ein Blog, ein internes Tool, ein kleiner Shop.
- Mit der App werden leseintensive Daten ausgeliefert.

Wählen Sie [PostgreSQL](postgresql.md), wenn mehrere Server gleichzeitig schreiben oder wenn Sie Rich Types und Volltextsuche in großem Maßstab benötigen.

## Die Verbindungszeichenfolge

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
```

| URL | Datenbank |
|---|---|
| `sqlite:///dev.db` | `dev.db`, relativ zum Ordner, in dem `nx dev` ausgeführt wird |
| `sqlite:////var/data/app.db` | ein absoluter Pfad: vier Schrägstriche |
| `sqlite://` | im Speicher, verschwunden, wenn der Prozess stoppt |
| `sqlite+aiosqlite:///dev.db` | Dieselbe Datei über den asynchronen Treiber |

## Der Motor

`nx new` schreibt diese Datei, wenn Sie SQLModel auswählen. Die einzige Zeile, die für SQLite hinzugefügt werden muss, ist `check_same_thread`: Eine Seite und ein Handler können die Engine aus verschiedenen Threads verwenden.

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(
    os.getenv("DATABASE_URL", "sqlite:///dev.db"),
    connect_args={"check_same_thread": False},
)
```

## Fremdschlüssel und WAL

SQLite erzwingt pro Verbindung keine Fremdschlüssel, es sei denn, sie werden dazu aufgefordert. Im WAL-Modus können Leser weitermachen, während ein Autor schreibt. Beides ist ein `PRAGMA`-Lauf bei jeder neuen Verbindung, der neben der Engine eingerichtet wird:

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlalchemy import event
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(
    os.getenv("DATABASE_URL", "sqlite:///dev.db"),
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def set_pragmas(connection, _record) -> None:
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()
```

## Ein Modell

```python filename="src/models/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    done: bool = False
```

## Eine Sitzung pro Anfrage

Eine Abhängigkeit öffnet eine Sitzung für die Anfrage und schließt sie nach der Antwort:

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

## Von einem Handler lesen und schreiben

<!-- router:fbr,custom -->
```python filename="src/routes/api/notes/index.py"
from pydantic import BaseModel
from sqlmodel import Session, select

from nexy.http import Depends, JSONResponse
from src.configs.session import get_session
from src.models.note_model import Note


class NewNote(BaseModel):
    title: str


async def GET(session: Session = Depends(get_session)):
    return session.exec(select(Note)).all()


async def POST(body: NewNote, session: Session = Depends(get_session)):
    note = Note(title=body.title)
    session.add(note)
    session.commit()
    session.refresh(note)
    return JSONResponse(note.model_dump(), status_code=201)
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/notes/notes_api_controller.py"
from pydantic import BaseModel
from sqlmodel import Session, select

from nexy.decorators import Controller
from nexy.http import Depends, JSONResponse
from src.configs.session import get_session
from src.models.note_model import Note


class NewNote(BaseModel):
    title: str


@Controller("/api/notes")
class NotesApiController:
    async def get(self, session: Session = Depends(get_session)):
        return session.exec(select(Note)).all()

    async def post(self, body: NewNote, session: Session = Depends(get_session)):
        note = Note(title=body.title)
        session.add(note)
        session.commit()
        session.refresh(note)
        return JSONResponse(note.model_dump(), status_code=201)
```

Listen Sie den Controller im `controllers` des Root-Moduls auf.
<!-- /router -->

## Von einer Seite lesen

Eine `.nexy`-Seite führt ihren Frontmatter auf dem Server aus, sodass sie denselben Code aufrufen kann. Behalten Sie die Abfrage in einer Funktion bei: Nur die auf der obersten Ebene des Frontmatters zugewiesenen Namen erreichen die Vorlage.

```python filename="src/services/notes.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def open_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).where(Note.done == False)))  # noqa: E712
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes.nexy"
---
from src.services.notes import open_notes

notes = open_notes()
---
<ul>
  {% for note in notes %}
  <li>{{ note.title | e }}</li>
  {% endfor %}
</ul>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from src.services.notes import open_notes

notes = open_notes()
---
<ul>
  {% for note in notes %}
  <li>{{ note.title | e }}</li>
  {% endfor %}
</ul>
```

```python filename="src/apps/notes/notes_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews("src/apps/notes/notes_view.nexy")
```
<!-- /router -->

## Erstellen Sie die Tabellen mit Migrationen

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` schreibt `alembic/env.py`, das die Modelle importiert, die es mit der Datenbank vergleicht. Importieren Sie dort jedes neue Modellmodul:

```python filename="alembic/env.py"
import src.models.note_model  # noqa: F401
```

SQLite kann `ALTER` die meisten Spalten nicht an Ort und Stelle halten. Aktivieren Sie den Batch-Modus von Alembic, der die Tabelle kopiert, in beiden `context.configure(...)`-Aufrufen von `alembic/env.py`:

```python filename="alembic/env.py"
context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
```

## Asynchron mit `aiosqlite`

```bash
uv add aiosqlite
```

```python filename="src/configs/async_db.py"
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

async_engine = create_async_engine("sqlite+aiosqlite:///dev.db")


async def get_async_session():
    async with AsyncSession(async_engine) as session:
        yield session
```

<!-- router:fbr,custom -->
```python filename="src/routes/api/notes/count.py"
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from nexy.http import Depends
from src.configs.async_db import get_async_session
from src.models.note_model import Note


async def GET(session: AsyncSession = Depends(get_async_session)):
    count = (await session.exec(select(func.count()).select_from(Note))).one()
    return {"count": count}
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/notes/notes_count_api_controller.py"
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from nexy.decorators import Controller
from nexy.http import Depends
from src.configs.async_db import get_async_session
from src.models.note_model import Note


@Controller("/api/notes/count")
class NotesCountApiController:
    async def get(self, session: AsyncSession = Depends(get_async_session)):
        count = (await session.exec(select(func.count()).select_from(Note))).one()
        return {"count": count}
```

Listen Sie den Controller im `controllers` des Root-Moduls auf.
<!-- /router -->

## Tests auf einer In-Memory-Datenbank

`StaticPool` behält eine Verbindung bei, sodass die In-Memory-Datenbank während des gesamten Tests bestehen bleibt. Die Abhängigkeit des Handlers wird gegen eine ausgetauscht, die sie verwendet:

```python filename="tests/test_notes.py"
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from nexy.app import app
from src.configs.session import get_session

test_engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
SQLModel.metadata.create_all(test_engine)


def override_session():
    with Session(test_engine) as session:
        yield session


def test_a_note_is_created():
    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)
    client.post("/api/notes", json={"title": "Write the docs"})
    assert client.get("/api/notes").json()[0]["title"] == "Write the docs"
```

## In Produktion

- **Bewahren Sie die Datei auf einer persistenten Festplatte auf.** Das eigene Dateisystem eines Containers geht bei der erneuten Bereitstellung verloren: Mounten Sie ein Volume und zeigen Sie `DATABASE_URL` darauf mit einem absoluten Pfad.
- **Ein Server, eine Datei.** SQLite hat jeweils einen Autor. Mehrere `nx start` Worker auf derselben Maschine sind mit WAL einverstanden; Bei einigen Maschinen ist dies nicht der Fall.
- **Sichern Sie es während der Ausführung** mit `sqlite3 app.db ".backup backup.db"`, nicht mit einer Dateikopie.

## Nächste Schritte

- [Datenbanken](../guides/databases.md)
- [Verwenden Sie PostgreSQL mit Nexy](postgresql.md)
- [Testen](../guides/testing.md)
