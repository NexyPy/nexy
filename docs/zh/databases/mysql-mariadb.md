# 将 MySQL 或 MariaDB 与 Nexy 结合使用

要将 MySQL 或 MariaDB 与 Nexy 结合使用，请安装 `pymysql` 驱动程序，使用 `charset=utf8mb4` 将 `DATABASE_URL` 设置为 `mysql+pymysql://` 或 `mariadb+pymysql://` URL，然后通过 SQLModel 进行查询。

## 本地运行 MySQL 或 MariaDB

```bash
docker run --name nexy-mysql -e MYSQL_ROOT_PASSWORD=secret -e MYSQL_DATABASE=app -p 3306:3306 -d mysql:8.4
docker run --name nexy-mariadb -e MARIADB_ROOT_PASSWORD=secret -e MARIADB_DATABASE=app -p 3306:3306 -d mariadb:11
```

## 安装驱动程序

```bash
uv add pymysql
```

`pymysql` 是纯粹的 Python，不需要任何其他东西。对于异步代码，`aiomysql` 在下面使用它：

```bash
uv add aiomysql
```

## 连接字符串

```bash filename=".env"
DATABASE_URL=mysql+pymysql://root:secret@localhost:3306/app?charset=utf8mb4
```

| 网址 | 服务器和驱动程序 |
|---|---|
| `mysql+pymysql://user:pass@host:3306/db?charset=utf8mb4` | MySQL，同步 |
| `mariadb+pymysql://user:pass@host:3306/db?charset=utf8mb4` | MariaDB，同步，与MariaDB自己的SQL |
| `mysql+aiomysql://user:pass@host:3306/db?charset=utf8mb4` | MySQL 或 MariaDB，异步 |

保留 `charset=utf8mb4`：MySQL的 `utf8` 每个字符存储三个字节，而表情符号需要四个字节。

## 发动机

MySQL 会关闭空闲 `wait_timeout` 秒（默认为八小时）的连接。 `pool_recycle` 删除之前的连接，`pool_pre_ping` 捕获其余连接：

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

如果没有它们，早上的第一个请求就会得到答复 `MySQL server has gone away`。

## 模型：给字符串一个长度

MySQL 需要每个 `VARCHAR` 的长度。 SQLModel 为没有任何内容的 `str` 写入 `VARCHAR(255)`；在您知道大小的地方设置 `max_length`，并使用 `Text` 来表示长内容：

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

唯一的或索引的 `VARCHAR` 必须适合索引：对于 InnoDB，3072 字节，因此 `utf8mb4` 中最多 768 个字符。

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

在根模块的 `controllers` 中列出控制器。
<!-- /router -->

## 重复的键是 `409`

第二篇具有相同 slug 的文章破坏了唯一索引。捕获错误并用状态回答：

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

在根模块的 `controllers` 中列出控制器。
<!-- /router -->

## 从页面读取

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

只有在 frontmatter 顶层分配的名称才能到达模板，因此查询位于函数中。

## 更新插入

MySQL 和 MariaDB 将 upsert 写为 `INSERT ... ON DUPLICATE KEY UPDATE`：

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

## 全文检索

在迁移中添加 `FULLTEXT` 索引，然后使用 `MATCH ... AGAINST` 进行查询：

```python filename="alembic/版本/xxxx_article_search.py"
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

在根模块的 `controllers` 中列出控制器。
<!-- /router -->

## 迁移

```bash
nx migrate --init
nx migrate -m "create articles"
nx migrate --upgrade
```

MySQL 单独提交 `CREATE` 和 `ALTER`，因此中途失败的迁移将保持一半应用状态：保持迁移规模较小，每个更改一次。

## 与 `aiomysql` 异步

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

## MySQL 或 MariaDB：有何不同

| | MySQL 8 | 玛丽亚数据库11 |
|---|---|---|
| 网址方案 | `mysql+pymysql://` | `mariadb+pymysql://` |
| `JSON` 栏目 | 原生型 | 带检查的 `LONGTEXT` 别名 |
| `RETURNING` | 不 | 是的，关于 `INSERT` 和 `DELETE` |
| 序列 | 不 | `CREATE SEQUENCE` |

此页面的代码在两者上运行。

## 托管MySQL

| 服务 | 有什么变化 |
|---|---|
| 星球规模 | 添加 `?ssl_ca=/etc/ssl/certs/ca-certificates.crt`；默认没有外键 |
| 亚马逊 RDS、Aurora、云 SQL、Azure | 允许应用程序的网络，并使用 TLS |

## 后续步骤

- [数据库](../guides/databases.md)
- [将 PostgreSQL 与 Nexy](postgresql.md) 一起使用
- [将 SQLite 与 Nexy](sqlite.md) 一起使用
