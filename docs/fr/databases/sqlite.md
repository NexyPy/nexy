# Utiliser SQLite avec Nexy

SQLite est la base de données qu'un nouveau projet Nexy utilise lorsque `DATABASE_URL` n'est pas défini : un fichier, aucun serveur et le propre pilote de Python, via SQLModel, SQLAlchemy ou Tortoise-ORM.

## Quand SQLite correspond

- Développement, tests et démos : rien à installer ni à démarrer.
- Un site avec un seul serveur et une écriture modeste : un blog, un outil interne, une petite boutique.
- Données lourdes en lecture livrées avec l'application.

Choisissez [PostgreSQL](postgresql.md) lorsque plusieurs serveurs écrivent en même temps ou lorsque vous avez besoin de types riches et d'une recherche en texte intégral à grande échelle.

## La chaîne de connexion

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
```

| URL | Base de données |
|---|---|
| `sqlite:///dev.db` | `dev.db`, par rapport au dossier `nx dev` dans lequel s'exécute |
| `sqlite:////var/data/app.db` | un chemin absolu : quatre barres obliques |
| `sqlite://` | en mémoire, disparu lorsque le processus s'arrête |
| `sqlite+aiosqlite:///dev.db` | le même fichier, via le pilote asynchrone |

## Le moteur

`nx new` écrit ce fichier lorsque vous sélectionnez SQLModel. La seule ligne à ajouter pour SQLite est `check_same_thread` : une page et un gestionnaire peuvent utiliser le moteur à partir de différents threads.

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

## Clés étrangères et WAL

SQLite n'applique pas les clés étrangères sauf si cela est demandé, par connexion. Le mode WAL permet aux lecteurs de continuer pendant qu'un écrivain écrit. Les deux sont un `PRAGMA` exécuté à chaque nouvelle connexion, configuré à côté du moteur :

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

## Un modèle

```python filename="src/models/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    done: bool = False
```

## Une séance par demande

Une dépendance ouvre une session pour la requête et la ferme après la réponse :

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

## Lire et écrire à partir d'un gestionnaire

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

## Lire à partir d'une page

Une page `.nexy` exécute son frontmatter sur le serveur, elle peut donc appeler le même code. Conservez la requête dans une fonction : seuls les noms attribués au niveau supérieur du frontmatter atteignent le modèle.

```python filename="src/services/notes.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def open_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).where(Note.done == False)))  # noqa: E712
```

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

## Créer les tables avec les migrations

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` écrit `alembic/env.py`, qui importe les modèles qu'il compare avec la base de données. Importez-y chaque nouveau module de modèle :

```python filename="alambic/env.py"
import src.models.note_model  # noqa: F401
```

SQLite ne peut pas `ALTER` la plupart des colonnes en place. Activez le mode batch de Alembic, qui copie la table, dans les deux appels `context.configure(...)` de `alembic/env.py` :

```python filename="alambic/env.py"
context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
```

## Asynchrone avec `aiosqlite`

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

## Tests sur une base de données en mémoire

`StaticPool` conserve une connexion, de sorte que la base de données en mémoire dure tout le test. La dépendance du gestionnaire est remplacée par celle qui l'utilise :

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

## En production

- **Conservez le fichier sur un disque persistant.** Le système de fichiers d'un conteneur est perdu lors du redéploiement : montez un volume et pointez `DATABASE_URL` dessus avec un chemin absolu.
- **Un serveur, un fichier.** SQLite n'a qu'un seul rédacteur à la fois. Plusieurs travailleurs `nx start` sur la même machine acceptent WAL ; plusieurs machines ne le sont pas.
- **Sauvegardez-le pendant son exécution** avec `sqlite3 app.db ".backup backup.db"`, pas avec une copie de fichier.

## Prochaines étapes

- [Bases de données](../guides/databases.md)
- [Utiliser PostgreSQL avec Nexy](postgresql.md)
- [Tests](../guides/testing.md)
