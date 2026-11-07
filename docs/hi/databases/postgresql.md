# नेक्सी के साथ PostgreSQL का प्रयोग करें

नेक्सी के साथ PostgreSQL का उपयोग करने के लिए, `psycopg` ड्राइवर स्थापित करें, `DATABASE_URL` को `postgresql+psycopg://` यूआरएल पर सेट करें, और इसे SQLModel या SQLAlchemy के माध्यम से हैंडलर और पेजों से क्वेरी करें।

## PostgreSQL स्थानीय रूप से चलाएँ

```bash
docker run --name nexy-db -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=app -p 5432:5432 -d postgres:17
```

## ड्राइवर स्थापित करें

```bash
uv add "psycopg[binary]"
```

`psycopg` सिंक और एसिंक कोड के लिए ड्राइवर का संस्करण 3 है। एसिंक-ओनली कोड के लिए, `asyncpg` दूसरा विकल्प है:

```bash
uv add asyncpg
```

## कनेक्शन स्ट्रिंग

```bash filename=".env"
DATABASE_URL=postgresql+psycopg://postgres:secret@localhost:5432/app
```

| यूआरएल | चालक |
|---|---|
| `postgresql+psycopg://user:pass@host:5432/db` | psycopg 3, सिंक और एसिंक |
| `postgresql+asyncpg://user:pass@host:5432/db` | asyncpg, केवल async |
| `postgresql://user:pass@host:5432/db` | psycopg2, यदि यह स्थापित है |
| `postgres://...` | SQLAlchemy द्वारा अस्वीकृत: योजना का नाम बदलकर `postgresql+psycopg://` कर दिया गया |

`@`, `:` या `/` वाला पासवर्ड यूआरएल में प्रतिशत-एन्कोडेड है: `p@ss` `p%40ss` है।

## इंजन

होस्टिंग प्लेटफ़ॉर्म अक्सर एक `postgres://` यूआरएल देते हैं। इसे वहीं परिवर्तित करें जहां इंजन बना है:

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

| पूल विकल्प | यह क्या करता है |
|---|---|
| `pool_size=5` | प्रति प्रक्रिया कनेक्शन खुले रखे गए |
| `max_overflow=10` | लोड के तहत अतिरिक्त कनेक्शन की अनुमति, बाद में बंद |
| `pool_pre_ping=True` | उपयोग से पहले कनेक्शन की जांच करता है, ताकि पुनः आरंभ किए गए डेटाबेस में कोई त्रुटि न हो |

प्रत्येक `nx start` कार्यकर्ता का अपना पूल है: `workers × (pool_size + max_overflow)` को सर्वर के `max_connections` के अंतर्गत रहना चाहिए।

## PostgreSQL प्रकार वाला एक मॉडल

`uuid` कुंजियाँ, `JSONB`, सरणियाँ और `timestamptz` मूल स्तंभ प्रकार हैं:

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

## प्रति अनुरोध एक सत्र

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

## हैंडलर से पढ़ें और लिखें

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

नियंत्रक को रूट मॉड्यूल के `controllers` में सूचीबद्ध करें।
<!-- /router -->

`Post.tags.contains([tag])` PostgreSQL की `@>` है: वे पोस्ट जिनके टैग में `tag` है।

## URL में एक `uuid`

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

नियंत्रक को रूट मॉड्यूल के `controllers` में सूचीबद्ध करें।
<!-- /router -->

एक खंड जो यूयूआईडी नहीं है, क्वेरी चलने से पहले `404` उत्तर देता है।

## प्रश्न `JSONB`

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

क्वेरी को किसी फ़ंक्शन में रखें: केवल फ्रंटमैटर के शीर्ष स्तर पर निर्दिष्ट नाम ही टेम्पलेट तक पहुंचते हैं।

## पूर्ण-पाठ खोज

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

नियंत्रक को रूट मॉड्यूल के `controllers` में सूचीबद्ध करें।
<!-- /router -->

एक सूचकांक इसे बड़ी मेज पर तेजी से रखता है। इसे माइग्रेशन में जोड़ें:

```python filename="एलेम्बिक/संस्करण/xxxx_search_index.py"
def upgrade() -> None:
    op.execute(
        "CREATE INDEX post_title_search ON post USING GIN (to_tsvector('english', title))"
    )
```

## अप्सर्ट्स

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

## पलायन

```bash
nx migrate --init
nx migrate -m "create posts"
nx migrate --upgrade
```

`nx migrate` `DATABASE_URL` पढ़ता है, जांचता है कि ड्राइवर स्थापित है और सर्वर उत्तर देता है, फिर Alembic चलाता है। प्रत्येक मॉडल मॉड्यूल को `alembic/env.py` में आयात करें ताकि ऑटोजेनरेट इसे देख सके।

## `asyncpg` के साथ एसिंक

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

रूट मॉड्यूल के `controllers` में नियंत्रक को `PostsByIdApiController` से पहले सूचीबद्ध करें: पहला नियंत्रक जिसका पथ उत्तरों से मेल खाता है, और उसके बाद सूचीबद्ध, `/api/posts/count/` उत्तर `404` देता है।
<!-- /router -->

psycopg 3 async भी चलाता है: `postgresql+psycopg://` `create_async_engine` के साथ भी काम करता है।

## लेन-देन में परीक्षण

प्रत्येक परीक्षण एक लेन-देन के अंदर चलता है जिसे वापस रोल किया जाता है, इसलिए परीक्षण डेटाबेस खाली रहता है:

```python filename="परीक्षण/conftest.py"
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

## प्रबंधित PostgreSQL

| सेवा | क्या बदलता है |
|---|---|
| [नियॉन](neon.md) | जोड़ें `?sslmode=require`; कई छोटे कनेक्शनों के लिए पूल्ड होस्ट का उपयोग करें |
| सुपाबेस | वही यूआरएल फॉर्म; कई श्रमिकों के लिए पूलर पोर्ट `6543` का उपयोग करें |
| अमेज़ॅन आरडीएस, क्लाउड एसक्यूएल, एज़्योर | `?sslmode=require` जोड़ें, और ऐप के नेटवर्क को अनुमति दें |

## अगले चरण

- [डेटाबेस](../guides/databases.md)
- [नेक्सी के साथ नियॉन का प्रयोग करें](neon.md)
- [उपयोग करें SQLite नेक्सी के साथ](sqlite.md)
