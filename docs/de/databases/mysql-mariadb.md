# Verwenden Sie MySQL oder MariaDB mit Nexy

Um MySQL oder MariaDB mit Nexy zu verwenden, installieren Sie den `pymysql`-Treiber, setzen Sie `DATABASE_URL` mit `charset=utf8mb4` auf eine `mysql+pymysql://`- oder `mariadb+pymysql://`-URL und fragen Sie diese über SQLModel ab.

## Führen Sie MySQL oder MariaDB lokal aus

```bash
docker run --name nexy-mysql -e MYSQL_ROOT_PASSWORD=secret -e MYSQL_DATABASE=app -p 3306:3306 -d mysql:8.4
docker run --name nexy-mariadb -e MARIADB_ROOT_PASSWORD=secret -e MARIADB_DATABASE=app -p 3306:3306 -d mariadb:11
```

## Installieren Sie den Treiber

```bash
uv add pymysql
```

`pymysql` ist rein Python und braucht nichts anderes. Für asynchronen Code verwendet `aiomysql` ihn unten:

```bash
uv add aiomysql
```

## Die Verbindungszeichenfolge

```bash filename=".env"
DATABASE_URL=mysql+pymysql://root:secret@localhost:3306/app?charset=utf8mb4
```

| URL | Server und Treiber |
|---|---|
| `mysql+pymysql://user:pass@host:3306/db?charset=utf8mb4` | MySQL, synchronisieren |
| `mariadb+pymysql://user:pass@host:3306/db?charset=utf8mb4` | MariaDB, synchron, mit MariaDBs eigenem SQL |
| `mysql+aiomysql://user:pass@host:3306/db?charset=utf8mb4` | MySQL oder MariaDB, asynchron |

Behalten Sie `charset=utf8mb4`: MySQLs `utf8` speichert drei Bytes pro Zeichen, und ein Emoji benötigt vier.

## Der Motor

MySQL schließt eine Verbindung, die `wait_timeout` Sekunden lang inaktiv war, standardmäßig acht Stunden. `pool_recycle` löscht vorher Verbindungen und `pool_pre_ping` fängt den Rest ab:

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

Ohne sie wird die erste Anfrage des Morgens beantwortet `MySQL server has gone away`.

## Ein Modell: Geben Sie Strings eine Länge

MySQL benötigt eine Länge für jedes `VARCHAR`. SQLModel schreibt `VARCHAR(255)` für ein `str` ohne; Legen Sie `max_length` fest, wobei Sie die Größe kennen, und verwenden Sie `Text` für lange Inhalte:

```python filename="src/models/article_model.py"
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

Ein eindeutiges oder indiziertes `VARCHAR` muss in den Index passen: 3072 Bytes mit InnoDB, also bis zu 768 Zeichen in `utf8mb4`.

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

<!-- router:fbr,custom -->
```python filename="src/routes/api/articles/index.py"
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

Listen Sie den Controller im `controllers` des Root-Moduls auf.
<!-- /router -->

## Ein Nachschlüssel ist ein `409`

Ein zweiter Artikel mit demselben Slug zerstört den eindeutigen Index. Fangen Sie den Fehler ab und antworten Sie mit einem Status:

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

Listen Sie den Controller im `controllers` des Root-Moduls auf.
<!-- /router -->

## Von einer Seite lesen

```python filename="src/services/articles.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.article_model import Article


def latest_articles() -> list[Article]:
    with Session(engine) as session:
        return list(session.exec(select(Article).order_by(Article.id.desc()).limit(5)))
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/articles.nexy"
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

Nur die auf der obersten Ebene des Frontmatters zugewiesenen Namen erreichen die Vorlage, sodass die Abfrage in einer Funktion gespeichert ist.

## Upserts

MySQL und MariaDB schreiben einen Upsert als `INSERT ... ON DUPLICATE KEY UPDATE`:

```python filename="src/services/counters.py"
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

## Volltextsuche

Fügen Sie einen `FULLTEXT`-Index in einer Migration hinzu und fragen Sie ihn dann mit `MATCH ... AGAINST` ab:

```python filename="alembic/versions/xxxx_article_search.py"
def upgrade() -> None:
    op.execute("CREATE FULLTEXT INDEX article_search ON article (title, body)")
```

<!-- router:fbr,custom -->
```python filename="src/routes/api/search.py"
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

Listen Sie den Controller im `controllers` des Root-Moduls auf.
<!-- /router -->

## Migrationen

```bash
nx migrate --init
nx migrate -m "create articles"
nx migrate --upgrade
```

MySQL schreibt jeweils `CREATE` und `ALTER` einzeln fest, so dass eine Migration, die zur Hälfte fehlschlägt, zur Hälfte durchgeführt bleibt: Halten Sie die Migrationen klein, jeweils eine Änderung.

## Asynchron mit `aiomysql`

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

## MySQL oder MariaDB: Was ist der Unterschied?

| | MySQL 8 | MariaDB 11 |
|---|---|---|
| URL-Schema | `mysql+pymysql://` | `mariadb+pymysql://` |
| `JSON` Spalte | nativer Typ | ein Alias von `LONGTEXT` mit einem Häkchen |
| `RETURNING` | Nein | ja, am `INSERT` und `DELETE` |
| Sequenzen | Nein | `CREATE SEQUENCE` |

Der Code dieser Seite läuft auf beiden.

## Verwaltetes MySQL

| Service | Was ändert sich |
|---|---|
| PlanetScale | füge `?ssl_ca=/etc/ssl/certs/ca-certificates.crt` hinzu; standardmäßig keine Fremdschlüssel |
| Amazon RDS, Aurora, Cloud SQL, Azure | Erlauben Sie das Netzwerk der App und verwenden Sie TLS |

## Nächste Schritte

- [Datenbanken](../guides/databases.md)
- [Verwenden Sie PostgreSQL mit Nexy](postgresql.md)
- [Verwenden Sie SQLite mit Nexy](sqlite.md)
