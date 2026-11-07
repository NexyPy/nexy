# Используйте MySQL или MariaDB с Nexy

Чтобы использовать MySQL или MariaDB с Nexy, установите драйвер `pymysql`, установите для `DATABASE_URL` URL-адрес `mysql+pymysql://` или `mariadb+pymysql://` с помощью `charset=utf8mb4` и выполните запрос через SQLModel.

## Запустите MySQL или MariaDB локально

```bash
docker run --name nexy-mysql -e MYSQL_ROOT_PASSWORD=secret -e MYSQL_DATABASE=app -p 3306:3306 -d mysql:8.4
docker run --name nexy-mariadb -e MARIADB_ROOT_PASSWORD=secret -e MARIADB_DATABASE=app -p 3306:3306 -d mariadb:11
```

## Установите драйвер

```bash
uv add pymysql
```

`pymysql` является чистым Python и больше ничего не требует. Для асинхронного кода `aiomysql` использует его ниже:

```bash
uv add aiomysql
```

## Строка подключения

```bash filename=".env"
DATABASE_URL=mysql+pymysql://root:secret@localhost:3306/app?charset=utf8mb4
```

| URL-адрес | Сервер и драйвер |
|---|---|
| `mysql+pymysql://user:pass@host:3306/db?charset=utf8mb4` | MySQL, синхронизация |
| `mariadb+pymysql://user:pass@host:3306/db?charset=utf8mb4` | MariaDB, синхронизация с собственным SQL MariaDB. |
| `mysql+aiomysql://user:pass@host:3306/db?charset=utf8mb4` | MySQL или MariaDB, асинхронный |

Сохраняйте `charset=utf8mb4`: MySQL `utf8` хранит три байта на символ, а для эмодзи требуется четыре.

## Двигатель

MySQL закрывает соединение, которое оставалось бездействующим в течение `wait_timeout` секунд (по умолчанию восемь часов). Перед этим `pool_recycle` отбрасывает соединения, а `pool_pre_ping` ловит остальные:

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

Без них на первый утренний запрос отвечает `MySQL server has gone away`.

## Модель: присвойте строкам длину

MySQL нуждается в длине каждого `VARCHAR`. SQLModel записывает `VARCHAR(255)` для `str` без нуля; установите `max_length` там, где вы знаете размер, и используйте `Text` для длинного контента:

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

Уникальный или индексированный `VARCHAR` должен соответствовать индексу: 3072 байта для InnoDB, то есть до 768 символов в `utf8mb4`.

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

Перечислите контроллер в `controllers` корневого модуля.
<!-- /router -->

## Дубликат ключа — это `409`

Вторая статья с таким же ярлыком нарушает уникальный индекс. Отловите ошибку и ответьте со статусом:

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

Перечислите контроллер в `controllers` корневого модуля.
<!-- /router -->

## Читать со страницы

```python filename="src/services/articles.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.article_model import Article


def latest_articles() -> list[Article]:
    with Session(engine) as session:
        return list(session.exec(select(Article).order_by(Article.id.desc()).limit(5)))
```

<!-- router:fbr,custom -->
```nexy filename="src/маршруты/articles.nexy"
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

В шаблон попадают только имена, назначенные на верхнем уровне заголовка, поэтому запрос находится в функции.

## Upserts

MySQL и MariaDB записывают обновление как `INSERT ... ON DUPLICATE KEY UPDATE`:

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

## Полнотекстовый поиск

Добавьте индекс `FULLTEXT` в миграцию, а затем запросите его с помощью `MATCH ... AGAINST`:

```python filename="перегонный куб/версии/xxxx_article_search.py"
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

Перечислите контроллер в `controllers` корневого модуля.
<!-- /router -->

## Миграции

```bash
nx migrate --init
nx migrate -m "create articles"
nx migrate --upgrade
```

MySQL фиксирует каждый `CREATE` и `ALTER` отдельно, поэтому миграция, которая терпит неудачу на полпути, остается наполовину примененной: сохраняйте небольшие миграции, по одному изменению в каждой.

## Асинхронно с `aiomysql`

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

## MySQL или MariaDB: что отличается

| | MySQL 8 | МарияДБ 11 |
|---|---|---|
| Схема URL | `mysql+pymysql://` | `mariadb+pymysql://` |
| `JSON` столбец | родной тип | псевдоним `LONGTEXT` с проверкой |
| `RETURNING` | нет | да, на `INSERT` и `DELETE` |
| Последовательности | нет | `CREATE SEQUENCE` |

Код этой страницы работает на обоих.

## Управляемый MySQL

| Сервис | Что меняется |
|---|---|
| PlanetScale | добавить `?ssl_ca=/etc/ssl/certs/ca-certificates.crt`; по умолчанию нет внешних ключей |
| Amazon RDS, Aurora, Cloud SQL, Azure | разрешить сеть приложения и использовать TLS |

## Следующие шаги

- [Базы данных](../guides/databases.md)
- [Используйте PostgreSQL с Nexy](postgresql.md)
- [Используйте SQLite с Nexy](sqlite.md)
