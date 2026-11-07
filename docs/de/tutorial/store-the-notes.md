# Erstellen Sie eine Notizen-App mit Nexy, Teil 5: Speichern Sie die Notizen in SQLite

Teil 5 verschiebt die Notizen aus einem Python-Wörterbuch in eine SQLite-Datenbank, mit einem Modell, einer Migration und zunächst zwei Notizen, und die Seiten lesen sie von dort aus.

**Bevor Sie beginnen:** die App von [Teil 4](components.md).

## Installieren Sie den ORM und das Migrationstool

```bash
uv add sqlmodel alembic
```

[SQLModel](https://sqlmodel.tiangolo.com/) beschreibt eine Tabelle als eine Python-Klasse, und Alembic wandelt Änderungen an diesen Klassen in Migrationen um. Nexy verpackt auch nicht: Sie verwenden sie so, wie sie sind.

## Öffnen Sie die Datenbank

Die Adresse der Datenbank befindet sich in `.env` im Stammverzeichnis des Projekts. `nx migrate` und die App haben es beide von dort gelesen:

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
```

`sqlite:///dev.db` ist eine Datei, `dev.db`, neben `nexyconfig.py`: SQLite benötigt keinen Server. Halten Sie `.env` von Git fern: Es birgt die Geheimnisse einer echten Datenbank.

Die Engine ist die Verbindung zur Datenbank. Es lautet `DATABASE_URL`, mit derselben Datei als Standard, wenn die Variable nicht gesetzt ist:

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///dev.db"))
```

## Beschreiben Sie eine Notiz

<!-- router:fbr,custom -->
```python filename="src/models/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

<!-- router:modular -->
Das Modell lebt mit der Funktion, zu der es gehört, neben seinem Controller:

```python filename="src/apps/notes/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

`table=True` macht die Klasse zu einer Tabelle, `note`. Der `id` wird von der Datenbank vergeben, wenn eine Notiz gespeichert wird.

## Erstellen Sie die Tabelle mit einer Migration

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` schreibt den Ordner `alembic/` und zeigt ihn auf Ihr Modell. `-m` vergleicht das Modell mit der Datenbank und schreibt die Migration, die die Tabelle erstellt; `--upgrade` führt es aus. Ändern Sie das Modell später, führen Sie die letzten beiden Befehle erneut aus und die Tabelle folgt.

## Lesen Sie die Notizen aus der Datenbank

Die Funktionen von `src/notes.py` behalten ihre Namen, daher ändern sich die Seiten kaum: Sie öffnen jetzt eine Sitzung, fragen die Tabelle ab und geben `Note`-Objekte anstelle von Zeichenfolgen zurück.

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

## Fügen Sie zunächst zwei Notizen hinzu

Ein Seed-Skript füllt eine leere Datenbank, sodass jede neue Kopie des Projekts mit etwas beginnt, das angezeigt werden soll:

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

Beim Start importiert Nexy jedes Modul von `src/`, um die Aktionen von [Teil 6](create-a-note.md) zu finden. `if __name__ == "__main__":` behält den Startwert für den obigen Befehl: Die von der App importierte Datei definiert nur `seed` und berührt nichts.

## Zeigen Sie die Notizen aus der Datenbank an

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

Öffnen Sie <http://localhost:3000/notes>: die gleichen zwei Karten, jetzt gelesen von `dev.db`. Starten Sie `nexy dev` neu und sie sind immer noch da.

## Was du gelernt hast

- SQLModel beschreibt eine Tabelle als Klasse; Die Engine in `src/configs/db.py` öffnet die Datenbank.
- `nx migrate` schreibt und führt die Migrationen aus: `--init` einmal, dann `-m` und `--upgrade` pro Änderung.
- Seiten und Controller rufen einfache Python Funktionen auf, die die Datenbank abfragen: Nexy fügt keine Ebene hinzu.

## Nächste Schritte

- [Teil 6: Eine Notiz aus einem Formular erstellen](create-a-note.md)
- [SQLite](../databases/sqlite.md): Pragmas, asynchroner Zugriff und Tests auf einer In-Memory-Datenbank
