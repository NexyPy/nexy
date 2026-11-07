# 使用 Nexy 构建笔记应用程序，第 5 部分：将笔记存储在 SQLite 中

第 5 部分将注释从 Python 字典移动到 SQLite 数据库中，并从一个模型、一个迁移和两个注释开始，页面从那里读取它们。

**开始之前：**[第 4 部分](components.md) 的应用程序。

## 安装ORM和迁移工具

```bash
uv add sqlmodel alembic
```

[SQLModel](https://sqlmodel.tiangolo.com/) 将表描述为 Python 类，Alembic 将对这些类的更改转换为迁移。 Nexy 也不换行：您可以按原样使用它们。

## 打开数据库

数据库的地址位于项目根目录的 `.env` 中。 `nx migrate` 和应用程序都从那里读取它：

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
```

`sqlite:///dev.db` 是一个文件，`dev.db`，紧邻 `nexyconfig.py`：SQLite 不需要服务器。让 `.env` 远离 Git：它掌握着真实数据库的秘密。

引擎是与数据库的连接。当变量未设置时，它读取 `DATABASE_URL`，并使用与默认文件相同的文件：

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///dev.db"))
```

## 描述一个注释

<!-- router:fbr,custom -->
```python filename="src/models/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

<!-- router:modular -->
该模型与它所属的功能一起存在，位于其控制器旁边：

```python filename="src/apps/notes/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

`table=True` 使该类成为一个表，`note`。 `id` 是在保存注释时由数据库给出的。

## 创建带有迁移的表

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` 写入 `alembic/` 文件夹并将其指向您的模型。 `-m` 将模型与数据库进行比较，并编写创建表的迁移； `--upgrade` 运行它。稍后更改模型，再次运行最后两条命令，如下表。

## 从数据库中读取注释

`src/notes.py` 的函数保留它们的名称，因此页面变化很小：它们现在打开一个会话，查询表，并返回 `Note` 对象而不是字符串。

<!-- router:fbr,custom -->
```python filename="src/notes.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def all_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).order_by(Note.id)))


def find(note_id: int) -> Note | None:
    with Session(engine) as session:
        return session.get(Note, note_id)
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/notes.py"
from sqlmodel import Session, select

from src.apps.notes.note_model import Note
from src.configs.db import engine


def all_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).order_by(Note.id)))


def find(note_id: int) -> Note | None:
    with Session(engine) as session:
        return session.get(Note, note_id)
```
<!-- /router -->

## 添加两个注释作为开头

种子脚本填充一个空数据库，因此项目的每个新副本都以要显示的内容开头：

<!-- router:fbr,custom -->
```python filename="src/seed.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def seed() -> None:
    with Session(engine) as session:
        if session.exec(select(Note)).first() is None:
            session.add_all([Note(text="Buy milk"), Note(text="Ship Nexy")])
            session.commit()


if __name__ == "__main__":
    seed()
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/seed.py"
from sqlmodel import Session, select

from src.apps.notes.note_model import Note
from src.configs.db import engine


def seed() -> None:
    with Session(engine) as session:
        if session.exec(select(Note)).first() is None:
            session.add_all([Note(text="Buy milk"), Note(text="Ship Nexy")])
            session.commit()


if __name__ == "__main__":
    seed()
```
<!-- /router -->

```bash
python -m src.seed
```

启动时，Nexy 导入 `src/` 的每个模块以查找 [第 6 部分 ](create-a-note.md) 的操作。 `if __name__ == "__main__":` 保留上述命令的种子：由应用程序导入，该文件仅定义 `seed`，并且不触及任何内容。

## 显示数据库中的注释

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import all_notes

notes = all_notes()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```

```nexy filename="src/routes/notes/[id].nexy"
---
from nexy import notFound
from src.notes import find

id: prop[int]
note = find(id)
if note is None:
    notFound()
---
<section class="app-page">
  <h1>{{ note.text }}</h1>
  <a href="/notes">All notes</a>
</section>
```

```python filename="src/routes/api/notes.py"
from src.notes import all_notes


async def GET():
    return [note.model_dump() for note in all_notes()]
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import all_notes

notes = all_notes()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```

```python filename="src/apps/notes/notes_controller.py"
from nexy import notFound
from nexy.decorators import Controller
from nexy.hooks import useViews
from src.notes import all_notes, find

LAYOUT = "src/apps/layout.nexy"


def page(view: str, **context: object):
    return useViews(LAYOUT, context={"children": useViews(view, context=context)})


@Controller("/notes")
class NotesController:
    async def get(self):
        return page("src/apps/notes/notes_view.nexy")


@Controller("/notes/{id}")
class NoteController:
    async def get(self, id: int):
        note = find(id)
        if note is None:
            notFound()
        return page("src/apps/notes/note_view.nexy", text=note.text)


@Controller("/api/notes")
class NotesApiController:
    async def get(self) -> list[dict]:
        return [note.model_dump() for note in all_notes()]
```
<!-- /router -->

打开 <http://localhost:3000/notes>：同样的两张牌，现在从 `dev.db`读取。重新启动 `nexy dev`，它们仍然在那里。

## 你学到了什么

- SQLModel 将表描述为类； `src/configs/db.py` 中的引擎打开数据库。
- `nx migrate` 写入并运行迁移： `--init` 一次，然后每次更改 `-m` 和 `--upgrade`。
- 页面和控制器调用查询数据库的普通 Python 函数：Nexy 不添加任何层。

## 后续步骤

- [第 6 部分：从表单创建注释](create-a-note.md)
- [SQLite](../databases/sqlite.md)：内存数据库上的编译指示、异步访问和测试
