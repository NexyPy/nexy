# Cree una aplicación de notas con Nexy, parte 5: almacene las notas en SQLite

La parte 5 mueve las notas de un diccionario Python a una base de datos SQLite, con un modelo, una migración y dos notas para empezar, y las páginas las leen desde allí.

**Antes de comenzar:** la aplicación de la [parte 4](components.md).

## Instale el ORM y la herramienta de migración.

```bash
uv add sqlmodel alembic
```

[SQLModel](https://sqlmodel.tiangolo.com/) describe una tabla como una clase Python y Alembic convierte los cambios a esas clases en migraciones. Nexy tampoco envuelve: los usas tal cual están.

## Abrir la base de datos

La dirección de la base de datos va en `.env`, en la raíz del proyecto. `nx migrate` y la aplicación lo leen desde allí:

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
```

`sqlite:///dev.db` es un archivo, `dev.db`, al lado de `nexyconfig.py`: SQLite no necesita servidor. Mantenga `.env` fuera de Git: contiene los secretos de una base de datos real.

El motor es la conexión a la base de datos. Lee `DATABASE_URL`, con el mismo archivo como predeterminado cuando la variable no está configurada:

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///dev.db"))
```

## describir una nota

<!-- router:fbr,custom -->
```python filename="src/modelos/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

<!-- router:modular -->
El modelo vive con la característica a la que pertenece, junto a su controlador:

```python filename="src/apps/notes/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

`table=True` convierte la clase en una tabla, `note`. El `id` lo proporciona la base de datos cuando se guarda una nota.

## Crear la tabla con una migración.

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` escribe la carpeta `alembic/` y apunta a tu modelo. `-m` compara el modelo con la base de datos y escribe la migración que crea la tabla; `--upgrade` lo ejecuta. Cambie el modelo más tarde, ejecute los dos últimos comandos nuevamente y la siguiente tabla.

## Leer las notas de la base de datos.

Las funciones de `src/notes.py` mantienen sus nombres, por lo que las páginas cambian poco: ahora abren una sesión, consultan la tabla y devuelven `Note` objetos en lugar de cadenas.

<!-- router:fbr,custom -->
```python filename="src/notas.py"
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
```python filename="src/notas.py"
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

## Añade dos notas para empezar.

Un script semilla llena una base de datos vacía, por lo que cada nueva copia del proyecto comienza con algo que mostrar:

<!-- router:fbr,custom -->
```python filename="src/semilla.py"
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
```python filename="src/semilla.py"
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

Al inicio, Nexy importa todos los módulos de `src/` para encontrar las acciones de [parte 6](create-a-note.md). `if __name__ == "__main__":` mantiene la semilla para el comando anterior: importado por la aplicación, el archivo solo define `seed` y no toca nada.

## Mostrar las notas de la base de datos.

<!-- router:fbr,custom -->
```nexy filename="src/rutas/notas/index.nexy"
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

```nexy filename="src/rutas/notas/[id].nexy"
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

```python filename="src/rutas/api/notes.py"
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

Abrir <http://localhost:3000/notes>: las mismas dos tarjetas, ahora leídas desde `dev.db`. Reinicie `nexy dev` y todavía están allí.

## lo que aprendiste

- SQLModel describe una tabla como una clase; el motor en `src/configs/db.py` abre la base de datos.
- `nx migrate` escribe y ejecuta las migraciones: `--init` una vez, luego `-m` y `--upgrade` por cambio.
- Las páginas y los controladores llaman a funciones simples Python que consultan la base de datos: Nexy no agrega ninguna capa.

## Próximos pasos

- [Parte 6: crear una nota a partir de un formulario](create-a-note.md)
- [SQLite](../databases/sqlite.md): pragmas, acceso asíncrono y pruebas en una base de datos en memoria
