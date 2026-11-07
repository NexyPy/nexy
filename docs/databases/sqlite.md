# Use SQLite with Nexy

SQLite is the database a new Nexy project uses when `DATABASE_URL` is unset: one file, no server,
and Python's own driver, through SQLModel, SQLAlchemy or Tortoise-ORM.

## When SQLite fits

- Development, tests and demos: nothing to install or start.
- A site with one server and modest writes: a blog, an internal tool, a small shop.
- Read-heavy data shipped with the app.

Pick [PostgreSQL](postgresql.md) when several servers write at once, or when you need rich types
and full-text search at scale.

## The connection string

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
```

| URL | Database |
|---|---|
| `sqlite:///dev.db` | `dev.db`, relative to the folder `nx dev` runs in |
| `sqlite:////var/data/app.db` | an absolute path: four slashes |
| `sqlite://` | in memory, gone when the process stops |
| `sqlite+aiosqlite:///dev.db` | the same file, through the async driver |

## The engine

`nx new` writes this file when you pick SQLModel. The one line to add for SQLite is
`check_same_thread`: a page and a handler may use the engine from different threads.

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

## Foreign keys and WAL

SQLite does not enforce foreign keys unless asked, per connection. WAL mode lets readers go on while
one writer writes. Both are a `PRAGMA` run on every new connection, set up next to the engine:

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

## A model

```python filename="src/models/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    done: bool = False
```

## A session per request

A dependency opens a session for the request and closes it after the answer:

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

## Read and write from a handler

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

List the controller in the `controllers` of the root module.
<!-- /router -->

## Read from a page

A `.nexy` page runs its frontmatter on the server, so it can call the same code. Keep the query in a
function: only the names assigned at the top level of the frontmatter reach the template.

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

## Create the tables with migrations

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` writes `alembic/env.py`, which imports the models it compares with the database. Import
each new model module there:

```python filename="alembic/env.py"
import src.models.note_model  # noqa: F401
```

SQLite cannot `ALTER` most columns in place. Turn on Alembic's batch mode, which copies the table,
in both `context.configure(...)` calls of `alembic/env.py`:

```python filename="alembic/env.py"
context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
```

## Async with `aiosqlite`

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

List the controller in the `controllers` of the root module.
<!-- /router -->

## Tests on an in-memory database

`StaticPool` keeps one connection, so the in-memory database lives for the whole test. The handler's
dependency is swapped for one that uses it:

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

## In production

- **Keep the file on a persistent disk.** A container's own file system is lost on redeploy:
  mount a volume and point `DATABASE_URL` at it with an absolute path.
- **One server, one file.** SQLite has one writer at a time. Several `nx start` workers on the same
  machine are fine with WAL; several machines are not.
- **Back it up while it runs** with `sqlite3 app.db ".backup backup.db"`, not with a file copy.

## Next steps

- [Databases](../guides/databases.md)
- [Use PostgreSQL with Nexy](postgresql.md)
- [Testing](../guides/testing.md)
