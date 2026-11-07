# Utilice MySQL o MariaDB con Nexy

Para usar MySQL o MariaDB con Nexy, instale el controlador `pymysql`, configure `DATABASE_URL` en una URL `mysql+pymysql://` o `mariadb+pymysql://` con `charset=utf8mb4` y consúltelo a través de SQLModel.

## Ejecute MySQL o MariaDB localmente

```bash
docker run --name nexy-mysql -e MYSQL_ROOT_PASSWORD=secret -e MYSQL_DATABASE=app -p 3306:3306 -d mysql:8.4
docker run --name nexy-mariadb -e MARIADB_ROOT_PASSWORD=secret -e MARIADB_DATABASE=app -p 3306:3306 -d mariadb:11
```

## Instale el controlador

```bash
uv add pymysql
```

`pymysql` es puro Python y no necesita nada más. Para código asíncrono, `aiomysql` lo usa debajo:

```bash
uv add aiomysql
```

## La cadena de conexión

```bash filename=".env"
DATABASE_URL=mysql+pymysql://root:secret@localhost:3306/app?charset=utf8mb4
```

| URL | Servidor y controlador |
|---|---|
| `mysql+pymysql://user:pass@host:3306/db?charset=utf8mb4` | MySQL, sincronización |
| `mariadb+pymysql://user:pass@host:3306/db?charset=utf8mb4` | MariaDB, sincronización, con el propio SQL de MariaDB |
| `mysql+aiomysql://user:pass@host:3306/db?charset=utf8mb4` | MySQL o MariaDB, asíncrono |

Mantenga `charset=utf8mb4`: `utf8` de MySQL almacena tres bytes por carácter y un emoji necesita cuatro.

## el motor

MySQL cierra una conexión que permaneció inactiva durante `wait_timeout` segundos, ocho horas de forma predeterminada. `pool_recycle` descarta las conexiones antes de eso y `pool_pre_ping` captura el resto:

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(
    os.environ["DATABASE_URL"],
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True,
)
```

Sin ellos, responde la primera petición de la mañana `MySQL server has gone away`.

## Un modelo: dar longitud a las cuerdas

MySQL necesita una longitud en cada `VARCHAR`. SQLModel escribe `VARCHAR(255)` para un `str` sin ninguno; configure `max_length` donde conozca el tamaño y use `Text` para contenido largo:

```python filename="src/modelos/article_model.py"
from datetime import datetime

from sqlalchemy import Column, DateTime, Text, func
from sqlmodel import Field, SQLModel


class Article(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(max_length=120, unique=True)
    title: str = Field(max_length=200)
    body: str = Field(sa_column=Column(Text))
    created_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime, server_default=func.now())
    )
```

Un `VARCHAR` único o indexado debe caber en el índice: 3072 bytes con InnoDB, por lo que hasta 768 caracteres en `utf8mb4`.

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
```python filename="src/rutas/api/articles/index.py"
from pydantic import BaseModel
from sqlmodel import Session, select

from nexy.http import Depends, JSONResponse
from src.configs.session import get_session
from src.models.article_model import Article


class NewArticle(BaseModel):
    slug: str
    title: str
    body: str


async def GET(session: Session = Depends(get_session)):
    return session.exec(select(Article).order_by(Article.id.desc()).limit(20)).all()


async def POST(body: NewArticle, session: Session = Depends(get_session)):
    article = Article(**body.model_dump())
    session.add(article)
    session.commit()
    session.refresh(article)
    return JSONResponse(article.model_dump(mode="json"), status_code=201)
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/articles/articles_api_controller.py"
from pydantic import BaseModel
from sqlmodel import Session, select

from nexy.decorators import Controller
from nexy.http import Depends, JSONResponse
from src.configs.session import get_session
from src.models.article_model import Article


class NewArticle(BaseModel):
    slug: str
    title: str
    body: str


@Controller("/api/articles")
class ArticlesApiController:
    async def get(self, session: Session = Depends(get_session)):
        return session.exec(select(Article).order_by(Article.id.desc()).limit(20)).all()

    async def post(self, body: NewArticle, session: Session = Depends(get_session)):
        article = Article(**body.model_dump())
        session.add(article)
        session.commit()
        session.refresh(article)
        return JSONResponse(article.model_dump(mode="json"), status_code=201)
```

Enumere el controlador en el `controllers` del módulo raíz.
<!-- /router -->

## Una clave duplicada es una `409`

Un segundo artículo con el mismo fragmento rompe el índice único. Capte el error y responda con un estado:

<!-- router:fbr,custom -->
```python filename="src/routes/api/articles/[slug].py"
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from nexy.http import Depends, HTTPException
from src.configs.session import get_session
from src.models.article_model import Article


class Rename(BaseModel):
    slug: str


async def PATCH(slug: str, body: Rename, session: Session = Depends(get_session)):
    article = session.exec(select(Article).where(Article.slug == slug)).first()
    if article is None:
        raise HTTPException(status_code=404, detail="No such article")
    article.slug = body.slug
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Slug already taken")
    return article
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/articles/articles_by_slug_api_controller.py"
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from nexy.decorators import Controller
from nexy.http import Depends, HTTPException
from src.configs.session import get_session
from src.models.article_model import Article


class Rename(BaseModel):
    slug: str


@Controller("/api/articles/{slug}")
class ArticlesBySlugApiController:
    async def patch(self, slug: str, body: Rename, session: Session = Depends(get_session)):
        article = session.exec(select(Article).where(Article.slug == slug)).first()
        if article is None:
            raise HTTPException(status_code=404, detail="No such article")
        article.slug = body.slug
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=409, detail="Slug already taken")
        return article
```

Enumere el controlador en el `controllers` del módulo raíz.
<!-- /router -->

## Leer de una página

```python filename="src/servicios/artículos.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.article_model import Article


def latest_articles() -> list[Article]:
    with Session(engine) as session:
        return list(session.exec(select(Article).order_by(Article.id.desc()).limit(5)))
```

<!-- router:fbr,custom -->
```nexy filename="src/rutas/artículos.nexy"
---
from src.services.articles import latest_articles

articles = latest_articles()
---
<ul>
  {% for article in articles %}
  <li><a href="/articles/{{ article.slug | e }}">{{ article.title | e }}</a></li>
  {% endfor %}
</ul>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/articles/articles_view.nexy"
---
from src.services.articles import latest_articles

articles = latest_articles()
---
<ul>
  {% for article in articles %}
  <li><a href="/articles/{{ article.slug | e }}">{{ article.title | e }}</a></li>
  {% endfor %}
</ul>
```

```python filename="src/apps/articles/articles_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/articles")
class ArticlesController:
    async def get(self):
        return useViews("src/apps/articles/articles_view.nexy")
```
<!-- /router -->

Solo los nombres asignados en el nivel superior del frontmatter llegan a la plantilla, por lo que la consulta reside en una función.

## Upserts

MySQL y MariaDB escriben un upsert como `INSERT ... ON DUPLICATE KEY UPDATE`:

```python filename="src/servicios/contadores.py"
from sqlalchemy.dialects.mysql import insert
from sqlmodel import Field, Session, SQLModel

from src.configs.db import engine


class PageView(SQLModel, table=True):
    path: str = Field(primary_key=True, max_length=255)
    views: int = 0


def count_view(path: str) -> None:
    statement = insert(PageView).values(path=path, views=1)
    statement = statement.on_duplicate_key_update(views=PageView.views + 1)
    with Session(engine) as session:
        session.exec(statement)
        session.commit()
```

## Búsqueda de texto completo

Agregue un índice `FULLTEXT` en una migración, luego consúltelo con `MATCH ... AGAINST`:

```python filename="alambique/versions/xxxx_article_search.py"
def upgrade() -> None:
    op.execute("CREATE FULLTEXT INDEX article_search ON article (title, body)")
```

<!-- router:fbr,custom -->
```python filename="src/rutas/api/search.py"
from sqlalchemy import text
from sqlmodel import Session, select

from nexy.http import Depends
from src.configs.session import get_session
from src.models.article_model import Article


async def GET(q: str, session: Session = Depends(get_session)):
    match = text("MATCH (title, body) AGAINST (:q IN NATURAL LANGUAGE MODE)")
    return session.exec(select(Article).where(match.bindparams(q=q))).all()
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/search/search_api_controller.py"
from sqlalchemy import text
from sqlmodel import Session, select

from nexy.decorators import Controller
from nexy.http import Depends
from src.configs.session import get_session
from src.models.article_model import Article


@Controller("/api/search")
class SearchApiController:
    async def get(self, q: str, session: Session = Depends(get_session)):
        match = text("MATCH (title, body) AGAINST (:q IN NATURAL LANGUAGE MODE)")
        return session.exec(select(Article).where(match.bindparams(q=q))).all()
```

Enumere el controlador en el `controllers` del módulo raíz.
<!-- /router -->

## Migraciones

```bash
nx migrate --init
nx migrate -m "create articles"
nx migrate --upgrade
```

MySQL confirma cada `CREATE` y `ALTER` por sí solo, por lo que una migración que falla a mitad de camino permanece aplicada a medias: mantenga las migraciones pequeñas, un cambio cada una.

## Asíncrono con `aiomysql`

```python filename="src/configs/async_db.py"
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

load_dotenv()

async_engine = create_async_engine(
    os.environ["DATABASE_URL"].replace("+pymysql", "+aiomysql", 1), pool_recycle=3600
)


async def get_async_session():
    async with AsyncSession(async_engine) as session:
        yield session
```

## MySQL o MariaDB: en qué se diferencia

| | mysql 8 | MaríaDB 11 |
|---|---|---|
| esquema de URL | `mysql+pymysql://` | `mariadb+pymysql://` |
| `JSON` columna | tipo nativo | un alias de `LONGTEXT` con un cheque |
| `RETURNING` | no | sí, en `INSERT` y `DELETE` |
| Secuencias | no | `CREATE SEQUENCE` |

El código de esta página se ejecuta en ambos.

## MySQL administrado

| Servicio | que cambia |
|---|---|
| Escala planetaria | añadir `?ssl_ca=/etc/ssl/certs/ca-certificates.crt`; sin claves foráneas por defecto |
| Amazon RDS, Aurora, Cloud SQL, Azure | permitir la red de la aplicación y usar TLS |

## Próximos pasos

- [Bases de datos](../guides/databases.md)
- [Utilice PostgreSQL con Nexy](postgresql.md)
- [Utilice SQLite con Nexy](sqlite.md)
