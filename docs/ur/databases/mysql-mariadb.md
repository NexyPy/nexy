# Nexy کے ساتھ MySQL یا MariaDB استعمال کریں۔

Nexy کے ساتھ MySQL یا MariaDB استعمال کرنے کے لیے، `pymysql` ڈرائیور انسٹال کریں، `DATABASE_URL` کو `mysql+pymysql://` یا `mariadb+pymysql://` URL پر `charset=utf8mb4` کے ساتھ سیٹ کریں، اور SQLModel کے ذریعے اس سے استفسار کریں۔

## مقامی طور پر MySQL یا MariaDB چلائیں۔

```bash
docker run --name nexy-mysql -e MYSQL_ROOT_PASSWORD=secret -e MYSQL_DATABASE=app -p 3306:3306 -d mysql:8.4
docker run --name nexy-mariadb -e MARIADB_ROOT_PASSWORD=secret -e MARIADB_DATABASE=app -p 3306:3306 -d mariadb:11
```

## ڈرائیور انسٹال کریں۔

```bash
uv add pymysql
```

`pymysql` خالص ہے Python اور کسی اور چیز کی ضرورت نہیں۔ async کوڈ کے لیے، `aiomysql` اسے نیچے استعمال کرتا ہے:

```bash
uv add aiomysql
```

## کنکشن کی تار

```bash filename="env"
DATABASE_URL=mysql+pymysql://root:secret@localhost:3306/app?charset=utf8mb4
```

| URL | سرور اور ڈرائیور |
|---|---|
| `mysql+pymysql://user:pass@host:3306/db?charset=utf8mb4` | MySQL، مطابقت پذیری |
| `mariadb+pymysql://user:pass@host:3306/db?charset=utf8mb4` | ماریا ڈی بی، ماریا ڈی بی کے اپنے ایس کیو ایل کے ساتھ مطابقت پذیری کریں۔ |
| `mysql+aiomysql://user:pass@host:3306/db?charset=utf8mb4` | MySQL یا MariaDB، async |

رکھیں `charset=utf8mb4`: MySQL کا `utf8` تین بائٹس فی کریکٹر اسٹور کرتا ہے، اور ایک ایموجی کو چار کی ضرورت ہوتی ہے۔

## انجن

MySQL ایک ایسا کنکشن بند کر دیتا ہے جو پہلے سے طے شدہ طور پر آٹھ گھنٹے `wait_timeout` سیکنڈ تک بیکار رہا۔ `pool_recycle` اس سے پہلے کنکشن چھوڑ دیتا ہے، اور `pool_pre_ping` باقی کو پکڑتا ہے:

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

ان کے بغیر صبح کی پہلی فرمائش جواب دیتی ہے۔ `MySQL server has gone away`۔

## ایک ماڈل: تاروں کو لمبائی دیں۔

MySQL کو ہر `VARCHAR` پر لمبائی کی ضرورت ہے۔ SQLModel لکھتے ہیں `VARCHAR(255)` ایک `str` کے ساتھ کوئی نہیں؛ سیٹ کریں `max_length` جہاں آپ کو سائز معلوم ہے، اور طویل مواد کے لیے `Text` کا استعمال کریں:

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

ایک منفرد یا انڈیکس شدہ `VARCHAR` انڈیکس میں فٹ ہونا ضروری ہے: InnoDB کے ساتھ 3072 بائٹس، لہذا `utf8mb4` میں 768 حروف تک۔

## فی درخواست ایک سیشن

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

## ہینڈلر سے پڑھیں اور لکھیں۔

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

## ڈپلیکیٹ کلید ایک `409` ہے

اسی سلگ کے ساتھ دوسرا مضمون منفرد انڈیکس کو توڑ دیتا ہے۔ غلطی کو پکڑیں اور اسٹیٹس کے ساتھ جواب دیں:

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

## ایک صفحے سے پڑھیں

```python filename="src/services/articles.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.article_model import Article


def latest_articles() -> list[Article]:
    with Session(engine) as session:
        return list(session.exec(select(Article).order_by(Article.id.desc()).limit(5)))
```

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

صرف فرنٹ میٹر کے اوپری سطح پر تفویض کردہ نام ٹیمپلیٹ تک پہنچتے ہیں، لہذا استفسار ایک فنکشن میں رہتا ہے۔

## اپسرٹس

مائی ایس کیو ایل اور ماریا ڈی بی ایک اوپرٹ لکھتے ہیں بطور `INSERT ... ON DUPLICATE KEY UPDATE`:

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

## مکمل متن کی تلاش

منتقلی میں ایک `FULLTEXT` انڈیکس شامل کریں، پھر `MATCH ... AGAINST` کے ساتھ استفسار کریں:

```python filename="alembic/versions/xxxx_article_search.py"
def upgrade() -> None:
    op.execute("CREATE FULLTEXT INDEX article_search ON article (title, body)")
```

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

## ہجرتیں

```bash
nx migrate --init
nx migrate -m "create articles"
nx migrate --upgrade
```

MySQL ہر ایک `CREATE` اور `ALTER` کو اپنے طور پر کرتا ہے، اس لیے جو ہجرت آدھے راستے میں ناکام ہو جاتی ہے وہ آدھی لاگو رہتی ہے: ہجرت کو چھوٹا رکھیں، ہر ایک کو تبدیل کریں۔

## `aiomysql` کے ساتھ مطابقت پذیری

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

## MySQL یا MariaDB: کیا فرق ہے۔

| | MySQL 8 | ماریا ڈی بی 11 |
|---|---|---|
| یو آر ایل اسکیم | `mysql+pymysql://` | `mariadb+pymysql://` |
| `JSON` کالم | مقامی قسم | ایک چیک کے ساتھ `LONGTEXT` کا عرف |
| `RETURNING` | نہیں | ہاں، `INSERT` اور `DELETE` پر |
| سلسلے | نہیں | `CREATE SEQUENCE` |

اس صفحہ کا کوڈ دونوں پر چلتا ہے۔

## MySQL کا نظم کیا گیا۔

| سروس | کیا تبدیلیاں |
|---|---|
| پلانیٹ اسکیل | شامل کریں `?ssl_ca=/etc/ssl/certs/ca-certificates.crt`؛ پہلے سے طے شدہ طور پر کوئی غیر ملکی چابیاں نہیں۔ |
| Amazon RDS، Aurora، Cloud SQL، Azure | ایپ کے نیٹ ورک کو اجازت دیں، اور TLS استعمال کریں۔ |

## اگلے اقدامات

- [ڈیٹا بیس](../guides/databases.md)
- [Nexy کے ساتھ PostgreSQL استعمال کریں](postgresql.md)
- [Nexy کے ساتھ SQLite استعمال کریں](sqlite.md)
