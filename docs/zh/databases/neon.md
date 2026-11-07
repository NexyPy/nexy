# 将 Neon 与 Nexy 一起使用

Neon 是无服务器的 PostgreSQL：Nexy 项目像 [PostgreSQL](postgresql.md) 一样使用它，使用 `psycopg` 驱动程序，`DATABASE_URL` 中 Neon 的池化连接字符串，以及一个在数据库进入睡眠状态后仍然存在的池。

## 获取连接字符串

在 Neon 控制台中， **Connect** 显示每个分支的两个字符串：

| 字符串 | 主持人 | 用它来 |
|---|---|---|
| 汇集 | `ep-xxx-pooler.region.aws.neon.tech` | 应用程序：许多短连接，通过 PgBouncer |
| 直接 | `ep-xxx.region.aws.neon.tech` | 迁移和长时间会话 |

唯一的区别是主机名中的 `-pooler`。

## 安装驱动程序

```bash
uv add "psycopg[binary]"
```

Neon 通过 HTTP 的无服务器驱动程序适用于 JavaScript；从 Python 开始，连接是通过 TCP 和 TLS 的普通 PostgreSQL。

## 两个网址

```bash filename=".env"
DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3-pooler.eu-central-1.aws.neon.tech/app?sslmode=require
DIRECT_DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3.eu-central-1.aws.neon.tech/app?sslmode=require
```

Neon 将其字符串复制为 `postgresql://...`：在 `postgresql` 之后添加 `+psycopg`。当控制台添加它时，保留 `sslmode=require` 和 `channel_binding=require`。

## 发动机

Neon 计算在空闲时会挂起，从而关闭池的连接。 `pool_pre_ping` 在使用前替换已失效的连接，并且 `pool_recycle` 在 Neon 之前断开连接：

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(
    os.environ["DATABASE_URL"],
    pool_size=5,
    max_overflow=5,
    pool_pre_ping=True,
    pool_recycle=300,
)
```

挂起后的第一个请求会在计算开始时等待数百毫秒。如果这对您很重要，请在生产分支上关闭自动挂起。

## 模型和处理程序

剩下的就是 PostgreSQL。型号：

```python filename="src/models/visit_model.py"
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


class Visit(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    path: str
    at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )
```

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

<!-- router:fbr,custom -->
```python filename="src/routes/api/visits.py"
from sqlmodel import Session, func, select

from nexy.http import Depends
from src.configs.session import get_session
from src.models.visit_model import Visit


async def POST(path: str, session: Session = Depends(get_session)):
    session.add(Visit(path=path))
    session.commit()
    return {"visits": session.exec(select(func.count()).select_from(Visit)).one()}
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/visits/visits_api_controller.py"
from sqlmodel import Session, func, select

from nexy.decorators import Controller
from nexy.http import Depends
from src.configs.session import get_session
from src.models.visit_model import Visit


@Controller("/api/visits")
class VisitsApiController:
    async def post(self, path: str, session: Session = Depends(get_session)):
        session.add(Visit(path=path))
        session.commit()
        return {"visits": session.exec(select(func.count()).select_from(Visit)).one()}
```

在根模块的 `controllers` 中列出控制器。
<!-- /router -->

## 迁移通过直接 URL

池主机前面的 PgBouncer 在客户端之间共享连接，这适合短查询，而不是迁移的长会话。 `nx migrate` 读取 `DATABASE_URL`，因此将其指向该命令的直接主机：

```bash
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate -m "create visits"
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate --upgrade
```

`alembic/env.py` 使用 `src/configs/db.py` 的引擎，它读取相同的变量。

## 池化器背后的准备语句

psycopg 准备一个已运行五次的查询。如果池主机回答 `prepared statement "_pg3_0" does not exist`，请将其关闭：

```python filename="src/configs/db.py"
engine = create_engine(
    os.environ["DATABASE_URL"],
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"prepare_threshold": None},
)
```

对于 `asyncpg`，设置为 `connect_args={"statement_cache_size": 0}`。

## 用于开发和预览的分支

Neon 分支是数据库的副本，在一秒钟内创建。每个开发人员或每个拉取请求一个，使测试数据远离生产：

```bash
neonctl branches create --name dev-ada
neonctl connection-string dev-ada --pooled
```

将该字符串放入开发人员的 `.env` 中，或预览部署的环境中。

## 测试

在回滚的事务内针对为其创建的分支运行测试：请参阅[事务中的测试](postgresql.md#tests-in-a-transaction)。

## 后续步骤

- [将 PostgreSQL 与 Nexy](postgresql.md) 结合使用：类型、搜索、更新插入和异步
- [数据库](../guides/databases.md)
- [部署](../deployment/README.md)
