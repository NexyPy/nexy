# Build a notes app with Nexy, part 5: store the notes in SQLite

Part 5 moves the notes from a Python dictionary into a SQLite database, with a model, a migration
and two notes to start with, and the pages read them from there.

**Before you start:** the app of [part 4](components.md).

## Install the ORM and the migration tool

```bash
uv add sqlmodel alembic
```

[SQLModel](https://sqlmodel.tiangolo.com/) describes a table as a Python class, and Alembic turns
changes to those classes into migrations. Nexy does not wrap either: you use them as they are.

## Open the database

The address of the database goes in `.env`, at the root of the project. `nx migrate` and the app
both read it from there:

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
```

`sqlite:///dev.db` is a file, `dev.db`, next to `nexyconfig.py`: SQLite needs no server. Keep
`.env` out of Git: it holds the secrets of a real database.

The engine is the connection to the database. It reads `DATABASE_URL`, with the same file as a
default when the variable is unset:

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///dev.db"))
```

## Describe a note

<!-- router:fbr,custom -->
```python filename="src/models/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

<!-- router:modular -->
The model lives with the feature it belongs to, next to its controller:

```python filename="src/apps/notes/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

`table=True` makes the class a table, `note`. The `id` is given by the database when a note is
saved.

## Create the table with a migration

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` writes the `alembic/` folder and points it at your model. `-m` compares the model with the
database and writes the migration that creates the table; `--upgrade` runs it. Change the model
later, run the last two commands again, and the table follows.

## Read the notes from the database

The functions of `src/notes.py` keep their names, so the pages change little: they now open a
session, query the table, and return `Note` objects instead of strings.

<!-- router:fbr,custom -->
```python filename="src/notes.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def all_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).order_by(Note.id)))


def find(note_id: int) -> Note | None:
    with Session(engine) as session:
        return session.get(Note, note_id)
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/notes.py"
from sqlmodel import Session, select

from src.apps.notes.note_model import Note
from src.configs.db import engine


def all_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).order_by(Note.id)))


def find(note_id: int) -> Note | None:
    with Session(engine) as session:
        return session.get(Note, note_id)
```
<!-- /router -->

## Add two notes to start with

A seed script fills an empty database, so every new copy of the project starts with something to
show:

<!-- router:fbr,custom -->
```python filename="src/seed.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def seed() -> None:
    with Session(engine) as session:
        if session.exec(select(Note)).first() is None:
            session.add_all([Note(text="Buy milk"), Note(text="Ship Nexy")])
            session.commit()


if __name__ == "__main__":
    seed()
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/seed.py"
from sqlmodel import Session, select

from src.apps.notes.note_model import Note
from src.configs.db import engine


def seed() -> None:
    with Session(engine) as session:
        if session.exec(select(Note)).first() is None:
            session.add_all([Note(text="Buy milk"), Note(text="Ship Nexy")])
            session.commit()


if __name__ == "__main__":
    seed()
```
<!-- /router -->

```bash
python -m src.seed
```

At startup, Nexy imports every module of `src/` to find the Actions of [part 6](create-a-note.md).
`if __name__ == "__main__":` keeps the seed for the command above: imported by the app, the file
only defines `seed`, and touches nothing.

## Show the notes from the database

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import all_notes

notes = all_notes()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```

```nexy filename="src/routes/notes/[id].nexy"
---
from nexy import notFound
from src.notes import find

id: prop[int]
note = find(id)
if note is None:
    notFound()
---
<section class="app-page">
  <h1>{{ note.text }}</h1>
  <a href="/notes">All notes</a>
</section>
```

```python filename="src/routes/api/notes.py"
from src.notes import all_notes


async def GET():
    return [note.model_dump() for note in all_notes()]
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import all_notes

notes = all_notes()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```

```python filename="src/apps/notes/notes_controller.py"
from nexy import notFound
from nexy.decorators import Controller
from nexy.hooks import useViews
from src.notes import all_notes, find

LAYOUT = "src/apps/layout.nexy"


def page(view: str, **context: object):
    return useViews(LAYOUT, context={"children": useViews(view, context=context)})


@Controller("/notes")
class NotesController:
    async def get(self):
        return page("src/apps/notes/notes_view.nexy")


@Controller("/notes/{id}")
class NoteController:
    async def get(self, id: int):
        note = find(id)
        if note is None:
            notFound()
        return page("src/apps/notes/note_view.nexy", text=note.text)


@Controller("/api/notes")
class NotesApiController:
    async def get(self) -> list[dict]:
        return [note.model_dump() for note in all_notes()]
```
<!-- /router -->

Open <http://localhost:3000/notes>: the same two cards, now read from `dev.db`. Restart
`nexy dev`, and they are still there.

## What you learned

- SQLModel describes a table as a class; the engine in `src/configs/db.py` opens the database.
- `nx migrate` writes and runs the migrations: `--init` once, then `-m` and `--upgrade` per change.
- Pages and controllers call plain Python functions that query the database: Nexy adds no layer.

## Next steps

- [Part 6: create a note from a form](create-a-note.md)
- [SQLite](../databases/sqlite.md): pragmas, async access and tests on an in-memory database
