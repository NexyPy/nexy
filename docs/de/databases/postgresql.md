# Verwenden Sie PostgreSQL mit Nexy

Um PostgreSQL mit Nexy zu verwenden, installieren Sie den `psycopg`-Treiber, legen Sie `DATABASE_URL` auf eine `postgresql+psycopg://`-URL fest und fragen Sie sie von Handlern und Seiten über SQLModel oder SQLAlchemy ab.

## Führen Sie PostgreSQL lokal aus

```bash
docker run --name nexy-db -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=app -p 5432:5432 -d postgres:17
```

## Installieren Sie den Treiber

```bash
uv add "psycopg[binary]"
```

`psycopg` ist Version 3 des Treibers für synchronen und asynchronen Code. Für rein asynchronen Code ist `asyncpg` die andere Wahl:

```bash
uv add asyncpg
```

## Die Verbindungszeichenfolge

```bash filename=".env"
DATABASE_URL=postgresql+psycopg://postgres:secret@localhost:5432/app
```

| URL | Fahrer |
|---|---|
| `postgresql+psycopg://user:pass@host:5432/db` | psycopg 3, synchron und asynchron |
| `postgresql+asyncpg://user:pass@host:5432/db` | asyncpg, nur asynchron |
| `postgresql://user:pass@host:5432/db` | psycopg2, falls es installiert ist |
| `postgres://...` | abgelehnt von SQLAlchemy: Benennen Sie das Schema um in `postgresql+psycopg://` |

Ein Passwort mit `@`, `:` oder `/` ist in der URL prozentual kodiert: `p@ss` ist `p%40ss`.

## Der Motor

Hosting-Plattformen geben häufig eine `postgres://`-URL aus. Konvertieren Sie es dort, wo der Motor hergestellt wird:

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()


def database_url() -> str:
    url = os.environ["DATABASE_URL"]
    return url.replace("postgres://", "postgresql+psycopg://", 1)


engine = create_engine(database_url(), pool_size=5, max_overflow=10, pool_pre_ping=True)
```

| Pool-Option | Was es bewirkt |
|---|---|
| `pool_size=5` | Verbindungen werden pro Prozess offen gehalten |
| `max_overflow=10` | Zusätzliche Verbindungen unter Last zulässig, danach geschlossen |
| `pool_pre_ping=True` | Überprüft eine Verbindung vor der Verwendung, sodass ein Neustart der Datenbank kein Fehler ist |

Jeder `nx start`-Worker hat seinen eigenen Pool: `workers × (pool_size + max_overflow)` muss unter dem `max_connections` des Servers bleiben.

## Ein Modell mit PostgreSQL-Typen

`uuid`-Schlüssel, `JSONB`, Arrays und `timestamptz` sind native Spaltentypen:

```python filename="src/models/post_model.py"
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlmodel import Field, SQLModel


class Post(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=200, index=True)
    tags: list[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    extra: dict = Field(default_factory=dict, sa_column=Column(JSONB))
    published_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )
```

## Eine Sitzung pro Anfrage

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

## Von einem Handler lesen und schreiben

```python filename="src/routes/api/posts/index.py"
from pydantic import BaseModel
from sqlmodel import Session, select

from nexy.http import Depends, JSONResponse
from src.configs.session import get_session
from src.models.post_model import Post


class NewPost(BaseModel):
    title: str
    tags: list[str] = []


async def GET(tag: str | None = None, session: Session = Depends(get_session)):
    query = select(Post).order_by(Post.published_at.desc())
    if tag:
        query = query.where(Post.tags.contains([tag]))
    return session.exec(query).all()


async def POST(body: NewPost, session: Session = Depends(get_session)):
    post = Post(title=body.title, tags=body.tags)
    session.add(post)
    session.commit()
    session.refresh(post)
    return JSONResponse(post.model_dump(mode="json"), status_code=201)
```

`Post.tags.contains([tag])` ist PostgreSQLs `@>`: die Beiträge, deren Tags `tag` enthalten.

## Ein `uuid` in der URL

```python filename="src/routes/api/posts/[id].py"
import uuid

from sqlmodel import Session

from nexy.http import Depends, HTTPException
from src.configs.session import get_session
from src.models.post_model import Post


async def GET(id: uuid.UUID, session: Session = Depends(get_session)):
    post = session.get(Post, id)
    if post is None:
        raise HTTPException(status_code=404, detail="No such post")
    return post
```

Ein Segment, das keine UUID ist, antwortet `404`, bevor die Abfrage ausgeführt wird.

## Abfrage `JSONB`

```python filename="src/services/posts.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.post_model import Post


def featured_posts() -> list[Post]:
    with Session(engine) as session:
        query = select(Post).where(Post.extra["featured"].as_boolean())
        return list(session.exec(query))
```

```nexy filename="src/routes/featured.nexy"
---
from src.services.posts import featured_posts

posts = featured_posts()
---
<ul>
  {% for post in posts %}
  <li>{{ post.title | e }}</li>
  {% endfor %}
</ul>
```

Behalten Sie die Abfrage in einer Funktion bei: Nur die auf der obersten Ebene des Frontmatters zugewiesenen Namen erreichen die Vorlage.

## Volltextsuche

```python filename="src/routes/api/search.py"
from sqlalchemy import func
from sqlmodel import Session, select

from nexy.http import Depends
from src.configs.session import get_session
from src.models.post_model import Post


async def GET(q: str, session: Session = Depends(get_session)):
    document = func.to_tsvector("english", Post.title)
    query = func.websearch_to_tsquery("english", q)
    rank = func.ts_rank(document, query)
    rows = session.exec(select(Post).where(document.op("@@")(query)).order_by(rank.desc()))
    return rows.all()
```

Ein Index hält es auf einer großen Tabelle schnell. Fügen Sie es in einer Migration hinzu:

```python filename="alembic/versions/xxxx_search_index.py"
def upgrade() -> None:
    op.execute(
        "CREATE INDEX post_title_search ON post USING GIN (to_tsvector('english', title))"
    )
```

## Upserts

```python filename="src/services/tags.py"
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Field, Session, SQLModel

from src.configs.db import engine


class TagCount(SQLModel, table=True):
    tag: str = Field(primary_key=True)
    count: int = 0


def count_tag(tag: str) -> None:
    statement = insert(TagCount).values(tag=tag, count=1)
    statement = statement.on_conflict_do_update(
        index_elements=[TagCount.tag], set_={"count": TagCount.count + 1}
    )
    with Session(engine) as session:
        session.exec(statement)
        session.commit()
```

## Migrationen

```bash
nx migrate --init
nx migrate -m "create posts"
nx migrate --upgrade
```

`nx migrate` liest `DATABASE_URL`, überprüft, ob der Treiber installiert ist und ob der Server antwortet, und führt dann Alembic aus. Importieren Sie jedes Modellmodul in `alembic/env.py`, damit die automatische Generierung es sieht.

## Asynchron mit `asyncpg`

```python filename="src/configs/async_db.py"
import os

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

async_engine = create_async_engine(
    os.environ["DATABASE_URL"].replace("+psycopg", "+asyncpg", 1), pool_pre_ping=True
)


async def get_async_session():
    async with AsyncSession(async_engine) as session:
        yield session
```

```python filename="src/routes/api/posts/count.py"
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from nexy.http import Depends
from src.configs.async_db import get_async_session
from src.models.post_model import Post


async def GET(session: AsyncSession = Depends(get_async_session)):
    count = (await session.exec(select(func.count()).select_from(Post))).one()
    return {"count": count}
```

psycopg 3 läuft auch asynchron: `postgresql+psycopg://` funktioniert auch mit `create_async_engine`.

## Tests in einer Transaktion

Jeder Test wird in einer Transaktion ausgeführt, die zurückgesetzt wird, sodass die Testdatenbank leer bleibt:

```python filename="tests/conftest.py"
import pytest
from sqlmodel import Session, SQLModel, create_engine

from nexy.app import app
from src.configs.session import get_session

test_engine = create_engine("postgresql+psycopg://postgres:secret@localhost:5432/app_test")
SQLModel.metadata.create_all(test_engine)


@pytest.fixture(autouse=True)
def session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    app.dependency_overrides[get_session] = lambda: session
    yield session
    session.close()
    transaction.rollback()
    connection.close()
```

## Verwaltet PostgreSQL

| Service | Was ändert sich |
|---|---|
| [Neon](neon.md) | füge `?sslmode=require` hinzu; Verwenden Sie den gepoolten Host für viele kurze Verbindungen |
| Supabase | das gleiche URL-Formular; Verwenden Sie für viele Worker den Pooler-Port `6543`. |
| Amazon RDS, Cloud SQL, Azure | Fügen Sie `?sslmode=require` hinzu und erlauben Sie das Netzwerk der App |

## Nächste Schritte

- [Datenbanken](../guides/databases.md)
- [Benutze Neon mit Nexy](neon.md)
- [Verwenden Sie SQLite mit Nexy](sqlite.md)
