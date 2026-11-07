# Utilice SQLite con Nexy

SQLite es la base de datos que utiliza un nuevo proyecto Nexy cuando `DATABASE_URL` no está configurado: un archivo, ningún servidor y el propio controlador de Python, a través de SQLModel, SQLAlchemy o Tortoise-ORM.

## Cuando SQLite encaja

- Desarrollo, pruebas y demostraciones: nada que instalar o iniciar.
- Un sitio con un servidor y escrituras modestas: un blog, una herramienta interna, una pequeña tienda.
- Datos de gran cantidad de lectura enviados con la aplicación.

Elija [PostgreSQL](postgresql.md) cuando varios servidores escriban a la vez o cuando necesite tipos enriquecidos y búsqueda de texto completo a escala.

## La cadena de conexión

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
```

| URL | Base de datos |
|---|---|
| `sqlite:///dev.db` | `dev.db`, relativo a la carpeta en la que se ejecuta `nx dev` |
| `sqlite:////var/data/app.db` | un camino absoluto: cuatro barras |
| `sqlite://` | en la memoria, desaparece cuando el proceso se detiene |
| `sqlite+aiosqlite:///dev.db` | el mismo archivo, a través del controlador asíncrono |

## el motor

`nx new` escribe este archivo cuando eliges SQLModel. La única línea que se debe agregar para SQLite es `check_same_thread`: una página y un controlador pueden usar el motor de diferentes hilos.

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

## Claves externas y WAL

SQLite no aplica claves externas a menos que se soliciten, por conexión. El modo WAL permite a los lectores continuar mientras un escritor escribe. Ambos se ejecutan `PRAGMA` en cada nueva conexión, configurados junto al motor:

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

## un modelo

```python filename="src/modelos/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    done: bool = False
```

## Una sesión por solicitud

Una dependencia abre una sesión para la solicitud y la cierra después de la respuesta:

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

## Leer y escribir desde un controlador.

<!-- router:fbr,custom -->
```python filename="src/rutas/api/notes/index.py"
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

Enumere el controlador en el `controllers` del módulo raíz.
<!-- /router -->

## Leer de una página

Una página `.nexy` ejecuta su frontmatter en el servidor, por lo que puede llamar al mismo código. Mantener la consulta en una función: solo los nombres asignados en el nivel superior del frontmatter llegan a la plantilla.

```python filename="src/servicios/notas.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def open_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).where(Note.done == False)))  # noqa: E712
```

<!-- router:fbr,custom -->
```nexy filename="src/rutas/notas.nexy"
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

## Crear las tablas con migraciones.

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` escribe `alembic/env.py`, que importa los modelos que compara con la base de datos. Importe cada nuevo módulo de modelo allí:

```python filename="alambique/env.py"
import src.models.note_model  # noqa: F401
```

SQLite no puede `ALTER` la mayoría de las columnas en su lugar. Active el modo por lotes de Alembic, que copia la tabla, en ambas llamadas de `context.configure(...)` de `alembic/env.py`:

```python filename="alambique/env.py"
context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
```

## Asíncrono con `aiosqlite`

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
```python filename="src/rutas/api/notes/count.py"
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

Enumere el controlador en el `controllers` del módulo raíz.
<!-- /router -->

## Pruebas en una base de datos en memoria

`StaticPool` mantiene una conexión, por lo que la base de datos en memoria permanece viva durante toda la prueba. La dependencia del controlador se cambia por una que lo usa:

```python filename="pruebas/test_notes.py"
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

## En producción

- **Mantenga el archivo en un disco persistente.** El propio sistema de archivos de un contenedor se pierde al volver a implementarlo: monte un volumen y apúntelo `DATABASE_URL` con una ruta absoluta.
- **Un servidor, un archivo.** SQLite tiene un escritor a la vez. Varios `nx start` trabajadores en la misma máquina están bien con WAL; varias máquinas no lo son.
- **Haga una copia de seguridad mientras se ejecuta** con `sqlite3 app.db ".backup backup.db"`, no con una copia del archivo.

## Próximos pasos

- [Bases de datos](../guides/databases.md)
- [Utilice PostgreSQL con Nexy](postgresql.md)
- [Pruebas](../guides/testing.md)
