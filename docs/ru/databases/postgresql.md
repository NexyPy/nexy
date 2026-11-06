# Используйте PostgreSQL с Nexy

Чтобы использовать PostgreSQL с Nexy, установите драйвер `psycopg`, установите для `DATABASE_URL` URL-адрес `postgresql+psycopg://` и запросите его из обработчиков и страниц через SQLModel или SQLAlchemy.

## Запустите PostgreSQL локально

```bash
docker run --name nexy-db -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=app -p 5432:5432 -d postgres:17
```

## Установите драйвер

```bash
uv add "psycopg[binary]"
```

`psycopg` — это версия 3 драйвера для синхронного и асинхронного кода. Для асинхронного кода другим выбором является `asyncpg`:

```bash
uv add asyncpg
```

## Строка подключения

```bash filename=".env"
DATABASE_URL=postgresql+psycopg://postgres:secret@localhost:5432/app
```

| URL-адрес | Водитель |
|---|---|
| `postgresql+psycopg://user:pass@host:5432/db` | psycopg 3, синхронизация и асинхронность |
| `postgresql+asyncpg://user:pass@host:5432/db` | asyncpg, только асинхронный |
| `postgresql://user:pass@host:5432/db` | psycopg2, если он установлен |
| `postgres://...` | отклонено SQLAlchemy: переименуйте схему в `postgresql+psycopg://` |

Пароль с `@`, `:` или `/` в URL-адресе закодирован в процентах: `p@ss` — это `p%40ss`.

## Двигатель

Хостинговые платформы часто предоставляют URL-адрес `postgres://`. Конвертируйте его там, где сделан двигатель:

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

| Вариант с бассейном | Что он делает |
|---|---|
| `pool_size=5` | соединения остаются открытыми для каждого процесса |
| `max_overflow=10` | дополнительные соединения разрешены под нагрузкой, закрываются после |
| `pool_pre_ping=True` | проверяет соединение перед использованием, поэтому перезапуск базы данных не является ошибкой |

У каждого рабочего `nx start` есть свой собственный пул: `workers × (pool_size + max_overflow)` должен оставаться под `max_connections` сервера.

## Модель с типами PostgreSQL

Ключи `uuid`, `JSONB`, массивы и `timestamptz` — это собственные типы столбцов:

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

## Сеанс по запросу

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

## Чтение и запись из обработчика

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

`Post.tags.contains([tag])` — это PostgreSQL's `@>`: сообщения, теги которых содержат `tag`.

## `uuid` в URL-адресе

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

Сегмент, который не является UUID, отвечает на `404` до выполнения запроса.

## Запрос `JSONB`

```python filename="src/services/posts.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.post_model import Post


def featured_posts() -> list[Post]:
    with Session(engine) as session:
        query = select(Post).where(Post.extra["featured"].as_boolean())
        return list(session.exec(query))
```

```nexy filename="src/маршруты/featured.nexy"
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

Сохраняйте запрос в функции: в шаблон попадают только имена, назначенные на верхнем уровне заголовка.

## Полнотекстовый поиск

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

Индекс позволяет быстро работать с большой таблицей. Добавьте его в миграцию:

```python filename="перегонный куб/версии/xxxx_search_index.py"
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

## Миграции

```bash
nx migrate --init
nx migrate -m "create posts"
nx migrate --upgrade
```

`nx migrate` читает `DATABASE_URL`, проверяет, установлен ли драйвер и отвечает ли сервер, затем запускает Alembic. Импортируйте каждый модуль модели в `alembic/env.py`, чтобы автогенерация его увидела.

## Асинхронно с `asyncpg`

```python filename="src/configs/async_db.py"
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from src.configs.db import database_url

async_engine = create_async_engine(
    database_url().replace("+psycopg", "+asyncpg", 1), pool_pre_ping=True
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

psycopg 3 также работает асинхронно: `postgresql+psycopg://` также работает с `create_async_engine`.

## Тесты в транзакции

Каждый тест выполняется внутри транзакции, которая откатывается, поэтому тестовая база данных остается пустой:

```python filename="тесты/conftest.py"
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

## Управляемый PostgreSQL

| Сервис | Что меняется |
|---|---|
| [Неон](neon.md) | добавить `?sslmode=require`; используйте объединенный хост для множества коротких соединений |
| Супабаза | та же форма URL; используйте порт пулера `6543` для многих воркеров |
| Amazon RDS, Cloud SQL, Azure | добавьте `?sslmode=require` и разрешите сеть приложения |

## Следующие шаги

- [Базы данных](../guides/databases.md)
- [Используйте Neon с Nexy](neon.md)
- [Используйте SQLite с Nexy](sqlite.md)
