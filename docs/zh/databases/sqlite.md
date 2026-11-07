# 将 SQLite 与 Nexy 一起使用

SQLite 是新 Nexy 项目在 `DATABASE_URL` 未设置时使用的数据库：一个文件，无服务器，以及 Python 自己的驱动程序，通过 SQLModel、SQLAlchemy 或 Tortoise-ORM。

## 当 SQLite 适合时

- 开发、测试和演示：无需安装或启动。
- 一个只有一台服务器且朴素的网站写道：一个博客、一个内部工具、一个小商店。
- 读取应用程序附带的大量数据。

当多个服务器同时写入时，或者当您需要丰富的类型和大规模的全文搜索时，请选择 [PostgreSQL](postgresql.md)。

## 连接字符串

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
```

| 网址 | 数据库 |
|---|---|
| `sqlite:///dev.db` | `dev.db`，相对于文件夹 `nx dev` 运行 |
| `sqlite:////var/data/app.db` | 绝对路径：四个斜杠 |
| `sqlite://` | 在内存中，当进程停止时就消失了 |
| `sqlite+aiosqlite:///dev.db` | 相同的文件，通过异步驱动程序 |

## 发动机

当您选择 SQLModel 时，`nx new` 会写入此文件。为 SQLite 添加的一行是 `check_same_thread`：页面和处理程序可以使用来自不同线程的引擎。

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(
    os.getenv("DATABASE_URL", "sqlite:///dev.db"),
    connect_args={"check_same_thread": False},
)
```

## 外键和 WAL

SQLite 不会强制执行外键，除非要求，每个连接。 WAL 模式允许读者在一位作者写作的同时继续阅读。两者都是在每个新连接上运行的 `PRAGMA`，在引擎旁边设置：

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlalchemy import event
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(
    os.getenv("DATABASE_URL", "sqlite:///dev.db"),
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def set_pragmas(connection, _record) -> None:
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()
```

## 一个模型

```python filename="src/models/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    done: bool = False
```

## 每个请求一个会话

依赖项为请求打开一个会话，并在得到应答后关闭它：

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
```python filename="src/routes/api/notes/index.py"
from pydantic import BaseModel
from sqlmodel import Session, select

from nexy.http import Depends, JSONResponse
from src.configs.session import get_session
from src.models.note_model import Note


class NewNote(BaseModel):
    title: str


async def GET(session: Session = Depends(get_session)):
    return session.exec(select(Note)).all()


async def POST(body: NewNote, session: Session = Depends(get_session)):
    note = Note(title=body.title)
    session.add(note)
    session.commit()
    session.refresh(note)
    return JSONResponse(note.model_dump(), status_code=201)
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/notes/notes_api_controller.py"
from pydantic import BaseModel
from sqlmodel import Session, select

from nexy.decorators import Controller
from nexy.http import Depends, JSONResponse
from src.configs.session import get_session
from src.models.note_model import Note


class NewNote(BaseModel):
    title: str


@Controller("/api/notes")
class NotesApiController:
    async def get(self, session: Session = Depends(get_session)):
        return session.exec(select(Note)).all()

    async def post(self, body: NewNote, session: Session = Depends(get_session)):
        note = Note(title=body.title)
        session.add(note)
        session.commit()
        session.refresh(note)
        return JSONResponse(note.model_dump(), status_code=201)
```

在根模块的 `controllers` 中列出控制器。
<!-- /router -->

## 从页面读取

`.nexy` 页面在服务器上运行其 frontmatter，因此它可以调用相同的代码。将查询保留在函数中：只有在 frontmatter 顶层分配的名称才能到达模板。

```python filename="src/services/notes.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def open_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).where(Note.done == False)))  # noqa: E712
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes.nexy"
---
from src.services.notes import open_notes

notes = open_notes()
---
<ul>
  {% for note in notes %}
  <li>{{ note.title | e }}</li>
  {% endfor %}
</ul>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from src.services.notes import open_notes

notes = open_notes()
---
<ul>
  {% for note in notes %}
  <li>{{ note.title | e }}</li>
  {% endfor %}
</ul>
```

```python filename="src/apps/notes/notes_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews("src/apps/notes/notes_view.nexy")
```
<!-- /router -->

## 创建带有迁移的表

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` 写入 `alembic/env.py`，导入与数据库进行比较的模型。在那里导入每个新模型模块：

```python filename="蒸馏器/env.py"
import src.models.note_model  # noqa: F401
```

SQLite 无法 `ALTER` 大多数列就位。打开 Alembic 的批处理模式，在 `alembic/env.py` 的两个 `context.configure(...)` 调用中复制表：

```python filename="蒸馏器/env.py"
context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
```

## 与 `aiosqlite` 异步

```bash
uv add aiosqlite
```

```python filename="src/configs/async_db.py"
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

async_engine = create_async_engine("sqlite+aiosqlite:///dev.db")


async def get_async_session():
    async with AsyncSession(async_engine) as session:
        yield session
```

<!-- router:fbr,custom -->
```python filename="src/routes/api/notes/count.py"
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from nexy.http import Depends
from src.configs.async_db import get_async_session
from src.models.note_model import Note


async def GET(session: AsyncSession = Depends(get_async_session)):
    count = (await session.exec(select(func.count()).select_from(Note))).one()
    return {"count": count}
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/notes/notes_count_api_controller.py"
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from nexy.decorators import Controller
from nexy.http import Depends
from src.configs.async_db import get_async_session
from src.models.note_model import Note


@Controller("/api/notes/count")
class NotesCountApiController:
    async def get(self, session: AsyncSession = Depends(get_async_session)):
        count = (await session.exec(select(func.count()).select_from(Note))).one()
        return {"count": count}
```

在根模块的 `controllers` 中列出控制器。
<!-- /router -->

## 在内存数据库上进行测试

`StaticPool` 保持一个连接，因此内存数据库在整个测试中都存在。处理程序的依赖项被交换为使用它的依赖项：

```python filename="测试/test_notes.py"
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from nexy.app import app
from src.configs.session import get_session

test_engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
SQLModel.metadata.create_all(test_engine)


def override_session():
    with Session(test_engine) as session:
        yield session


def test_a_note_is_created():
    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)
    client.post("/api/notes", json={"title": "Write the docs"})
    assert client.get("/api/notes").json()[0]["title"] == "Write the docs"
```

## 生产中

- **将文件保存在永久磁盘上。** 容器自己的文件系统在重新部署时丢失：安装一个卷并使用绝对路径将 `DATABASE_URL` 指向它。
- **一台服务器，一个文件。** SQLite 一次只有一名写入者。同一台机器上的多个 `nx start` 工作人员可以使用 WAL；有几台机器不是。
- **在运行** 时使用 `sqlite3 app.db ".backup backup.db"`备份它，而不是使用文件副本。

## 后续步骤

- [数据库](../guides/databases.md)
- [将 PostgreSQL 与 Nexy](postgresql.md) 一起使用
- [测试](../guides/testing.md)
