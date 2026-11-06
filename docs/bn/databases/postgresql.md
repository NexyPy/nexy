# Nexy এর সাথে PostgreSQL ব্যবহার করুন

Nexy-এর সাথে PostgreSQL ব্যবহার করতে, `psycopg` ড্রাইভার ইনস্টল করুন, `DATABASE_URL` একটি `postgresql+psycopg://` URL এ সেট করুন এবং SQLModel বা SQLAlchemy এর মাধ্যমে হ্যান্ডলার এবং পৃষ্ঠাগুলি থেকে এটি অনুসন্ধান করুন।

## স্থানীয়ভাবে PostgreSQL চালান

```bash
docker run --name nexy-db -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=app -p 5432:5432 -d postgres:17
```

## ড্রাইভার ইনস্টল করুন

```bash
uv add "psycopg[binary]"
```

সিঙ্ক এবং অ্যাসিঙ্ক কোডের জন্য ড্রাইভারের সংস্করণ 3 হল `psycopg`। শুধুমাত্র অ্যাসিঙ্ক কোডের জন্য, `asyncpg` হল অন্য পছন্দ:

```bash
uv add asyncpg
```

## সংযোগ স্ট্রিং

```bash filename=".env"
DATABASE_URL=postgresql+psycopg://postgres:secret@localhost:5432/app
```

| URL | ড্রাইভার |
|---|---|
| `postgresql+psycopg://user:pass@host:5432/db` | psycopg 3, সিঙ্ক এবং অ্যাসিঙ্ক |
| `postgresql+asyncpg://user:pass@host:5432/db` | asyncpg, শুধুমাত্র async |
| `postgresql://user:pass@host:5432/db` | psycopg2, যদি এটি ইনস্টল করা থাকে |
| `postgres://...` | SQLAlchemy দ্বারা প্রত্যাখ্যান: স্কিমটির নাম পরিবর্তন করে `postgresql+psycopg://` |

`@`, `:` বা `/` সহ একটি পাসওয়ার্ড ইউআরএলে শতাংশ-এনকোড করা হয়: `p@ss` হল `p%40ss`।

## ইঞ্জিন

হোস্টিং প্ল্যাটফর্মগুলি প্রায়ই একটি `postgres://` URL দেয়। ইঞ্জিন যেখানে তৈরি করা হয় সেখানে এটি রূপান্তর করুন:

```python filename=""
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()


def database_url() -> str:
    url = os.environ["DATABASE_URL"]
    return url.replace("postgres://", "postgresql+psycopg://", 1)


engine = create_engine(database_url(), pool_size=5, max_overflow=10, pool_pre_ping=True)
```

| পুল বিকল্প | এটা কি করে |
|---|---|
| `pool_size=5` | সংযোগ প্রক্রিয়া প্রতি খোলা রাখা |
| `max_overflow=10` | অতিরিক্ত সংযোগ লোড অধীনে অনুমোদিত, পরে বন্ধ |
| `pool_pre_ping=True` | ব্যবহারের আগে একটি সংযোগ পরীক্ষা করে, তাই একটি পুনঃসূচনা ডাটাবেস কোন ত্রুটি নেই |

প্রতিটি `nx start` কর্মীর নিজস্ব পুল আছে: `workers × (pool_size + max_overflow)` সার্ভারের `max_connections` অধীনে থাকতে হবে।

## PostgreSQL ধরনের একটি মডেল

`uuid` কী, `JSONB`, অ্যারে এবং `timestamptz` হল নেটিভ কলামের ধরন:

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

`Post.tags.contains([tag])` হল PostgreSQL এর `@>`: যে পোস্টের ট্যাগগুলি `tag` ধরে।

## URL এ একটি `uuid`

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

একটি সেগমেন্ট যা UUID নয় `404` ক্যোয়ারী চালানোর আগে উত্তর দেয়।

## প্রশ্ন `JSONB`

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

ক্যোয়ারীটিকে একটি ফাংশনে রাখুন: শুধুমাত্র ফ্রন্টম্যাটারের শীর্ষ স্তরে নির্ধারিত নামগুলি টেমপ্লেটে পৌঁছায়৷

## পূর্ণ-পাঠ্য অনুসন্ধান

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

একটি সূচক একটি বড় টেবিলে এটি দ্রুত রাখে। এটি একটি মাইগ্রেশনে যোগ করুন:

```python filename="alembic/versions/xxxx_search_index.py"
def upgrade() -> None:
    op.execute(
        "CREATE INDEX post_title_search ON post USING GIN (to_tsvector('english', title))"
    )
```

## আপসার্ট

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

## মাইগ্রেশন

```bash
nx migrate --init
nx migrate -m "create posts"
nx migrate --upgrade
```

`nx migrate` পড়ে `DATABASE_URL`, ড্রাইভার ইনস্টল করা আছে কিনা তা পরীক্ষা করে এবং সার্ভার উত্তর দেয়, তারপর Alembic চালায়। প্রতিটি মডেল মডিউল আমদানি করুন `alembic/env.py` যাতে স্বয়ংক্রিয়ভাবে এটি দেখতে পায়।

## সাথে অ্যাসিঙ্ক করুন `asyncpg`

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

psycopg 3 এছাড়াও async চালায়: `postgresql+psycopg://` `create_async_engine` এর সাথেও কাজ করে।

## একটি লেনদেনে পরীক্ষা

প্রতিটি পরীক্ষা একটি লেনদেনের ভিতরে চলে যা রোল ব্যাক করা হয়, তাই পরীক্ষার ডাটাবেস খালি থাকে:

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

## পরিচালিত PostgreSQL

| সেবা | কি পরিবর্তন |
|---|---|
| [নিয়ন](neon.md) | যোগ করুন `?sslmode=require`; অনেক ছোট সংযোগের জন্য পুল হোস্ট ব্যবহার করুন |
| সুপাবেস | একই URL ফর্ম; অনেক শ্রমিকের জন্য পুলার পোর্ট `6543` ব্যবহার করুন |
| আমাজন RDS, ক্লাউড SQL, Azure | যোগ করুন `?sslmode=require`, এবং অ্যাপের নেটওয়ার্ককে অনুমতি দিন |

## পরবর্তী পদক্ষেপ

- [ডাটাবেস](../guides/databases.md)
- [Nexy এর সাথে নিয়ন ব্যবহার করুন](neon.md)
- [ব্যবহার করুন SQLite নেক্সির সাথে](sqlite.md)
