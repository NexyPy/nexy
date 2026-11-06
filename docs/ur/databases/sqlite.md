# Nexy کے ساتھ SQLite استعمال کریں۔

SQLite وہ ڈیٹابیس ہے جسے ایک نیا Nexy پروجیکٹ استعمال کرتا ہے جب `DATABASE_URL` کو سیٹ نہیں کیا جاتا ہے: ایک فائل، کوئی سرور نہیں، اور Python کا اپنا ڈرائیور، SQLModel، SQLAlchemy یا Tortoise-ORM کے ذریعے۔

## جب SQLite فٹ ہوجاتا ہے۔

- ترقی، ٹیسٹ اور ڈیمو: انسٹال کرنے یا شروع کرنے کے لیے کچھ نہیں۔
- ایک سرور اور معمولی لکھنے والی سائٹ: ایک بلاگ، ایک اندرونی ٹول، ایک چھوٹی سی دکان۔
- پڑھنے والا بھاری ڈیٹا ایپ کے ساتھ بھیج دیا گیا۔

چنیں [PostgreSQL](postgresql.md) جب کئی سرورز ایک ساتھ لکھتے ہیں، یا جب آپ کو بھرپور اقسام اور پیمانے پر مکمل متن کی تلاش کی ضرورت ہوتی ہے۔

## کنکشن کی تار

```bash filename="env"
DATABASE_URL=sqlite:///dev.db
```

| URL | ڈیٹا بیس |
|---|---|
| `sqlite:///dev.db` | `dev.db`، فولڈر `nx dev` کے مقابلے میں چلتا ہے۔ |
| `sqlite:////var/data/app.db` | ایک مطلق راستہ: چار سلیشس |
| `sqlite://` | میموری میں، جب عمل رک جاتا ہے تو چلا جاتا ہے۔ |
| `sqlite+aiosqlite:///dev.db` | اسی فائل، async ڈرائیور کے ذریعے |

## انجن

جب آپ SQLModel کو چنتے ہیں تو اس فائل کو `nx new` لکھتا ہے۔ SQLite کے لیے جو ایک لائن شامل کرنا ہے وہ ہے `check_same_thread`: ایک صفحہ اور ایک ہینڈلر مختلف دھاگوں سے انجن کا استعمال کر سکتا ہے۔

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

## غیر ملکی چابیاں اور WAL

SQLite غیر ملکی کلیدوں کو نافذ نہیں کرتا جب تک کہ فی کنکشن نہ پوچھا جائے۔ WAL موڈ قارئین کو آگے بڑھنے دیتا ہے جب ایک مصنف لکھتا ہے۔ دونوں ہر نئے کنکشن پر ایک `PRAGMA` چلتے ہیں، جو انجن کے آگے سیٹ اپ ہوتے ہیں:

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

## ایک ماڈل

```python filename="src/models/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    done: bool = False
```

## فی درخواست ایک سیشن

ایک انحصار درخواست کے لئے ایک سیشن کھولتا ہے اور جواب کے بعد اسے بند کر دیتا ہے:

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

## ہینڈلر سے پڑھیں اور لکھیں۔

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

## ایک صفحے سے پڑھیں

ایک `.nexy` صفحہ سرور پر اپنا فرنٹ میٹر چلاتا ہے، لہذا یہ اسی کوڈ کو کال کرسکتا ہے۔ سوال کو ایک فنکشن میں رکھیں: صرف فرنٹ میٹر کے اوپری سطح پر تفویض کردہ نام ہی ٹیمپلیٹ تک پہنچتے ہیں۔

```python filename="src/services/notes.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def open_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).where(Note.done == False)))  # noqa: E712
```

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

## ہجرت کے ساتھ میزیں بنائیں

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` لکھتا ہے `alembic/env.py`، جو ڈیٹا بیس کے ساتھ موازنہ کرنے والے ماڈلز کو درآمد کرتا ہے۔ ہر نئے ماڈل کے ماڈیول کو وہاں درآمد کریں:

```python filename="alembic/env.py"
import src.models.note_model  # noqa: F401
```

SQLite زیادہ تر کالم جگہ پر `ALTER` نہیں کر سکتے۔ Alembic کے بیچ موڈ کو آن کریں، جو ٹیبل کو کاپی کرتا ہے، `context.configure(...)` `alembic/env.py` کی دونوں کالوں میں:

```python filename="alembic/env.py"
context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
```

## `aiosqlite` کے ساتھ مطابقت پذیری

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

## ان میموری ڈیٹا بیس پر ٹیسٹ

`StaticPool` ایک کنکشن رکھتا ہے، لہذا ان میموری ڈیٹا بیس پورے ٹیسٹ کے لیے زندہ رہتا ہے۔ ہینڈلر کا انحصار اس کے استعمال کرنے والے کے لیے بدل جاتا ہے:

```python filename="tests/test_notes.py"
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

## پیداوار میں

- **فائل کو مستقل رکھیں ڈسک** ایک کنٹینر کا اپنا فائل سسٹم دوبارہ تعینات کرنے پر کھو جاتا ہے: ایک حجم کو ماؤنٹ کریں اور اس پر ایک مطلق راستے کے ساتھ `DATABASE_URL` پوائنٹ کریں۔
- **ایک سرور، ایک فائل** SQLite میں ایک وقت میں ایک مصنف ہوتا ہے۔ ایک ہی مشین پر کئی `nx start` ورکرز WAL کے ساتھ ٹھیک ہیں۔ کئی مشینیں نہیں ہیں.
- **اس کا بیک اپ لیں جب یہ چلتا ہے** کے ساتھ `sqlite3 app.db ".backup backup.db"`، فائل کاپی کے ساتھ نہیں۔

## اگلے اقدامات

- [ڈیٹا بیس ](../guides/databases.md)
- [Nexy کے ساتھ PostgreSQL استعمال کریں](postgresql.md)
- [جانچ ](../guides/testing.md)
