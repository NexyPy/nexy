# Nexy کے ساتھ PostgreSQL استعمال کریں۔

Nexy کے ساتھ PostgreSQL کو استعمال کرنے کے لیے، `psycopg` ڈرائیور کو انسٹال کریں، `DATABASE_URL` کو `postgresql+psycopg://` URL پر سیٹ کریں، اور SQLModel یا SQLAlchemy کے ذریعے ہینڈلرز اور صفحات سے استفسار کریں۔

## مقامی طور پر PostgreSQL چلائیں۔

```bash
docker run --name nexy-db -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=app -p 5432:5432 -d postgres:17
```

## ڈرائیور انسٹال کریں۔

```bash
uv add "psycopg[binary]"
```

مطابقت پذیری اور async کوڈ کے لیے، ڈرائیور کا ورژن 3 ہے `psycopg`۔ صرف async کوڈ کے لیے، `asyncpg` دوسرا انتخاب ہے:

```bash
uv add asyncpg
```

## کنکشن کی تار

```bash filename="env"
DATABASE_URL=postgresql+psycopg://postgres:secret@localhost:5432/app
```

| URL | ڈرائیور |
|---|---|
| `postgresql+psycopg://user:pass@host:5432/db` | psycopg 3، مطابقت پذیری اور async |
| `postgresql+asyncpg://user:pass@host:5432/db` | asyncpg، صرف async |
| `postgresql://user:pass@host:5432/db` | psycopg2، اگر یہ انسٹال ہے |
| `postgres://...` | SQLAlchemy کے ذریعہ مسترد: اسکیم کا نام `postgresql+psycopg://` رکھو |

`@`، `:` یا `/` کے ساتھ پاس ورڈ یو آر ایل میں فیصد انکوڈ شدہ ہے: `p@ss` ہے `p%40ss`۔

## انجن

ہوسٹنگ پلیٹ فارم اکثر ایک `postgres://` URL فراہم کرتے ہیں۔ اسے تبدیل کریں جہاں انجن بنایا گیا ہے:

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

| پول آپشن | یہ کیا کرتا ہے |
|---|---|
| `pool_size=5` | کنکشن ہر عمل کے لیے کھلے رہتے ہیں۔ |
| `max_overflow=10` | بوجھ کے تحت اضافی کنکشن کی اجازت ہے، بعد میں بند کر دیا گیا ہے۔ |
| `pool_pre_ping=True` | استعمال سے پہلے کنکشن کی جانچ پڑتال کرتا ہے، لہذا دوبارہ شروع ہونے والے ڈیٹا بیس میں کوئی غلطی نہیں ہے۔ |

ہر `nx start` ورکر کا اپنا پول ہوتا ہے: `workers × (pool_size + max_overflow)` سرور کے `max_connections` کے نیچے رہنا چاہیے۔

## PostgreSQL اقسام کے ساتھ ایک ماڈل

`uuid` کلیدیں، `JSONB`، ارے اور `timestamptz` مقامی کالم کی اقسام ہیں:

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

<!-- router:fbr,custom -->
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

روٹ ماڈیول کے `controllers` میں کنٹرولر کی فہرست بنائیں۔
<!-- /router -->

`Post.tags.contains([tag])` ہے PostgreSQL کا `@>`: وہ پوسٹس جن کے ٹیگ `tag` ہیں۔

## یو آر ایل میں ایک `uuid`

<!-- router:fbr,custom -->
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

روٹ ماڈیول کے `controllers` میں کنٹرولر کی فہرست بنائیں۔
<!-- /router -->

ایک سیگمنٹ جو UUID نہیں ہے سوال چلنے سے پہلے `404` جواب دیتا ہے۔

## استفسار `JSONB`

```python filename="src/services/posts.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.post_model import Post


def featured_posts() -> list[Post]:
    with Session(engine) as session:
        query = select(Post).where(Post.extra["featured"].as_boolean())
        return list(session.exec(query))
```

<!-- router:fbr,custom -->
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

سوال کو ایک فنکشن میں رکھیں: صرف فرنٹ میٹر کے اوپری سطح پر تفویض کردہ نام ہی ٹیمپلیٹ تک پہنچتے ہیں۔

## مکمل متن کی تلاش

<!-- router:fbr,custom -->
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

روٹ ماڈیول کے `controllers` میں کنٹرولر کی فہرست بنائیں۔
<!-- /router -->

ایک انڈیکس اسے ایک بڑی میز پر تیزی سے رکھتا ہے۔ اسے منتقلی میں شامل کریں:

```python filename="alembic/versions/xxxx_search_index.py"
def upgrade() -> None:
    op.execute(
        "CREATE INDEX post_title_search ON post USING GIN (to_tsvector('english', title))"
    )
```

## اپسرٹس

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

## ہجرتیں

```bash
nx migrate --init
nx migrate -m "create posts"
nx migrate --upgrade
```

`nx migrate` پڑھتا ہے `DATABASE_URL`، چیک کرتا ہے کہ ڈرائیور انسٹال ہے اور سرور جواب دیتا ہے، پھر چلتا ہے Alembic۔ ہر ماڈل ماڈیول کو `alembic/env.py` میں امپورٹ کریں تاکہ آٹو جنریٹ اسے دیکھ سکے۔

## `asyncpg` کے ساتھ مطابقت پذیری

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

کنٹرولر کی فہرست روٹ ماڈیول کے `controllers` میں، `PostsByIdApiController` سے پہلے: پہلا کنٹرولر جس کا راستہ جوابات سے میل کھاتا ہے، اور اس کے بعد درج، `/api/posts/count/` جوابات `404`۔
<!-- /router -->

psycopg 3 async بھی چلاتا ہے: `postgresql+psycopg://` `create_async_engine` کے ساتھ بھی کام کرتا ہے۔

## ٹرانزیکشن میں ٹیسٹ

ہر ٹیسٹ ایک ٹرانزیکشن کے اندر چلتا ہے جسے رول بیک کیا جاتا ہے، لہذا ٹیسٹ ڈیٹا بیس خالی رہتا ہے:

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

## منظم PostgreSQL

| سروس | کیا تبدیلیاں |
|---|---|
| [نیین ](neon.md) | شامل کریں `?sslmode=require`؛ بہت سے مختصر رابطوں کے لیے پولڈ ہوسٹ کا استعمال کریں۔ |
| سوپا بیس | ایک ہی URL فارم؛ بہت سے کارکنوں کے لیے پولر پورٹ `6543` کا استعمال کریں۔ |
| Amazon RDS، Cloud SQL، Azure | `?sslmode=require` شامل کریں، اور ایپ کے نیٹ ورک کو اجازت دیں۔ |

## اگلے اقدامات

- [ڈیٹا بیس](../guides/databases.md)
- [Nexy کے ساتھ نیین کا استعمال کریں](neon.md)
- [Nexy کے ساتھ SQLite استعمال کریں](sqlite.md)
