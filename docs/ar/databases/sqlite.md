# استخدم SQLite مع Nexy

SQLite هي قاعدة البيانات التي يستخدمها مشروع Nexy الجديد عندما يتم إلغاء تعيين `DATABASE_URL`: ملف واحد، بدون خادم، وبرنامج التشغيل الخاص بـ Python، من خلال SQLModel، SQLAlchemy أو Tortoise-ORM.

## عندما يناسب SQLite

- التطوير والاختبارات والعروض التوضيحية: لا يوجد شيء للتثبيت أو البدء.
- موقع بخادم واحد ومتواضع يكتب: مدونة، أداة داخلية، متجر صغير.
- قراءة البيانات الثقيلة التي يتم شحنها مع التطبيق.

اختر [PostgreSQL ](postgresql.md) عندما تقوم عدة خوادم بالكتابة في وقت واحد، أو عندما تحتاج إلى أنواع منسقة والبحث عن النص الكامل على نطاق واسع.

## سلسلة الاتصال

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
```

| عنوان URL | قاعدة البيانات |
|---|---|
| `sqlite:///dev.db` | `dev.db`، نسبة إلى المجلد الذي يعمل فيه `nx dev` |
| `sqlite:////var/data/app.db` | المسار المطلق: أربع خطوط مائلة |
| `sqlite://` | في الذاكرة، ويختفي عندما تتوقف العملية |
| `sqlite+aiosqlite:///dev.db` | نفس الملف، من خلال برنامج التشغيل غير المتزامن |

## المحرك

`nx new` يكتب هذا الملف عند اختيار SQLModel. السطر الوحيد الذي يجب إضافته لـ SQLite هو `check_same_thread`: قد تستخدم الصفحة والمعالج المحرك من سلاسل رسائل مختلفة.

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

## المفاتيح الخارجية وWAL

SQLite لا يفرض المفاتيح الخارجية إلا إذا طلب منها ذلك لكل اتصال. يتيح وضع WAL للقراء الاستمرار أثناء الكتابة. كلاهما `PRAGMA` يتم تشغيلهما عند كل اتصال جديد، ويتم إعدادهما بجوار المحرك:

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

## نموذج

```python filename="src/models/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    done: bool = False
```

## جلسة لكل طلب

تفتح التبعية جلسة للطلب وتغلقها بعد الإجابة:

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

## القراءة والكتابة من المعالج

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

## إقرأ من إحدى الصفحات

تقوم صفحة `.nexy` بتشغيل مادتها الأمامية على الخادم، حتى تتمكن من استدعاء نفس الرمز. احتفظ بالاستعلام في دالة: فقط الأسماء المعينة في المستوى الأعلى من المادة الأمامية هي التي تصل إلى القالب.

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

## إنشاء الجداول مع الهجرات

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` يكتب `alembic/env.py`، الذي يستورد النماذج التي يقارنها مع قاعدة البيانات. قم باستيراد كل وحدة نموذجية جديدة هناك:

```python filename="الإنبك/env.py"
import src.models.note_model  # noqa: F401
```

SQLite لا يمكن `ALTER` وضع معظم الأعمدة في مكانها. قم بتشغيل الوضع الدفعي لـ Alembic، الذي ينسخ الجدول، في كلا استدعاءات `context.configure(...)` لـ `alembic/env.py`:

```python filename="الإنبك/env.py"
context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
```

## غير متزامن مع `aiosqlite`

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

## اختبارات على قاعدة بيانات في الذاكرة

`StaticPool` يحتفظ باتصال واحد، وبالتالي فإن قاعدة البيانات الموجودة في الذاكرة تظل صالحة للاختبار بأكمله. يتم تبديل تبعية المعالج بأخرى تستخدمه:

```python filename="الاختبارات/test_notes.py"
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

## في الإنتاج

- **احتفظ بالملف على قرص ثابت.** يتم فقدان نظام الملفات الخاص بالحاوية عند إعادة النشر: قم بتحميل وحدة تخزين وأشر `DATABASE_URL` إليها بمسار مطلق.
- **خادم واحد، ملف واحد.** SQLite لديه كاتب واحد في كل مرة. العديد من `nx start` العاملين على نفس الجهاز يتعاملون بشكل جيد مع WAL؛ عدة آلات ليست كذلك.
- **قم بعمل نسخة احتياطية أثناء تشغيله** مع `sqlite3 app.db ".backup backup.db"`، وليس مع نسخة ملف.

## الخطوات التالية

- [قواعد البيانات](../guides/databases.md)
- [استخدم PostgreSQL مع Nexy](postgresql.md)
- [الاختبار](../guides/testing.md)
