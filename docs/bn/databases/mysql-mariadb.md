# Nexy এর সাথে MySQL বা MariaDB ব্যবহার করুন

Nexy-এর সাথে MySQL বা MariaDB ব্যবহার করতে, `pymysql` ড্রাইভার ইনস্টল করুন, `DATABASE_URL` একটি `mysql+pymysql://` বা `mariadb+pymysql://` URL-এ `charset=utf8mb4` সেট করুন, এবং SQLModel এর মাধ্যমে অনুসন্ধান করুন।

## স্থানীয়ভাবে MySQL বা MariaDB চালান

```bash
docker run --name nexy-mysql -e MYSQL_ROOT_PASSWORD=secret -e MYSQL_DATABASE=app -p 3306:3306 -d mysql:8.4
docker run --name nexy-mariadb -e MARIADB_ROOT_PASSWORD=secret -e MARIADB_DATABASE=app -p 3306:3306 -d mariadb:11
```

## ড্রাইভার ইনস্টল করুন

```bash
uv add pymysql
```

`pymysql` খাঁটি Python এবং অন্য কিছুর প্রয়োজন নেই। অ্যাসিঙ্ক কোডের জন্য, `aiomysql` এটি নীচে ব্যবহার করে:

```bash
uv add aiomysql
```

## সংযোগ স্ট্রিং

```bash filename=".env"
DATABASE_URL=mysql+pymysql://root:secret@localhost:3306/app?charset=utf8mb4
```

| URL | সার্ভার এবং ড্রাইভার |
|---|---|
| `mysql+pymysql://user:pass@host:3306/db?charset=utf8mb4` | মাইএসকিউএল, সিঙ্ক |
| `mariadb+pymysql://user:pass@host:3306/db?charset=utf8mb4` | MariaDB, MariaDB এর নিজস্ব SQL এর সাথে সিঙ্ক করুন |
| `mysql+aiomysql://user:pass@host:3306/db?charset=utf8mb4` | মাইএসকিউএল বা মারিয়াডিবি, অ্যাসিঙ্ক |

রাখুন `charset=utf8mb4`: MySQL-এর `utf8` অক্ষর প্রতি তিন বাইট সঞ্চয় করে এবং একটি ইমোজির প্রয়োজন চারটি।

## ইঞ্জিন

MySQL একটি সংযোগ বন্ধ করে যা `wait_timeout` সেকেন্ডের জন্য নিষ্ক্রিয় থাকে, ডিফল্টরূপে আট ঘন্টা। `pool_recycle` তার আগে সংযোগগুলি বাদ দেয় এবং `pool_pre_ping` বাকিগুলি ধরে ফেলে:

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

তাদের ছাড়া, সকালের প্রথম অনুরোধের উত্তর দেয় `MySQL server has gone away`।

## একটি মডেল: স্ট্রিং একটি দৈর্ঘ্য দিন

MySQL এর প্রতি `VARCHAR` এর একটি দৈর্ঘ্য প্রয়োজন। SQLModel লিখেন `VARCHAR(255)` একটি `str` এর জন্য যার কোনোটি নেই; যেখানে আপনি আকার জানেন সেখানে `max_length` সেট করুন এবং দীর্ঘ বিষয়বস্তুর জন্য `Text` ব্যবহার করুন:

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

একটি অনন্য বা সূচীযুক্ত `VARCHAR` অবশ্যই ইনডেক্সে ফিট হতে হবে: InnoDB এর সাথে 3072 বাইট, তাই `utf8mb4` এ 768 অক্ষর পর্যন্ত।

## অনুরোধ প্রতি একটি সেশন

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

## হ্যান্ডলার থেকে পড়ুন এবং লিখুন

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

রুট মডিউলের `controllers` কন্ট্রোলারের তালিকা করুন।
<!-- /router -->

## একটি ডুপ্লিকেট কী একটি `409`

একই স্লাগ সহ একটি দ্বিতীয় নিবন্ধ অনন্য সূচক ভেঙে দেয়। ত্রুটি ধরুন এবং একটি স্ট্যাটাস সহ উত্তর দিন:

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

রুট মডিউলের `controllers` কন্ট্রোলারের তালিকা করুন।
<!-- /router -->

## একটি পৃষ্ঠা থেকে পড়ুন

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

শুধুমাত্র ফ্রন্টম্যাটারের শীর্ষ স্তরে নির্ধারিত নামগুলি টেমপ্লেটে পৌঁছায়, তাই ক্যোয়ারীটি একটি ফাংশনে থাকে।

## আপসার্ট

মাইএসকিউএল এবং মারিয়াডিবি `INSERT ... ON DUPLICATE KEY UPDATE` হিসাবে একটি আপসার্ট লেখে:

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

## পূর্ণ-পাঠ্য অনুসন্ধান

একটি মাইগ্রেশনে একটি `FULLTEXT` সূচক যুক্ত করুন, তারপর এটি `MATCH ... AGAINST` দিয়ে জিজ্ঞাসা করুন:

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

রুট মডিউলের `controllers` কন্ট্রোলারের তালিকা করুন।
<!-- /router -->

## মাইগ্রেশন

```bash
nx migrate --init
nx migrate -m "create articles"
nx migrate --upgrade
```

MySQL প্রত্যেকটি `CREATE` এবং `ALTER` নিজের থেকে কমিট করে, তাই একটি মাইগ্রেশন যা অর্ধেকে ব্যর্থ হয় অর্ধেক প্রয়োগ করা হয়: মাইগ্রেশন ছোট রাখুন, প্রতিটি পরিবর্তন করুন।

## সাথে অ্যাসিঙ্ক করুন `aiomysql`

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

## মাইএসকিউএল বা মারিয়াডিবি: কি পার্থক্য

| | মাইএসকিউএল 8 | মারিয়াডিবি 11 |
|---|---|---|
| URL স্কিম | `mysql+pymysql://` | `mariadb+pymysql://` |
| `JSON` কলাম | নেটিভ টাইপ | একটি চেক সহ `LONGTEXT` এর একটি উপনাম |
| `RETURNING` | না | হ্যাঁ, `INSERT` এবং `DELETE` এ |
| সিকোয়েন্স | না | `CREATE SEQUENCE` |

এই পৃষ্ঠার কোড উভয়েই চলে।

## পরিচালিত MySQL

| সেবা | কি পরিবর্তন |
|---|---|
| প্ল্যানেটস্কেল | যোগ করুন `?ssl_ca=/etc/ssl/certs/ca-certificates.crt`; ডিফল্টরূপে কোন বিদেশী কী |
| Amazon RDS, Aurora, Cloud SQL, Azure | অ্যাপের নেটওয়ার্ককে অনুমতি দিন এবং TLS ব্যবহার করুন |

## পরবর্তী পদক্ষেপ

- [ডাটাবেস](../guides/databases.md)
- [Nexy এর সাথে PostgreSQL ব্যবহার করুন](postgresql.md)
- [ব্যবহার করুন SQLite নেক্সির সাথে](sqlite.md)
