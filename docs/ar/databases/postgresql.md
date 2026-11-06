# استخدم PostgreSQL مع Nexy

لاستخدام PostgreSQL مع Nexy، قم بتثبيت برنامج التشغيل `psycopg`، وقم بتعيين `DATABASE_URL` إلى عنوان URL `postgresql+psycopg://`، واستعلام عنه من المعالجات والصفحات من خلال SQLModel أو SQLAlchemy.

## قم بتشغيل PostgreSQL محليًا

```bash
docker run --name nexy-db -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=app -p 5432:5432 -d postgres:17
```

## تثبيت برنامج التشغيل

```bash
uv add "psycopg[binary]"
```

`psycopg` هو الإصدار 3 من برنامج التشغيل، للمزامنة والتعليمات البرمجية غير المتزامنة. بالنسبة للكود غير المتزامن فقط، `asyncpg` هو الخيار الآخر:

```bash
uv add asyncpg
```

## سلسلة الاتصال

```bash filename=".env"
DATABASE_URL=postgresql+psycopg://postgres:secret@localhost:5432/app
```

| عنوان URL | سائق |
|---|---|
| `postgresql+psycopg://user:pass@host:5432/db` | psycopg 3، المزامنة وغير المتزامنة |
| `postgresql+asyncpg://user:pass@host:5432/db` | غير متزامن، غير متزامن فقط |
| `postgresql://user:pass@host:5432/db` | psycopg2، إذا كان مثبتًا |
| `postgres://...` | مرفوض من قبل SQLAlchemy: إعادة تسمية المخطط إلى `postgresql+psycopg://` |

كلمة المرور التي تحتوي على `@` أو `:` أو `/` تكون مشفرة بنسبة مئوية في عنوان URL: `p@ss` هي `p%40ss`.

## المحرك

غالبًا ما تقوم منصات الاستضافة بتسليم `postgres://` عنوان URL. تحويله حيث يتم صنع المحرك:

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

| خيار المسبح | ماذا يفعل |
|---|---|
| `pool_size=5` | تبقى الاتصالات مفتوحة لكل عملية |
| `max_overflow=10` | اتصالات إضافية مسموح بها تحت الحمل، مغلقة بعد |
| `pool_pre_ping=True` | يتحقق من الاتصال قبل الاستخدام، لذلك لا يوجد خطأ في قاعدة البيانات المعاد تشغيلها |

كل `nx start` لديه تجمع خاص به: `workers × (pool_size + max_overflow)` يجب أن يبقى تحت `max_connections` الخاص بالخادم].

## نموذج به PostgreSQL أنواع

`uuid` المفاتيح، `JSONB`، المصفوفات و `timestamptz` هي أنواع أعمدة أصلية:

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

## جلسة لكل طلب

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

## القراءة والكتابة من المعالج

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

`Post.tags.contains([tag])` هو PostgreSQL `@>`: المنشورات التي تحمل علامات `tag`.

## أ `uuid` في عنوان URL

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

يجيب الجزء الذي ليس UUID على `404` قبل تشغيل الاستعلام.

## الاستعلام `JSONB`

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

احتفظ بالاستعلام في دالة: فقط الأسماء المعينة في المستوى الأعلى من المادة الأمامية هي التي تصل إلى القالب.

## البحث عن النص الكامل

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

الفهرس يبقيه سريعًا على طاولة كبيرة. أضفه في الترحيل:

```python filename="alembic/versions/xxxx_search_index.py"
def upgrade() -> None:
    op.execute(
        "CREATE INDEX post_title_search ON post USING GIN (to_tsvector('english', title))"
    )
```

## يزعج

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

## الهجرات

```bash
nx migrate --init
nx migrate -m "create posts"
nx migrate --upgrade
```

`nx migrate` يقرأ `DATABASE_URL`، ويتحقق من تثبيت برنامج التشغيل وأن الخادم يجيب، ثم يقوم بتشغيل Alembic. قم باستيراد كل وحدة نمطية في `alembic/env.py` حتى يراها الإنشاء التلقائي.

## غير متزامن مع `asyncpg`

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

يعمل psycopg 3 أيضًا بشكل غير متزامن: `postgresql+psycopg://` يعمل مع `create_async_engine` أيضًا.

## الاختبارات في الصفقة

يتم تشغيل كل اختبار داخل معاملة تم إرجاعها، بحيث تظل قاعدة بيانات الاختبار فارغة:

```python filename="الاختبارات/conftest.py"
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

## أدار PostgreSQL

| الخدمة | ما يتغير |
|---|---|
| [النيون](neon.md) | إضافة `?sslmode=require`؛ استخدم المضيف المجمع للعديد من الاتصالات القصيرة |
| سوباباس | نفس نموذج URL؛ استخدم منفذ المجمع `6543` للعديد من العمال |
| أمازون آر دي إس، كلاود إس كيو إل، أزور | إضافة `?sslmode=require`، والسماح بشبكة التطبيق |

## الخطوات التالية

- [قواعد البيانات](../guides/databases.md)
- [استخدم النيون مع Nexy](neon.md)
- [استخدم SQLite مع Nexy](sqlite.md)
