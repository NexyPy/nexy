# 将 PostgreSQL 与 Nexy 一起使用

要将 PostgreSQL 与 Nexy 一起使用，请安装 `psycopg` 驱动程序，将 `DATABASE_URL` 设置为 `postgresql+psycopg://` URL，并通过 SQLModel 或 SQLAlchemy 从处理程序和页面查询它。

## 本地运行 PostgreSQL

```bash
docker run --name nexy-db -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=app -p 5432:5432 -d postgres:17
```

## 安装驱动程序

```bash
uv add "psycopg[binary]"
```

`psycopg` 是驱动程序的版本 3，用于同步和异步代码。对于仅异步代码，`asyncpg` 是另一个选择：

```bash
uv add asyncpg
```

## 连接字符串

```bash filename=".env"
DATABASE_URL=postgresql+psycopg://postgres:secret@localhost:5432/app
```

| 网址 | 司机 |
|---|---|
| `postgresql+psycopg://user:pass@host:5432/db` | psycopg 3，同步和异步 |
| `postgresql+asyncpg://user:pass@host:5432/db` | asyncpg，仅异步 |
| `postgresql://user:pass@host:5432/db` | psycopg2，如果已安装 |
| `postgres://...` | 被 SQLAlchemy 拒绝：将方案重命名为 `postgresql+psycopg://` |

包含 `@`、`:` 或 `/` 的密码在 URL 中进行百分比编码：`p@ss` 为 `p%40ss`。

## 发动机

托管平台通常会分发 `postgres://` URL。在引擎制造地对其进行转换：

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

| 池选项 | 它的作用 |
|---|---|
| `pool_size=5` | 每个进程的连接保持打开状态 |
| `max_overflow=10` | 负载下允许额外连接，之后关闭 |
| `pool_pre_ping=True` | 使用前检查连接，重启数据库不会报错 |

每个 `nx start` 工作线程都有自己的池：`workers × (pool_size + max_overflow)` 必须保留在服务器的 `max_connections` 下。

## 具有 PostgreSQL 类型的模型

`uuid` 键、`JSONB`、数组和 `timestamptz` 是本机列类型：

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

## 每个请求一个会话

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

## 从处理程序读取和写入

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

在根模块的 `controllers` 中列出控制器。
<!-- /router -->

`Post.tags.contains([tag])` 是 PostgreSQL 的 `@>`：标签包含 `tag` 的帖子。

## URL 中的 `uuid`

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

在根模块的 `controllers` 中列出控制器。
<!-- /router -->

非 UUID 的段在查询运行之前回答 `404`。

## 查询 `JSONB`

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

将查询保留在函数中：只有在 frontmatter 顶层分配的名称才能到达模板。

## 全文检索

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

在根模块的 `controllers` 中列出控制器。
<!-- /router -->

索引可以在大表上保持快速。将其添加到迁移中：

```python filename="alembic/版本/xxxx_search_index.py"
def upgrade() -> None:
    op.execute(
        "CREATE INDEX post_title_search ON post USING GIN (to_tsvector('english', title))"
    )
```

## 更新插入

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

## 迁移

```bash
nx migrate --init
nx migrate -m "create posts"
nx migrate --upgrade
```

`nx migrate` 读取 `DATABASE_URL`，检查驱动程序是否已安装以及服务器是否应答，然后运行 Alembic。导入 `alembic/env.py` 中的每个模型模块，以便自动生成可以看到它。

## 与 `asyncpg` 异步

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

列出根模块的 `controllers` 中的控制器，在 `PostsByIdApiController` 之前：路径与答案匹配的第一个控制器，在其后面列出 `/api/posts/count/` 答案 `404`。
<!-- /router -->

psycopg 3 也运行异步：`postgresql+psycopg://` 也可以与 `create_async_engine` 一起使用。

## 在事务中进行测试

每个测试都在回滚的事务内运行，因此测试数据库保持为空：

```python filename="测试/conftest.py"
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

## 管理 PostgreSQL

| 服务 | 有什么变化 |
|---|---|
| [霓虹灯](neon.md) | 添加 `?sslmode=require`；使用池主机进行许多短连接 |
| 苏帕贝斯 | 相同的 URL 形式；对许多工作人员使用池化端口 `6543` |
| 亚马逊 RDS、云 SQL、Azure | 添加 `?sslmode=require`，并允许应用程序的网络 |

## 后续步骤

- [数据库](../guides/databases.md)
- [将 Neon 与 Nexy 结合使用](neon.md)
- [将 SQLite 与 Nexy](sqlite.md) 一起使用
