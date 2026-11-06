# استخدم MySQL أو MariaDB مع Nexy

لاستخدام MySQL أو MariaDB مع Nexy، قم بتثبيت برنامج التشغيل `pymysql`، وقم بتعيين `DATABASE_URL` إلى عنوان URL `mysql+pymysql://` أو `mariadb+pymysql://` مع `charset=utf8mb4`، واستعلام عنه من خلال SQLModel.

## قم بتشغيل MySQL أو MariaDB محليًا

```bash
docker run --name nexy-mysql -e MYSQL_ROOT_PASSWORD=secret -e MYSQL_DATABASE=app -p 3306:3306 -d mysql:8.4
docker run --name nexy-mariadb -e MARIADB_ROOT_PASSWORD=secret -e MARIADB_DATABASE=app -p 3306:3306 -d mariadb:11
```

## تثبيت برنامج التشغيل

```bash
uv add pymysql
```

`pymysql` طاهر Python ولا يحتاج إلى غيره. بالنسبة للكود غير المتزامن، يستخدمه `aiomysql` أدناه:

```bash
uv add aiomysql
```

## سلسلة الاتصال

```bash filename=".env"
DATABASE_URL=mysql+pymysql://root:secret@localhost:3306/app?charset=utf8mb4
```

| عنوان URL | الخادم والسائق |
|---|---|
| `mysql+pymysql://user:pass@host:3306/db?charset=utf8mb4` | ماي إس كيو إل، المزامنة |
| `mariadb+pymysql://user:pass@host:3306/db?charset=utf8mb4` | MariaDB، متزامنة مع SQL الخاصة بـ MariaDB |
| `mysql+aiomysql://user:pass@host:3306/db?charset=utf8mb4` | MySQL أو MariaDB، غير متزامن |

الاحتفاظ بـ `charset=utf8mb4`: يقوم `utf8` في MySQL بتخزين ثلاثة بايتات لكل حرف، ويحتاج الرمز التعبيري إلى أربعة بايتات.

## المحرك

يقوم MySQL بإغلاق الاتصال الذي ظل خاملاً لمدة `wait_timeout` ثانية، أي ثماني ساعات افتراضيًا. `pool_recycle` يسقط الاتصالات قبل ذلك، و `pool_pre_ping` يلتقط الباقي:

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

ومن دونهم أول طلب الصبح يجيب `MySQL server has gone away`.

## نموذج: إعطاء الأوتار طولاً

يحتاج MySQL إلى طول في كل `VARCHAR`. SQLModel يكتب `VARCHAR(255)` لـ `str` بلا شيء؛ اضبط `max_length` حيث تعرف الحجم، واستخدم `Text` للمحتوى الطويل:

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

يجب أن يتناسب `VARCHAR` الفريد أو المفهرس مع الفهرس: 3072 بايت مع InnoDB، أي ما يصل إلى 768 حرفًا في `utf8mb4`.

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

## المفتاح المكرر هو `409`

مقالة ثانية بنفس السلسلة الثابتة تكسر الفهرس الفريد. اكتشف الخطأ وأجب بالحالة:

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

## إقرأ من إحدى الصفحات

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

فقط الأسماء المعينة في المستوى الأعلى من المادة الأمامية تصل إلى القالب، وبالتالي فإن الاستعلام يعيش في وظيفة.

## يزعج

يقوم MySQL وMariaDB بكتابة رسالة نصية كـ `INSERT ... ON DUPLICATE KEY UPDATE`:

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

## البحث عن النص الكامل

قم بإضافة فهرس `FULLTEXT` في عملية الترحيل، ثم قم بالاستعلام عنه باستخدام `MATCH ... AGAINST`:

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

## الهجرات

```bash
nx migrate --init
nx migrate -m "create articles"
nx migrate --upgrade
```

ينفذ MySQL كلاً من `CREATE` و `ALTER` من تلقاء نفسه، وبالتالي فإن الترحيل الذي يفشل في منتصف الطريق يظل نصف مطبق: أبقِ عمليات الترحيل صغيرة، مع تغيير واحد لكل منهما.

## غير متزامن مع `aiomysql`

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

## MySQL أو MariaDB: ما الفرق

| | ماي إس كيو إل 8 | ماريا دي بي 11 |
|---|---|---|
| مخطط URL | `mysql+pymysql://` | `mariadb+pymysql://` |
| `JSON` العمود | النوع الأصلي | اسم مستعار `LONGTEXT` بشيك |
| `RETURNING` | لا | نعم على `INSERT` و `DELETE` |
| تسلسلات | لا | `CREATE SEQUENCE` |

رمز هذه الصفحة يعمل على كليهما.

## إدارة MySQL

| الخدمة | ما يتغير |
|---|---|
| PlanetScale | إضافة `?ssl_ca=/etc/ssl/certs/ca-certificates.crt`؛ لا توجد مفاتيح خارجية بشكل افتراضي |
| أمازون آر دي إس، أورورا، كلاود إس كيو إل، أزور | السماح بشبكة التطبيق واستخدام TLS |

## الخطوات التالية

- [قواعد البيانات](../guides/databases.md)
- [استخدم PostgreSQL مع Nexy](postgresql.md)
- [استخدم SQLite مع Nexy](sqlite.md)
