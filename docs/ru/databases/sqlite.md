# Используйте SQLite с Nexy

SQLite — это база данных, которую новый проект Nexy использует, когда `DATABASE_URL` не установлено: один файл, без сервера и собственный драйвер Python через SQLModel, SQLAlchemy или Tortoise-ORM.

## Когда SQLite подходит

- Разработка, тесты и демо: ничего устанавливать и запускать не нужно.
- Сайт с одним сервером и скромными пишет: блог, внутренний инструмент, небольшой магазин.
- Данные, требующие большого чтения, поставляются вместе с приложением.

Выбирайте [PostgreSQL](postgresql.md), когда несколько серверов пишут одновременно или когда вам нужны расширенные типы и полнотекстовый поиск в большом масштабе.

## Строка подключения

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
```

| URL-адрес | База данных |
|---|---|
| `sqlite:///dev.db` | `dev.db`, относительно папки `nx dev` работает в |
| `sqlite:////var/data/app.db` | абсолютный путь: четыре косые черты |
| `sqlite://` | в памяти, исчезает, когда процесс останавливается |
| `sqlite+aiosqlite:///dev.db` | тот же файл через асинхронный драйвер |

## Двигатель

`nx new` записывает этот файл, когда вы выбираете SQLModel. Единственная строка, которую нужно добавить для SQLite — это `check_same_thread`: страница и обработчик могут использовать движок из разных потоков.

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

## Внешние ключи и WAL

SQLite не применяет внешние ключи, если не задано для каждого соединения. Режим WAL позволяет читателям продолжать работу, пока пишет один писатель. Оба `PRAGMA` запускаются при каждом новом соединении и устанавливаются рядом с движком:

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

## Модель

```python filename="src/models/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    done: bool = False
```

## Сеанс по запросу

Зависимость открывает сессию для запроса и закрывает ее после ответа:

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

## Чтение и запись из обработчика

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

Перечислите контроллер в `controllers` корневого модуля.
<!-- /router -->

## Читать со страницы

Страница `.nexy` запускает свой внешний интерфейс на сервере, поэтому она может вызывать тот же код. Сохраняйте запрос в функции: в шаблон попадают только имена, назначенные на верхнем уровне заголовка.

```python filename="src/services/notes.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def open_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).where(Note.done == False)))  # noqa: E712
```

<!-- router:fbr,custom -->
```nexy filename="src/маршруты/notes.nexy"
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

## Создайте таблицы с миграциями

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` записывает `alembic/env.py`, который импортирует модели, которые сравнивает с базой данных. Импортируйте туда каждый новый модуль модели:

```python filename="перегонный куб/env.py"
import src.models.note_model  # noqa: F401
```

SQLite не может `ALTER` разместить большинство столбцов. Включите пакетный режим Alembic для копирования таблицы в обоих вызовах `context.configure(...)` `alembic/env.py`:

```python filename="перегонный куб/env.py"
context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
```

## Асинхронно с `aiosqlite`

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

Перечислите контроллер в `controllers` корневого модуля.
<!-- /router -->

## Тесты в базе данных в памяти

`StaticPool` сохраняет одно соединение, поэтому база данных в памяти сохраняется на протяжении всего теста. Зависимость обработчика заменяется на ту, которая его использует:

```python filename="тесты/test_notes.py"
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

## В производстве

- **Храните файл на постоянном диске.** Собственная файловая система контейнера теряется при повторном развертывании: смонтируйте том и укажите на него `DATABASE_URL` абсолютный путь.
- **Один сервер, один файл.** SQLite одновременно имеет один писатель. Несколько `nx start` рабочих на одной машине прекрасно справляются с WAL; несколько машин нет.
- **Создайте резервную копию во время работы** с `sqlite3 app.db ".backup backup.db"`, а не с копией файла.

## Следующие шаги

- [Базы данных](../guides/databases.md)
- [Используйте PostgreSQL с Nexy](postgresql.md)
- [Тестирование](../guides/testing.md)
