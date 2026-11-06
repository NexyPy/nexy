# Nexy এর সাথে SQLite ব্যবহার করুন

SQLite হল একটি ডাটাবেস যা একটি নতুন Nexy প্রকল্প ব্যবহার করে যখন `DATABASE_URL` সেট না থাকে: একটি ফাইল, কোনো সার্ভার নেই এবং Python-এর নিজস্ব ড্রাইভার, SQLModel, SQLAlchemy বা Tortoise-ORM এর মাধ্যমে।

## যখন SQLite ফিট হয়

- উন্নয়ন, পরীক্ষা এবং ডেমো: ইনস্টল বা শুরু করার কিছুই নেই।
- একটি সার্ভার সহ একটি সাইট এবং বিনয়ী লিখেছেন: একটি ব্লগ, একটি অভ্যন্তরীণ সরঞ্জাম, একটি ছোট দোকান৷
- অ্যাপের সাথে রিড-হেভি ডেটা পাঠানো হয়েছে।

যখন একাধিক সার্ভার একবারে লিখবে, অথবা যখন আপনার সমৃদ্ধ প্রকার এবং স্কেলে পূর্ণ-পাঠ্য অনুসন্ধানের প্রয়োজন হবে তখন [PostgreSQL](postgresql.md) বেছে নিন।

## সংযোগ স্ট্রিং

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
```

| URL | ডাটাবেস |
|---|---|
| `sqlite:///dev.db` | `dev.db`, ফোল্ডারের সাপেক্ষে `nx dev` চলে |
| `sqlite:////var/data/app.db` | একটি পরম পথ: চারটি স্ল্যাশ |
| `sqlite://` | মেমরিতে, প্রক্রিয়া বন্ধ হয়ে গেলে চলে যায় |
| `sqlite+aiosqlite:///dev.db` | একই ফাইল, async ড্রাইভারের মাধ্যমে |

## ইঞ্জিন

যখন আপনি SQLModel বাছাই করেন তখন `nx new` এই ফাইলটি লেখেন। SQLite এর জন্য একটি লাইন যোগ করতে হবে `check_same_thread`: একটি পৃষ্ঠা এবং একটি হ্যান্ডলার বিভিন্ন থ্রেড থেকে ইঞ্জিন ব্যবহার করতে পারে।

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

## বিদেশী কী এবং WAL

SQLite বিদেশী কীগুলি প্রয়োগ করে না যদি না চাওয়া হয়, প্রতি সংযোগের জন্য। একজন লেখক লেখার সময় WAL মোড পাঠকদের চলতে দেয়। উভয়ই একটি `PRAGMA` প্রতিটি নতুন সংযোগে চালিত, ইঞ্জিনের পাশে সেট আপ করা হয়:

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

## একজন মডেল

```python filename="src/models/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    done: bool = False
```

## অনুরোধ প্রতি একটি সেশন

একটি নির্ভরতা অনুরোধের জন্য একটি সেশন খোলে এবং উত্তরের পরে এটি বন্ধ করে:

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

## হ্যান্ডলার থেকে পড়ুন এবং লিখুন

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

## একটি পৃষ্ঠা থেকে পড়ুন

একটি `.nexy` পৃষ্ঠা সার্ভারে তার ফ্রন্টম্যাটার চালায়, তাই এটি একই কোড কল করতে পারে। ক্যোয়ারীটিকে একটি ফাংশনে রাখুন: শুধুমাত্র ফ্রন্টম্যাটারের শীর্ষ স্তরে নির্ধারিত নামগুলি টেমপ্লেটে পৌঁছায়৷

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

## মাইগ্রেশন সহ টেবিল তৈরি করুন

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` লিখেছেন `alembic/env.py`, যা ডাটাবেসের সাথে তুলনা করে এমন মডেল আমদানি করে। সেখানে প্রতিটি নতুন মডেল মডিউল আমদানি করুন:

```python filename="alembic/env.py"
import src.models.note_model  # noqa: F401
```

SQLite বেশিরভাগ কলাম জায়গায় `ALTER` করতে পারে না। Alembic এর ব্যাচ মোড চালু করুন, যা টেবিলটি অনুলিপি করে, `context.configure(...)` উভয় `alembic/env.py`-এর কলে:

```python filename="alembic/env.py"
context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
```

## সাথে অ্যাসিঙ্ক করুন `aiosqlite`

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

## একটি ইন-মেমরি ডাটাবেসে পরীক্ষা

`StaticPool` একটি সংযোগ রাখে, তাই ইন-মেমরি ডাটাবেস পুরো পরীক্ষার জন্য বেঁচে থাকে। যে এটি ব্যবহার করে তার জন্য হ্যান্ডলারের নির্ভরতা অদলবদল করা হয়:

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

## উৎপাদনে

- **একটি অবিরাম ফাইল রাখুন ডিস্ক** একটি কন্টেইনারের নিজস্ব ফাইল সিস্টেম পুনঃনিয়োগ করার সময় হারিয়ে যায়: একটি ভলিউম মাউন্ট করুন এবং একটি পরম পথের সাথে এটিতে `DATABASE_URL` নির্দেশ করুন।
- **একটি সার্ভার, একটি ফাইল** SQLite এক সময়ে একজন লেখক আছে একই মেশিনে বেশ কিছু `nx start` কর্মী WAL এর সাথে ঠিক আছে; বেশ কিছু মেশিন নেই।
- **এটি যখন এটি ব্যাক আপ `sqlite3 app.db ".backup backup.db"` দিয়ে চলে**, ফাইল কপি দিয়ে নয়।

## পরবর্তী পদক্ষেপ

- [ডাটাবেস](../guides/databases.md)
- [ব্যবহার করুন PostgreSQL নেক্সির সাথে](postgresql.md)
- [পরীক্ষা ](../guides/testing.md)
