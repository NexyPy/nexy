# Utilice PostgreSQL con Nexy

Para usar PostgreSQL con Nexy, instale el controlador `psycopg`, configure `DATABASE_URL` en una URL `postgresql+psycopg://` y consúltelo desde los controladores y páginas hasta SQLModel o SQLAlchemy.

## Ejecute PostgreSQL localmente

```bash
docker run --name nexy-db -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=app -p 5432:5432 -d postgres:17
```

## Instale el controlador

```bash
uv add "psycopg[binary]"
```

`psycopg` es la versión 3 del controlador, para código de sincronización y asíncrono. Para código solo asíncrono, `asyncpg` es la otra opción:

```bash
uv add asyncpg
```

## La cadena de conexión

```bash filename=".env"
DATABASE_URL=postgresql+psycopg://postgres:secret@localhost:5432/app
```

| URL | Conductor |
|---|---|
| `postgresql+psycopg://user:pass@host:5432/db` | psycopg 3, sincronización y asíncrono |
| `postgresql+asyncpg://user:pass@host:5432/db` | asyncpg, solo asíncrono |
| `postgresql://user:pass@host:5432/db` | psycopg2, si está instalado |
| `postgres://...` | rechazado por SQLAlchemy: cambie el nombre del esquema a `postgresql+psycopg://` |

Una contraseña con `@`, `:` o `/` está codificada en porcentaje en la URL: `p@ss` es `p%40ss`.

## el motor

Las plataformas de alojamiento suelen proporcionar una URL `postgres://`. Conviértalo donde se fabrica el motor:

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

| Opción piscina | que hace |
|---|---|
| `pool_size=5` | conexiones mantenidas abiertas por proceso |
| `max_overflow=10` | conexiones adicionales permitidas bajo carga, cerradas después |
| `pool_pre_ping=True` | comprueba una conexión antes de su uso, por lo que una base de datos reiniciada no es un error |

Cada `nx start` trabajador tiene su propio grupo: `workers × (pool_size + max_overflow)` debe permanecer debajo del `max_connections` del servidor.

## Un modelo con PostgreSQL tipos

`uuid` claves, `JSONB`, matrices y `timestamptz` son tipos de columnas nativas:

```python filename="src/modelos/post_model.py"
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

## Una sesión por solicitud

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
```python filename="src/rutas/api/posts/index.py"
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
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/posts/posts_api_controller.py"
from pydantic import BaseModel
from sqlmodel import Session, select

from nexy.decorators import Controller
from nexy.http import Depends, JSONResponse
from src.configs.session import get_session
from src.models.post_model import Post


class NewPost(BaseModel):
    title: str
    tags: list[str] = []


@Controller("/api/posts")
class PostsApiController:
    async def get(self, tag: str | None = None, session: Session = Depends(get_session)):
        query = select(Post).order_by(Post.published_at.desc())
        if tag:
            query = query.where(Post.tags.contains([tag]))
        return session.exec(query).all()

    async def post(self, body: NewPost, session: Session = Depends(get_session)):
        post = Post(title=body.title, tags=body.tags)
        session.add(post)
        session.commit()
        session.refresh(post)
        return JSONResponse(post.model_dump(mode="json"), status_code=201)
```

Enumere el controlador en el `controllers` del módulo raíz.
<!-- /router -->

`Post.tags.contains([tag])` es el `@>` de PostgreSQL: las publicaciones cuyas etiquetas contienen `tag`.

## Un `uuid` en la URL

<!-- router:fbr,custom -->
```python filename="src/rutas/api/posts/[id].py"
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
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/posts/posts_by_id_api_controller.py"
import uuid

from sqlmodel import Session

from nexy.decorators import Controller
from nexy.http import Depends, HTTPException
from src.configs.session import get_session
from src.models.post_model import Post


@Controller("/api/posts/{id}")
class PostsByIdApiController:
    async def get(self, id: uuid.UUID, session: Session = Depends(get_session)):
        post = session.get(Post, id)
        if post is None:
            raise HTTPException(status_code=404, detail="No such post")
        return post
```

Enumere el controlador en el `controllers` del módulo raíz.
<!-- /router -->

Un segmento que no es un UUID responde `404` antes de que se ejecute la consulta.

## Consulta `JSONB`

```python filename="src/servicios/posts.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.post_model import Post


def featured_posts() -> list[Post]:
    with Session(engine) as session:
        query = select(Post).where(Post.extra["featured"].as_boolean())
        return list(session.exec(query))
```

<!-- router:fbr,custom -->
```nexy filename="src/rutas/featured.nexy"
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
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/featured/featured_view.nexy"
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

```python filename="src/apps/featured/featured_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/featured")
class FeaturedController:
    async def get(self):
        return useViews("src/apps/featured/featured_view.nexy")
```
<!-- /router -->

Mantener la consulta en una función: solo los nombres asignados en el nivel superior del frontmatter llegan a la plantilla.

## Búsqueda de texto completo

<!-- router:fbr,custom -->
```python filename="src/rutas/api/search.py"
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
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/search/search_api_controller.py"
from sqlalchemy import func
from sqlmodel import Session, select

from nexy.decorators import Controller
from nexy.http import Depends
from src.configs.session import get_session
from src.models.post_model import Post


@Controller("/api/search")
class SearchApiController:
    async def get(self, q: str, session: Session = Depends(get_session)):
        document = func.to_tsvector("english", Post.title)
        query = func.websearch_to_tsquery("english", q)
        rank = func.ts_rank(document, query)
        rows = session.exec(select(Post).where(document.op("@@")(query)).order_by(rank.desc()))
        return rows.all()
```

Enumere el controlador en el `controllers` del módulo raíz.
<!-- /router -->

Un índice lo mantiene rápido en una mesa grande. Agréguelo en una migración:

```python filename="alambique/versions/xxxx_search_index.py"
def upgrade() -> None:
    op.execute(
        "CREATE INDEX post_title_search ON post USING GIN (to_tsvector('english', title))"
    )
```

## Upserts

```python filename="src/servicios/etiquetas.py"
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

## Migraciones

```bash
nx migrate --init
nx migrate -m "create posts"
nx migrate --upgrade
```

`nx migrate` lee `DATABASE_URL`, verifica que el controlador esté instalado y que el servidor responda, luego ejecuta Alembic. Importe cada módulo de modelo en `alembic/env.py` para que la generación automática lo vea.

## Asíncrono con `asyncpg`

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

<!-- router:fbr,custom -->
```python filename="src/rutas/api/posts/count.py"
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from nexy.http import Depends
from src.configs.async_db import get_async_session
from src.models.post_model import Post


async def GET(session: AsyncSession = Depends(get_async_session)):
    count = (await session.exec(select(func.count()).select_from(Post))).one()
    return {"count": count}
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/posts/posts_count_api_controller.py"
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from nexy.decorators import Controller
from nexy.http import Depends
from src.configs.async_db import get_async_session
from src.models.post_model import Post


@Controller("/api/posts/count")
class PostsCountApiController:
    async def get(self, session: AsyncSession = Depends(get_async_session)):
        count = (await session.exec(select(func.count()).select_from(Post))).one()
        return {"count": count}
```

Enumere el controlador en el `controllers` del módulo raíz, antes de `PostsByIdApiController`: el primer controlador cuya ruta coincide con las respuestas, y en la lista después de él, `/api/posts/count/` responde a `404`.
<!-- /router -->

psycopg 3 también se ejecuta asíncrono: `postgresql+psycopg://` también funciona con `create_async_engine`.

## Pruebas en una transacción

Cada prueba se ejecuta dentro de una transacción que se revierte, por lo que la base de datos de prueba permanece vacía:

```python filename="pruebas/conftest.py"
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

## Gestionado PostgreSQL

| Servicio | que cambia |
|---|---|
| [Neón](neon.md) | agregar `?sslmode=require`; use el host agrupado para muchas conexiones cortas |
| Supabase | el mismo formulario de URL; utilizar el puerto pooler `6543` para muchos trabajadores |
| Amazon RDS, Nube SQL, Azure | agregue `?sslmode=require` y permita la red de la aplicación |

## Próximos pasos

- [Bases de datos](../guides/databases.md)
- [Usa Neón con Nexy](neon.md)
- [Utilice SQLite con Nexy](sqlite.md)
