# Use PostgreSQL with Nexy

To use PostgreSQL with Nexy, install the `psycopg` driver, set `DATABASE_URL` to a
`postgresql+psycopg://` URL, and query it from handlers and pages through SQLModel or SQLAlchemy.

## Run PostgreSQL locally

```bash
docker run --name nexy-db -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=app -p 5432:5432 -d postgres:17
```

## Install the driver

```bash
uv add "psycopg[binary]"
```

`psycopg` is version 3 of the driver, for sync and async code. For async-only code, `asyncpg` is the
other choice:

```bash
uv add asyncpg
```

## The connection string

```bash filename=".env"
DATABASE_URL=postgresql+psycopg://postgres:secret@localhost:5432/app
```

| URL | Driver |
|---|---|
| `postgresql+psycopg://user:pass@host:5432/db` | psycopg 3, sync and async |
| `postgresql+asyncpg://user:pass@host:5432/db` | asyncpg, async only |
| `postgresql://user:pass@host:5432/db` | psycopg2, if it is installed |
| `postgres://...` | rejected by SQLAlchemy: rename the scheme to `postgresql+psycopg://` |

A password with `@`, `:` or `/` in it is percent-encoded in the URL: `p@ss` is `p%40ss`.

## The engine

Hosting platforms often hand out a `postgres://` URL. Convert it where the engine is made:

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

| Pool option | What it does |
|---|---|
| `pool_size=5` | connections kept open per process |
| `max_overflow=10` | extra connections allowed under load, closed after |
| `pool_pre_ping=True` | checks a connection before use, so a restarted database is no error |

Each `nx start` worker has its own pool: `workers × (pool_size + max_overflow)` must stay under the
server's `max_connections`.

## A model with PostgreSQL types

`uuid` keys, `JSONB`, arrays and `timestamptz` are native column types:

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

## A session per request

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

## Read and write from a handler

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

`Post.tags.contains([tag])` is PostgreSQL's `@>`: the posts whose tags hold `tag`.

## A `uuid` in the URL

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

A segment that is not a UUID answers `404` before the query runs.

## Query `JSONB`

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

Keep the query in a function: only the names assigned at the top level of the frontmatter reach the
template.

## Full-text search

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

An index keeps it fast on a large table. Add it in a migration:

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

## Migrations

```bash
nx migrate --init
nx migrate -m "create posts"
nx migrate --upgrade
```

`nx migrate` reads `DATABASE_URL`, checks that the driver is installed and that the server
answers, then runs Alembic. Import each model module in `alembic/env.py` so autogenerate sees it.

## Async with `asyncpg`

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

psycopg 3 also runs async: `postgresql+psycopg://` works with `create_async_engine` as well.

## Tests in a transaction

Each test runs inside a transaction that is rolled back, so the test database stays empty:

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

## Managed PostgreSQL

| Service | What changes |
|---|---|
| [Neon](neon.md) | add `?sslmode=require`; use the pooled host for many short connections |
| Supabase | the same URL form; use the pooler port `6543` for many workers |
| Amazon RDS, Cloud SQL, Azure | add `?sslmode=require`, and allow the app's network |

## Next steps

- [Databases](../guides/databases.md)
- [Use Neon with Nexy](neon.md)
- [Use SQLite with Nexy](sqlite.md)
